"""
LearnTerminalAgent File Search Tool

实现文件名搜索和按内容查找文件的功能
支持通配符、递归搜索等高级能力
"""

import fnmatch
from pathlib import Path
from typing import List, Dict, Optional
from langchain_core.tools import tool

from ..infrastructure.tool_logger import log_tool_call
from ..infrastructure.logger import logger_tools
from ..infrastructure.workspace import get_workspace
from ..core.config import get_config


class FileSearcher:
    """
    文件搜索引擎
    
    负责搜索文件名和按内容查找文件
    """
    
    def __init__(self, workspace_root: str):
        """
        初始化文件搜索引擎
        
        Args:
            workspace_root: 工作空间根路径
        """
        self.workspace = Path(workspace_root)
        
        # 从配置加载设置
        config = get_config()
        search_config = getattr(config, 'search', {})
        self.exclude_dirs = search_config.get('exclude_directories', ['node_modules', '.git', '__pycache__'])
        self.max_depth = search_config.get('max_search_depth', 10)
        self.default_max_results = search_config.get('default_max_results', 50)
    
    def search_by_name(
        self,
        name_pattern: str,
        recursive: bool = True,
        case_sensitive: bool = False,
        max_depth: Optional[int] = None,
        max_results: Optional[int] = None
    ) -> List[Dict]:
        """
        搜索文件名
        
        Args:
            name_pattern: 文件名模式（支持通配符 * 和 ?）
            recursive: 是否递归子目录
            case_sensitive: 是否区分大小写
            max_depth: 最大递归深度
            max_results: 最大返回结果数
            
        Returns:
            匹配的文件列表，每项包含：path, size, modified_time
        """
        if not self.workspace.exists():
            logger_tools.error(f"Workspace does not exist: {self.workspace}")
            return []
        
        # 使用配置默认值
        if max_depth is None:
            max_depth = self.max_depth
        if max_results is None:
            max_results = self.default_max_results
        
        results = []
        
        # 处理通配符模式
        if '*' in name_pattern or '?' in name_pattern:
            # 使用 glob 模式
            glob_pattern = f"**/{name_pattern}" if recursive else f"{name_pattern}"
        else:
            # 精确匹配或模糊匹配
            glob_pattern = f"**/*{name_pattern}*" if recursive else f"*{name_pattern}*"
        
        try:
            # 使用 glob 查找
            for file_path in self.workspace.glob(glob_pattern):
                if len(results) >= max_results:
                    break
                
                if file_path.is_file():
                    # 检查是否在排除目录中
                    try:
                        rel_path = file_path.relative_to(self.workspace)
                        depth = len(rel_path.parts) - 1
                        if depth > max_depth:
                            continue
                        
                        should_exclude = False
                        for part in rel_path.parts[:-1]:
                            if part in self.exclude_dirs or part.startswith('.'):
                                should_exclude = True
                                break
                        
                        if should_exclude:
                            continue
                        
                        # 获取文件信息
                        try:
                            stat_info = file_path.stat()
                            results.append({
                                'path': str(rel_path),
                                'size': stat_info.st_size,
                                'modified_time': stat_info.st_mtime,
                                'absolute_path': str(file_path)
                            })
                        except Exception as e:
                            logger_tools.warning(f"Failed to get file info for {file_path}: {e}")
                            continue
                    
                    except ValueError:
                        continue
        
        except Exception as e:
            logger_tools.error(f"File search failed: {e}")
        
        # 按路径排序
        results.sort(key=lambda x: x['path'])
        
        logger_tools.info(f"File search completed: {len(results)} results for pattern: {name_pattern}")
        return results
    
    def search_by_content(
        self,
        content_pattern: str,
        file_pattern: str = "*",
        directory: Optional[str] = None,
        max_results: Optional[int] = None,
        context_lines: int = 2
    ) -> List[Dict]:
        """
        按内容查找文件
        
        Args:
            content_pattern: 内容模式（支持正则）
            file_pattern: 文件名过滤（通配符模式）
            directory: 搜索目录（可选）
            max_results: 最大结果数
            context_lines: 上下文行数
            
        Returns:
            匹配的文件列表，每项包含：file, line, match, context
        """
        if not self.workspace.exists():
            logger_tools.error(f"Workspace does not exist: {self.workspace}")
            return []
        
        # 使用配置默认值
        if max_results is None:
            max_results = self.default_max_results
        
        # 确定搜索根目录
        search_root = Path(directory) if directory else self.workspace
        
        results = []
        files_searched = 0
        
        # 首先找到匹配的文件名模式
        for file_path in search_root.glob(f"**/{file_pattern}"):
            if len(results) >= max_results:
                break
            
            if not file_path.is_file():
                continue
            
            # 检查是否在排除目录中
            try:
                rel_path = file_path.relative_to(search_root)
                should_exclude = False
                for part in rel_path.parts[:-1]:
                    if part in self.exclude_dirs or part.startswith('.'):
                        should_exclude = True
                        break
                
                if should_exclude:
                    continue
            except ValueError:
                continue
            
            # 搜索文件内容
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    if content_pattern.lower() in line.lower():
                        # 提取上下文
                        start_line = max(0, line_num - 1 - context_lines)
                        end_line = min(len(lines), line_num + context_lines)
                        context = ''.join(lines[start_line:end_line])
                        
                        results.append({
                            'file': str(rel_path),
                            'line': line_num,
                            'match': line.strip(),
                            'context': context.strip(),
                            'absolute_path': str(file_path)
                        })
                        
                        if len(results) >= max_results:
                            break
                
                files_searched += 1
            
            except Exception as e:
                logger_tools.warning(f"Failed to search {file_path}: {e}")
                continue
        
        logger_tools.info(f"Content search completed: {len(results)} results from {files_searched} files")
        return results
    
    def _format_name_results(self, results: List[Dict]) -> str:
        """
        格式化文件名搜索结果
        
        Args:
            results: 搜索结果列表
            
        Returns:
            格式化的 Markdown 字符串
        """
        if not results:
            return "未找到匹配的文件"
        
        output_lines = [f"## 文件搜索结果 (找到 {len(results)} 个文件)\n"]
        
        for i, result in enumerate(results, 1):
            path = result['path']
            size = result['size']
            
            # 格式化大小
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f} MB"
            
            output_lines.append(f"### {i}. `{path}`")
            output_lines.append(f"- 大小：{size_str}")
            output_lines.append("")
        
        return "\n".join(output_lines)
    
    def _format_content_results(self, results: List[Dict]) -> str:
        """
        格式化内容搜索结果
        
        Args:
            results: 搜索结果列表
            
        Returns:
            格式化的 Markdown 字符串
        """
        if not results:
            return "未找到匹配的内容"
        
        output_lines = [f"## 按内容查找结果 (找到 {len(results)} 处匹配)\n"]
        
        # 按文件和行号排序
        sorted_results = sorted(results, key=lambda x: (x['file'], x['line']))
        
        current_file = None
        for i, result in enumerate(sorted_results, 1):
            if result['file'] != current_file:
                current_file = result['file']
                output_lines.append(f"\n### {i}. {current_file}:{result['line']}")
            else:
                output_lines.append(f"\n### {i}. Line {result['line']}")
            
            # 显示匹配行和上下文
            output_lines.append("```")
            output_lines.append(result['context'])
            output_lines.append("```\n")
        
        return "\n".join(output_lines)


# ========== 工具定义 ==========

@tool
@log_tool_call
def search_files(
    name_pattern: str,
    directory: Optional[str] = None,
    recursive: bool = True,
    case_sensitive: bool = False,
    max_depth: Optional[int] = None,
    max_results: int = 100
) -> str:
    """
    搜索文件名
    
    支持通配符（* 和 ?）、递归搜索等高级能力
    
    Args:
        name_pattern: 文件名模式（支持通配符 * 和 ?）
        directory: 搜索目录（默认当前工作空间）
        recursive: 是否递归子目录
        case_sensitive: 是否区分大小写
        max_depth: 最大递归深度
        max_results: 最大返回结果数
    
    Returns:
        匹配的文件列表
    
    USAGE TRIGGER: 当用户需要"查找某个文件"、"搜索配置文件"、"定位特定名称的文件"时使用
    """
    try:
        # 获取工作空间
        workspace = get_workspace()
        
        # 确定搜索根目录
        if directory:
            search_root = workspace.resolve_path(directory)
        else:
            search_root = workspace.root
        
        # 创建搜索引擎
        searcher = FileSearcher(str(search_root))
        
        # 执行搜索
        logger_tools.info(f"Searching files for pattern: {name_pattern}")
        results = searcher.search_by_name(
            name_pattern=name_pattern,
            recursive=recursive,
            case_sensitive=case_sensitive,
            max_depth=max_depth,
            max_results=max_results
        )
        
        # 格式化输出
        if not results:
            return f"📁 未找到匹配 \"{name_pattern}\" 的文件\n\n搜索范围：{search_root}\n递归：{recursive}"
        
        output = searcher._format_name_results(results)
        
        # 添加搜索信息
        output = f"搜索模式：`{name_pattern}`\n搜索范围：{search_root}\n递归：{recursive}\n\n" + output
        
        return output
        
    except Exception as e:
        logger_tools.error(f"File search failed: {e}")
        return f"❌ 文件搜索失败：{type(e).__name__}: {str(e)}"


@tool
@log_tool_call
def find_files_by_content(
    content_pattern: str,
    file_pattern: str = "*",
    directory: Optional[str] = None,
    max_results: int = 50
) -> str:
    """
    按内容查找文件
    
    在文件中搜索包含特定内容的行
    
    Args:
        content_pattern: 内容模式（会进行不区分大小写的匹配）
        file_pattern: 文件名过滤（通配符模式，如 "*.py"）
        directory: 搜索目录（默认当前工作空间）
        max_results: 最大结果数
    
    Returns:
        匹配结果列表
    
    USAGE TRIGGER: 当用户需要"查找某段代码在哪里"、"搜索包含特定文本的文件"时使用
    """
    try:
        # 获取工作空间
        workspace = get_workspace()
        
        # 确定搜索根目录
        if directory:
            search_root = workspace.resolve_path(directory)
        else:
            search_root = workspace.root
        
        # 创建搜索引擎
        searcher = FileSearcher(str(search_root))
        
        # 执行搜索
        logger_tools.info(f"Searching by content: {content_pattern}")
        results = searcher.search_by_content(
            content_pattern=content_pattern,
            file_pattern=file_pattern,
            max_results=max_results
        )
        
        # 格式化输出
        if not results:
            return f"🔍 未找到包含 \"{content_pattern}\" 的内容\n\n搜索范围：{search_root}\n文件模式：{file_pattern}"
        
        output = searcher._format_content_results(results)
        
        # 添加搜索信息
        output = f"搜索内容：`{content_pattern}`\n文件模式：`{file_pattern}`\n搜索范围：{search_root}\n\n" + output
        
        return output
        
    except Exception as e:
        logger_tools.error(f"Content search failed: {e}")
        return f"❌ 内容搜索失败：{type(e).__name__}: {str(e)}"


# ========== 全局函数 ==========

def get_file_searcher(workspace_root: str) -> FileSearcher:
    """获取 FileSearcher 实例"""
    return FileSearcher(workspace_root)
