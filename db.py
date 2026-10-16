"""
db.py —— SQLite 本地存储层。

职责：
1. 打开/创建 SQLite 数据库文件（sessions、messages 两张表）。
2. 首次运行时自动建表。
3. 提供会话与消息的增删查（CRUD）函数占位。

安全红线：
- 数据库只存会话和消息内容，绝不存 API Key。
- 数据库文件（*.db）已被 .gitignore 排除，只留在本地。
"""
import sqlite3
from pathlib import Path


def get_connection(db_path: Path) -> sqlite3.Connection:
    """返回一个 SQLite 连接（可配置 row_factory 等）。"""
    raise NotImplementedError("待我手动实现")


def init_db(db_path: Path) -> None:
    """建表：sessions、messages（若不存在）。"""
    raise NotImplementedError("待我手动实现")


def create_session(title: str) -> int:
    """新建会话，返回 session_id。"""
    raise NotImplementedError("待我手动实现")


def list_sessions() -> list:
    """列出所有会话（供侧边栏展示）。"""
    raise NotImplementedError("待我手动实现")


def save_message(session_id: int, role: str, content: str) -> None:
    """保存一条消息到指定会话。"""
    raise NotImplementedError("待我手动实现")


def load_messages(session_id: int) -> list:
    """读取指定会话的全部消息（供组装 LLM 上下文）。"""
    raise NotImplementedError("待我手动实现")
