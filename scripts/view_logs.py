#!/usr/bin/env python
"""
快速查看最新日志

用法:
    python view_logs.py [日志文件名关键词] [显示行数]
    
示例:
    python view_logs.py              # 查看最新 Agent 日志的前 50 行
    python view_logs.py Tools        # 查看最新 Tools 日志
    python view_logs.py Agent 100    # 查看最新 Agent 日志的前 100 行
"""

import sys
import os
from pathlib import Path

def get_latest_log_file(module_name: str = "Agent") -> Path:
    """获取指定模块的最新日志文件"""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("❌ logs 目录不存在")
        return None
    
    # 查找匹配的日志文件
    log_files = list(logs_dir.glob(f"{module_name}_*.log"))
    
    if not log_files:
        print(f"❌ 未找到 {module_name} 模块的日志文件")
        return None
    
    # 按修改时间排序，返回最新的
    latest = max(log_files, key=lambda p: p.stat().st_mtime)
    return latest


def view_log_file(log_file: Path, lines: int = 50):
    """查看日志文件内容"""
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            
        # 只显示最后 N 行
        display_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        print(f"\n📄 文件：{log_file}")
        print(f"📊 总行数：{len(all_lines)}, 显示：{len(display_lines)} 行\n")
        print("=" * 80)
        
        for line in display_lines:
            print(line, end='')
            
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ 读取失败：{e}")


def main():
    # 解析命令行参数
    module_name = "Agent"
    num_lines = 50
    
    if len(sys.argv) > 1:
        module_name = sys.argv[1].capitalize()
    
    if len(sys.argv) > 2:
        try:
            num_lines = int(sys.argv[2])
        except ValueError:
            print(f"⚠️ 无效的行数：{sys.argv[2]}, 使用默认值 50")
    
    # 获取最新日志文件
    log_file = get_latest_log_file(module_name)
    
    if log_file:
        view_log_file(log_file, num_lines)


if __name__ == "__main__":
    main()
