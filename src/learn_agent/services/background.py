"""
LearnTerminalAgent Background Tasks 模块 - s08

实现后台任务功能，支持在后台线程中运行命令
通过通知队列在 LLM 调用前注入结果
"""

import os
import subprocess
import threading
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from langchain_core.tools import tool


class BackgroundManager:
    """
    后台任务管理器
    
    使用线程在后台执行命令，通过通知队列传递结果
    """
    
    def __init__(self):
        self.tasks: Dict[str, dict] = {}  # task_id -> {status, result, command}
        self._notification_queue: List[dict] = []  # 已完成任务的结果
        self._lock = threading.Lock()
    
    def run(self, command: str) -> str:
        """
        启动后台任务
        
        Args:
            command: 要执行的命令
            
        Returns:
            任务 ID
        """
        task_id = str(uuid.uuid4())[:8]
        self.tasks[task_id] = {
            "status": "running",
            "result": None,
            "command": command,
        }
        
        thread = threading.Thread(
            target=self._execute,
            args=(task_id, command),
            daemon=True,
        )
        thread.start()
        
        return f"Background task {task_id} started: {command[:80]}"
    
    def _execute(self, task_id: str, command: str):
        """
        执行后台任务（在线程中运行）
        
        Args:
            task_id: 任务 ID
            command: 命令
        """
        try:
            from ..infrastructure.workspace import get_workspace
            workspace = get_workspace()
            
            r = subprocess.run(
                command,
                shell=True,
                cwd=workspace.root,  # 使用工作空间根目录
                capture_output=True,
                text=True,
                timeout=300,
            )
            output = (r.stdout + r.stderr).strip()[:50000]
            status = "completed"
        except subprocess.TimeoutExpired:
            output = "Error: Timeout (300s)"
            status = "timeout"
        except Exception as e:
            output = f"Error: {e}"
            status = "error"
        
        self.tasks[task_id]["status"] = status
        self.tasks[task_id]["result"] = output or "(no output)"
        
        # 添加到通知队列
        with self._lock:
            self._notification_queue.append({
                "task_id": task_id,
                "status": status,
                "command": command[:80],
                "result": (output or "(no output)")[:500],
            })
    
    def check(self, task_id: Optional[str] = None) -> str:
        """
        检查任务状态
        
        Args:
            task_id: 任务 ID（可选，不提供则列出所有）
            
        Returns:
            任务状态信息
        """
        if task_id:
            t = self.tasks.get(task_id)
            if not t:
                return f"Error: Unknown task {task_id}"
            result = t.get('result') or '(running)'
            return f"[{t['status']}] {t['command'][:60]}\n{result}"
        
        # 列出所有任务
        lines = []
        for tid, t in self.tasks.items():
            lines.append(f"{tid}: [{t['status']}] {t['command'][:60]}")
        return "\n".join(lines) if lines else "No background tasks."
    
    def drain_notifications(self) -> List[dict]:
        """
        返回并清空所有待处理的通知
        
        Returns:
            通知列表
        """
        with self._lock:
            notifs = list(self._notification_queue)
            self._notification_queue.clear()
        return notifs
    
    def get_task_status(self, task_id: str) -> Optional[dict]:
        """获取任务状态"""
        return self.tasks.get(task_id)


# 全局后台管理器实例
_bg_manager: Optional[BackgroundManager] = None


def get_bg_manager() -> BackgroundManager:
    """获取全局后台管理器"""
    global _bg_manager
    if _bg_manager is None:
        _bg_manager = BackgroundManager()
    return _bg_manager


@tool
def background_run(command: str) -> str:
    """
    在后台运行命令（非阻塞）
    
    Args:
        command: 要执行的命令
        
    Returns:
        任务 ID
    """
    manager = get_bg_manager()
    return manager.run(command)


@tool
def check_background(task_id: Optional[str] = None) -> str:
    """
    检查后台任务状态
    
    Args:
        task_id: 任务 ID（可选，不提供则列出所有）
        
    Returns:
        任务状态
    """
    manager = get_bg_manager()
    return manager.check(task_id)


def drain_bg_notifications() -> List[dict]:
    """
    排出后台通知（用于在 Agent 循环中注入结果）
    
    Returns:
        通知列表
    """
    manager = get_bg_manager()
    return manager.drain_notifications()


def reset_background():
    """重置后台管理器"""
    global _bg_manager
    _bg_manager = BackgroundManager()


def get_background_tools():
    """获取所有后台任务相关工具"""
    return [
        background_run,
        check_background,
    ]
