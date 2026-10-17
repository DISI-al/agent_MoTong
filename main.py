"""
main.py —— Flet 应用入口（Flet 1.0：入口是 ft.run，不是 ft.app）。

最小接线版：输入框 -> 点发送 -> 后台跑 agent -> 显示最终回复。
后续再接入：流式显示、审批弹窗、会话列表。
"""
import flet as ft

from agent.agent_loop import AgentLoop
from agent.state import AgentStateContainer


def main(page: ft.Page):
    page.title = "Agent 客户端"

    state = AgentStateContainer()
    loop = AgentLoop(state)

    output = ft.Text("")
    input_field = ft.TextField()

    def on_send(e):
        text = input_field.value
        if not text:
            return
        input_field.value = ""
        page.run_task(run_turn, text)

    async def run_turn(text):
        output.value = "思考中..."
        page.update()
        final = await loop.start_turn(text)
        output.value = final
        page.update()

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
            ]
        )
    )


ft.run(main)
