"""
测试改进后的系统提示词
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from learn_agent.agent import AgentLoop
from learn_agent.config import get_config

print("=== 创建 Agent ===")
config = get_config()
agent = AgentLoop(config=config, workspace_path='F:/ProjectCode/PersionalProject')

# 打印新的系统提示词
print("\n=== 新的 System Prompt ===")
print(agent.messages[0].content)
print("=" * 60)

# 测试场景 1：运行文件
print("\n=== 测试 1: '运行 hello.py' ===")
result = agent.run("运行 hello.py", verbose=True, stream=False)
print(f"\n响应:\n{result}")

# 重置并测试场景 2：执行脚本
agent.reset()
print("\n=== 测试 2: '执行这个脚本' ===")
result = agent.run("执行这个脚本 hello.py", verbose=True, stream=False)
print(f"\n响应:\n{result}")

# 重置并测试场景 3：查看目录
agent.reset()
print("\n=== 测试 3: '查看当前目录' ===")
result = agent.run("查看当前目录", verbose=True, stream=False)
print(f"\n响应:\n{result[:300]}...")
