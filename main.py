"""
main.py —— Flet 应用入口。

暗色 UI（Vercel 风）+ 会话列表（新建/切换）+ 完整 agent（流式/审批/工具/记忆/中断）。
"""
import asyncio
from pathlib import Path

import flet as ft
from flet import Border, BorderSide

import db
from agent.agent_loop import AgentLoop
from agent.state import AgentStateContainer

DB_PATH = Path("app.db")


def _format_tools(tools):
    return "；".join(f"{t['name']}({t['arguments']})" for t in tools)


def _role_label(role):
    return "你" if role == "user" else "助手"


def _format_history(messages):
    return "\n\n".join(f"{_role_label(m['role'])}：{m['content']}" for m in messages)


def main(page: ft.Page):
    # ===== 窗口 + 样式 =====
    page.title = "My Claude Harness"
    page.bgcolor = "#0a0a0a"
    page.window.width = 1180
    page.window.height = 800
    page.window.min_width = 900
    page.window.min_height = 600

    card_side = BorderSide(width=1, color="#27272a")
    card_border = Border(top=card_side, bottom=card_side, left=card_side, right=card_side)
    light = ft.ButtonStyle(color="#f1f1f1")

    # ===== db + agent =====
    db.init_db(DB_PATH)
    state = AgentStateContainer()
    loop = AgentLoop(state)

    current_session_id = None
    auto_approve = False
    approval_future = None

    # ===== 消息区 =====
    message_text = ft.Text("", color="#f1f1f1", selectable=True)
    message_area = ft.Container(
        expand=True,
        padding=20,
        bgcolor="#0a0a0a",
        content=ft.Column(
            controls=[message_text],
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            auto_scroll=True,
        ),
    )

    # ===== 侧边栏会话列表（动态） =====
    sidebar_list = ft.Column(controls=[], spacing=4)

    # ===== 输入框 =====
    input_field = ft.TextField(
        hint_text="输入消息，和 Claude 对话...",
        expand=True,
        bgcolor="#0a0a0a",
        border_color="#27272a",
        color="#f1f1f1",
    )

    # ===== 审批栏 =====
    approval_text = ft.Text("", color="#f1f1f1")

    # ===== 事件处理 =====
    def on_allow(e):
        if approval_future and not approval_future.done():
            approval_future.set_result(True)

    def on_reject(e):
        if approval_future and not approval_future.done():
            approval_future.set_result(False)

    def toggle_auto(e):
        nonlocal auto_approve
        auto_approve = not auto_approve
        auto_btn.content = f"自动允许：{'开' if auto_approve else '关'}"
        page.update()

    def on_send(e):
        text = input_field.value
        if not text or current_session_id is None:
            return
        input_field.value = ""
        page.run_task(run_turn, text)

    def refresh_sessions():
        sidebar_list.controls = [
            ft.TextButton(
                s["title"],
                style=light,
                on_click=lambda e, sid=s["id"]: switch_session(sid),
            )
            for s in db.list_sessions()
        ]
        page.update()

    def switch_session(sid):
        nonlocal current_session_id
        current_session_id = sid
        message_text.value = _format_history(db.load_messages(sid))
        page.update()

    def new_session(e):
        sid = db.create_session("新对话")
        refresh_sessions()
        switch_session(sid)

    approval_row = ft.Row(
        controls=[
            approval_text,
            ft.FilledButton("允许", on_click=on_allow),
            ft.FilledButton("拒绝", on_click=on_reject),
        ],
        visible=False,
    )
    auto_btn = ft.TextButton(content="自动允许：关", style=light, on_click=toggle_auto)
    stop_btn = ft.TextButton(content="停止", style=light, on_click=lambda e: loop.cancel())

    async def on_approval_request(tools):
        nonlocal approval_future
        if auto_approve:
            return True
        approval_text.value = f"要执行：{_format_tools(tools)}"
        approval_row.visible = True
        page.update()

        approval_future = asyncio.get_running_loop().create_future()
        approved = await approval_future

        approval_row.visible = False
        approval_text.value = ""
        page.update()
        return approved

    async def run_turn(text):
        history = [
            {"role": m["role"], "content": m["content"]}
            for m in db.load_messages(current_session_id)
        ]
        message_text.value += f"\n\n你：{text}\n助手："
        page.update()

        async def on_text(delta):
            message_text.value += delta
            page.update()

        final = await loop.start_turn(
            text,
            history=history,
            on_text=on_text,
            on_approval_request=on_approval_request,
        )

        db.save_message(current_session_id, "user", text)
        if final:
            db.save_message(current_session_id, "assistant", final)

    # ===== 布局 =====
    sidebar = ft.Container(
        width=280,
        padding=20,
        bgcolor="#111111",
        border=card_border,
        border_radius=12,
        content=ft.Column(
            controls=[
                ft.Text("会话列表", size=20, weight=ft.FontWeight.W_600, color="#f1f1f1"),
                ft.Divider(color="#27272a", height=1),
                ft.TextButton("＋ 新建对话", style=light, on_click=new_session),
                sidebar_list,
            ],
            spacing=12,
        ),
    )

    input_box_area = ft.Container(
        padding=12,
        bgcolor="#111111",
        border=card_border,
        border_radius=12,
        content=ft.Row(
            controls=[
                input_field,
                ft.FilledButton("发送", bgcolor="#ffffff", color="#000000", on_click=on_send),
                auto_btn,
                stop_btn,
            ],
            spacing=12,
        ),
    )

    main_panel = ft.Column(
        controls=[message_area, approval_row, input_box_area],
        expand=True,
        spacing=16,
    )

    page.add(ft.Row(controls=[sidebar, main_panel], expand=True, spacing=16))

    # ===== 初始化：加载会话（默认切到最新） =====
    sessions = db.list_sessions()
    if sessions:
        current_session_id = sessions[0]["id"]
        message_text.value = _format_history(db.load_messages(current_session_id))
    else:
        current_session_id = db.create_session("新对话")
        message_text.value = ""
    sidebar_list.controls = [
        ft.TextButton(
            s["title"],
            style=light,
            on_click=lambda e, sid=s["id"]: switch_session(sid),
        )
        for s in db.list_sessions()
    ]


ft.run(main)
