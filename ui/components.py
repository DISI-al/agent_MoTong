"""
components.py —— 可复用 UI 组件 + 全局样式。

只负责「构建控件」，业务逻辑（回调、数据）由调用方通过参数传入。
"""
import flet as ft
from flet import Border, BorderSide, ControlState


def build_styles() -> dict:
    """返回全局样式：卡片边框 + 各类按钮样式。"""
    card_side = BorderSide(width=1, color="#222222")
    card_border = Border(top=card_side, bottom=card_side, left=card_side, right=card_side)
    return {
        "card_border": card_border,
        "light": ft.ButtonStyle(
            color={ControlState.DEFAULT: "#a1a1aa", ControlState.HOVERED: "#ffffff"},
            animation_duration=180,
            shape=ft.RoundedRectangleBorder(radius=6),
        ),
        "icon": ft.ButtonStyle(
            bgcolor={ControlState.HOVERED: "#1f1f1f"},
            color={ControlState.DEFAULT: "#888888", ControlState.HOVERED: "#ffffff"},
            shape=ft.RoundedRectangleBorder(radius=5),
            animation_duration=180,
        ),
        "primary": ft.ButtonStyle(
            bgcolor={ControlState.DEFAULT: "#ffffff", ControlState.HOVERED: "#e5e5e5"},
            color="#0a0a0a",
            shape=ft.RoundedRectangleBorder(radius=6),
            animation_duration=180,
        ),
        "secondary": ft.ButtonStyle(
            bgcolor={ControlState.DEFAULT: "#171717", ControlState.HOVERED: "#222222"},
            color="#f1f1f1",
            shape=ft.RoundedRectangleBorder(radius=6),
            animation_duration=180,
        ),
        "danger": ft.ButtonStyle(
            color="#f87171",
            shape=ft.RoundedRectangleBorder(radius=6),
            animation_duration=180,
        ),
        "danger_filled": ft.ButtonStyle(
            bgcolor={ControlState.DEFAULT: "#171717", ControlState.HOVERED: "#222222"},
            color="#f87171",
            shape=ft.RoundedRectangleBorder(radius=6),
            animation_duration=180,
        ),
    }


def build_message_bubble(content: str, is_user: bool, icon_btn_style) -> tuple:
    """构建一条消息气泡，返回 (气泡行, Markdown控件) 供流式写入。"""
    copy_btn = ft.IconButton(
        icon=ft.Icons.COPY_ALL,
        icon_size=15,
        style=icon_btn_style,
        tooltip="复制消息内容",
        action=ft.CopyToClipboard(data=content),
    )
    md_content = ft.Markdown(
        value=content,
        selectable=True,
        extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED,
        code_theme=ft.MarkdownCodeTheme.ATOM_ONE_DARK,
        fit_content=False,
        expand=True,
    )
    bubble_bg = "#111111" if not is_user else "#171717"
    bubble = ft.Container(
        padding=14,
        border_radius=8,
        bgcolor=bubble_bg,
        expand=7,  # 占 70% 宽
        content=ft.Row([md_content, copy_btn], spacing=8),
    )
    spacer = ft.Container(expand=3)  # 占 30% 宽
    row = ft.Row([spacer, bubble]) if is_user else ft.Row([bubble, spacer])
    return row, md_content


def build_session_item(sid: int, title: str, is_active: bool, icon_btn_style, on_delete, on_switch) -> ft.Container:
    """构建一条会话条目。"""
    del_btn = ft.IconButton(
        icon=ft.Icons.DELETE_OUTLINE,
        icon_size=15,
        style=icon_btn_style,
        tooltip="删除会话",
        on_click=lambda e, sid=sid: on_delete(sid),
    )
    return ft.Container(
        content=ft.Row(
            [
                ft.Text(
                    title,
                    color="#ffffff" if is_active else "#a1a1aa",
                    expand=True,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    size=14,
                ),
                del_btn,
            ],
            spacing=8,
        ),
        padding=9,
        border_radius=6,
        bgcolor="#1f1f1f" if is_active else None,
        on_click=lambda e, sid=sid: on_switch(sid),
    )
