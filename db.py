"""
db.py —— SQLite 本地存储层。

职责：
1. 打开/创建 SQLite 数据库文件（sessions、messages 两张表）。
2. 首次运行时自动建表。
3. 提供会话与消息的增删查（CRUD）函数。

安全红线：
- 数据库只存会话和消息内容，绝不存 API Key。
- 数据库文件（*.db）已被 .gitignore 排除，只留在本地。

注意：必须先调用 init_db()，其余 CRUD 函数才可用。
"""
import sqlite3
from pathlib import Path

_DB_PATH: Path | None = None  # 由 init_db() 设置，供各 CRUD 函数使用


def get_connection(db_path: Path) -> sqlite3.Connection:
    """打开一个 SQLite 连接（按列名取值，开启外键约束）。"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Path) -> None:
    """建表（sessions、messages）并记录全局数据库路径。"""
    global _DB_PATH
    _DB_PATH = db_path
    conn = get_connection(db_path)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            title      TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS messages (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            role       TEXT NOT NULL,
            content    TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );
        """
    )
    conn.commit()
    conn.close()


def create_session(title: str) -> int:
    """新建会话，返回 session_id。"""
    conn = get_connection(_DB_PATH)
    cur = conn.execute("INSERT INTO sessions (title) VALUES (?)", (title,))
    conn.commit()
    session_id = cur.lastrowid
    conn.close()
    return session_id


def list_sessions() -> list[dict]:
    """列出所有会话（新在前），供侧边栏展示。"""
    conn = get_connection(_DB_PATH)
    rows = conn.execute("SELECT * FROM sessions ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_message(session_id: int, role: str, content: str) -> None:
    """保存一条消息到指定会话。"""
    conn = get_connection(_DB_PATH)
    conn.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content),
    )
    conn.commit()
    conn.close()


def load_messages(session_id: int) -> list[dict]:
    """读取指定会话的全部消息（按时间正序，供组装 LLM 上下文）。"""
    conn = get_connection(_DB_PATH)
    rows = conn.execute(
        "SELECT * FROM messages WHERE session_id = ? ORDER BY id ASC",
        (session_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
