"""
测试完整的思考 -> 工具调用流程
"""

from src.learn_agent.infrastructure.display import TerminalDisplay
import time

display = TerminalDisplay(verbose=True)

print("\n" + "="*60)
print("模拟完整流程：思考 -> 思考完毕 -> 调用工具")
print("="*60 + "\n")

# 步骤 1: 思考阶段
print("【步骤 1】Agent 思考中...")
display.show_loading_animation("🤖 Agent 思考中:", show_complete_message=True)
time.sleep(2)  # 模拟思考时间
display.stop_loading_animation()  # 显示"思考完毕"

# 步骤 2: 打印工具调用信息
print("\n【步骤 2】准备调用工具：bash")
print(f"\033[33m$ ls -la\033[0m")

# 步骤 3: 工具执行阶段（启动静态动画，不显示完成消息）
print("\n【步骤 3】工具执行中...")
display.show_loading_animation(
    "🤖 执行 bash:", 
    show_complete_message=False,
    is_static=True  # 使用静态指示器
)
time.sleep(3)  # 模拟工具执行时间
display.stop_loading_animation()  # 不显示"思考完毕"，只换行

# 步骤 4: 打印工具结果
print("✅ total 0")
print("-rw-r--r-- 1 user user 0 Mar  9 10:00 test.txt")

print("\n" + "="*60)
print("流程演示完成！")
print("="*60)
print("\n预期效果：")
print("1. 思考阶段显示动画 → 停止时显示'思考完毕'")
print("2. 工具调用阶段显示动画 → 停止时只显示换行，不显示文字")
print("3. 清晰区分'思考'和'工具执行'两个阶段")
print()
