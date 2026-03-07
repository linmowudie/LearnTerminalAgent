"""
LearnTerminalAgent 快速启动脚本

使用方法:
    python run_agent.py [工作空间路径]
    
示例:
    # 在当前目录启动
    python run_agent.py
    
    # 指定工作空间
    python run_agent.py F:\\ProjectCode\\MyProject
"""

import sys
import os
from pathlib import Path

# 添加 src 目录到 Python 路径
script_dir = Path(__file__).resolve()
src_dir = script_dir.parent / 'src'
sys.path.insert(0, str(src_dir))

# 现在可以导入 learn_agent
from learn_agent.core.main import main

if __name__ == "__main__":
    # 传递命令行参数
    sys.argv = sys.argv  # 保留所有参数
    main()
