"""
agent_loop.py —— Agent 主循环（灵魂）。

职责：
1. 驱动一轮完整对话：发请求 -> 流式接收 -> 遇工具 -> 审批 -> 执行 -> 回传 -> 循环。
2. 支持暂停 / 取消。
3. 用 asyncio.Future 在审批时「原地挂起」，由 UI 按钮 set_result 唤醒。

核心机制（实现前必读）：
- 审批不是轮询 flag 死等，而是 await 一个 Future；UI 回调里 future.set_result(...)。
- 一次响应可能带多个 tool_use，审批粒度建议【批量一次】。
- 循环终止条件：Claude 返回纯文本且没有新的 tool_use。
"""
import asyncio

from agent.state import AgentState, AgentStateContainer


class AgentLoop:
    """可暂停、带人工审批的 Agent 主循环。"""

    def __init__(self, state: AgentStateContainer) -> None:
        raise NotImplementedError("待我手动实现")

    async def start_turn(self, session_id: int, user_text: str) -> None:
        """开始新一轮对话（仅当状态为 IDLE）。"""
        raise NotImplementedError("待我手动实现")

    async def _request_approval(self, tools: list[dict]) -> bool:
        """挂起等待用户审批，返回 True=允许 / False=拒绝。"""
        raise NotImplementedError("待我手动实现")

    async def _run_tool(self, tool_use: dict) -> dict:
        """调用 tools.executor 执行单个工具，返回 tool_result。"""
        raise NotImplementedError("待我手动实现")

    async def cancel(self) -> None:
        """取消当前运行（置 CANCELLED，并中断流式请求）。"""
        raise NotImplementedError("待我手动实现")
