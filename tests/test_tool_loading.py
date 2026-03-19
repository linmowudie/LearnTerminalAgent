"""
测试工具调用时的加载动画
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.learn_agent.infrastructure.display import TerminalDisplay
import time


def test_tool_loading_animation():
    """测试工具执行时的加载动画"""
    
    print("\n" + "="*60)
    print("测试：工具调用加载动画")
    print("="*60 + "\n")
    
    display = TerminalDisplay(verbose=True)
    
    # 模拟工具调用场景
    tools_to_test = [
        ("bash", {"command": "ls -la"}),
        ("read_file", {"path": "./test.txt"}),
        ("write_file", {"path": "./output.txt", "content": "Hello"}),
    ]
    
    for tool_name, tool_args in tools_to_test:
        print(f"\n📋 准备调用工具：{tool_name}")
        
        # 启动加载动画
        display.show_loading_animation(f"🤖 执行 {tool_name}:")
        
        # 打印工具调用信息
        display.print_tool_call(tool_name, tool_args)
        
        # 模拟工具执行（延迟 2 秒）
        time.sleep(2)
        
        # 停止加载动画
        display.stop_loading_animation()
        
        # 打印工具结果
        display.print_tool_result(f"✅ {tool_name} 执行成功！", max_preview=200)
        
        print()
    
    print("="*60)
    print("测试完成！")
    print("="*60)


if __name__ == "__main__":
    test_tool_loading_animation()
