"""
main.py —— Flet 应用入口（Flet 1.0：入口是 ft.run，不是 ft.app）。

当前：输入框 -> 流式输出 -> 工具审批 -> 多轮对话（db 持久化）。
"""
import asyncio
from pathlib import Path

import flet as ft

import db
from agent.agent_loop import AgentLoop
from agent.state import AgentStateContainer

DB_PATH = Path("app.db")


def _format_tools(tools: list) -> str:
    return "；".join(f"{t['name']}({t['arguments']})" for t in tools)


def _role_label(role: str) -> str:
    return "你" if role == "user" else "助手"


def main(page: ft.Page):
    page.title = "Agent 客户端"

    # 初始化数据库，取最近的会话（没有就新建）
    db.init_db(DB_PATH)
    sessions = db.list_sessions()
    session_id = sessions[0]["id"] if sessions else db.create_session("默认会话")

    state = AgentStateContainer()
    loop = AgentLoop(state)

    output = ft.Text("")
    input_field = ft.TextField()

    # 启动时把已有历史显示出来（持久化效果）
    for m in db.load_messages(session_id):
        output.value += f"{_role_label(m['role'])}：{m['content']}\n\n"

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

    auto_approve = False

    def toggle_auto(e):
        nonlocal auto_approve
        auto_approve = not auto_approve
        auto_btn.content = f"自动允许：{'开' if auto_approve else '关'}"
        page.update()

    auto_btn = ft.Button(content="自动允许：关", on_click=toggle_auto)
    stop_btn = ft.Button(content="停止", on_click=lambda e: loop.cancel())

    async def on_approval_request(tools):
        nonlocal approval_future
        if auto_approve:
            return True  # 信任模式：不弹窗，直接允许
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
        # 加载历史（之前轮次的 user/assistant），转成 OpenAI 格式
        history = [
            {"role": m["role"], "content": m["content"]}
            for m in db.load_messages(session_id)
        ]

        output.value += f"你：{text}\n助手："
        page.update()

        async def on_text(delta):
            output.value += delta
            page.update()

        final = await loop.start_turn(
            text,
            history=history,
            on_text=on_text,
            on_approval_request=on_approval_request,
        )

        output.value += "\n\n"
        page.update()

        # 保存这一轮
        db.save_message(session_id, "user", text)
        if final:
            db.save_message(session_id, "assistant", final)

    page.add(
        ft.Column(
            controls=[
                ft.Column(
                    controls=[output],
                    height=400,
                    scroll=ft.ScrollMode.AUTO,
                    auto_scroll=True,
                ),
                ft.Row(
                    controls=[
                        input_field,
                        ft.Button(content="发送", on_click=on_send),
                        auto_btn,
                        stop_btn,
                    ]
                ),
                approval_row,
            ]
        )
    )


ft.run(main)
