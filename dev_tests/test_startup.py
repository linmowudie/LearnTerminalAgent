"""
简单测试启动脚本
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

print("=" * 60)
print("LearnTerminalAgent 启动测试")
print("=" * 60)

try:
    from learn_agent.workspace import WorkspaceManager
    from learn_agent.tools import list_directory
    
    print("\n[OK] 模块导入成功")
    
    # 初始化工作空间
    workspace = WorkspaceManager()
    workspace.initialize(str(Path.cwd()))
    
    print("[OK] 工作空间初始化成功")
    
    # 测试工具
    result = list_directory.invoke({"path": "."})
    print(f"[OK] 工具调用成功 - 看到 {result.count('📁') + result.count('📄')} 个项目")
    
    print("\n" + "=" * 60)
    print("所有测试通过！可以正常使用 run_agent.py 启动")
    print("=" * 60)
    
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
