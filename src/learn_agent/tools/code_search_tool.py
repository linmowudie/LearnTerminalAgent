"""
LearnTerminalAgent Code Search Tool

实现在代码文件中搜索特定模式或片段的功能
支持正则表达式、文件类型过滤等高级搜索能力
"""

import re
from pathlib import Path
from typing import List, Dict, Optional
from langchain_core.tools import tool

from ..infrastructure.tool_logger import log_tool_call
from ..infrastructure.logger import logger_tools
from ..infrastructure.workspace import get_workspace
from ..core.config import get_config


class CodeSearcher:
    """
    代码搜索引擎
    
    负责在指定目录范围内搜索代码片段
    """
    
    def __init__(self, workspace_root: str):
        """
        初始化代码搜索引擎
        
        Args:
            workspace_root: 工作空间根路径
        """
        self.workspace = Path(workspace_root)
        
        # 从配置加载设置
        config = get_config()
        search_config = getattr(config, 'search', {})
        self.supported_extensions = search_config.get('supported_extensions', ['.py', '.js', '.ts', '.java'])
        self.exclude_dirs = search_config.get('exclude_directories', ['node_modules', '.git', '__pycache__'])
        self.max_depth = search_config.get('max_search_depth', 10)
        self.default_max_results = search_config.get('default_max_results', 50)
    
    def search(
        self,
        pattern: str,
        extensions: Optional[List[str]] = None,
        exclude_dirs: Optional[List[str]] = None,
        use_regex: bool = False,
        case_sensitive: bool = False,
        max_results: Optional[int] = None,
        context_lines: int = 2
    ) -> List[Dict]:
        """
        执行代码搜索
        
        Args:
            pattern: 搜索模式
            extensions: 文件扩展名过滤（默认使用配置）
            exclude_dirs: 排除的目录列表（默认使用配置）
            use_regex: 是否使用正则表达式
            case_sensitive: 是否区分大小写
            max_results: 最大结果数（默认使用配置）
            context_lines: 上下文行数
            
        Returns:
            搜索结果列表，每项包含：file, line, match, context
        """
        if not self.workspace.exists():
            logger_tools.error(f"Workspace does not exist: {self.workspace}")
            return []
        
        # 使用配置默认值
        if extensions is None:
            extensions = self.supported_extensions
        if exclude_dirs is None:
            exclude_dirs = self.exclude_dirs
        if max_results is None:
            max_results = self.default_max_results
        
        # 编译正则表达式（如果是正则模式）
        if use_regex:
            try:
                flags = 0 if case_sensitive else re.IGNORECASE
                regex = re.compile(pattern, flags)
            except re.error as e:
                logger_tools.error(f"Invalid regex pattern: {e}")
                return []
        else:
            # 普通文本搜索
            search_text = pattern if case_sensitive else pattern.lower()
        
        results = []
        files_searched = 0
        
        # 遍历文件
        for file_path in self._iterate_files(extensions, exclude_dirs):
            if len(results) >= max_results:
                break
            
            try:
                matches = self._search_file(file_path, search_text if not use_regex else regex, use_regex, case_sensitive, context_lines)
                results.extend(matches)
                files_searched += 1
            except Exception as e:
                logger_tools.warning(f"Failed to search {file_path}: {e}")
                continue
        
        # 限制结果数量
        if len(results) > max_results:
            results = results[:max_results]
        
        logger_tools.info(f"Code search completed: {len(results)} results from {files_searched} files")
        return results
    
    def _iterate_files(self, extensions: List[str], exclude_dirs: List[str]) -> List[Path]:
        """
        迭代获取所有匹配的文件
        
        Args:
            extensions: 允许的扩展名列表
            exclude_dirs: 要排除的目录
            
        Returns:
            文件路径列表
        """
        files = []
        
        # 使用 glob 递归查找
        for ext in extensions:
            # 限制深度
            pattern = f"**/*{ext}"
            for file_path in self.workspace.glob(pattern):
                if file_path.is_file():
                    # 检查是否在排除目录中
                    should_exclude = False
                    try:
                        rel_path = file_path.relative_to(self.workspace)
                        for part in rel_path.parts[:-1]:  # 排除文件名，只检查目录部分
                            if part in exclude_dirs or part.startswith('.'):
                                should_exclude = True
                                break
                    except ValueError:
                        should_exclude = True
                    
                    if not should_exclude:
                        files.append(file_path)
        
        return files
    
    def _search_file(
        self,
        file_path: Path,
        search_target,
        use_regex: bool,
        case_sensitive: bool,
        context_lines: int
    ) -> List[Dict]:
        """
        搜索单个文件
        
        Args:
            file_path: 文件路径
            search_target: 搜索目标（字符串或正则对象）
            use_regex: 是否使用正则
            case_sensitive: 是否区分大小写
            context_lines: 上下文行数
            
        Returns:
            匹配结果列表
        """
        matches = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                match_found = False
                
                if use_regex:
                    # 正则匹配
                    if search_target.search(line):
                        match_found = True
                else:
                    # 文本匹配
                    check_line = line if case_sensitive else line.lower()
                    if search_target in check_line:
                        match_found = True
                
                if match_found:
                    # 提取上下文
                    start_line = max(0, line_num - 1 - context_lines)
                    end_line = min(len(lines), line_num + context_lines)
                    
                    context = ''.join(lines[start_line:end_line])
                    
                    # 获取相对路径
                    try:
                        rel_path = file_path.relative_to(self.workspace)
                    except ValueError:
                        rel_path = file_path
                    
                    matches.append({
                        'file': str(rel_path),
                        'line': line_num,
                        'match': line.strip(),
                        'context': context.strip()
                    })
        
        except Exception as e:
            logger_tools.warning(f"Error reading {file_path}: {e}")
        
        return matches
    
    def _format_results(self, results: List[Dict]) -> str:
        """
        格式化为 Markdown 输出
        
        Args:
            results: 搜索结果列表
            
        Returns:
            格式化的 Markdown 字符串
        """
        if not results:
            return "未找到匹配的代码"
        
        output_lines = [f"## 代码搜索结果 (找到 {len(results)} 处匹配)\n"]
        
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
def search_code(
    pattern: str,
    directory: Optional[str] = None,
    file_extensions: Optional[List[str]] = None,
    use_regex: bool = False,
    case_sensitive: bool = False,
    max_results: int = 50
) -> str:
    """
    在代码文件中搜索模式
    
    支持正则表达式、文件类型过滤等高级搜索能力
    
    Args:
        pattern: 搜索模式（支持正则）
        directory: 搜索目录（默认当前工作空间）
        file_extensions: 文件扩展名过滤 (如 ['.py', '.js'])
        use_regex: 是否使用正则表达式
        case_sensitive: 是否区分大小写
        max_results: 最大返回结果数
    
    Returns:
        搜索结果列表
    
    USAGE TRIGGER: 当用户需要"查找某段代码"、"搜索函数定义"、"定位特定实现"时使用
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
        searcher = CodeSearcher(str(search_root))
        
        # 执行搜索
        logger_tools.info(f"Searching code for pattern: {pattern}")
        results = searcher.search(
            pattern=pattern,
            extensions=file_extensions,
            use_regex=use_regex,
            case_sensitive=case_sensitive,
            max_results=max_results
        )
        
        # 格式化输出
        if not results:
            return f"🔍 未找到匹配 \"{pattern}\" 的代码\n\n搜索范围：{search_root}\n文件类型：{file_extensions or '默认'}"
        
        output = searcher._format_results(results)
        
        # 添加搜索信息
        output = f"搜索模式：`{pattern}`\n搜索范围：{search_root}\n\n" + output
        
        return output
        
    except Exception as e:
        logger_tools.error(f"Code search failed: {e}")
        return f"❌ 代码搜索失败：{type(e).__name__}: {str(e)}"


# ========== 全局函数 ==========

def get_code_searcher(workspace_root: str) -> CodeSearcher:
    """获取 CodeSearcher 实例"""
    return CodeSearcher(workspace_root)
