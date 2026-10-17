"""
agent_loop.py —— Agent 主循环（灵魂，第一版）。

职责：
1. 驱动一轮完整对话：发请求 -> 流式接收 -> 遇工具 -> 审批 -> 执行 -> 回传 -> 循环。
2. 状态机流转：IDLE -> WAIT_LLM -> WAIT_APPROVAL -> RUN_TOOL -> ... -> IDLE。
3. 支持取消。

第一版说明（后续会改）：
- 审批 _request_approval 是【占位】：打印 + 自动允许；TODO 换成 asyncio.Future + UI 弹窗。
- 暂未接入 db（会话持久化）、暂未实时刷 UI。
- 工具调用走 OpenAI 格式：assistant 消息带 tool_calls，结果用 role="tool" 回传。
"""
import asyncio
import json

from agent.llm_client import stream_message
from agent.state import AgentState, AgentStateContainer
from agent.stream_parser import StreamParser
from tools.executor import execute as execute_tool
from tools.schemas import get_tool_schemas

MAX_TOOL_ROUNDS = 10  # 最多工具调用轮数，防死循环

SYSTEM_PROMPT = "你是一个本地文件助手，可以使用工具读取文件、列出目录。需要时调用工具完成任务。"


class AgentLoop:
    """可暂停、带人工审批的 Agent 主循环。"""

    def __init__(self, state: AgentStateContainer) -> None:
        self._state = state
        self._cancelled = False

    async def start_turn(
        self,
        user_text: str,
        history: list | None = None,
        on_text=None,
        on_approval_request=None,
    ) -> str:
        """开始一轮对话，返回最终的 assistant 文本。

        on_text: 可选 async 回调，每收到一段文字增量时调用（用于实时流式显示）。
        on_approval_request: 可选 async 回调，需要审批工具时调用，返回 bool（允许/拒绝）。
        """
        self._cancelled = False
        self._state.set(AgentState.WAIT_LLM)

        messages = list(history) if history else []
        messages.append({"role": "user", "content": user_text})

        final_text = ""

        for _ in range(MAX_TOOL_ROUNDS):
            # 1. 流式请求，边收边拼
            parser = StreamParser()
            async for chunk in stream_message(
                messages, tools=get_tool_schemas(), system=SYSTEM_PROMPT
            ):
                delta = chunk.choices[0].delta
                if delta.content:
                    parser.feed_text(delta.content)
                    if on_text:
                        await on_text(delta.content)  # 实时回调给 UI
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        parser.feed_tool_call(
                            index=tc.index,
                            tool_id=tc.id,
                            name=tc.function.name if tc.function else None,
                            arguments=tc.function.arguments if tc.function else None,
                        )

            text = parser.text()
            tools = parser.completed_tools()

            # 2. 没有工具调用 → 本轮结束
            if not tools:
                final_text = text
                break

            # 3. 有工具调用 → 审批 → 执行 → 回传
            self._state.set(AgentState.WAIT_APPROVAL)
            if on_approval_request:
                approved = await on_approval_request(tools)
            else:
                approved = await self._request_approval(tools)

            # 把 assistant 的 tool_calls 消息加进历史（OpenAI 格式）
            messages.append(
                {
                    "role": "assistant",
                    "content": text or None,
                    "tool_calls": [
                        {
                            "id": t["id"],
                            "type": "function",
                            "function": {
                                "name": t["name"],
                                "arguments": json.dumps(t["arguments"], ensure_ascii=False),
                            },
                        }
                        for t in tools
                    ],
                }
            )

            # 逐个执行工具，结果用 role="tool" 回传
            self._state.set(AgentState.RUN_TOOL)
            for t in tools:
                if approved:
                    result = await self._run_tool(t)
                else:
                    result = {"error": "用户拒绝执行该工具"}
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": t["id"],
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                )

            if self._cancelled:
                break

        self._state.set(AgentState.IDLE)
        return final_text

    async def _request_approval(self, tools: list[dict]) -> bool:
        """占位审批：打印待执行工具并自动允许。TODO：换成 Future + UI 弹窗。"""
        for t in tools:
            print(f"[审批占位] 将执行 {t['name']}({t['arguments']}) —— 自动允许")
        return True

    async def _run_tool(self, tool: dict) -> dict:
        """执行单个工具，返回结果 dict。"""
        return await execute_tool(tool["name"], tool["arguments"])

    async def cancel(self) -> None:
        """取消当前轮（置 CANCELLED；第一版只设标志，不中途强行中断流）。"""
        self._cancelled = True
        self._state.set(AgentState.CANCELLED)
