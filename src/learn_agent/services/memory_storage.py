"""
LearnTerminalAgent Memory Storage Module

实现会话记忆的持久化存储功能
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
)

from ..infrastructure.project_config import get_project_config
from ..infrastructure.logger import logger_tools

# 获取项目配置
PROJECT = get_project_config()


class MemoryStorage:
    """
    记忆存储管理器
    
    负责会话的创建、更新和持久化存储
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化记忆存储器
        
        Args:
            config: 配置字典（可选，默认从 config.json 读取）
        """
        # 默认配置
        self.default_config = {
            'enabled': True,
            'storage_dir': str(PROJECT.data_dir / ".transcripts"),
            'min_duration_seconds': 10,
            'save_triggers': ['session_end', 'task_completed'],
            'retention_days': 90,
        }
        
        # 合并用户配置
        if config:
            self.config = {**self.default_config, **config}
        else:
            self.config = self.default_config
        
        self.enabled = self.config.get('enabled', True)
        self.storage_dir = Path(self.config['storage_dir'])
        self.min_duration = self.config.get('min_duration_seconds', 10)
        
        # 确保存储目录存在
        if self.enabled:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # 当前活跃的会话
        self._active_sessions: Dict[str, Dict] = {}
        
        logger_tools.info(f"MemoryStorage initialized: {self.storage_dir}")
    
    def start_session(self, workspace_root: str) -> str:
        """
        开始新会话
        
        Args:
            workspace_root: 当前工作空间路径
            
        Returns:
            session_id: 会话 ID
        """
        if not self.enabled:
            return "disabled"
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        session_id = f"session_{timestamp}"
        
        # 创建会话记录
        session_data = {
            'session_id': session_id,
            'start_time': datetime.now().isoformat(),
            'workspace_root': str(workspace_root),
            'messages': [],
            'metadata': {
                'tool_calls_count': 0,
                'tasks_completed': [],
                'errors': [],
            }
        }
        
        # 保存到内存
        self._active_sessions[session_id] = session_data
        
        logger_tools.debug(f"Session started: {session_id} in {workspace_root}")
        
        return session_id
    
    def end_session(self, session_id: str):
        """
        结束会话并持久化
        
        Args:
            session_id: 会话 ID
        """
        if not self.enabled or session_id == "disabled":
            return
        
        if session_id not in self._active_sessions:
            logger_tools.warning(f"Session not found: {session_id}")
            return
        
        session_data = self._active_sessions[session_id]
        
        # 计算持续时间
        start_time = datetime.fromisoformat(session_data['start_time'])
        duration = (datetime.now() - start_time).total_seconds()
        
        # 判断是否需要保存
        if not self._should_save(session_data, duration):
            logger_tools.debug(f"Session {session_id} skipped (duration={duration}s < {self.min_duration}s)")
            del self._active_sessions[session_id]
            return
        
        # 添加结束时间和持续时间
        session_data['end_time'] = datetime.now().isoformat()
        session_data['metadata']['duration_seconds'] = duration
        
        # 序列化并保存
        try:
            self._save_to_disk(session_data)
            logger_tools.info(f"Session saved: {session_data['session_id']} ({duration:.1f}s)")
        except Exception as e:
            logger_tools.error(f"Failed to save session {session_id}: {e}")
        finally:
            # 从内存中移除
            del self._active_sessions[session_id]
    
    def save_message(self, session_id: str, message: Any, message_type: str = "human"):
        """
        保存单条消息到会话
        
        Args:
            session_id: 会话 ID
            message: 消息对象或内容
            message_type: 消息类型 ("human", "ai", "system", "tool")
        """
        if not self.enabled or session_id == "disabled":
            return
        
        if session_id not in self._active_sessions:
            logger_tools.warning(f"Session not found: {session_id}")
            return
        
        # 转换为可序列化格式
        serialized = self._serialize_message(message, message_type)
        
        if serialized:
            self._active_sessions[session_id]['messages'].append(serialized)
            
            # 统计工具调用
            if message_type == "tool":
                self._active_sessions[session_id]['metadata']['tool_calls_count'] += 1
    
    def mark_task_completed(self, session_id: str, task_id: str):
        """
        标记任务完成（触发保存）
        
        Args:
            session_id: 会话 ID
            task_id: 任务 ID
        """
        if not self.enabled or session_id == "disabled":
            return
        
        if session_id in self._active_sessions:
            self._active_sessions[session_id]['metadata']['tasks_completed'].append(task_id)
            
            # 如果配置了 task_completed 触发保存，立即保存
            if 'task_completed' in self.config.get('save_triggers', []):
                self.end_session(session_id)
    
    def record_error(self, session_id: str, error_msg: str):
        """
        记录错误信息
        
        Args:
            session_id: 会话 ID
            error_msg: 错误消息
        """
        if not self.enabled or session_id == "disabled":
            return
        
        if session_id in self._active_sessions:
            self._active_sessions[session_id]['metadata']['errors'].append({
                'message': error_msg,
                'timestamp': datetime.now().isoformat()
            })
    
    def _should_save(self, session_data: Dict, duration: float) -> bool:
        """
        判断是否满足保存条件
        
        Args:
            session_data: 会话数据
            duration: 持续时间（秒）
            
        Returns:
            bool: 是否应该保存
        """
        # 检查时长
        if duration < self.min_duration:
            return False
        
        # 检查是否有实际内容
        if len(session_data['messages']) == 0:
            return False
        
        # 检查是否在保存触发列表中
        triggers = self.config.get('save_triggers', [])
        
        # 如果有任务完成或错误，总是保存
        if session_data['metadata']['tasks_completed']:
            return True
        if session_data['metadata']['errors']:
            return True
        
        # 如果配置了 session_end 触发器
        if 'session_end' in triggers:
            return True
        
        return False
    
    def _serialize_message(self, message: Any, message_type: str) -> Optional[Dict]:
        """
        序列化消息为 JSON 格式
        
        Args:
            message: 消息对象
            message_type: 消息类型
            
        Returns:
            序列化后的字典
        """
        try:
            item = {
                'type': message_type,
                'timestamp': datetime.now().isoformat()
            }
            
            # 处理 LangChain 消息对象
            if isinstance(message, (HumanMessage, AIMessage, SystemMessage, ToolMessage)):
                item['message_class'] = type(message).__name__
                
                if hasattr(message, 'content'):
                    item['content'] = str(message.content)
                if hasattr(message, 'role'):
                    item['role'] = message.role
                if hasattr(message, 'name'):
                    item['name'] = message.name
                if hasattr(message, 'tool_call_id'):
                    item['tool_call_id'] = message.tool_call_id
            
            # 处理普通字符串
            elif isinstance(message, str):
                item['content'] = message
            
            # 处理字典
            elif isinstance(message, dict):
                item.update(message)
            
            else:
                # 尝试转换为字符串
                item['content'] = str(message)
            
            return item
        
        except Exception as e:
            logger_tools.error(f"Failed to serialize message: {e}")
            return None
    
    def _save_to_disk(self, session_data: Dict):
        """
        保存会话到磁盘
        
        Args:
            session_data: 会话数据
        """
        # 生成文件名
        filename = f"{session_data['session_id']}.json"
        filepath = self.storage_dir / filename
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        logger_tools.debug(f"Session file written: {filepath}")
    
    def cleanup_old_sessions(self, retention_days: Optional[int] = None):
        """
        清理过期会话
        
        Args:
            retention_days: 保留天数（默认使用配置值）
        """
        if not self.enabled:
            return
        
        days = retention_days or self.config.get('retention_days', 90)
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        deleted_count = 0
        
        for session_file in self.storage_dir.glob("session_*.json"):
            try:
                file_mtime = session_file.stat().st_mtime
                if file_mtime < cutoff_time:
                    session_file.unlink()
                    deleted_count += 1
                    logger_tools.debug(f"Deleted old session: {session_file.name}")
            except Exception as e:
                logger_tools.error(f"Failed to delete {session_file}: {e}")
        
        logger_tools.info(f"Cleaned up {deleted_count} old sessions (>{days} days)")
    
    def get_active_session_count(self) -> int:
        """获取当前活跃会话数"""
        return len(self._active_sessions)
    
    def get_storage_stats(self) -> Dict:
        """
        获取存储统计信息
        
        Returns:
            统计信息字典
        """
        session_files = list(self.storage_dir.glob("session_*.json"))
        
        total_size = sum(f.stat().st_size for f in session_files)
        
        return {
            'total_sessions': len(session_files),
            'active_sessions': len(self._active_sessions),
            'storage_dir': str(self.storage_dir),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'enabled': self.enabled,
        }


# 全局实例
_memory_storage: Optional[MemoryStorage] = None


def get_memory_storage(config: Optional[Dict] = None) -> MemoryStorage:
    """
    获取全局 MemoryStorage 实例
    
    Args:
        config: 配置字典（可选）
        
    Returns:
        MemoryStorage 实例
    """
    global _memory_storage
    if _memory_storage is None:
        _memory_storage = MemoryStorage(config)
    return _memory_storage


def reset_memory_storage():
    """重置 MemoryStorage 实例"""
    global _memory_storage
    if _memory_storage:
        # 结束所有活跃会话
        for session_id in list(_memory_storage._active_sessions.keys()):
            _memory_storage.end_session(session_id)
    _memory_storage = None
