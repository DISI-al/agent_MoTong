"""
chat_panel.py —— 中间聊天视图。

职责：展示对话消息、流式追加 assistant 文本。只展示，不持有业务状态。
（本步骤：静态占位，流式追加后续接）
"""
import flet as ft


class ChatPanel:
    def build(self) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("用户：你好", size=14),
                    ft.Text("助手：你好！有什么可以帮你？", size=14),
                ],
            ),
            height=400,
            bgcolor=ft.Colors.WHITE,
        )

    def append_message(self, role: str, content: str) -> None:
        raise NotImplementedError("待我手动实现")

    def append_stream_delta(self, text: str) -> None:
        raise NotImplementedError("待我手动实现")
