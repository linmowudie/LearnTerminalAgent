"""
LearnAgent Task System 模块 - s07

实现基于 JSON 文件的持久化任务管理系统，支持依赖关系图
任务以 JSON 文件形式存储在 .tasks/ 目录中，即使上下文压缩也能保存
"""

import json
import os
from pathlib import Path
from typing import List, Optional, Dict
from langchain_core.tools import tool
from dataclasses import dataclass, field

# 使用 ProjectConfig 管理路径
from .project_config import get_project_config
PROJECT = get_project_config()
tasks_dir = PROJECT.data_dir / ".tasks"


@dataclass
class Task:
    """任务数据结构"""
    id: int
    subject: str
    description: str = ""
    status: str = "pending"  # pending, in_progress, completed
    blockedBy: List[int] = field(default_factory=list)
    blocks: List[int] = field(default_factory=list)
    owner: str = ""


class TaskManager:
    """
    任务管理器
    
    CRUD 操作 + 依赖图管理，所有任务持久化为 JSON 文件
    """
    
    def __init__(self, tasks_dir: Path):
        self.dir = tasks_dir
        self.dir.mkdir(exist_ok=True)
        self._next_id = self._max_id() + 1
    
    def _max_id(self) -> int:
        """获取当前最大任务 ID"""
        ids = []
        for f in self.dir.glob("task_*.json"):
            try:
                task_id = int(f.stem.split("_")[1])
                ids.append(task_id)
            except (ValueError, IndexError):
                continue
        return max(ids) if ids else 0
    
    def _load(self, task_id: int) -> Task:
        """加载任务"""
        path = self.dir / f"task_{task_id}.json"
        if not path.exists():
            raise ValueError(f"Task {task_id} not found")
        
        data = json.loads(path.read_text(encoding='utf-8'))
        return Task(**data)
    
    def _save(self, task: Task):
        """保存任务"""
        path = self.dir / f"task_{task.id}.json"
        path.write_text(
            json.dumps(task.__dict__, indent=2),
            encoding='utf-8'
        )
    
    def create(self, subject: str, description: str = "") -> str:
        """创建新任务"""
        task = Task(
            id=self._next_id,
            subject=subject,
            description=description,
            status="pending",
            blockedBy=[],
            blocks=[],
            owner="",
        )
        self._save(task)
        self._next_id += 1
        return json.dumps(task.__dict__, indent=2, ensure_ascii=False)
    
    def get(self, task_id: int) -> str:
        """获取任务详情"""
        task = self._load(task_id)
        return json.dumps(task.__dict__, indent=2, ensure_ascii=False)
    
    def update(
        self,
        task_id: int,
        status: Optional[str] = None,
        add_blocked_by: Optional[List[int]] = None,
        add_blocks: Optional[List[int]] = None,
    ) -> str:
        """更新任务状态或依赖关系"""
        task = self._load(task_id)
        
        if status:
            if status not in ("pending", "in_progress", "completed"):
                raise ValueError(f"Invalid status: {status}")
            task.status = status
            
            # 完成任务时，从所有其他任务的 blockedBy 中移除
            if status == "completed":
                self._clear_dependency(task_id)
        
        if add_blocked_by:
            task.blockedBy = list(set(task.blockedBy + add_blocked_by))
        
        if add_blocks:
            task.blocks = list(set(task.blocks + add_blocks))
            # 双向绑定：更新被阻塞任务的 blockedBy 列表
            for blocked_id in add_blocks:
                try:
                    blocked = self._load(blocked_id)
                    if task_id not in blocked.blockedBy:
                        blocked.blockedBy.append(task_id)
                        self._save(blocked)
                except ValueError:
                    pass
        
        self._save(task)
        return json.dumps(task.__dict__, indent=2, ensure_ascii=False)
    
    def _clear_dependency(self, completed_id: int):
        """从所有任务中移除已完成的依赖"""
        for f in self.dir.glob("task_*.json"):
            try:
                data = json.loads(f.read_text(encoding='utf-8'))
                if completed_id in data.get("blockedBy", []):
                    data["blockedBy"].remove(completed_id)
                    f.write_text(json.dumps(data, indent=2), encoding='utf-8')
            except Exception:
                continue
    
    def list_all(self) -> str:
        """列出所有任务"""
        tasks = []
        for f in sorted(self.dir.glob("task_*.json")):
            try:
                data = json.loads(f.read_text(encoding='utf-8'))
                tasks.append(data)
            except Exception:
                continue
        
        if not tasks:
            return "No tasks."
        
        lines = []
        for t in tasks:
            marker = {
                "pending": "[ ]",
                "in_progress": "[>]",
                "completed": "[x]"
            }.get(t["status"], "[?]")
            
            blocked = f" (blocked by: {t['blockedBy']})" if t.get("blockedBy") else ""
            lines.append(f"{marker} #{t['id']}: {t['subject']}{blocked}")
        
        return "\n".join(lines)


# 全局任务管理器实例
_task_manager: Optional[TaskManager] = None


def get_task_manager() -> TaskManager:
    """获取全局任务管理器"""
    global _task_manager
    if _task_manager is None:
        tasks_dir = Path.cwd() / ".tasks"
        _task_manager = TaskManager(tasks_dir)
    return _task_manager


@tool
def task_create(subject: str, description: str = "") -> str:
    """
    创建新任务
    
    Args:
        subject: 任务主题
        description: 任务描述（可选）
        
    Returns:
        创建的任务详情
    """
    manager = get_task_manager()
    return manager.create(subject, description)


@tool
def task_get(task_id: int) -> str:
    """
    获取任务详情
    
    Args:
        task_id: 任务 ID
        
    Returns:
        任务详情
    """
    manager = get_task_manager()
    return manager.get(task_id)


@tool
def task_update(
    task_id: int,
    status: Optional[str] = None,
    addBlockedBy: Optional[List[int]] = None,
    addBlocks: Optional[List[int]] = None,
) -> str:
    """
    更新任务状态或依赖关系
    
    Args:
        task_id: 任务 ID
        status: 新状态 (pending, in_progress, completed)
        addBlockedBy: 添加依赖的任务 ID 列表（被这些任务阻塞）
        addBlocks: 添加阻塞的任务 ID 列表（阻塞这些任务）
        
    Returns:
        更新后的任务详情
    """
    manager = get_task_manager()
    return manager.update(task_id, status, addBlockedBy, addBlocks)


@tool
def task_list() -> str:
    """
    列出所有任务
    
    Returns:
        任务列表
    """
    manager = get_task_manager()
    return manager.list_all()


def reset_tasks():
    """重置任务管理器（清空所有任务）"""
    global _task_manager
    if tasks_dir.exists():
        for f in tasks_dir.glob("task_*.json"):
            f.unlink()
    _task_manager = TaskManager(tasks_dir)


def get_task_tools():
    """获取所有任务相关工具"""
    return [
        task_create,
        task_get,
        task_update,
        task_list,
    ]
