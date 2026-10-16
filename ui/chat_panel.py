"""
chat_panel.py —— 中间聊天视图。

职责：展示对话消息、流式追加 assistant 文本。只展示，不持有业务状态。
"""
import flet as ft


class ChatPanel:
    """中间聊天区。"""

    def __init__(self) -> None:
        raise NotImplementedError("待我手动实现")

    def build(self) -> ft.Control:
        """构建聊天区控件。"""
        raise NotImplementedError("待我手动实现")

    def append_message(self, role: str, content: str) -> None:
        """追加一条完整消息。"""
        raise NotImplementedError("待我手动实现")

    def append_stream_delta(self, text: str) -> None:
        """流式追加一段文本到当前 assistant 消息。"""
        raise NotImplementedError("待我手动实现")
