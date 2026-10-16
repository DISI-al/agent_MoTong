"""
llm_client.py —— 封装异步 Anthropic 客户端。

职责：
1. 初始化 anthropic 异步客户端（AsyncAnthropic），Key 从 config 读取。
2. 提供「非流式」和「流式」两种请求方法占位。
3. 负责把「会话历史 + 工具定义」打包成 Messages API 请求。

注意：
- 使用官方 SDK 的流式接口（结构化事件），不要手写 SSE 解析。
- httpx / httpx-sse 仅作为兜底，正常情况下用不到。
"""
import anthropic


def get_client() -> anthropic.AsyncAnthropic:
    """返回全局单例的异步客户端。"""
    raise NotImplementedError("待我手动实现")


async def send_message(messages: list, tools: list) -> anthropic.types.Message:
    """非流式请求（用于先验证 API 连通性）。"""
    raise NotImplementedError("待我手动实现")


async def stream_message(messages: list, tools: list):
    """流式请求：yield 结构化事件（文本增量 / tool_use 增量）。"""
    raise NotImplementedError("待我手动实现")
