import flet as ft
from flet import Border, BorderSide

def main(page: ft.Page):
    page.title = "My Claude Harness"
    page.bgcolor = "#0a0a0a"
    page.window.width = 1180
    page.window.height = 800
    page.window.min_width = 900
    page.window.min_height = 600

    # 通用边框样式，Vercel细灰边框
    card_side = BorderSide(width=1, color="#27272a")
    card_border = Border(top=card_side, bottom=card_side, left=card_side, right=card_side)

    # 侧边栏
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
                ft.TextButton("新建对话", style=ft.ButtonStyle(color="#f1f1f1")),
                ft.Text("对话 #1", color="#a1a1aa"),
                ft.Text("对话 #2", color="#a1a1aa"),
            ],
            spacing=12,
            expand=True
        )
    )

    # 消息区域占位
    message_area = ft.Container(
        expand=True,
        padding=20,
        bgcolor="#0a0a0a",
        content=ft.Column(
            controls=[
                ft.Text("聊天消息区域", color="#a1a1aa")
            ],
            spacing=16,
            scroll=ft.ScrollMode.AUTO
        )
    )

    # 底部输入框区域
    input_box_area = ft.Container(
        padding=12,
        bgcolor="#111111",
        border=card_border,
        border_radius=12,
        content=ft.Row(
            controls=[
                ft.TextField(
                    hint_text="输入消息，和 Claude 对话...",
                    expand=True,
                    bgcolor="#0a0a0a",
                    border_color="#27272a",
                    color="#f1f1f1"
                ),
                # ✅ Flet1.0 填充按钮：FilledButton
                ft.FilledButton("发送", bgcolor="#ffffff", color="#000000")
            ],
            spacing=12
        )
    )

    # 主布局，垂直排布：消息区 + 底部输入框
    main_panel = ft.Column(
        controls=[
            message_area,
            input_box_area
        ],
        expand=True,
        spacing=16
    )

    # 页面整体：侧边栏 + 主面板
    page.add(
        ft.Row(
            controls=[
                sidebar,
                main_panel
            ],
            expand=True,
            spacing=16
        )
    )

if __name__ == "__main__":
    ft.run(main)