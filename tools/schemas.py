"""
schemas.py —— 工具定义。

职责：
1. 每个工具对应的 Pydantic 参数模型（本地校验用）。
2. 生成 OpenAI function 格式的工具定义（给模型看）。

格式说明：DeepSeek 是 OpenAI 兼容接口，工具用 function 类型定义。
"""
from pydantic import BaseModel


# ---- Pydantic 参数模型（本地校验 / 文档用）----
class ReadFileParams(BaseModel):
    path: str


class ListDirParams(BaseModel):
    path: str


class WriteFileParams(BaseModel):
    path: str
    content: str


class RunShellParams(BaseModel):
    command: str


# ---- 给模型看的工具定义（OpenAI function 格式）----
def get_tool_schemas() -> list[dict]:
    """返回当前已实现工具的定义列表（先只放 read_file / list_dir）。"""
    return [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "读取一个文本文件的内容",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "文件路径"}
                    },
                    "required": ["path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_dir",
                "description": "列出目录下的文件和子目录名",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "目录路径"}
                    },
                    "required": ["path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "写入一个文本文件",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "文件路径"},
                        "content": {"type": "string", "description": "要写入的内容"},
                    },
                    "required": ["path", "content"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_shell",
                "description": "执行一个 shell 命令，返回 stdout/stderr/返回码",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "要执行的命令"},
                    },
                    "required": ["command"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "save_note",
                "description": "把内容保存为一条记忆笔记（Markdown 文件），存在 memory/ 目录下",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "笔记标题（作为文件名）"},
                        "content": {"type": "string", "description": "笔记内容（Markdown）"},
                    },
                    "required": ["title", "content"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "grep_files",
                "description": "在目录下搜索包含指定文本的文件，返回匹配的文件路径列表",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "要搜索的文本"},
                        "path": {"type": "string", "description": "要搜索的目录路径"},
                    },
                    "required": ["pattern", "path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "current_time",
                "description": "获取当前的日期和时间",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "append_file",
                "description": "往文件末尾追加内容（不覆盖原有内容）",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "文件路径"},
                        "content": {"type": "string", "description": "要追加的内容"},
                    },
                    "required": ["path", "content"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "fetch_url",
                "description": "抓取一个网页的文本内容（去掉 HTML 标签）",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "要抓取的网页 URL"},
                    },
                    "required": ["url"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "schedule_task",
                "description": "安排一个定时提醒任务，到时间会弹出提醒",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "提醒内容"},
                        "fire_at": {"type": "string", "description": "触发时间（YYYY-MM-DD HH:MM:SS），与 minutes/seconds 三选一"},
                        "minutes": {"type": "integer", "description": "多少分钟后触发"},
                        "seconds": {"type": "integer", "description": "多少秒后触发"},
                    },
                    "required": ["content"],
                },
            },
        },
    ]
