"""临时测试 agent_loop，跑通后删除。"""
import asyncio

from agent.agent_loop import AgentLoop
from agent.state import AgentStateContainer


async def main():
    state = AgentStateContainer()
    loop = AgentLoop(state)

    final = await loop.start_turn("请用 list_dir 工具列出 D:/HOME/my_workspace 目录下有什么")
    print("\n=== 最终回复 ===")
    print(final)


asyncio.run(main())
