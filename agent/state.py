"""
state.py —— Agent 状态枚举 + 状态容器。

职责：
1. 定义 Agent 生命周期状态枚举。
2. 提供一个可被 UI 订阅的状态容器。

状态机（务必覆盖到「错误」和「取消」两条腿）：
    IDLE -> WAIT_LLM -> (WAIT_APPROVAL -> RUN_TOOL -> WAIT_LLM) ... -> IDLE
    任意时刻可被用户取消 -> CANCELLED；出错 -> ERROR -> 可恢复回 IDLE。
"""
from enum import Enum, auto


class AgentState(Enum):
    IDLE = auto()          # 空闲，可接收新消息
    WAIT_LLM = auto()      # 等待 Claude 流式返回
    WAIT_APPROVAL = auto()  # 等待人工审批工具
    RUN_TOOL = auto()      # 正在执行工具
    CANCELLED = auto()     # 已被用户取消
    ERROR = auto()         # 出错，可恢复


class AgentStateContainer:
    """状态容器：当前状态 + 切换方法 + 可供 UI 订阅/监听。"""

    def __init__(self) -> None:
        raise NotImplementedError("待我手动实现")

    def set(self, state: AgentState) -> None:
        """切换状态（可在此通知订阅者）。"""
        raise NotImplementedError("待我手动实现")

    def get(self) -> AgentState:
        """返回当前状态。"""
        raise NotImplementedError("待我手动实现")
