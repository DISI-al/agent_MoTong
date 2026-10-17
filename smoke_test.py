"""临时冒烟测试：确认 Flet 能弹出桌面窗口。验证通过后可删除本文件。"""
import flet as ft


def main(page: ft.Page):
    page.title = "冒烟测试"
    page.add(ft.Text("窗口能弹出来，Flet 就通了！"))
    page.add(ft.Text("如果你看到这个窗口，说明 Flet 可以正常工作。"))
    #添加背景图片
    


ft.run(main)
