"""临时测试流式 + stream_parser，跑通后删除。"""
import asyncio

from agent.llm_client import stream_message
from agent.stream_parser import StreamParser


async def main():
    parser = StreamParser()
    async for chunk in stream_message([{"role": "user", "content": "用三句话介绍你自己"}]):
        delta = chunk.choices[0].delta
        if delta.content:
            text = parser.feed_text(delta.content)
            print(text, end="", flush=True)  # 打字机效果

    print("\n\n--- 完整文本 ---")
    print(parser.text())


asyncio.run(main())
