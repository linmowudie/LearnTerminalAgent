#!/usr/bin/env python3
"""
LearnAgent 启动脚本

用法:
    python run.py              # 启动交互式 Agent
    python run.py --help       # 显示帮助
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LearnAgent.main import main

if __name__ == "__main__":
    main()
