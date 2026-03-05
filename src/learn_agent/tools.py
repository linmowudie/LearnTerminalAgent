"""
LearnTerminalAgent 工具模块

提供所有可用的工具定义
"""

import os
import subprocess
from typing import Optional
from langchain_core.tools import tool
from .config import get_config


@tool
def bash(command: str) -> str:
    """
    运行 shell 命令并返回输出
    
    Args:
        command: 要执行的 shell 命令
        
    Returns:
        命令的输出结果
    """
    config = get_config()
    
    # 安全检查：阻止危险命令
    for pattern in config.dangerous_patterns:
        if pattern in command:
            return f"Error: Dangerous command '{pattern}' blocked"
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            timeout=config.timeout
        )
        
        # 合并标准输出和标准错误
        output = (result.stdout + result.stderr).strip()
        
        # 限制输出长度
        if len(output) > 50000:
            output = output[:50000] + "\n... (output truncated)"
        
        return output if output else "(no output)"
        
    except subprocess.TimeoutExpired:
        return f"Error: Command timeout after {config.timeout}s"
    except Exception as e:
        return f"Error: {type(e).__name__}: {str(e)}"


@tool
def read_file(path: str, limit: Optional[int] = None) -> str:
    """
    读取文件内容
    
    Args:
        path: 文件路径
        limit: 最大读取行数（可选）
        
    Returns:
        文件内容
    """
    try:
        # 安全检查：确保路径在工作目录内
        abs_path = os.path.abspath(path)
        if not abs_path.startswith(os.getcwd()):
            return f"Error: Path escapes workspace: {path}"
        
        with open(abs_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            if limit and limit < len(lines):
                lines = lines[:limit]
                lines.append(f"\n... ({len(lines) - limit} more lines)")
            
            content = ''.join(lines)
            return content[:50000] if len(content) > 50000 else content
            
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except Exception as e:
        return f"Error: {type(e).__name__}: {str(e)}"


@tool
def write_file(path: str, content: str) -> str:
    """
    写入文件内容
    
    Args:
        path: 文件路径
        content: 要写入的内容
        
    Returns:
        操作结果
    """
    try:
        # 安全检查：确保路径在工作目录内
        abs_path = os.path.abspath(path)
        if not abs_path.startswith(os.getcwd()):
            return f"Error: Path escapes workspace: {path}"
        
        # 创建父目录（如果不存在）
        os.makedirs(os.path.dirname(abs_path) or '.', exist_ok=True)
        
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully wrote {len(content)} characters to {path}"
        
    except Exception as e:
        return f"Error: {type(e).__name__}: {str(e)}"


@tool
def list_directory(path: str = ".") -> str:
    """
    列出目录内容
    
    Args:
        path: 目录路径（默认当前目录）
        
    Returns:
        目录中的文件和文件夹列表
    """
    try:
        abs_path = os.path.abspath(path)
        
        if not abs_path.startswith(os.getcwd()):
            return f"Error: Path escapes workspace: {path}"
        
        if not os.path.exists(abs_path):
            return f"Error: Directory not found: {path}"
        
        items = os.listdir(abs_path)
        
        # 分类文件和目录
        dirs = []
        files = []
        
        for item in sorted(items):
            item_path = os.path.join(abs_path, item)
            if os.path.isdir(item_path):
                dirs.append(f"📁 {item}/")
            else:
                files.append(f"📄 {item}")
        
        result = [f"Directory: {abs_path}"]
        if dirs:
            result.append("\nFolders:")
            result.extend(dirs)
        if files:
            result.append("\nFiles:")
            result.extend(files)
        
        return '\n'.join(result)
        
    except Exception as e:
        return f"Error: {type(e).__name__}: {str(e)}"


def get_all_tools():
    """获取所有可用工具"""
    from .todo import get_todo_tools
    from .task_system import get_task_tools
    from .background import get_background_tools
    from .teams import get_team_tools
    from .skills import get_skill_tools
    
    return [
        # 基础工具
        bash,
        read_file,
        write_file,
        list_directory,
        # Todo 工具 (s03)
        *get_todo_tools(),
        # Task System 工具 (s07)
        *get_task_tools(),
        # Background Tools (s08)
        *get_background_tools(),
        # Team Tools (s09)
        *get_team_tools(),
        # Skill Tools (s05)
        *get_skill_tools(),
    ]
