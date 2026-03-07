"""
测试 bash 工具
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from learn_agent.infrastructure.workspace import WorkspaceManager
from learn_agent.tools.tools import bash

# 初始化工作空间
workspace = WorkspaceManager()
workspace.initialize('F:/ProjectCode/PersionalProject', force=True)

print(f"[Workspace] 工作空间：{workspace.root}")

# 测试 bash 工具
print("\n=== 测试 1: dir 命令 ===")
result = bash.invoke({"command": "dir"})
print(f"结果长度：{len(result)} 字符")
print(f"前 200 字符:\n{result[:200]}...")

print("\n=== 测试 2: python hello.py ===")
result = bash.invoke({"command": "python hello.py"})
print(f"结果:\n{result}")

print("\n=== 测试 3: pwd (检查当前目录) ===")
result = bash.invoke({"command": "cd"})
print(f"当前目录:\n{result}")
