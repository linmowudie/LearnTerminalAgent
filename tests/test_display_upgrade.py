#!/usr/bin/env python
"""
测试 Display 系统升级后的效果
"""

import sys
sys.path.insert(0, '.')

from src.learn_agent.infrastructure.display import TerminalDisplay
import time

display = TerminalDisplay(verbose=True)

print("\n" + "="*60)
print("Display 系统升级测试")
print("="*60)

# 测试 1: 灰色加载动画
print("\n【测试 1】灰色加载动画（思考过程）")
print("预期：文字显示为灰色，不刺眼")
display.show_loading_animation("🤖 Agent 思考中:", show_complete_message=True)
time.sleep(2)
display.stop_loading_animation()
print("✓ 完成\n")

# 测试 2: write_file 工具调用
print("【测试 2】write_file 工具调用（隐藏内容）")
print("预期：只显示路径和长度，不显示实际内容")
display.print_tool_call('write_file', {'path': 'test.txt', 'content': '这是测试内容，不应该在终端显示'})
print("✓ 完成\n")

# 测试 3: bash 工具调用
print("【测试 3】bash 工具调用（正常显示）")
print("预期：黄色显示命令")
display.print_tool_call('bash', {'command': 'ls -la'})
print("✓ 完成\n")

# 测试 4: 其他工具调用
print("【测试 4】其他工具调用（正常显示）")
print("预期：黄色显示工具信息")
display.print_tool_call('read_file', {'path': 'config.json'})
print("✓ 完成\n")

print("="*60)
print("所有测试完成！")
print("="*60)
print("\n视觉效果说明：")
print("1. 思考过程：灰色显示（降低视觉干扰）")
print("2. write_file: 只显示路径和长度（保护隐私）")
print("3. bash/其他：黄色显示（保持现状）")
print()
