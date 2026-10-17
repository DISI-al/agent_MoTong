"""
executor.py —— 工具执行器（安全闸门）。

职责：
1. 执行前先做路径安全校验（utils.safe_path），不在白名单内直接拒绝。
2. 按工具名从 registry 取执行函数并执行。
3. 捕获异常，包装成统一的结果格式。

安全红线：
- shell 与文件写入必须经用户审批后才允许执行（审批在 agent_loop 层）。
- 本层不信任任何路径，一律过 safe_path（用 resolve() 防 ../ 与符号链接逃逸）。
"""
import asyncio
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

import httpx

import db
from config import get_workspace_roots
from utils.safe_path import resolve_safe
from tools.registry import get_handler, register


@register("read_file")
async def _read_file(args: dict) -> dict:
    """读取文件内容（args 里的 path 已由 execute 校验过）。"""
    path = args["path"]
    content = await asyncio.to_thread(Path(path).read_text, encoding="utf-8")
    return {"content": content}


@register("list_dir")
async def _list_dir(args: dict) -> dict:
    """列出目录内容（目录小，同步读即可）。"""
    path = args["path"]
    entries = sorted(p.name for p in Path(path).iterdir())
    return {"entries": entries}


@register("write_file")
async def _write_file(args: dict) -> dict:
    """写入文件（path 已由 execute 校验过白名单）。"""
    path = args["path"]
    content = args["content"]
    await asyncio.to_thread(Path(path).write_text, content, encoding="utf-8")
    return {"written": path, "bytes": len(content)}


@register("run_shell")
async def _run_shell(args: dict) -> dict:
    """执行 shell 命令（安全性靠审批门，不靠路径白名单）。"""
    command = args["command"]
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return {
        "returncode": proc.returncode,
        "stdout": stdout.decode(errors="replace"),
        "stderr": stderr.decode(errors="replace"),
    }


@register("save_note")
async def _save_note(args: dict) -> dict:
    """把内容保存为一条记忆笔记（写入 memory/ 目录）。"""
    title = args["title"]
    content = args["content"]
    # 标题做安全处理，防止路径穿越
    safe_title = "".join(c if (c.isalnum() or c in "-_ ") else "_" for c in title).strip() or "note"
    memory_dir = Path("memory")
    memory_dir.mkdir(exist_ok=True)
    path = memory_dir / f"{safe_title}.md"
    await asyncio.to_thread(path.write_text, content, encoding="utf-8")
    return {"saved": str(path), "title": title}


@register("grep_files")
async def _grep_files(args: dict) -> dict:
    """在目录下搜索包含指定文本的文件。"""
    pattern = args["pattern"]
    directory = args["path"]
    matches = []

    def search():
        for filepath in Path(directory).rglob("*"):
            if not filepath.is_file():
                continue
            try:
                if pattern in filepath.read_text(encoding="utf-8", errors="ignore"):
                    matches.append(str(filepath))
            except Exception:
                continue

    await asyncio.to_thread(search)
    return {"matches": matches}


@register("current_time")
async def _current_time(args: dict) -> dict:
    """返回当前日期和时间。"""
    return {"now": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


@register("append_file")
async def _append_file(args: dict) -> dict:
    """往文件末尾追加内容（path 已由 execute 校验过白名单）。"""
    path = args["path"]
    content = args["content"]

    def append():
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)

    await asyncio.to_thread(append)
    return {"appended": path}


@register("fetch_url")
async def _fetch_url(args: dict) -> dict:
    """抓取网页文本内容（去掉 HTML 标签）。"""
    url = args["url"]
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        resp = await client.get(url)
        resp.raise_for_status()
    text = re.sub(r"<[^>]+>", " ", resp.text)
    text = re.sub(r"\s+", " ", text).strip()
    return {"status": resp.status_code, "text": text[:5000]}


@register("schedule_task")
async def _schedule_task(args: dict) -> dict:
    """安排一个定时提醒任务。"""
    content = args["content"]
    fire_at = args.get("fire_at")
    minutes = args.get("minutes")
    seconds = args.get("seconds")
    if not fire_at and (minutes or seconds):
        delta = timedelta(minutes=minutes or 0, seconds=seconds or 0)
        fire_at = (datetime.now() + delta).strftime("%Y-%m-%d %H:%M:%S")
    if not fire_at:
        return {"error": "需要提供 fire_at、minutes 或 seconds 之一"}
    task_id = db.add_task(content, fire_at)
    return {"task_id": task_id, "fire_at": fire_at}


async def execute(tool_name: str, tool_input: dict) -> dict:
    """执行一个工具：查处理器 -> 校验路径 -> 执行 -> 返回结果。"""
    handler = get_handler(tool_name)
    if handler is None:
        return {"error": f"未知工具: {tool_name}"}

    # 路径安全闸门：带 path 参数的工具，先过白名单校验
    if "path" in tool_input:
        try:
            tool_input["path"] = str(resolve_safe(tool_input["path"], get_workspace_roots()))
        except PermissionError as e:
            return {"error": str(e)}

    try:
        return await handler(tool_input)
    except Exception as e:
        return {"error": f"执行失败: {e}"}
