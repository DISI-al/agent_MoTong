"""
main.py —— Flet 应用入口。

职责：
1. 以【桌面窗口模式】启动 Flet（不是浏览器模式）。
2. 初始化顶层布局：左侧会话侧边栏 | 中间聊天区 | 底部日志区。
3. 把 UI 事件（发消息、新建会话、审批按钮等）绑定到 agent / tools / db 的接口。

架构红线（务必遵守）：
- UI 只负责「展示 + 接收点击 + 触发」，绝不在这里写业务逻辑。
- 会话、Agent 状态、工具调用全部在 agent / tools / db 里，UI 只订阅与触发。
- 采用【单 asyncio 事件循环】方案：agent_loop 作为 asyncio.Task
  跑在 Flet 的 async 事件循环里；审批用 asyncio.Future 挂起/唤醒。
"""
import asyncio

import flet as ft


async def main(page: ft.Page) -> None:
    """Flet 异步入口：初始化布局、挂载各面板、启动事件绑定。"""
    raise NotImplementedError("待我手动实现")


if __name__ == "__main__":
    # 桌面窗口模式启动（async 入口，Flet 1.0）：ft.run_async(main)
    raise NotImplementedError("待我手动实现")
