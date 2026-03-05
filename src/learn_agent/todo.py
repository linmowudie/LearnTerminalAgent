"""
LearnTerminalAgent TodoWrite 模块 - s03

实现任务管理和进度追踪功能
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from langchain_core.tools import tool


@dataclass
class TodoItem:
    """任务项"""
    id: str
    text: str
    status: str = "pending"  # pending, in_progress, completed
    
    def __post_init__(self):
        """验证状态"""
        if self.status not in ("pending", "in_progress", "completed"):
            raise ValueError(
                f"Invalid status '{self.status}'. "
                f"Must be: pending, in_progress, completed"
            )


class TodoManager:
    """任务管理器"""
    
    def __init__(self, max_items: int = 20):
        self.items: List[TodoItem] = []
        self.max_items = max_items
        self._counter = 0
    
    def add(self, text: str) -> TodoItem:
        """添加新任务"""
        self._counter += 1
        item = TodoItem(id=str(self._counter), text=text)
        self.items.append(item)
        self._validate()
        return item
    
    def update(self, item_id: str, status: str, text: Optional[str] = None) -> Optional[TodoItem]:
        """更新任务状态或内容"""
        for item in self.items:
            if item.id == item_id:
                if status:
                    item.status = status
                if text:
                    item.text = text
                self._validate()
                return item
        return None
    
    def remove(self, item_id: str) -> bool:
        """删除任务"""
        for i, item in enumerate(self.items):
            if item.id == item_id:
                del self.items[i]
                return True
        return False
    
    def _validate(self):
        """验证任务列表"""
        if len(self.items) > self.max_items:
            raise ValueError(f"Max {self.max_items} todos allowed")
        
        # 检查只有一个 in_progress
        in_progress_count = sum(
            1 for item in self.items if item.status == "in_progress"
        )
        if in_progress_count > 1:
            raise ValueError("Only one task can be in_progress at a time")
        
        # 验证每个任务
        for item in self.items:
            if not item.text.strip():
                raise ValueError(f"Item {item.id}: text required")
    
    def render(self) -> str:
        """渲染任务列表"""
        if not self.items:
            return "No todos."
        
        lines = []
        for item in self.items:
            marker = {
                "pending": "[ ]",
                "in_progress": "[>]",
                "completed": "[x]"
            }[item.status]
            lines.append(f"{marker} #{item.id}: {item.text}")
        
        # 统计进度
        done = sum(1 for item in self.items if item.status == "completed")
        lines.append(f"\n({done}/{len(self.items)} completed)")
        
        return "\n".join(lines)
    
    def get_progress(self) -> Dict:
        """获取进度统计"""
        total = len(self.items)
        done = sum(1 for item in self.items if item.status == "completed")
        in_progress = sum(1 for item in self.items if item.status == "in_progress")
        pending = total - done - in_progress
        
        return {
            "total": total,
            "completed": done,
            "in_progress": in_progress,
            "pending": pending,
            "percentage": (done / total * 100) if total > 0 else 0
        }


# 全局任务管理器实例
_todo_manager: Optional[TodoManager] = None


def get_todo_manager() -> TodoManager:
    """获取全局任务管理器"""
    global _todo_manager
    if _todo_manager is None:
        _todo_manager = TodoManager()
    return _todo_manager


@tool
def todo_add(text: str) -> str:
    """
    添加新任务到待办列表
    
    Args:
        text: 任务描述
        
    Returns:
        更新后的任务列表
    """
    manager = get_todo_manager()
    item = manager.add(text)
    return f"Added task #{item.id}. Current list:\n{manager.render()}"


@tool
def todo_update(item_id: str, status: str, text: Optional[str] = None) -> str:
    """
    更新任务状态或内容
    
    Args:
        item_id: 任务 ID
        status: 新状态 (pending, in_progress, completed)
        text: 新描述（可选）
        
    Returns:
        更新后的任务列表
    """
    manager = get_todo_manager()
    item = manager.update(item_id, status, text)
    if item:
        return f"Updated task #{item_id}. Current list:\n{manager.render()}"
    else:
        return f"Error: Task #{item_id} not found"


@tool
def todo_remove(item_id: str) -> str:
    """
    删除任务
    
    Args:
        item_id: 任务 ID
        
    Returns:
        删除后的任务列表
    """
    manager = get_todo_manager()
    if manager.remove(item_id):
        return f"Removed task #{item_id}. Current list:\n{manager.render()}"
    else:
        return f"Error: Task #{item_id} not found"


@tool
def todo_list() -> str:
    """
    列出所有任务
    
    Returns:
        任务列表字符串
    """
    manager = get_todo_manager()
    return manager.render()


@tool
def todo_progress() -> str:
    """
    显示任务进度统计
    
    Returns:
        进度统计信息
    """
    manager = get_todo_manager()
    progress = manager.get_progress()
    
    lines = [
        f"Total: {progress['total']} tasks",
        f"Completed: {progress['completed']}",
        f"In Progress: {progress['in_progress']}",
        f"Pending: {progress['pending']}",
        f"Progress: {progress['percentage']:.1f}%"
    ]
    
    return "\n".join(lines)


def reset_todo():
    """重置任务管理器"""
    global _todo_manager
    _todo_manager = TodoManager()


def get_todo_tools():
    """获取所有任务工具"""
    return [
        todo_add,
        todo_update,
        todo_remove,
        todo_list,
        todo_progress,
    ]
