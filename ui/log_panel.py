"""
log_panel.py —— 底部实时日志控制台。

职责：展示 Agent 运行日志（工具执行、返回码、错误等）。只展示。
"""
import flet as ft


class LogPanel:
    """底部日志控制台。"""

    def __init__(self) -> None:
        raise NotImplementedError("待我手动实现")

    def build(self) -> ft.Control:
        """构建日志区控件。"""
        raise NotImplementedError("待我手动实现")

    def log(self, text: str) -> None:
        """追加一行日志。"""
        raise NotImplementedError("待我手动实现")
