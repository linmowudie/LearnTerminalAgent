"""
测试导入时是否初始化了工作空间
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

print("1. 导入前")
from learn_agent.infrastructure.workspace import WorkspaceManager

print("2. 导入后，检查 workspace 状态")
workspace = WorkspaceManager()
print(f"   workspace._workspace_root = {workspace._workspace_root}")

print("\n3. 现在导入 tools")
from learn_agent.tools.tools import bash

print("4. 再次检查 workspace 状态")
print(f"   workspace._workspace_root = {workspace._workspace_root}")

if workspace._workspace_root is not None:
    print(f"\n❌ 问题确认：导入 tools 时自动初始化了工作空间！")
    print(f"   工作空间被设置为：{workspace._workspace_root}")
else:
    print(f"\n✅ 正常：工作空间未自动初始化")
