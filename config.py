"""
config.py —— 全局配置中心。

职责：
1. 读 API Key / 模型 / 白名单（settings.json 优先，.env 兜底）。
2. save_settings 供设置界面写入。

安全红线：
- API Key 只从 settings.json / .env 读，绝不硬编码、绝不入库。
- settings.json 已被 .gitignore 排除。
"""
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

SETTINGS_FILE = Path("settings.json")


def _load_settings() -> dict:
    """读 settings.json；不存在或损坏则返回空字典。"""
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_settings(data: dict) -> None:
    """把设置写入 settings.json（供设置界面调用）。"""
    SETTINGS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def get_settings_for_ui() -> dict:
    """返回当前设置（供设置界面显示），未配置的返回空串。"""
    s = _load_settings()
    return {
        "api_key": s.get("api_key") or os.getenv("DEEPSEEK_API_KEY") or "",
        "model": s.get("model") or os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        "workspace_roots": s.get("workspace_roots") or os.getenv("WORKSPACE_ROOTS", ""),
    }


def get_api_key() -> str:
    """读 API Key（settings.json 优先，.env 兜底）。"""
    key = _load_settings().get("api_key") or os.getenv("DEEPSEEK_API_KEY")
    if not key:
        raise RuntimeError("缺少 API Key，请在设置里配置或填 .env")
    return key


def get_model() -> str:
    """读模型名（settings.json 优先，.env 兜底）。"""
    return _load_settings().get("model") or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


def get_workspace_roots() -> list[Path]:
    """读工作目录白名单（settings.json 优先，.env 兜底）。"""
    raw = _load_settings().get("workspace_roots") or os.getenv("WORKSPACE_ROOTS", "")
    roots = [Path(p.strip()).resolve() for p in raw.split(",") if p.strip()]
    if not roots:
        raise RuntimeError("缺少工作目录白名单，请在设置里配置")
    return roots


@dataclass
class Config:
    model: str = field(default_factory=get_model)
    temperature: float = 0.7
    max_tokens: int = 4096
