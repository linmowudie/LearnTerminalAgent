"""
测试 Agent 工具绑定
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from learn_agent.agent import AgentLoop
from learn_agent.config import get_config

print("=== 创建 Agent ===")
config = get_config()
agent = AgentLoop(config=config, workspace_path='F:/ProjectCode/PersionalProject')

print(f"\n[OK] Agent 创建成功")
print(f"[Tools] 工具数量：{len(agent.tools)}")
print(f"[Tools] 工具列表：")
for tool in agent.tools:
    print(f"   - {tool.name}: {tool.description[:50]}...")

print(f"\n[Messages] 消息数量：{len(agent.messages)}")
print(f"[System] System prompt 前 200 字符:")
print(agent.messages[0].content[:200])

print("\n=== 测试工具调用 ===")
# 模拟用户输入
user_query = "查看当前目录内容"
print(f"用户输入：{user_query}")

# 添加到消息历史
from langchain_core.messages import HumanMessage
agent.messages.append(HumanMessage(content=user_query))

# 执行一步推理
print("\n[Agent] Agent 执行中...")
result = agent.step()
print(f"\n[Result] 结果类型：{type(result)}")
print(f"[Result] 结果：{result}")

if result:
    print(f"\n[OK] Agent 有输出！")
    print(f"输出内容：{result[:500]}")
else:
    print(f"\n[ERROR] Agent 没有返回任何内容！")
