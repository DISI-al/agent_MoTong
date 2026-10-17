"""
log_panel.py —— 底部实时日志控制台。

职责：展示 Agent 运行日志（工具执行、返回码、错误等）。只展示。
（本步骤：静态占位，实时日志后续接）
"""
import flet as ft


class LogPanel:
    def build(self) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("日志", size=16),
                    ft.Text("[12:00] Agent 启动"),
                    ft.Text("[12:01] 等待输入..."),
                ],
            ),
            height=150,
            bgcolor=ft.Colors.GREY_100,
        )

    def log(self, text: str) -> None:
        raise NotImplementedError("待我手动实现")
