"""
executor.py —— 工具执行器（安全闸门）。

职责：
1. 执行前先做路径安全校验（utils.safe_path），不在白名单内直接拒绝。
2. 按工具名从 registry 取执行函数并 await 执行。
3. 捕获 stdout / stderr / 返回码，包装成 Claude 规定的 tool_result 格式。

安全红线：
- shell 与文件写入必须经用户审批后才允许执行（审批在 agent_loop 层）。
- 本层不信任任何路径，一律过 safe_path（用 resolve() 防 ../ 与符号链接逃逸）。
"""
async def execute(tool_name: str, tool_input: dict) -> dict:
    """执行一个工具，返回 Claude 的 tool_result 内容。"""
    raise NotImplementedError("待我手动实现")


async def _read_file(path: str) -> dict:
    raise NotImplementedError("待我手动实现")


async def _list_dir(path: str) -> dict:
    raise NotImplementedError("待我手动实现")


async def _write_file(path: str, content: str) -> dict:
    raise NotImplementedError("待我手动实现")


async def _run_shell(command: str) -> dict:
    """用 asyncio.subprocess 异步执行；绝不用阻塞的 subprocess.run。"""
    raise NotImplementedError("待我手动实现")
