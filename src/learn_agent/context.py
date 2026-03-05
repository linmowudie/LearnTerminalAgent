"""
LearnAgent Context Compaction 模块 - s06

实现上下文压缩功能，支持三层压缩策略
"""

import json
import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
)


# 常量
DEFAULT_THRESHOLD = 50000  # token 阈值
KEEP_RECENT = 3  # 保留最近的工具结果数量

# 使用 ProjectConfig 管理路径
from .project_config import get_project_config
PROJECT = get_project_config()
TRANSCRIPT_DIR = PROJECT.data_dir / ".transcripts"


def estimate_tokens(messages: List) -> int:
    """
    估算 token 数量
    
    粗略估计：每 4 个字符约 1 个 token
    
    Args:
        messages: 消息列表
        
    Returns:
        估算的 token 数量
    """
    return len(str(messages)) // 4


class ContextCompactor:
    """
    上下文压缩器
    
    三层压缩策略：
    1. micro_compact: 静默替换旧的工具结果为占位符（每次迭代）
    2. auto_compact: 超过阈值时保存记录并总结
    3. compact tool: 手动触发立即压缩
    """
    
    def __init__(
        self,
        threshold: int = DEFAULT_THRESHOLD,
        keep_recent: int = KEEP_RECENT,
        transcript_dir: Optional[Path] = None,
    ):
        """
        初始化压缩器
        
        Args:
            threshold: token 阈值
            keep_recent: 保留最近的工具结果数量
            transcript_dir: 记录保存目录
        """
        self.threshold = threshold
        self.keep_recent = keep_recent
        self.transcript_dir = transcript_dir or TRANSCRIPT_DIR
        
        # 确保目录存在
        self.transcript_dir.mkdir(parents=True, exist_ok=True)
        
        # 压缩历史
        self.compact_history: List[Dict] = []
    
    def micro_compact(self, messages: List) -> List:
        """
        Layer 1: 微压缩
        
        替换最近 N 个之外的工具结果为占位符
        
        Args:
            messages: 原始消息列表
            
        Returns:
            压缩后的消息列表
        """
        # 收集所有工具结果
        tool_results = []
        for msg_idx, msg in enumerate(messages):
            if isinstance(msg, ToolMessage):
                tool_results.append((msg_idx, msg))
        
        # 如果不超过阈值，直接返回
        if len(tool_results) <= self.keep_recent:
            return messages
        
        # 创建消息副本
        compacted = list(messages)
        
        # 保留最近的，清除旧的
        to_clear = tool_results[:-self.keep_recent]
        
        for msg_idx, tool_msg in to_clear:
            # 替换为占位符
            tool_name = getattr(tool_msg, 'name', 'tool')
            compacted[msg_idx] = ToolMessage(
                content=f"[Previous: used {tool_name}]",
                tool_call_id=getattr(tool_msg, 'tool_call_id', ''),
                name=tool_name,
            )
        
        return compacted
    
    def auto_compact(self, messages: List, llm=None) -> List:
        """
        Layer 2: 自动压缩
        
        当 token 数超过阈值时触发：
        1. 保存完整记录到磁盘
        2. 使用 LLM 总结对话
        3. 替换所有消息为摘要
        
        Args:
            messages: 原始消息列表
            llm: LLM 实例（用于总结）
            
        Returns:
            压缩后的消息列表
        """
        # 检查是否需要压缩
        token_count = estimate_tokens(messages)
        if token_count <= self.threshold:
            return messages
        
        print(f"\n[Auto Compact] Token count ({token_count}) exceeds threshold ({self.threshold})")
        
        # 1. 保存完整记录
        self._save_transcript(messages)
        
        # 2. 使用 LLM 总结（如果有 LLM）
        if llm:
            summary = self._summarize_with_llm(messages, llm)
        else:
            summary = f"[Context compressed at {time.strftime('%Y-%m-%d %H:%M:%S')}]"
        
        # 3. 替换为摘要
        compacted = [
            SystemMessage(content="You are a coding agent."),
            HumanMessage(
                content=f"{summary}\n\n[Previous conversation compressed. Continue from here.]"
            ),
        ]
        
        # 记录压缩历史
        self.compact_history.append({
            "timestamp": time.time(),
            "original_tokens": token_count,
            "compacted_tokens": estimate_tokens(compacted),
            "type": "auto",
        })
        
        print(f"[Auto Compact] Saved transcript and compressed context")
        
        return compacted
    
    def compact(self, messages: List, llm=None) -> List:
        """
        Layer 3: 手动压缩
        
        立即触发压缩
        
        Args:
            messages: 原始消息列表
            llm: LLM 实例（可选）
            
        Returns:
            压缩后的消息列表
        """
        # 保存记录
        self._save_transcript(messages)
        
        # 总结
        if llm:
            summary = self._summarize_with_llm(messages, llm)
        else:
            summary = f"[Context manually compacted at {time.strftime('%Y-%m-%d %H:%M:%S')}]"
        
        # 替换为摘要
        compacted = [
            SystemMessage(content="You are a coding agent."),
            HumanMessage(
                content=f"{summary}\n\n[Context compacted on user request. Continue from here.]"
            ),
        ]
        
        # 记录
        self.compact_history.append({
            "timestamp": time.time(),
            "original_tokens": estimate_tokens(messages),
            "compacted_tokens": estimate_tokens(compacted),
            "type": "manual",
        })
        
        return compacted
    
    def _save_transcript(self, messages: List):
        """
        保存对话记录到磁盘
        
        Args:
            messages: 消息列表
        """
        self.transcript_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = int(time.time())
        transcript_path = self.transcript_dir / f"transcript_{timestamp}.json"
        
        # 转换为可序列化格式
        serializable = []
        for msg in messages:
            item = {"type": type(msg).__name__}
            
            if hasattr(msg, 'content'):
                item["content"] = str(msg.content)
            if hasattr(msg, 'role'):
                item["role"] = msg.role
            if hasattr(msg, 'name'):
                item["name"] = msg.name
            if hasattr(msg, 'tool_call_id'):
                item["tool_call_id"] = msg.tool_call_id
            
            serializable.append(item)
        
        # 保存
        with open(transcript_path, 'w', encoding='utf-8') as f:
            json.dump(serializable, f, indent=2, ensure_ascii=False)
        
        print(f"[Transcript Saved] {transcript_path}")
    
    def _summarize_with_llm(self, messages: List, llm) -> str:
        """
        使用 LLM 总结对话
        
        Args:
            messages: 原始消息列表
            llm: LLM 实例
            
        Returns:
            摘要字符串
        """
        try:
            # 创建总结请求
            summary_prompt = (
                "Please summarize the following conversation into a concise summary. "
                "Include key decisions, completed tasks, and important context. "
                "The summary should allow continuing the work seamlessly.\n\n"
                "Conversation:\n"
            )
            
            # 添加消息内容
            for i, msg in enumerate(messages[-20:]):  # 只总结最近 20 条
                if isinstance(msg, SystemMessage):
                    continue
                prefix = {"HumanMessage": "User", "AIMessage": "Assistant"}.get(
                    type(msg).__name__, ""
                )
                if prefix and hasattr(msg, 'content'):
                    summary_prompt += f"{prefix}: {msg.content[:500]}\n"
            
            # 调用 LLM
            response = llm.invoke(summary_prompt)
            return response.content or "[Summary unavailable]"
        
        except Exception as e:
            print(f"[Summarization Error] {e}")
            return f"[Summary failed at {time.strftime('%Y-%m-%d %H:%M:%S')}]"
    
    def get_stats(self) -> Dict:
        """
        获取压缩统计
        
        Returns:
            统计信息字典
        """
        total_saved = sum(
            h.get("original_tokens", 0) - h.get("compacted_tokens", 0)
            for h in self.compact_history
        )
        
        return {
            "total_compactions": len(self.compact_history),
            "auto_compactions": sum(1 for h in self.compact_history if h["type"] == "auto"),
            "manual_compactions": sum(1 for h in self.compact_history if h["type"] == "manual"),
            "tokens_saved": total_saved,
            "transcripts_saved": len(list(self.transcript_dir.glob("*.json"))),
        }


# 全局压缩器实例
_compactor: Optional[ContextCompactor] = None


def get_compactor() -> ContextCompactor:
    """获取全局压缩器"""
    global _compactor
    if _compactor is None:
        _compactor = ContextCompactor()
    return _compactor


def reset_compactor():
    """重置压缩器"""
    global _compactor
    _compactor = None
