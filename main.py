"""
main.py —— Flet 应用入口（Flet 1.0：入口是 ft.run，不是 ft.app）。

职责：
1. 以桌面窗口模式启动。
2. 初始化三栏布局：左侧会话侧边栏 | 中间聊天区 | 底部日志区。
3. 把 UI 事件绑定到 agent/tools/db（后续步骤接）。

架构红线：
- UI 只负责「展示 + 接收点击 + 触发」，不写业务。
- 单 asyncio 事件循环：接 agent_loop 时把本函数改成 async def 即可。
"""
import flet as ft

from ui.chat_panel import ChatPanel
from ui.log_panel import LogPanel
from ui.session_sidebar import SessionSidebar


def main(page: ft.Page):
    page.title = "Agent 客户端"
    page.bgcolor = ft.Colors.WHITE

    sidebar = SessionSidebar().build()
    chat = ChatPanel().build()
    log = LogPanel().build()

    page.add(
        ft.Row(
            controls=[
                sidebar,
                ft.Column(controls=[chat, log]),
            ],
        )
    )


ft.run(main)
