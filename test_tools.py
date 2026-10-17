"""临时测试工具层，跑通后删除。"""
import asyncio
from pathlib import Path

from tools.executor import execute

WORKSPACE = Path("D:/HOME/my_workspace")


async def main():
    # 先准备一个测试文件（用普通 Python 写，不是用工具）
    test_file = WORKSPACE / "hello.txt"
    test_file.write_text("你好，工具层！", encoding="utf-8")

    # 1. 白名单内 list_dir → 应能看到 hello.txt
    print("list_dir(白名单内):", await execute("list_dir", {"path": str(WORKSPACE)}))

    # 2. 白名单内 read_file → 应读到内容
    print("read_file(白名单内):", await execute("read_file", {"path": str(test_file)}))

    # 3. 白名单外 → 应被拒绝
    print("list_dir(白名单外):", await execute("list_dir", {"path": "D:/Windows"}))


asyncio.run(main())
