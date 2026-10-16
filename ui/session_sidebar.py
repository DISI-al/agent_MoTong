"""
session_sidebar.py —— 左侧会话侧边栏。

职责：会话列表展示、新建会话、切换会话。事件只触发 agent / db，不写业务。
"""
import flet as ft


class SessionSidebar:
    """左侧会话列表 + 新建按钮。"""

    def __init__(self) -> None:
        raise NotImplementedError("待我手动实现")

    def build(self) -> ft.Control:
        """构建侧边栏控件。"""
        raise NotImplementedError("待我手动实现")

    def refresh_sessions(self) -> None:
        """从 db 重新加载会话列表。"""
        raise NotImplementedError("待我手动实现")
