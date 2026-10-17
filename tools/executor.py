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
import subprocess
from pathlib import Path

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
