"""临时测试 llm_client，验证 DeepSeek 连通，跑通后删除。"""
import asyncio

from agent.llm_client import send_message


async def main():
    reply = await send_message([{"role": "user", "content": "你好，请回复一句话"}])
    print(reply.choices[0].message.content)


asyncio.run(main())
