"""
LearnTerminalAgent Memory Retrieval Tool

实现从历史会话中检索相关记忆片段的功能
核心优化：仅在当前工作空间有历史记录时才触发检索
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Optional
from langchain_core.tools import tool

from ..infrastructure.tool_logger import log_tool_call
from ..infrastructure.logger import logger_tools
from ..infrastructure.project_config import get_project_config

# 获取项目配置
PROJECT = get_project_config()


class MemoryRetriever:
    """
    记忆检索器
    
    负责从历史会话中搜索与当前查询相关的记忆片段
    优化策略：只检索当前工作空间的历史记录
    """
    
    def __init__(self, storage_dir: Optional[str] = None):
        """
        初始化检索器
        
        Args:
            storage_dir: 存储目录路径（可选，默认使用配置）
        """
        self.storage_dir = Path(storage_dir) if storage_dir else PROJECT.data_dir / ".transcripts"
        
        # 缓存机制
        self._workspace_cache: Dict[str, bool] = {}
        self._last_check_time: float = 0
        self._check_interval: int = 300  # 5 分钟检查间隔
        
        # 确保目录存在
        if not self.storage_dir.exists():
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        logger_tools.debug(f"MemoryRetriever initialized: {self.storage_dir}")
    
    def has_workspace_history(self, workspace_root: str) -> bool:
        """
        快速检查当前工作空间是否有历史记忆
        
        Args:
            workspace_root: 工作空间路径
            
        Returns:
            bool: True 表示有历史记录
        """
        current_time = time.time()
        
        # 使用缓存避免频繁 IO（5 分钟内有效）
        cache_key = str(workspace_root)
        if (current_time - self._last_check_time) < self._check_interval:
            return self._workspace_cache.get(cache_key, False)
        
        # 扫描文件系统
        for session_file in self.storage_dir.glob("session_*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session = json.load(f)
                    if session.get('workspace_root') == workspace_root:
                        self._workspace_cache[cache_key] = True
                        self._last_check_time = current_time
                        logger_tools.debug(f"Found workspace history: {workspace_root}")
                        return True
            except (json.JSONDecodeError, IOError) as e:
                logger_tools.warning(f"Failed to read {session_file}: {e}")
                continue
        
        # 缓存负面结果
        self._workspace_cache[cache_key] = False
        self._last_check_time = current_time
        logger_tools.debug(f"No workspace history found: {workspace_root}")
        return False
    
    def search(
        self,
        query: str,
        workspace_filter: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        执行搜索（仅在有历史记忆时调用）
        
        Args:
            query: 搜索关键词
            workspace_filter: 工作空间路径（必须与当前工作空间一致）
            limit: 最大结果数
            
        Returns:
            相关记忆片段列表
        """
        # 优先筛选工作空间匹配的会话
        sessions = self._load_sessions(workspace_filter=workspace_filter)
        
        if not sessions:
            logger_tools.debug(f"No sessions found for workspace: {workspace_filter}")
            return []
        
        # 计算相关性并排序
        results_with_scores = []
        for session in sessions:
            score = self._calculate_relevance(query, session)
            if score > 0.3:  # 最低相关性阈值
                results_with_scores.append((score, session))
        
        # 按相关性排序
        results_with_scores.sort(key=lambda x: x[0], reverse=True)
        
        # 返回 Top-N
        top_results = [
            {'score': score, 'session': session}
            for score, session in results_with_scores[:limit]
        ]
        
        logger_tools.info(f"Found {len(top_results)} relevant memories for query: {query[:50]}")
        return top_results
    
    def _load_sessions(
        self,
        force_reload: bool = False,
        workspace_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        加载会话到缓存
        
        Args:
            force_reload: 强制重新加载
            workspace_filter: 工作空间路径过滤
            
        Returns:
            会话列表
        """
        # 简单实现：每次都重新加载（可以后续优化为缓存）
        sessions = []
        
        for session_file in self.storage_dir.glob("session_*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session = json.load(f)
                    
                    # 如果指定了工作空间过滤，只保留匹配的
                    if workspace_filter:
                        if session.get('workspace_root') == workspace_filter:
                            sessions.append(session)
                    else:
                        sessions.append(session)
            except Exception as e:
                logger_tools.error(f"Failed to load {session_file}: {e}")
                continue
        
        return sessions
    
    def _calculate_relevance(self, query: str, session: Dict) -> float:
        """
        计算查询与会话的相关性分数
        
        简单实现：基于关键词匹配
        TODO: 可以实现 BM25 或语义相似度
        
        Args:
            query: 搜索查询
            session: 会话数据
            
        Returns:
            相关性分数 (0.0 - 1.0)
        """
        query_lower = query.lower()
        score = 0.0
        
        # 检查消息内容
        messages = session.get('messages', [])
        for msg in messages:
            content = msg.get('content', '').lower()
            
            # 简单的关键词匹配计数
            query_words = query_lower.split()
            for word in query_words:
                if len(word) > 2 and word in content:
                    score += 0.1
        
        # 归一化到 0-1 范围
        normalized_score = min(score / 5.0, 1.0)
        
        return normalized_score
    
    def _format_results(self, results: List[Dict]) -> str:
        """
        格式化为 Markdown 输出
        
        Args:
            results: 搜索结果列表
            
        Returns:
            格式化的 Markdown 字符串
        """
        if not results:
            return "未找到相关记忆记录"
        
        output_lines = [f"## 记忆搜索结果 (找到 {len(results)} 条相关记录)\n"]
        
        for i, result in enumerate(results, 1):
            session = result['session']
            score = result['score']
            
            # 基本信息
            session_id = session.get('session_id', 'Unknown')
            start_time = session.get('start_time', 'Unknown')
            workspace = session.get('workspace_root', 'Unknown')
            
            output_lines.append(f"### {i}. {session_id} (相关性：{score:.2f})")
            output_lines.append(f"**时间**: {start_time}")
            output_lines.append(f"**工作空间**: {workspace}")
            
            # 提取关键消息
            messages = session.get('messages', [])
            if messages:
                output_lines.append("**片段**:")
                for msg in messages[:3]:  # 只显示前 3 条消息
                    msg_type = msg.get('type', 'unknown')
                    content = msg.get('content', '')[:200]
                    if content:
                        prefix = "👤 User" if msg_type == "human" else "🤖 Assistant" if msg_type == "ai" else "🔧 Tool"
                        output_lines.append(f"> {prefix}: {content}...")
            
            # 元数据
            metadata = session.get('metadata', {})
            tool_calls = metadata.get('tool_calls_count', 0)
            tasks = metadata.get('tasks_completed', [])
            
            if tool_calls > 0:
                output_lines.append(f"\n**工具调用**: {tool_calls} 次")
            if tasks:
                output_lines.append(f"**完成任务**: {', '.join(tasks)}")
            
            output_lines.append("\n---\n")
        
        return "\n".join(output_lines)
    
    def clear_cache(self):
        """清除缓存"""
        self._workspace_cache.clear()
        self._last_check_time = 0


# ========== 工具定义 ==========

@tool
@log_tool_call
def search_memory(
    query: str,
    workspace_path: Optional[str] = None,
    limit: int = 5
) -> str:
    """
    从历史会话中搜索相关记忆
    
    仅在当前工作空间有历史记录时才触发检索
    
    Args:
        query: 搜索关键词或语义查询
        workspace_path: 工作空间路径（可选，默认当前工作空间）
        limit: 最大返回结果数（默认 5）
    
    Returns:
        格式化的搜索结果
    
    USAGE TRIGGER: 当用户询问"之前做过类似的事情吗？"、"查找历史记录"等时使用
    """
    try:
        from ..infrastructure.workspace import get_workspace
        
        # 获取当前工作空间
        workspace = get_workspace()
        current_workspace = str(workspace.root)
        
        # 如果没有指定工作空间，使用当前工作空间
        target_workspace = workspace_path or current_workspace
        
        # 创建检索器
        retriever = MemoryRetriever()
        
        # 首先检查是否有历史记忆
        logger_tools.info(f"Checking workspace history: {target_workspace}")
        if not retriever.has_workspace_history(target_workspace):
            return f"⚠️ 当前工作空间没有历史记忆记录\n\n工作空间：{target_workspace}\n\n建议：开始新的任务，系统将自动保存会话记录。"
        
        # 执行搜索
        logger_tools.info(f"Searching memory for: {query}")
        results = retriever.search(
            query=query,
            workspace_filter=target_workspace,
            limit=limit
        )
        
        # 格式化输出
        if not results:
            return f"📝 未找到与 \"{query}\" 相关的记忆记录\n\n虽然当前工作空间有历史记录，但没有匹配此查询的内容。"
        
        # 使用检索器的格式化方法
        output = retriever._format_results(results)
        return output
        
    except Exception as e:
        logger_tools.error(f"Memory search failed: {e}")
        return f"❌ 记忆搜索失败：{type(e).__name__}: {str(e)}"


# ========== 全局函数 ==========

def get_memory_retriever() -> MemoryRetriever:
    """获取全局 MemoryRetriever 实例"""
    return MemoryRetriever()
