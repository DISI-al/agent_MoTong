"""
registry.py —— 工具注册表。

职责：维护「工具名 -> 执行函数」的映射，供 executor 按名分发。
"""
from typing import Awaitable, Callable

# 类型别名：工具执行函数 = 接收参数字典、返回结果字典的异步函数
ToolHandler = Callable[[dict], Awaitable[dict]]

_REGISTRY: dict[str, ToolHandler] = {}


def register(name: str) -> Callable:
    """装饰器：把一个 async 函数注册为工具（按 name 存进 _REGISTRY）。"""
    raise NotImplementedError("待我手动实现")


def get_handler(name: str) -> ToolHandler | None:
    """按工具名取执行函数；不存在返回 None。"""
    raise NotImplementedError("待我手动实现")


def list_tools() -> list[str]:
    """列出所有已注册工具名。"""
    raise NotImplementedError("待我手动实现")
