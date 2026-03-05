# LearnTerminalAgent 核心模块

from .agent import AgentLoop
from .config import AgentConfig, get_config
from .tools import get_all_tools
from .todo import TodoManager, get_todo_manager, reset_todo
from .subagent import SubAgent, spawn_subagent
from .skills import SkillLoader, get_skill_loader
from .context import ContextCompactor, get_compactor, estimate_tokens
from .task_system import TaskManager, get_task_manager, reset_tasks
from .background import BackgroundManager, get_bg_manager, reset_background
from .teams import TeammateManager, MessageBus, get_teammate_manager, get_bus, reset_teams

__version__ = "2.1.0"
__all__ = [
    # 核心
    "AgentLoop",
    "AgentConfig",
    "get_config",
    "get_all_tools",
    
    # s03: TodoWrite
    "TodoManager",
    "get_todo_manager",
    "reset_todo",
    
    # s04: SubAgent
    "SubAgent",
    "spawn_subagent",
    
    # s05: Skills
    "SkillLoader",
    "get_skill_loader",
    
    # s06: Context
    "ContextCompactor",
    "get_compactor",
    "estimate_tokens",
    
    # s07: Task System
    "TaskManager",
    "get_task_manager",
    "reset_tasks",
    
    # s08: Background Tasks
    "BackgroundManager",
    "get_bg_manager",
    "reset_background",
    
    # s09: Agent Teams
    "TeammateManager",
    "MessageBus",
    "get_teammate_manager",
    "get_bus",
    "reset_teams",
]
