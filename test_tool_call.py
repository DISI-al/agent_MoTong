"""诊断：看模型收到"写文件"请求时，返回 tool_calls 还是纯文本。跑完删。"""
import asyncio

from agent.llm_client import send_message
from config import Config
from tools.schemas import get_tool_schemas

SYSTEM = "你是一个本地文件助手，可以使用工具：读取文件、列出目录、写入文件、执行 shell 命令。需要时调用工具完成任务。"


async def main():
    print("模型:", Config().model)
    print("工具名:", [t["function"]["name"] for t in get_tool_schemas()])
    print("---")

    reply = await send_message(
        [{"role": "user", "content": "请在 D:/HOME/my_workspace 下写一个 hello2.txt，内容为 hi"}],
        tools=get_tool_schemas(),
        system=SYSTEM,
    )
    msg = reply.choices[0].message
    print("content:", repr(msg.content))
    print("tool_calls:", msg.tool_calls)


asyncio.run(main())
