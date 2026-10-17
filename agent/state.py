"""
state.py —— Agent 状态枚举 + 状态容器。

职责：
1. 定义 Agent 生命周期状态枚举。
2. 提供一个可被 UI 订阅的状态容器。

状态机（务必覆盖到「错误」和「取消」两条腿）：
    IDLE -> WAIT_LLM -> (WAIT_APPROVAL -> RUN_TOOL -> WAIT_LLM) ... -> IDLE
    任意时刻可被用户取消 -> CANCELLED；出错 -> ERROR -> 可恢复回 IDLE。

注意：本项目采用【单 asyncio 事件循环】，get/set 在同一线程内，无需加锁。
"""
from enum import Enum, auto


class AgentState(Enum):
    IDLE = auto()          # 空闲，可接收新消息
    WAIT_LLM = auto()      # 等待 MoTong 流式返回
    WAIT_APPROVAL = auto()  # 等待人工审批工具
    RUN_TOOL = auto()      # 正在执行工具
    CANCELLED = auto()     # 已被用户取消
    ERROR = auto()         # 出错，可恢复


class AgentStateContainer:
    """当前状态 + 切换方法 + 订阅通知（供 UI 监听）。"""

    def __init__(self) -> None:
        self._state = AgentState.IDLE
        self._listeners: list = []

    def get(self) -> AgentState:
        """返回当前状态。"""
        return self._state

    def set(self, state: AgentState) -> None:
        """切换状态；状态没变就不通知，变了才通知所有订阅者。"""
        if self._state == state:
            return
        self._state = state
        for cb in self._listeners:
            cb(state)

    def subscribe(self, callback) -> None:
        """注册一个回调，状态变化时被调用（入参为新状态）。"""
        self._listeners.append(callback)
