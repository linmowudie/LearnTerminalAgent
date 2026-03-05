"""
LearnAgent Autonomous Agents 模块 - s11

实现自主代理功能：
- Idle 周期轮询
- 自动认领未分配任务
- 身份重新注入（上下文压缩后）
"""

import json
import os
import threading
import time
from pathlib import Path
from typing import List, Optional, Dict
from langchain_core.tools import tool

from .task_system import get_task_manager


# 全局锁
_claim_lock = threading.Lock()


def scan_unclaimed_tasks() -> List[dict]:
    """扫描未认领的任务"""
    from .task_system import get_task_manager
    manager = get_task_manager()
    
    # 获取所有任务
    tasks_dir = Path.cwd() / ".tasks"
    if not tasks_dir.exists():
        return []
    
    unclaimed = []
    for f in sorted(tasks_dir.glob("task_*.json")):
        try:
            task = json.loads(f.read_text())
            if (task.get("status") == "pending" 
                and not task.get("owner") 
                and not task.get("blockedBy")):
                unclaimed.append(task)
        except Exception:
            continue
    
    return unclaimed


def claim_task(task_id: int, owner: str) -> str:
    """认领任务"""
    with _claim_lock:
        manager = get_task_manager()
        try:
            result = manager.update(task_id, status="in_progress", owner=owner)
            return f"Claimed task #{task_id} for {owner}"
        except Exception as e:
            return f"Error: {e}"


@tool
def idle() -> str:
    """
    进入空闲状态，轮询新任务
    
    Returns:
        状态信息
    """
    return "Entering idle phase. Will poll for new tasks."


@tool
def claim_task_tool(task_id: int) -> str:
    """
    认领任务
    
    Args:
        task_id: 任务 ID
        
    Returns:
        认领结果
    """
    # 从上下文中获取当前队友名称（简化处理，使用默认名称）
    return claim_task(task_id, "autonomous_agent")


def make_identity_block(name: str, role: str, team_name: str) -> dict:
    """
    创建身份块（用于上下文压缩后重新注入）
    
    Args:
        name: 队友名称
        role: 角色
        team_name: 团队名称
        
    Returns:
        身份消息字典
    """
    return {
        "role": "user",
        "content": f"<identity>You are '{name}', role: {role}, team: {team_name}. Continue your work.</identity>",
    }


def reset_autonomous():
    """重置自主代理状态"""
    pass


def get_autonomous_tools():
    """获取所有自主代理相关工具"""
    return [
        idle,
        claim_task_tool,
    ]
