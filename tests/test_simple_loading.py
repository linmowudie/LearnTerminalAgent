"""
简单测试加载动画
"""

from src.learn_agent.infrastructure.display import TerminalDisplay
import time

display = TerminalDisplay(verbose=True)

print("\n开始测试加载动画...\n")

# 测试 1: 基础动画
print("测试 1: 基础加载动画")
display.show_loading_animation("🤖 Agent 思考中:")
time.sleep(2)
display.stop_loading_animation()
print("✓ 动画停止\n")

# 测试 2: 工具执行动画
print("测试 2: 工具执行动画")
display.show_loading_animation("🤖 执行 bash:")
time.sleep(2)
display.stop_loading_animation()
print("✓ 工具执行完成\n")

print("测试完成！\n")
