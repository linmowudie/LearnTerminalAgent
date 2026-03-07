#!/usr/bin/env python
"""
模型响应诊断工具

用于详细记录和分析 LLM 的响应行为，帮助诊断工具调用失败的原因
"""

import sys
import os
import logging

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.learn_agent.agent import AgentLoop
from src.learn_agent.logger import set_log_level

def run_diagnostic_test():
    """运行诊断测试"""
    
    print("\n" + "="*60)
    print("🔍 模型响应诊断工具")
    print("="*60)
    
    # 设置日志级别为 DEBUG 以获取最详细的信息
    print("\n📝 已设置日志级别为 DEBUG")
    print("📁 日志文件位置：logs/ 目录")
    set_log_level(logging.DEBUG)
    
    # 创建 Agent 实例
    print("\n🤖 初始化 Agent...")
    agent = AgentLoop()
    
    print("\n" + "="*60)
    print("请选择测试场景:")
    print("="*60)
    print("1. 查看目录内容 (list_directory)")
    print("2. 创建文件 (write_file)")
    print("3. 运行命令 (bash)")
    print("4. 读取文件 (read_file)")
    print("5. 自定义查询")
    print("="*60)
    
    choice = input("\n请输入选项 (1-5): ").strip()
    
    test_queries = {
        '1': "查看当前文件夹内容",
        '2': "创建一个 test_diagnostic.txt 文件，写入 diagnostic content",
        '3': "运行 python --version",
        '4': "读取 README.md 的内容"
    }
    
    if choice in test_queries:
        query = test_queries[choice]
    elif choice == '5':
        query = input("请输入您的查询：").strip()
    else:
        print(f"\n❌ 无效选项：{choice}")
        return
    
    print(f"\n📝 执行查询：{query}")
    print("="*60)
    
    try:
        # 运行 Agent
        response = agent.run(query, verbose=True, stream=True)
        
        print("\n" + "="*60)
        print("✅ 执行完成！")
        print("="*60)
        
        print(f"\n📄 最终响应:\n{response[:500]}")
        if len(response) > 500:
            print(f"... (共 {len(response)} 字符)")
        
        print("\n" + "="*60)
        print("📊 诊断信息汇总:")
        print("="*60)
        
        # 分析消息历史
        total_messages = len(agent.messages)
        tool_call_count = sum(
            1 for msg in agent.messages 
            if hasattr(msg, 'tool_calls') and msg.tool_calls
        )
        
        print(f"总消息数：{total_messages}")
        print(f"包含工具调用的消息数：{tool_call_count}")
        
        # 统计工具调用
        all_tools = []
        for msg in agent.messages:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tc in msg.tool_calls:
                    all_tools.append(tc['name'])
        
        if all_tools:
            print(f"使用的工具：{', '.join(set(all_tools))}")
        else:
            print("⚠️ 未使用任何工具")
        
        print("\n" + "="*60)
        print("📁 查看详细日志:")
        print("="*60)
        print("请查看 logs/ 目录下的最新日志文件")
        print("\n快速查看命令:")
        print("  Windows: Get-Content logs\\Agent_*.log -Tail 100")
        print("  Linux/Mac: tail -n 100 logs/Agent_*.log")
        print("\n或使用查看脚本:")
        print("  python view_logs.py Agent 100")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 发生错误：{type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_diagnostic_test()
