"""
端到端测试：模拟真实的 Agent 对话
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from learn_agent.core.agent import AgentLoop
from learn_agent.core.config import get_config

print("=== 创建 Agent (工作空间：PersionalProject) ===")
config = get_config()
agent = AgentLoop(config=config, workspace_path='F:/ProjectCode/PersionalProject')

print(f"\n[OK] Agent 创建成功")
print(f"[Workspace] 工作空间：{agent.messages[0].content.split('directory: ')[1].split('\\n')[0]}")

# 模拟真实对话
user_query = "查看当前目录内容"
print(f"\n{'='*60}")
print(f"用户输入：{user_query}")
print(f"{'='*60}\n")

# 运行 Agent
result = agent.run(user_query, verbose=True, stream=False)

print(f"\n{'='*60}")
print(f"最终响应:")
print(f"{'='*60}")
print(result[:500])

# 清理
agent.reset()
