"""
safe_path.py —— 路径安全校验（安全地基）。

职责：判断一个路径是否落在「工作目录白名单」内。

实现要点（防逃逸，务必用 resolve）：
- 用 Path.resolve() 拿到规范化真实路径后再比较前缀；
  不能只做字符串前缀判断，否则 `../` 或符号链接可逃出白名单。
"""
from pathlib import Path


def is_safe_path(path: str | Path, roots: list[Path]) -> bool:
    """判断 path 是否落在白名单 roots 内；不在则返回 False。"""
    raise NotImplementedError("待我手动实现")


def resolve_safe(path: str | Path, roots: list[Path]) -> Path:
    """返回解析后的安全绝对路径；不安全则抛出异常。"""
    raise NotImplementedError("待我手动实现")
