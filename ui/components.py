"""
components.py —— 可复用 UI 组件。

职责：消息卡片、日志行、审批弹窗等控件的构建函数/类。只负责展示。
"""
import flet as ft


def message_card(role: str, content: str) -> ft.Control:
    """按角色（user / assistant / tool）生成一条消息卡片。"""
    raise NotImplementedError("待我手动实现")


def log_line(text: str) -> ft.Control:
    """生成一条日志行控件。"""
    raise NotImplementedError("待我手动实现")


class ApprovalDialog:
    """审批弹窗：展示待执行工具 + 参数，收集用户决定（允许/拒绝）。"""

    def __init__(self, tools: list[dict]) -> None:
        raise NotImplementedError("待我手动实现")

    def build(self) -> ft.Control:
        """构建弹窗控件。"""
        raise NotImplementedError("待我手动实现")
