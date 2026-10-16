"""
helpers.py —— 通用小工具。

职责：时间格式化、ID 生成等与业务无关的小函数。
"""
import uuid
from datetime import datetime


def now_str() -> str:
    """返回当前时间的格式化字符串。"""
    raise NotImplementedError("待我手动实现")


def new_id() -> str:
    """生成一个唯一 ID。"""
    raise NotImplementedError("待我手动实现")
