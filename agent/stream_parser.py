"""
stream_parser.py —— 流式分片解析器（OpenAI / DeepSeek 格式）。

职责：
1. 接收流式 chunk 里的文本增量（delta.content），累计成完整文本。
2. 按 index 归并工具调用分片（delta.tool_calls），拼装出完整的工具调用。

格式说明（OpenAI 流式）：
- 每个 chunk 的 choices[0].delta 有：
  - content: 文本增量（可能为 None）
  - tool_calls: 工具调用增量列表，每项含 index / id / function.name / function.arguments
- function.arguments 是分片的 JSON 字符串，需按 index 累加，最后 json.loads 成 dict。
"""
import json


class StreamParser:
    """把零散的流式分片，还原成完整文本与完整工具调用。"""

    def __init__(self) -> None:
        self._text_parts: list[str] = []
        self._tool_calls: dict[int, dict] = {}  # index -> {id, name, arguments}

    def feed_text(self, delta: str) -> str:
        """累计一段文本增量，并返回它（可直接交给 UI 渲染）。"""
        self._text_parts.append(delta)
        return delta

    def feed_tool_call(
        self,
        index: int,
        tool_id: str | None,
        name: str | None,
        arguments: str | None,
    ) -> None:
        """按 index 归并某个工具调用的分片。"""
        tc = self._tool_calls.setdefault(index, {"id": None, "name": None, "arguments": ""})
        if tool_id is not None:
            tc["id"] = tool_id
        if name is not None:
            tc["name"] = name
        if arguments is not None:
            tc["arguments"] += arguments

    def text(self) -> str:
        """返回累计的完整文本。"""
        return "".join(self._text_parts)

    def completed_tools(self) -> list[dict]:
        """返回拼装完成的工具调用列表（arguments 已解析成 dict）。"""
        result = []
        for tc in self._tool_calls.values():
            args_str = tc["arguments"].strip()
            try:
                args = json.loads(args_str) if args_str else {}
            except json.JSONDecodeError:
                args = {}  # 参数 JSON 不完整/非法，给空字典
            result.append({"id": tc["id"], "name": tc["name"], "arguments": args})
        return result

    def reset(self) -> None:
        """清空缓冲区，为下一轮做准备。"""
        self._text_parts = []
        self._tool_calls = {}
