"""
main.py —— Flet 应用入口。

Vercel 暗色 UI + 会话列表（新建/切换/删除）+ 完整 agent（流式/审批/工具/记忆/中断）。
"""
import asyncio
from datetime import datetime
from pathlib import Path

import flet as ft

import db
from agent.agent_loop import AgentLoop
from agent.llm_client import reset_client
from agent.state import AgentStateContainer
from config import get_settings_for_ui, save_settings
from tools.schemas import get_tool_schemas
from ui.components import build_message_bubble, build_session_item, build_styles

DB_PATH = Path("app.db")


def _format_tools(tools):
    return "；".join(f"{t['name']}({t['arguments']})" for t in tools)


def main(page: ft.Page):
    # ====================== 窗口全局配置 ======================
    page.title = "My Claude Harness"
    page.bgcolor = "#0a0a0a"
    page.window.width = 1180
    page.window.height = 800
    page.window.min_width = 900
    page.window.min_height = 600
    page.theme_mode = ft.ThemeMode.DARK
    page.window.icon = str(Path(__file__).parent / "favicon.ico")

    # ====================== 全局样式 ======================
    _styles = build_styles()
    card_border = _styles["card_border"]
    light_btn_style = _styles["light"]
    icon_btn_style = _styles["icon"]
    primary_btn_style = _styles["primary"]
    secondary_btn_style = _styles["secondary"]
    danger_btn_style = _styles["danger"]
    danger_filled_style = _styles["danger_filled"]

    # ====================== db + agent ======================
    db.init_db(DB_PATH)
    state = AgentStateContainer()
    loop = AgentLoop(state)

    current_session_id = None
    auto_approve = False
    approval_future = None

    # ====================== UI 组件 ======================
    message_column = ft.Column(
        controls=[], spacing=14, scroll=ft.ScrollMode.AUTO, auto_scroll=True,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )
    message_area = ft.Container(expand=True, padding=20, bgcolor="#0a0a0a", content=message_column)

    sidebar_list = ft.Column(controls=[], spacing=4, expand=True)
    task_list = ft.Column(controls=[], spacing=4)

    input_field = ft.TextField(
        hint_text="输入消息，发送给 Claude...",
        expand=True,
        bgcolor="#111111",
        border_color="#222222",
        color="#e5e5e5",
        multiline=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        border_radius=6,
    )

    approval_text = ft.Text("Claude 请求调用工具，是否允许执行？", color="#e5e5e5", size=14, text_align=ft.TextAlign.CENTER)
    usage_text = ft.Text("", color="#666666", size=12)

    # ====================== 回调 ======================
    def on_allow(e):
        if approval_future and not approval_future.done():
            approval_future.set_result(True)

    def on_reject(e):
        if approval_future and not approval_future.done():
            approval_future.set_result(False)

    def toggle_auto(e):
        nonlocal auto_approve
        auto_approve = not auto_approve
        auto_btn.content = "自动许可：开" if auto_approve else "自动许可"
        auto_btn.style = danger_btn_style if auto_approve else light_btn_style
        page.update()

    def on_stop(e):
        loop.cancel()

    def input_change(e):
        send_btn.disabled = input_field.value.strip() == ""
        page.update()

    def on_send(e):
        text = input_field.value.strip()
        if not text or current_session_id is None:
            return
        input_field.value = ""
        send_btn.disabled = True
        page.update()
        page.run_task(run_turn, text)

    def refresh_sessions():
        sessions = db.list_sessions()
        if not sessions:
            sidebar_list.controls = [ft.Text("暂无会话，点击新建对话", color="#666666", size=14)]
        else:
            sidebar_list.controls = [
                build_session_item(s["id"], s["title"], s["id"] == current_session_id, icon_btn_style, on_delete_session, switch_session)
                for s in sessions
            ]
        page.update()

    def switch_session(sid):
        nonlocal current_session_id
        current_session_id = sid
        message_column.controls = [
            build_message_bubble(m["content"], m["role"] == "user", icon_btn_style)[0]
            for m in db.load_messages(sid)
        ]
        refresh_sessions()  # 重建侧边栏，更新选中高亮

    def new_session(e):
        sid = db.create_session("新对话")
        refresh_sessions()
        switch_session(sid)

    def on_delete_session(sid):
        nonlocal current_session_id
        db.delete_session(sid)
        if current_session_id == sid:
            current_session_id = None
        refresh_sessions()
        sessions = db.list_sessions()
        if sessions:
            switch_session(sessions[0]["id"])
        else:
            message_column.controls = []
            page.update()

    def build_task_item(task):
        del_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE, icon_size=14, style=icon_btn_style,
            tooltip="删除任务", on_click=lambda e, tid=task["id"]: delete_task_click(tid),
        )
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        f"{task['fire_at'][5:16]} · {task['content']}",
                        color="#a1a1aa", expand=True, overflow=ft.TextOverflow.ELLIPSIS, size=12,
                    ),
                    del_btn,
                ],
                spacing=4,
            ),
        )

    def refresh_task_list():
        tasks = db.list_tasks()
        if not tasks:
            task_list.controls = [ft.Text("暂无定时任务", color="#666666", size=12)]
        else:
            task_list.controls = [build_task_item(t) for t in tasks]

    def delete_task_click(tid):
        db.delete_task(tid)
        refresh_task_list()
        page.update()

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
        page.update()
        return approved

    async def run_turn(text):
        history = [
            {"role": m["role"], "content": m["content"]}
            for m in db.load_messages(current_session_id)
        ]

        # 用户气泡
        user_row, _ = build_message_bubble(text, True, icon_btn_style)
        message_column.controls.append(user_row)
        # 助手气泡（流式写入）
        assistant_row, assistant_md = build_message_bubble("", False, icon_btn_style)
        message_column.controls.append(assistant_row)
        page.update()

        async def on_text(delta):
            assistant_md.value += delta
            page.update()

        final, usage = await loop.start_turn(
            text,
            history=history,
            on_text=on_text,
            on_approval_request=on_approval_request,
        )

        if usage:
            usage_text.value = f"tokens {usage.total_tokens}（输入 {usage.prompt_tokens} + 输出 {usage.completion_tokens}）"
            page.update()

        db.save_message(current_session_id, "user", text)
        if final:
            db.save_message(current_session_id, "assistant", final)
        elif assistant_md.value.strip():
            # 被中断时也可能有部分文本，一并保存
            db.save_message(current_session_id, "assistant", assistant_md.value)

        # 第一条消息：用消息内容自动命名会话
        if not history:
            title = text[:20] + ("…" if len(text) > 20 else "")
            db.update_session_title(current_session_id, title)
            refresh_sessions()

        refresh_task_list()  # 工具可能新增了任务，刷新任务列表

    async def scheduler_loop():
        """后台循环：每秒检查一次到期的定时任务。"""
        while True:
            try:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                due = db.get_due_tasks(now)
                if due:
                    for task in due:
                        reminder, _ = build_message_bubble(f"⏰ 提醒：{task['content']}", False, icon_btn_style)
                        message_column.controls.append(reminder)
                        db.mark_task_done(task["id"])
                    refresh_task_list()
                    page.update()
            except Exception:
                pass
            await asyncio.sleep(1)

    # ====================== 审批栏 + 按钮 ======================
    approval_row = ft.Column(
        controls=[
            approval_text,
            ft.Row(
                [
                    ft.FilledButton(content="允许", style=secondary_btn_style, on_click=on_allow),
                    ft.FilledButton(content="拒绝", style=danger_filled_style, on_click=on_reject),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=12,
            ),
        ],
        visible=False,
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )
    send_btn = ft.FilledButton(content="发送", style=primary_btn_style, on_click=on_send, disabled=True)
    auto_btn = ft.TextButton(content="自动许可", style=light_btn_style, on_click=toggle_auto)
    stop_btn = ft.FilledButton(content="停止", style=secondary_btn_style, on_click=on_stop)

    input_field.on_change = input_change
    input_field.on_submit = on_send

    input_box_area = ft.Container(
        padding=12,
        bgcolor="#0a0a0a",
        content=ft.Row(controls=[input_field, send_btn, auto_btn, stop_btn], spacing=10),
    )

    # ====================== 设置对话框 ======================
    ui_settings = get_settings_for_ui()

    api_key_field = ft.TextField(
        label="API Key", password=True, value=ui_settings["api_key"],
        bgcolor="#111111", color="#e5e5e5",
    )
    model_field = ft.TextField(
        label="模型", value=ui_settings["model"],
        bgcolor="#111111", color="#e5e5e5",
    )
    workspace_field = ft.TextField(
        label="工作目录白名单（逗号分隔）", value=ui_settings["workspace_roots"],
        bgcolor="#111111", color="#e5e5e5",
    )

    def save_settings_click(e):
        save_settings({
            "api_key": api_key_field.value.strip(),
            "model": model_field.value.strip() or "deepseek-chat",
            "workspace_roots": workspace_field.value.strip(),
        })
        reset_client()  # 让新 Key 下次请求生效
        page.pop_dialog()

    settings_dialog = ft.AlertDialog(
        title=ft.Text("设置", color="#e5e5e5"),
        content=ft.Column(
            controls=[
                api_key_field,
                model_field,
                workspace_field,
            ],
            spacing=14,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            width=440,
        ),
        actions=[
            ft.FilledButton(content="保存", style=primary_btn_style, on_click=save_settings_click),
            ft.FilledButton(content="关闭", style=secondary_btn_style, on_click=lambda e: page.pop_dialog()),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )

    def open_settings(e):
        page.show_dialog(settings_dialog)

    # ====================== 布局 ======================
    sidebar = ft.Container(
        width=280,
        padding=20,
        bgcolor="#111111",
        border=card_border,
        border_radius=10,
        content=ft.Column(
            controls=[
                ft.Text("会话列表", size=18, weight=ft.FontWeight.W_500, color="#e5e5e5"),
                ft.Divider(color="#222222", height=1),
                ft.Row(
                    [ft.TextButton(content="＋ 新建对话", style=light_btn_style, on_click=new_session)],
                    alignment=ft.MainAxisAlignment.START,
                ),
                sidebar_list,
                ft.Divider(color="#222222", height=1),
                ft.Text("定时任务", size=14, weight=ft.FontWeight.W_500, color="#e5e5e5"),
                task_list,
                ft.IconButton(
                    icon=ft.Icons.SETTINGS,
                    icon_size=18,
                    style=icon_btn_style,
                    tooltip="设置",
                    on_click=open_settings,
                ),
            ],
            spacing=12,
            expand=True,
        ),
    )

    main_panel = ft.Column(
        controls=[message_area, approval_row, input_box_area, usage_text],
        expand=True,
        spacing=14,
    )

    page.add(ft.Row(controls=[sidebar, main_panel], expand=True, spacing=16))

    # ====================== 初始化 ======================
    refresh_sessions()
    sessions = db.list_sessions()
    if sessions:
        switch_session(sessions[0]["id"])
    refresh_task_list()
    page.run_task(scheduler_loop)


ft.run(main)
