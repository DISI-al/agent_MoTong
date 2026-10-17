"""
llm_client.py —— 封装 DeepSeek 客户端（OpenAI 兼容接口）。

职责：
1. 初始化 OpenAI 异步客户端（AsyncOpenAI），指向 DeepSeek 的 API 地址。
2. 提供「非流式」和「流式」两种请求方法。
3. 负责把「会话历史 + 工具定义」打包成请求。

注意：
- DeepSeek 是 OpenAI 兼容接口，用 openai SDK，base_url 指向 api.deepseek.com。
- 消息格式是 OpenAI 风格：{role, content}；工具用 function 类型定义。
- 流式返回 SSE chunk（delta.content 文本增量 / delta.tool_calls 工具调用增量）。
"""
from openai import AsyncOpenAI

from config import Config, get_api_key

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    """返回全局单例的异步客户端（指向 DeepSeek）。"""
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=get_api_key(), base_url="https://api.deepseek.com")
    return _client


async def send_message(messages: list, tools: list | None = None, system: str | None = None):
    """非流式请求，返回完整响应（文本在 choices[0].message.content）。"""
    cfg = Config()
    msgs = list(messages)
    if system:
        msgs = [{"role": "system", "content": system}] + msgs
    kwargs = {
        "model": cfg.model,
        "messages": msgs,
        "max_tokens": cfg.max_tokens,
        "temperature": cfg.temperature,
    }
    if tools:
        kwargs["tools"] = tools
    return await get_client().chat.completions.create(**kwargs)


async def stream_message(messages: list, tools: list | None = None, system: str | None = None):
    """流式请求：yield 每个 chunk（含 delta.content / delta.tool_calls）。"""
    cfg = Config()
    msgs = list(messages)
    if system:
        msgs = [{"role": "system", "content": system}] + msgs
    kwargs = {
        "model": cfg.model,
        "messages": msgs,
        "max_tokens": cfg.max_tokens,
        "temperature": cfg.temperature,
        "stream": True,
    }
    if tools:
        kwargs["tools"] = tools
    stream = await get_client().chat.completions.create(**kwargs)
    async for chunk in stream:
        yield chunk
