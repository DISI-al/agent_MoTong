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
    ]
