"""
LearnTerminalAgent 工具模块

提供所有可用的工具定义
"""

import os
import subprocess
from typing import Optional
from langchain_core.tools import tool
from ..infrastructure.tool_logger import log_tool_call
from ..core.config import get_config
from ..infrastructure.workspace import get_workspace
from ..infrastructure.logger import logger_tools, timing


@tool
@log_tool_call
def bash(command: str) -> str:
    """
    运行 shell 命令 - 当用户要求“运行”、“执行”命令或脚本时使用
    
    Args:
        command: 要执行的 shell 命令
        
    Returns:
        命令的输出结果
    
    USAGE TRIGGER: User says "运行...", "执行...", "run command", "execute..."
    """
    config = get_config()
    workspace = get_workspace()  # 获取工作空间
    
    # 安全检查：阻止危险命令
    for pattern in config.dangerous_patterns:
        if pattern in command:
            return f"Error: Dangerous command '{pattern}' blocked"
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=workspace.root,  # 强制在工作空间根目录执行
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
@log_tool_call
def read_file(path: str, limit: Optional[int] = None) -> str:
    """
    读取文件内容 - 当用户要求“读取”、“查看...内容”时使用
    
    Args:
        path: 文件路径
        limit: 最大读取行数（可选）
        
    Returns:
        文件内容
    
    USAGE TRIGGER: User says "读取...", "查看...的内容", "read file", "show me..."
    """
    try:
        workspace = get_workspace()
        # 使用工作空间管理器验证路径
        abs_path = workspace.resolve_path(path)
        
        with open(abs_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            if limit and limit < len(lines):
                lines = lines[:limit]
                lines.append(f"\n... ({len(lines) - limit} more lines)")
            
            content = ''.join(lines)
            return content[:50000] if len(content) > 50000 else content
            
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except ValueError as e:
        # 路径越界错误
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error: {type(e).__name__}: {str(e)}"


@tool
@log_tool_call
def write_file(path: str, content: str) -> str:
    """
    写入文件内容 - 当用户要求“创建”、“新建”、“写入”文件时使用
    
    Args:
        path: 文件路径
        content: 要写入的内容
        
    Returns:
        操作结果
    
    USAGE TRIGGER: User says "创建...文件", "新建...", "write to file", "create..."
    """
    try:
        workspace = get_workspace()
        abs_path = workspace.resolve_path(path)
        
        # 创建父目录（如果不存在）
        os.makedirs(os.path.dirname(abs_path) or '.', exist_ok=True)
        
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 日志记录详细信息（包含内容预览）
        content_preview = content[:100] + "..." if len(content) > 100 else content
        logger_tools.debug(f"写入文件：{path}")
        logger_tools.debug(f"  - 内容长度：{len(content)} 字符")
        logger_tools.debug(f"  - 内容预览：{content_preview}")
        
        # 终端返回简洁结果
        return f"Successfully wrote {len(content)} characters to {path}"
        
    except ValueError as e:
        logger_tools.error(f"写入文件失败：{path}")
        logger_tools.error(f"  - 错误：{str(e)}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger_tools.error(f"写入文件异常：{path}")
        logger_tools.error(f"  - 错误类型：{type(e).__name__}")
        logger_tools.error(f"  - 错误：{str(e)}")
        return f"Error: {type(e).__name__}: {str(e)}"


@tool
@log_tool_call
def edit_file(file_path: str, original_text: str, new_text: str) -> str:
    """
    编辑文件中的文本内容 - 执行精确的字符串替换（自动创建备份）
    
    Args:
        file_path: 要编辑的文件路径
        original_text: 要被替换的原始文本 (必须完全匹配)
        new_text: 替换后的新文本
        
    Returns:
        操作结果
    """
    try:
        workspace = get_workspace()
        abs_path = workspace.resolve_path(file_path)
        
        if not os.path.exists(abs_path):
            return f"Error: File not found: {file_path}"
        
        # 【后悔药】创建备份
        from .backup import get_backup_manager
        backup_manager = get_backup_manager(str(workspace.root))
        backup_id = backup_manager.create_backup(file_path, operation="edit")
        
        if backup_id:
            logger_tools.info(f"Backup created before edit: {backup_id}")
        
        # 读取文件内容
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找原始文本
        if original_text not in content:
            return f"Error: Original text not found in file"
        
        # 执行替换
        new_content = content.replace(original_text, new_text, 1)
        
        # 写回文件
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        changes = len(new_text) - len(original_text)
        change_desc = f"+{changes}" if changes > 0 else str(changes)
        
        result = f"Successfully edited {file_path}: replaced {len(original_text)} chars with {len(new_text)} chars (net change: {change_desc} chars)"
        if backup_id:
            result += f"\nBackup ID: {backup_id} (use restore_backup to revert)"
        
        return result
        
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error: {type(e).__name__}: {str(e)}"


@tool
@log_tool_call
def delete_file(file_path: str, force: bool = False) -> str:
    """
    删除文件 - 自动创建备份（后悔药功能）
    
    Args:
        file_path: 要删除的文件路径
        force: 是否强制删除（不创建备份，默认 False）
        
    Returns:
        操作结果
    """
    try:
        workspace = get_workspace()
        abs_path = workspace.resolve_path(file_path)
        
        if not abs_path.exists():
            return f"Error: File not found: {file_path}"
        
        # 检查是否是目录
        if abs_path.is_dir():
            return f"Error: Cannot delete directory with this tool. Use bash command instead."
        
        # 【后悔药】创建备份（除非强制删除）
        backup_id = None
        if not force:
            from .backup import get_backup_manager
            backup_manager = get_backup_manager(str(workspace.root))
            backup_id = backup_manager.create_backup(file_path, operation="delete")
            
            if backup_id:
                logger_tools.info(f"Backup created before delete: {backup_id}")
        
        # 删除文件
        abs_path.unlink()
        
        result = f"Successfully deleted {file_path}"
        if backup_id:
            result += f"\nBackup ID: {backup_id} (use restore_backup to recover)"
        elif force:
            result += "\nNote: No backup created (force=True)"
        
        return result
        
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error: {type(e).__name__}: {str(e)}"


@tool
@log_tool_call
def format_html_output(content: str, style: str = "default") -> str:
    """
    使用 HTML 标签格式化输出内容，优化终端显示效果
    
    Args:
        content: 要格式化的内容
        style: 样式类型 (default, code, success, warning, error, info)
        
    Returns:
        格式化后的 HTML 内容
    """
    styles = {
        "default": "color: #333; background: #f5f5f5; padding: 8px; border-radius: 4px;",
        "code": "color: #24292e; background: #f6f8fa; padding: 12px; border-radius: 6px; font-family: monospace; white-space: pre-wrap;",
        "success": "color: #22863a; background: #dcffe4; padding: 8px; border-radius: 4px; border-left: 4px solid #28a745;",
        "warning": "color: #735c0f; background: #fffbdd; padding: 8px; border-radius: 4px; border-left: 4px solid #f0b37e;",
        "error": "color: #cb2431; background: #ffeef0; padding: 8px; border-radius: 4px; border-left: 4px solid #d73a49;",
        "info": "color: #0366d6; background: #f1f8ff; padding: 8px; border-radius: 4px; border-left: 4px solid #2188ff;",
    }
    
    selected_style = styles.get(style, styles["default"])
    
    # 创建 HTML 片段
    html_content = (
        f"<div style=\"{selected_style}\">"
        f"{content}"
        f"</div>"
    )
    
    return html_content


@tool
@log_tool_call
def list_directory(path: str = ".") -> str:
    """
    列出目录内容 - 当用户要求“查看”、“列出”文件或文件夹时使用
    
    Args:
        path: 目录路径（默认当前目录）
        
    Returns:
        目录中的文件和文件夹列表
    
    USAGE TRIGGER: User says "查看...", "列出...", "show files", "list directory"
    """
    try:
        workspace = get_workspace()
        abs_path = workspace.resolve_path(path)
        
        if not abs_path.exists():
            return f"Error: Directory not found: {path}"
        
        items = os.listdir(abs_path)
        
        # 分类文件和目录
        dirs = []
        files = []
        
        for item in sorted(items):
            item_path = abs_path / item
            if item_path.is_dir():
                dirs.append(f"[DIR] {item}/")
            else:
                files.append(f"[FILE] {item}")
        
        rel_path = workspace.get_relative_path(abs_path)
        result = [f"Directory: {rel_path}"]
        if dirs:
            result.append("\nFolders:")
            result.extend(dirs)
        if files:
            result.append("\nFiles:")
            result.extend(files)
        
        return '\n'.join(result)
        
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error: {type(e).__name__}: {str(e)}"


def get_all_tools():
    """获取所有可用工具"""
    from .todo import get_todo_tools
    from .task_system import get_task_tools
    from ..services.background import get_background_tools
    from ..agents.teams import get_team_tools
    from .skills import get_skill_tools
    # 新增：记忆管理和搜索工具
    from .memory_retrieval_tool import search_memory
    from .code_search_tool import search_code
    from .file_search_tool import search_files, find_files_by_content
    
    return [
        # 基础工具
        bash,
        read_file,
        write_file,
        edit_file,
        delete_file,  # 新增删除工具
        list_directory,
        format_html_output,
        # 备份管理工具（后悔药）
        restore_backup,
        list_backups,
        delete_backup,
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
        # 记忆管理和搜索工具（新增）
        search_memory,
        search_code,
        search_files,
        find_files_by_content,
    ]


# ========== 后悔药功能：备份管理工具 ==========

@tool
@log_tool_call
def restore_backup(backup_id: str) -> str:
    """
    恢复备份 - 回滚文件到之前的版本（后悔药功能）
    
    Args:
        backup_id: 备份 ID（通过 list_backups 查看）
        
    Returns:
        恢复结果
    
    USAGE: 当需要撤销编辑或恢复误删的文件时使用
    """
    from .backup import get_backup_manager
    workspace = get_workspace()
    backup_manager = get_backup_manager(str(workspace.root))
    return backup_manager.restore_backup(backup_id)


@tool
@log_tool_call
def list_backups(limit: int = 10) -> str:
    """
    列出最近的备份 - 查看所有可用的"后悔药"
    
    Args:
        limit: 最大显示数量（默认 10）
        
    Returns:
        备份列表
    
    USAGE: 需要查看可恢复的备份时使用
    """
    from .backup import get_backup_manager
    workspace = get_workspace()
    backup_manager = get_backup_manager(str(workspace.root))
    return backup_manager.list_backups(limit)


@tool
@log_tool_call
def delete_backup(backup_id: str) -> str:
    """
    删除指定的备份 - 清理不需要的"后悔药"
    
    Args:
        backup_id: 备份 ID
        
    Returns:
        删除结果
    
    USAGE: 清理旧备份以节省空间
    """
    from .backup import get_backup_manager
    workspace = get_workspace()
    backup_manager = get_backup_manager(str(workspace.root))
    return backup_manager.delete_backup(backup_id)
