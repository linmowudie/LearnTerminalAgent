"""
LearnTerminalAgent 主程序入口

提供交互式命令行界面
"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .config import get_config
from .agent import AgentLoop
from ..infrastructure.logger import logger_workspace
from ..services.memory_storage import reset_memory_storage


def print_banner():
    """打印欢迎横幅"""
    print("\n" + "=" * 60)
    print("LearnTerminalAgent - LangChain 实现的智能 Agent")
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
    import os
    
    # 尝试从 docs/help.md 读取帮助信息
    script_dir = os.path.dirname(os.path.abspath(__file__))  # src/learn_agent
    project_root = os.path.dirname(os.path.dirname(script_dir))  # 项目根目录
    help_file = os.path.join(project_root, 'docs', 'help.md')
    
    if os.path.exists(help_file):
        with open(help_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 简单的 Markdown 格式化清理
            lines = []
            for line in content.split('\n'):
                # 移除标题标记
                if line.startswith('# '):
                    lines.append('\n' + line[2:])
                elif line.startswith('## '):
                    lines.append('\n' + line[3:])
                elif line.startswith('### '):
                    lines.append(line[4:])
                elif line.startswith('- [') or line.startswith('|'):
                    # 跳过链接和表格
                    continue
                elif line.strip() == '---':
                    # 跳过分割线
                    continue
                else:
                    lines.append(line.replace('**', ''))
            print('\n'.join(lines))
    else:
        # 如果文件不存在，使用默认帮助信息
        print("""
                LearnTerminalAgent 使用指南 (s01-s06 功能):

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
                LearnTerminalAgent >> 创建一个 test.py 文件，包含 print("Hello")
                LearnTerminalAgent >> 用子代理探索项目结构
                LearnTerminalAgent >> 加载 pdf 技能
                """)


def _format_response_card(content: str) -> str:
    """
    将响应格式化为卡片输出（使用 display 模块的 Rich 功能）
    
    Args:
        content: 要格式化的内容
        
    Returns:
        格式化后的字符串（Rich 会自动渲染，这里返回原始内容）
    """
    # 这个函数现在只是占位，实际格式化由 TerminalDisplay.print_response_card 处理
    return content


def main():
    """主程序入口"""
    
    # Windows 下设置 UTF-8 编码
    if sys.platform == 'win32':
        try:
            os.system('chcp 65001 >nul')  # 设置控制台为 UTF-8
        except:
            pass
    
    # 从命令行参数获取工作空间路径
    workspace_path = None
    if len(sys.argv) > 1:
        workspace_path = sys.argv[1]
        print(f"\n[WORKSPACE] 使用工作空间：{workspace_path}\n")
    
    # 初始化工作空间（只初始化一次）
    from learn_agent.infrastructure.workspace import get_workspace
    workspace = get_workspace()
    
    # 检查工作空间是否已经在其他地方被初始化
    if workspace.root is not None:
        logger_workspace.debug(f"工作空间已在别处初始化：{workspace.root}")
        # 如果用户指定了不同的工作空间，需要重新初始化
        if workspace_path and str(workspace.root) != workspace_path:
            logger_workspace.info(f"用户指定了不同的工作空间：{workspace_path}，重新初始化")
            workspace.initialize(workspace_path, force=True)
    else:
        logger_workspace.info(f"初始化工作空间：{workspace_path or '当前目录'}")
        workspace.initialize(workspace_path)
    
    try:
        # 加载并打印配置（此时工作空间已设置，不会影响到）
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
    
    # 创建 Agent 实例，传入工作空间路径
    agent = AgentLoop(workspace_path=workspace_path)
    
    # 主循环
    print("\n提示：输入 /help 查看帮助，/quit 或 Ctrl+D 退出\n")
    
    while True:
        try:
            # 获取用户输入
            query = input("\033[36mLearnTerminalAgent >> \033[0m").strip()
            
            # 只有带 '/' 前缀的才是特殊命令
            if query.startswith('/'):
                command = query[1:].lower()  # 移除 '/' 前缀
                
                # 处理特殊命令
                if command in ("q", "quit", "exit"):
                    print("\n👋 再见！\n")
                    break
                
                elif command == "help":
                    print_help()
                    continue
                
                elif command == "reset":
                    agent.reset()
                    print("✓ 对话已重置\n")
                    continue
                
                elif command == "config":
                    config.print_info()
                    print()
                    continue
                
                elif command == "history":
                    history = agent.get_history()
                    print(f"\n对话历史 ({len(history)} 条消息):")
                    for i, msg in enumerate(history[-10:], 1):  # 只显示最近 10 条
                        print(f"  {i}. [{msg.type}] {str(msg.content)[:100]}...")
                    print()
                    continue
                
                elif command == "todo":
                    progress = agent.get_todo_progress()
                    print(f"\n{progress}\n")
                    continue
                
                elif command == "skills":
                    from ..tools.skills import get_skill_loader
                    loader = get_skill_loader()
                    skills = loader.get_descriptions()
                    print(f"\n可用技能:\n{skills}\n")
                    continue
                
                elif command == "compact":
                    result = agent.compact_context()
                    print(f"\n✓ {result}\n")
                    continue
                
                elif command == "stats":
                    stats = agent.get_context_stats()
                    print(f"\n上下文统计:")
                    print(f"  Token 数：{stats['current_tokens']}")
                    print(f"  阈值：{stats['threshold']}")
                    print(f"  消息数：{stats['message_count']}")
                    print(f"  压缩次数：{stats['compactions']['total_compactions']}")
                    print()
                    continue
            
            # 空输入
            if not query:
                continue
            
            # 运行 Agent - 使用流式输出
            response = agent.run(query, verbose=True, stream=True)
            
            # 打印响应 - 使用 Rich 卡片格式化
            # 只有当响应包含实际内容且不是错误信息时才显示卡片
            # 工具调用的过程已经在 verbose 模式中输出，不需要重复显示
            if response and len(response.strip()) > 0 and not any(x in response for x in ['Error:', '❌', '我已收到您的请求']):
                # 检查是否已经有工具调用输出（通过日志判断）
                # 如果有工具调用，verbose 模式已经显示了过程和结果，不需要再显示卡片
                # 只有纯文本回答才需要显示卡片
                if not hasattr(agent, '_has_tool_calls') or not agent._has_tool_calls:
                    # 使用 Rich 渲染 Markdown 和卡片
                    agent.display.print_response_card(response, style="default")
        
        except KeyboardInterrupt:
            print("\n\n👋 中断退出\n")
            # 结束当前记忆会话
            if hasattr(agent, '_current_session_id') and agent._current_session_id:
                agent.memory_storage.end_session(agent._current_session_id)
            break
        
        except EOFError:
            print("\n\n👋 再见！\n")
            # 结束当前记忆会话
            if hasattr(agent, '_current_session_id') and agent._current_session_id:
                agent.memory_storage.end_session(agent._current_session_id)
            break
        
        except Exception as e:
            print(f"\n\033[31m❌ 错误：{type(e).__name__}: {str(e)}\033[0m")
            print("请检查配置或重试\n")


if __name__ == "__main__":
    main()
