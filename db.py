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

        CREATE TABLE IF NOT EXISTS tasks (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            content    TEXT NOT NULL,
            fire_at    TEXT NOT NULL,
            done       INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
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


def delete_session(session_id: int) -> None:
    """删除会话及其所有消息。"""
    conn = get_connection(_DB_PATH)
    conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()


def update_session_title(session_id: int, title: str) -> None:
    """更新会话标题。"""
    conn = get_connection(_DB_PATH)
    conn.execute("UPDATE sessions SET title = ? WHERE id = ?", (title, session_id))
    conn.commit()
    conn.close()


def add_task(content: str, fire_at: str) -> int:
    """新增一个定时任务，返回 task_id。"""
    conn = get_connection(_DB_PATH)
    cur = conn.execute(
        "INSERT INTO tasks (content, fire_at) VALUES (?, ?)", (content, fire_at)
    )
    conn.commit()
    task_id = cur.lastrowid
    conn.close()
    return task_id


def get_due_tasks(now_str: str) -> list[dict]:
    """返回已到期且未完成的任务。"""
    conn = get_connection(_DB_PATH)
    rows = conn.execute(
        "SELECT * FROM tasks WHERE fire_at <= ? AND done = 0 ORDER BY fire_at ASC",
        (now_str,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_tasks() -> list[dict]:
    """列出所有未完成的任务。"""
    conn = get_connection(_DB_PATH)
    rows = conn.execute(
        "SELECT * FROM tasks WHERE done = 0 ORDER BY fire_at ASC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_task_done(task_id: int) -> None:
    """标记任务为已完成。"""
    conn = get_connection(_DB_PATH)
    conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


def delete_task(task_id: int) -> None:
    """删除任务。"""
    conn = get_connection(_DB_PATH)
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
