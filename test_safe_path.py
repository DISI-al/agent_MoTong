"""临时测试 safe_path，验证通过后可删除。"""
from pathlib import Path

from utils.safe_path import is_safe_path

roots = [Path("D:/HOME/my_workspace")]

print("白名单内 :", is_safe_path("D:/HOME/my_workspace/a.txt", roots))          # 期望 True
print("../ 逃逸:", is_safe_path("D:/HOME/my_workspace/../secret.txt", roots))  # 期望 False
print("前缀撞名 :", is_safe_path("D:/HOME/my_workspace2/x.txt", roots))         # 期望 False
