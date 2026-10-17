"""
safe_path.py —— 路径安全校验（安全地基）。

职责：判断一个路径是否落在「工作目录白名单」内。

实现要点（防逃逸，务必用 resolve）：
- 用 Path.resolve() 拿到规范化真实路径后再比较；
  不能只做字符串前缀判断，否则 `../` 或符号链接可逃出白名单。
- 用 `root in resolved.parents` 逐级目录比较，避免字符串 startswith
  的前缀撞名（如 my_workspace 误匹配 my_workspace2）。
"""
from pathlib import Path


def is_safe_path(path: str | Path, roots: list[Path]) -> bool:
    """True = 安全（在白名单内）；False = 不安全。"""
    try:
        resolved = Path(path).resolve()
    except (OSError, RuntimeError):
        return False  # 路径解析不了，一律拒绝
    return any(resolved == root or root in resolved.parents for root in roots)


def resolve_safe(path: str | Path, roots: list[Path]) -> Path:
    """返回安全绝对路径；不安全就抛异常。"""
    if not is_safe_path(path, roots):
        raise PermissionError(f"拒绝访问：路径不在白名单内 -> {path}")
    return Path(path).resolve()
