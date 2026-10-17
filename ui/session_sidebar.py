"""
session_sidebar.py —— 左侧会话侧边栏。

职责：会话列表展示、新建会话、切换会话。事件只触发 agent/db，不写业务。
（本步骤：静态占位，数据绑定后续接 db）
"""
import flet as ft


class SessionSidebar:
    def build(self) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("会话", size=16),
                    ft.Text("会话 1"),
                    ft.Text("会话 2"),
                    ft.Text("会话 3"),
                ],
            ),
            width=200,
            bgcolor=ft.Colors.BLUE_GREY_50,
        )

    def refresh_sessions(self) -> None:
        raise NotImplementedError("待我手动实现（接 db 时补）")
