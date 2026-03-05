"""
LearnAgent 主程序入口

提供交互式命令行界面
"""

import os
import sys

from .config import get_config
from .agent import AgentLoop


def print_banner():
    """打印欢迎横幅"""
    print("\n" + "=" * 60)
    print("LearnAgent - LangChain 实现的智能 Agent")
    print("基于 learn-claude-code 项目重构")
    print("=" * 60)
    print("\n可用命令:")
    print("  /help     - 显示帮助")
    print("  /reset    - 重置对话")
    print("  /config   - 显示配置")
    print("  /history  - 显示对话历史")
    print("  /quit     - 退出程序")
    print("=" * 60 + "\n")


def print_help():
    """打印帮助信息"""
    print("""
LearnAgent 使用指南 (s01-s06 功能):

1. 直接输入自然语言描述你的任务，例如:
   - "创建一个 hello.txt 文件"
   - "列出当前目录的所有文件"
   - "查看 README.md 的内容"
   - "运行 python --version"

2. 特殊命令:
   - /help      显示此帮助信息
   - /reset     清除对话历史，开始新对话
   - /config    显示当前配置信息
   - /history   显示当前对话历史
   - /todo      显示任务进度
   - /skills    列出可用技能
   - /compact   手动压缩上下文
   - /stats     显示上下文统计
   - /quit      退出程序

3. 可用工具:
   - bash          运行 shell 命令
   - read_file     读取文件内容
   - write_file    写入文件内容
   - list_directory 列出目录内容
   - todo_add      添加任务
   - todo_update   更新任务
   - load_skill    加载技能

4. 高级功能:
   - TodoWrite: Agent 会自动管理任务进度
   - SubAgent: 可委派子任务给子代理
   - Skills: 按需加载外部知识
   - Context: 自动压缩长对话

示例:
   LearnAgent >> 创建一个 test.py 文件，包含 print("Hello")
   LearnAgent >> 用子代理探索项目结构
   LearnAgent >> 加载 pdf 技能
""")


def main():
    """主程序入口"""
    
    try:
        # 加载并打印配置
        config = get_config()
        config.print_info()
        
    except ValueError as e:
        print(f"\033[31m❌ 配置错误：{e}\033[0m")
        print("\n请设置环境变量，例如:")
        print("  PowerShell: $env:QWEN_API_KEY=\"sk-xxxxx\"")
        print("  或创建 .env 文件:\n    QWEN_API_KEY=sk-xxxxx")
        sys.exit(1)
    
    # 打印欢迎横幅
    print_banner()
    
    # 创建 Agent 实例
    agent = AgentLoop()
    
    # 主循环
    while True:
        try:
            # 获取用户输入
            query = input("\033[36mLearnAgent >> \033[0m").strip()
            
            # 处理特殊命令
            if query.lower() in ("q", "quit", "exit"):
                print("\n👋 再见！")
                break
            
            elif query.lower() == "help":
                print_help()
                continue
            
            elif query.lower() == "reset":
                agent.reset()
                print("✓ 对话已重置")
                continue
            
            elif query.lower() == "config":
                config.print_info()
                continue
            
            elif query.lower() == "history":
                history = agent.get_history()
                print(f"\n对话历史 ({len(history)} 条消息):")
                for i, msg in enumerate(history[-10:], 1):  # 只显示最近 10 条
                    print(f"  {i}. [{msg.type}] {str(msg.content)[:100]}...")
                continue
            
            elif query.lower() == "todo":
                progress = agent.get_todo_progress()
                print(f"\n{progress}")
                continue
            
            elif query.lower() == "skills":
                skills = agent.list_skills()
                print(f"\n可用技能:\n{skills}")
                continue
            
            elif query.lower() == "compact":
                result = agent.compact_context()
                print(f"\n✓ {result}")
                continue
            
            elif query.lower() == "stats":
                stats = agent.get_context_stats()
                print(f"\n上下文统计:")
                print(f"  Token 数：{stats['current_tokens']}")
                print(f"  阈值：{stats['threshold']}")
                print(f"  消息数：{stats['message_count']}")
                print(f"  压缩次数：{stats['compactions']['total_compactions']}")
                continue
            
            # 空输入
            if not query:
                continue
            
            # 运行 Agent
            response = agent.run(query, verbose=True)
            
            # 打印响应
            if response:
                print(f"\n\033[32m{response}\033[0m\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 中断退出")
            break
        
        except EOFError:
            print("\n\n👋 再见！")
            break
        
        except Exception as e:
            print(f"\n\033[31m❌ 错误：{type(e).__name__}: {str(e)}\033[0m")
            print("请检查配置或重试")


if __name__ == "__main__":
    main()
