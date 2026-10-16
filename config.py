"""
config.py —— 全局配置中心。

职责：
1. 从 .env 读取 API Key（绝不硬编码、绝不入库）。
2. 定义模型名、温度、最大 token 等请求参数。
3. 定义「工作目录白名单」——所有本地工具只能在这几个目录下读写。

安全红线：
- API Key 只从环境变量 / .env 读取，任何地方不得出现明文 Key。
- 工作目录白名单是本地工具的权限边界，必须在这里集中定义。
"""
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def get_api_key() -> str:
    """从环境变量读取 Anthropic API Key；缺失时抛出明确异常。"""
    raise NotImplementedError("待我手动实现")


def get_workspace_roots() -> list[Path]:
    """返回工作目录白名单（绝对路径列表），供 safe_path 校验。"""
    raise NotImplementedError("待我手动实现")


@dataclass
class Config:
    """全局配置容器：模型 / 采样参数等（默认值仅为占位，按需改）。"""
    model: str = "claude-sonnet-5-5"
    temperature: float = 0.7
    max_tokens: int = 4096
