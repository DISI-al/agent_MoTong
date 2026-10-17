"""
main.py —— Flet 应用入口（Flet 1.0：入口是 ft.run，不是 ft.app）。

当前：输入框 -> 流式输出 -> 工具审批（允许/拒绝）-> 显示回复。
"""
import asyncio

import flet as ft

from agent.agent_loop import AgentLoop
from agent.state import AgentStateContainer


def _format_tools(tools: list) -> str:
    return "；".join(f"{t['name']}({t['arguments']})" for t in tools)


def main(page: ft.Page):
    page.title = "Agent 客户端"

    state = AgentStateContainer()
    loop = AgentLoop(state)

    output = ft.Text("")
    input_field = ft.TextField()

    approval_text = ft.Text("")
    approval_future = None

    def on_allow(e):
        if approval_future and not approval_future.done():
            approval_future.set_result(True)

    def on_reject(e):
        if approval_future and not approval_future.done():
            approval_future.set_result(False)

    approval_row = ft.Row(
        controls=[
            approval_text,
            ft.Button(content="允许", on_click=on_allow),
            ft.Button(content="拒绝", on_click=on_reject),
        ],
        visible=False,
    )

    async def on_approval_request(tools):
        nonlocal approval_future
        approval_text.value = f"要执行：{_format_tools(tools)}"
        approval_row.visible = True
        page.update()

        approval_future = asyncio.get_running_loop().create_future()
        approved = await approval_future

        approval_row.visible = False
        approval_text.value = ""
        page.update()
        return approved

    def on_send(e):
        text = input_field.value
        if not text:
            return
        input_field.value = ""
        page.run_task(run_turn, text)

    async def run_turn(text):
        output.value = ""
        page.update()

        async def on_text(delta):
            output.value += delta
            page.update()

        await loop.start_turn(
            text,
            on_text=on_text,
            on_approval_request=on_approval_request,
        )

    page.add(
        ft.Column(
            controls=[
                output,
                ft.Row(
                    controls=[
                        input_field,
                        ft.Button(content="发送", on_click=on_send),
                    ]
                ),
                approval_row,
            ]
        )
    )


ft.run(main)
