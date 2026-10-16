"""
schemas.py —— 工具定义。

职责：
1. 每个工具一个 JSON Schema（给 Claude 识别工具 + 参数）。
2. 每个工具对应的 Pydantic 参数模型（本地校验）。

首批工具（按实现顺序）：read_file / list_dir，再补 write_file / run_shell。
"""
from pydantic import BaseModel


# ---- Pydantic 参数模型（本地校验用）----
class ReadFileParams(BaseModel):
    path: str


class ListDirParams(BaseModel):
    path: str


class WriteFileParams(BaseModel):
    path: str
    content: str


class RunShellParams(BaseModel):
    command: str


# ---- 给 Claude 的工具 JSON Schema 列表 ----
def get_tool_schemas() -> list[dict]:
    """返回全部工具的 JSON Schema 列表，用于 Messages API 的 tools 参数。"""
    raise NotImplementedError("待我手动实现")
