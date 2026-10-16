"""
stream_parser.py —— 流式分片解析器。

职责：
1. 接收 SDK 流式事件，实时产出「文本增量」给 UI 追加渲染。
2. 在缓冲区累加 tool_use 的 input_json_delta 分片，拼装成完整 tool_use 对象。

注意（比预想简单）：
- SDK 给的是结构化事件（content_block_start / content_block_delta /
  content_block_stop），不是原始 SSE 字节流；这里只需累加 partial_json
  再 json.loads。
- 一个响应可能包含【多个】tool_use 块，本解析器要能收集一批。
"""
import json


class StreamParser:
    """把零散的流式分片，还原成完整文本与完整 tool_use 对象。"""

    def __init__(self) -> None:
        raise NotImplementedError("待我手动实现")

    def feed_text_delta(self, text: str) -> str:
        """处理文本增量，返回可直接渲染的文本。"""
        raise NotImplementedError("待我手动实现")

    def feed_tool_delta(self, block_index: int, partial_json: str) -> None:
        """累加某个 tool_use 块的 JSON 分片。"""
        raise NotImplementedError("待我手动实现")

    def completed_tools(self) -> list[dict]:
        """返回本轮已拼装完成的 tool_use 对象列表。"""
        raise NotImplementedError("待我手动实现")

    def reset(self) -> None:
        """清空缓冲区，为下一轮做准备。"""
        raise NotImplementedError("待我手动实现")
