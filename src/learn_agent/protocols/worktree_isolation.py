"""
LearnTerminalAgent Worktree Task Isolation 模块 - s12

实现工作树和任务隔离功能：
- Git worktree 管理
- 任务与 worktree 绑定
- 生命周期事件追踪
"""

import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional
from langchain_core.tools import tool
from ..infrastructure.tool_logger import log_tool_call
from ..core.config import get_config

# 使用 ProjectConfig 管理路径
from ..infrastructure.project_config import get_project_config
PROJECT = get_project_config()
REPO_ROOT = PROJECT.project_root
WORKDIR = PROJECT.data_dir


class EventBus:
    """事件总线 - 记录 worktree/任务生命周期事件"""
    
    def __init__(self, event_log_path: Path):
        self.path = event_log_path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("")
    
    def emit(self, event: str, task: dict = None, worktree: dict = None, error: str = None):
        """发射事件"""
        payload = {
            "event": event,
            "ts": time.time(),
            "task": task or {},
            "worktree": worktree or {},
        }
        if error:
            payload["error"] = error
        
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
    
    def list_recent(self, limit: int = 20) -> str:
        """列出最近事件"""
        n = max(1, min(int(limit or 20), 200))
        lines = self.path.read_text(encoding="utf-8").splitlines()
        recent = lines[-n:]
        
        items = []
        for line in recent:
            try:
                items.append(json.loads(line))
            except Exception:
                items.append({"event": "parse_error", "raw": line})
        
        return json.dumps(items, indent=2)


class WorktreeManager:
    """Worktree 管理器"""
    
    def __init__(self, repo_root: Path, events: EventBus):
        self.repo_root = repo_root
        self.events = events
        self.dir = repo_root / ".worktrees"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.dir / "index.json"
        
        if not self.index_path.exists():
            self.index_path.write_text(json.dumps({"worktrees": []}, indent=2))
        
        self.git_available = self._is_git_repo()
    
    def _is_git_repo(self) -> bool:
        """检查是否是 git 仓库"""
        try:
            r = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return r.returncode == 0
        except Exception:
            return False
    
    def _run_git(self, args: list) -> str:
        """运行 git 命令"""
        if not self.git_available:
            raise RuntimeError("Not in a git repository. worktree tools require git.")
        
        r = subprocess.run(
            ["git"] + args,
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            timeout=120,
        )
        
        if r.returncode != 0:
            msg = (r.stdout + r.stderr).strip()
            raise RuntimeError(msg or f"git {' '.join(args)} failed")
        
        return (r.stdout + r.stderr).strip() or "(no output)"
    
    def _load_index(self) -> dict:
        """加载索引"""
        return json.loads(self.index_path.read_text())
    
    def _save_index(self, data: dict):
        """保存索引"""
        self.index_path.write_text(json.dumps(data, indent=2))
    
    def _find(self, name: str) -> Optional[dict]:
        """查找 worktree"""
        idx = self._load_index()
        for wt in idx.get("worktrees", []):
            if wt.get("name") == name:
                return wt
        return None
    
    def _validate_name(self, name: str):
        """验证名称"""
        if not re.fullmatch(r"[A-Za-z0-9._-]{1,40}", name or ""):
            raise ValueError("Invalid worktree name. Use 1-40 chars: letters, numbers, ., _, -")
    
    def create(self, name: str, task_id: int = None, base_ref: str = "HEAD") -> str:
        """创建 worktree"""
        self._validate_name(name)
        
        if self._find(name):
            raise ValueError(f"Worktree '{name}' already exists in index")
        
        path = self.dir / name
        branch = f"wt/{name}"
        
        self.events.emit(
            "worktree.create.before",
            task={"id": task_id} if task_id is not None else {},
            worktree={"name": name, "base_ref": base_ref},
        )
        
        try:
            self._run_git(["worktree", "add", "-b", branch, str(path), base_ref])
            
            entry = {
                "name": name,
                "path": str(path),
                "branch": branch,
                "task_id": task_id,
                "status": "active",
                "created_at": time.time(),
            }
            
            idx = self._load_index()
            idx["worktrees"].append(entry)
            self._save_index(idx)
            
            # 绑定任务
            if task_id is not None:
                from .tools.task_system import get_task_manager
                manager = get_task_manager()
                try:
                    manager.update(task_id, owner=name)
                except Exception:
                    pass
            
            self.events.emit(
                "worktree.create.after",
                task={"id": task_id} if task_id is not None else {},
                worktree={
                    "name": name,
                    "path": str(path),
                    "branch": branch,
                    "status": "active",
                },
            )
            
            return json.dumps(entry, indent=2)
        
        except Exception as e:
            self.events.emit(
                "worktree.create.failed",
                task={"id": task_id} if task_id is not None else {},
                worktree={"name": name, "base_ref": base_ref},
                error=str(e),
            )
            raise
    
    def list_all(self) -> str:
        """列出所有 worktree"""
        idx = self._load_index()
        wts = idx.get("worktrees", [])
        
        if not wts:
            return "No worktrees in index."
        
        lines = []
        for wt in wts:
            suffix = f" task={wt['task_id']}" if wt.get("task_id") else ""
            lines.append(f"[{wt.get('status', 'unknown')}] {wt['name']} -> {wt['path']} ({wt.get('branch', '-')}){suffix}")
        
        return "\n".join(lines)
    
    def status(self, name: str) -> str:
        """查看 worktree 状态"""
        wt = self._find(name)
        if not wt:
            return f"Error: Unknown worktree '{name}'"
        
        path = Path(wt["path"])
        if not path.exists():
            return f"Error: Worktree path missing: {path}"
        
        r = subprocess.run(
            ["git", "status", "--short", "--branch"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=60,
        )
        
        text = (r.stdout + r.stderr).strip()
        return text or "Clean worktree"
    
    def run(self, name: str, command: str) -> str:
        """在 worktree 中运行命令"""
        # 使用配置文件的危险命令检查（而不是硬编码）
        config = get_config()
        for pattern in config.dangerous_patterns:
            if pattern in command:
                return f"Error: Dangerous command '{pattern}' blocked"
        
        wt = self._find(name)
        if not wt:
            return f"Error: Unknown worktree '{name}'"
        
        path = Path(wt["path"])
        if not path.exists():
            return f"Error: Worktree path missing: {path}"
        
        try:
            r = subprocess.run(
                command,
                shell=True,
                cwd=path,
                capture_output=True,
                text=True,
                timeout=300,
            )
            out = (r.stdout + r.stderr).strip()
            return out[:50000] if out else "(no output)"
        except subprocess.TimeoutExpired:
            return "Error: Timeout (300s)"
    
    def remove(self, name: str, force: bool = False, complete_task: bool = False) -> str:
        """删除 worktree"""
        wt = self._find(name)
        if not wt:
            return f"Error: Unknown worktree '{name}'"
        
        self.events.emit(
            "worktree.remove.before",
            task={"id": wt.get("task_id")} if wt.get("task_id") is not None else {},
            worktree={"name": name, "path": wt.get("path")},
        )
        
        try:
            args = ["worktree", "remove"]
            if force:
                args.append("--force")
            args.append(wt["path"])
            self._run_git(args)
            
            # 完成任务
            if complete_task and wt.get("task_id") is not None:
                from .tools.task_system import get_task_manager
                manager = get_task_manager()
                try:
                    manager.update(wt["task_id"], status="completed")
                    self.events.emit(
                        "task.completed",
                        task={"id": wt["task_id"]},
                        worktree={"name": name},
                    )
                except Exception:
                    pass
            
            # 更新索引
            idx = self._load_index()
            for item in idx.get("worktrees", []):
                if item.get("name") == name:
                    item["status"] = "removed"
                    item["removed_at"] = time.time()
            self._save_index(idx)
            
            self.events.emit(
                "worktree.remove.after",
                task={"id": wt.get("task_id")} if wt.get("task_id") is not None else {},
                worktree={"name": name, "path": wt.get("path"), "status": "removed"},
            )
            
            return f"Removed worktree '{name}'"
        
        except Exception as e:
            self.events.emit(
                "worktree.remove.failed",
                task={"id": wt.get("task_id")} if wt.get("task_id") is not None else {},
                worktree={"name": name, "path": wt.get("path")},
                error=str(e),
            )
            raise
    
    def keep(self, name: str) -> str:
        """保留 worktree"""
        wt = self._find(name)
        if not wt:
            return f"Error: Unknown worktree '{name}'"
        
        idx = self._load_index()
        kept = None
        for item in idx.get("worktrees", []):
            if item.get("name") == name:
                item["status"] = "kept"
                item["kept_at"] = time.time()
                kept = item
        self._save_index(idx)
        
        self.events.emit(
            "worktree.keep",
            task={"id": wt.get("task_id")} if wt.get("task_id") is not None else {},
            worktree={"name": name, "path": wt.get("path"), "status": "kept"},
        )
        
        return json.dumps(kept, indent=2) if kept else f"Error: Unknown worktree '{name}'"


# 全局实例
_events_bus: Optional[EventBus] = None
_worktree_manager: Optional[WorktreeManager] = None


def get_event_bus() -> EventBus:
    """获取事件总线"""
    global _events_bus
    if _events_bus is None:
        _events_bus = EventBus(PROJECT.data_dir / ".worktrees" / "events.jsonl")
    return _events_bus


def get_worktree_manager() -> WorktreeManager:
    """获取 worktree 管理器"""
    global _worktree_manager
    if _worktree_manager is None:
        _worktree_manager = WorktreeManager(REPO_ROOT, get_event_bus())
    return _worktree_manager


@tool
@log_tool_call
def worktree_create(name: str, task_id: int = None, base_ref: str = "HEAD") -> str:
    """创建 worktree"""
    manager = get_worktree_manager()
    return manager.create(name, task_id, base_ref)


@tool
@log_tool_call
def worktree_list() -> str:
    """列出 worktree"""
    manager = get_worktree_manager()
    return manager.list_all()


@tool
@log_tool_call
def worktree_status(name: str) -> str:
    """查看 worktree 状态"""
    manager = get_worktree_manager()
    return manager.status(name)


@tool
@log_tool_call
def worktree_run(name: str, command: str) -> str:
    """在 worktree 中运行命令"""
    manager = get_worktree_manager()
    return manager.run(name, command)


@tool
@log_tool_call
def worktree_remove(name: str, force: bool = False, complete_task: bool = False) -> str:
    """删除 worktree"""
    manager = get_worktree_manager()
    return manager.remove(name, force, complete_task)


@tool
@log_tool_call
def worktree_keep(name: str) -> str:
    """保留 worktree"""
    manager = get_worktree_manager()
    return manager.keep(name)


@tool
@log_tool_call
def worktree_events(limit: int = 20) -> str:
    """查看最近事件"""
    bus = get_event_bus()
    return bus.list_recent(limit)


def reset_worktree():
    """重置 worktree 管理器"""
    global _worktree_manager, _events_bus
    _worktree_manager = None
    _events_bus = None


def get_worktree_tools():
    """获取所有 worktree 相关工具"""
    return [
        worktree_create,
        worktree_list,
        worktree_status,
        worktree_run,
        worktree_remove,
        worktree_keep,
        worktree_events,
    ]
