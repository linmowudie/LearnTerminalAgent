"""
LearnTerminalAgent Agent Teams 模块 - s09

实现持久化命名代理（队友）功能，支持基于文件 JSONL 收件箱的通信
每个队友在独立线程中运行，通过消息队列进行异步通信
"""

import json
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Set
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

from .config import get_config, AgentConfig
from .project_config import get_project_config

# 使用 ProjectConfig 管理路径
PROJECT = get_project_config()
TEAM_DIR = PROJECT.data_dir / ".team"
INBOX_DIR = TEAM_DIR  # inbox 就在 team 目录下


# 有效的消息类型
VALID_MSG_TYPES: Set[str] = {
    "message",
    "broadcast",
    "shutdown_request",
    "shutdown_response",
    "plan_approval_response",
}


class MessageBus:
    """
    消息总线
    
    每个队友一个 JSONL 收件箱，支持发送、接收和广播消息
    """
    
    def __init__(self, inbox_dir: Path):
        self.dir = inbox_dir
        self.dir.mkdir(parents=True, exist_ok=True)
    
    def send(
        self,
        sender: str,
        to: str,
        content: str,
        msg_type: str = "message",
        extra: Optional[Dict] = None,
    ) -> str:
        """
        发送消息到队友收件箱
        
        Args:
            sender: 发送者名称
            to: 接收者名称
            content: 消息内容
            msg_type: 消息类型
            extra: 额外字段
            
        Returns:
            发送结果
        """
        if msg_type not in VALID_MSG_TYPES:
            return f"Error: Invalid type '{msg_type}'. Valid: {VALID_MSG_TYPES}"
        
        msg = {
            "type": msg_type,
            "from": sender,
            "content": content,
            "timestamp": time.time(),
        }
        if extra:
            msg.update(extra)
        
        inbox_path = self.dir / f"{to}.jsonl"
        with open(inbox_path, "a", encoding='utf-8') as f:
            f.write(json.dumps(msg, ensure_ascii=False) + "\n")
        
        return f"Sent {msg_type} to {to}"
    
    def read_inbox(self, name: str) -> List[dict]:
        """
        读取并清空收件箱
        
        Args:
            name: 队友名称
            
        Returns:
            消息列表
        """
        inbox_path = self.dir / f"{name}.jsonl"
        if not inbox_path.exists():
            return []
        
        messages = []
        for line in inbox_path.read_text(encoding='utf-8').strip().splitlines():
            if line.strip():
                messages.append(json.loads(line))
        
        # 清空收件箱
        inbox_path.write_text("", encoding='utf-8')
        
        return messages
    
    def broadcast(self, sender: str, content: str, teammates: List[str]) -> str:
        """
        广播消息给所有队友
        
        Args:
            sender: 发送者名称
            content: 消息内容
            teammates: 队友名称列表
            
        Returns:
            广播结果
        """
        count = 0
        for name in teammates:
            if name != sender:
                self.send(sender, name, content, "broadcast")
                count += 1
        return f"Broadcast to {count} teammates"


class TeammateManager:
    """
    队友管理器
    
    管理持久化命名代理，每个代理在独立线程中运行
    """
    
    def __init__(self, team_dir: Path):
        self.dir = team_dir
        self.dir.mkdir(exist_ok=True)
        self.config_path = self.dir / "config.json"
        self.config = self._load_config()
        self.threads: Dict[str, threading.Thread] = {}
    
    def _load_config(self) -> dict:
        """加载团队配置"""
        if self.config_path.exists():
            return json.loads(self.config_path.read_text(encoding='utf-8'))
        return {"team_name": "default", "members": []}
    
    def _save_config(self):
        """保存团队配置"""
        self.config_path.write_text(
            json.dumps(self.config, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
    
    def _find_member(self, name: str) -> Optional[dict]:
        """查找成员"""
        for m in self.config["members"]:
            if m["name"] == name:
                return m
        return None
    
    def spawn(self, name: str, role: str, prompt: str) -> str:
        """
        创建新队友
        
        Args:
            name: 队友名称
            role: 角色描述
            prompt: 任务提示
            
        Returns:
            创建结果
        """
        member = self._find_member(name)
        if member:
            if member["status"] not in ("idle", "shutdown"):
                return f"Error: '{name}' is currently {member['status']}"
            member["status"] = "working"
            member["role"] = role
        else:
            member = {"name": name, "role": role, "status": "working"}
            self.config["members"].append(member)
        
        self._save_config()
        
        # 启动队友线程
        thread = threading.Thread(
            target=self._teammate_loop,
            args=(name, role, prompt),
            daemon=True,
        )
        self.threads[name] = thread
        thread.start()
        
        return f"Spawned '{name}' (role: {role})"
    
    def _teammate_loop(self, name: str, role: str, prompt: str):
        """
        队友代理循环（在线程中运行）
        
        Args:
            name: 队友名称
            role: 角色
            prompt: 初始任务
        """
        from .tools import get_all_tools
        
        sys_prompt = (
            f"You are '{name}', role: {role}, at {os.getcwd()}. "
            f"Use send_message to communicate. Complete your task."
        )
        
        messages = [HumanMessage(content=prompt)]
        tools = self._teammate_tools()
        
        # 初始化 LLM
        config = get_config()
        llm = ChatOpenAI(
            model=config.model_name,
            base_url=config.base_url,
            api_key=config.api_key,
            max_tokens=config.max_tokens,
        )
        llm_with_tools = llm.bind_tools(tools)
        
        for _ in range(50):
            # 检查收件箱 - 使用全局的 BUS
            if BUS is None:
                local_bus = MessageBus(INBOX_DIR)
            else:
                local_bus = BUS
            
            inbox = local_bus.read_inbox(name)
            for msg in inbox:
                messages.append(HumanMessage(content=json.dumps(msg, ensure_ascii=False)))
            
            try:
                response = llm_with_tools.invoke(messages)
            except Exception:
                break
            
            messages.append(response)
            
            if not response.tool_calls:
                break
            
            # 执行工具调用
            results = []
            for block in response.tool_calls:
                tool_name = block["name"]
                tool_args = block["args"]
                
                output = self._exec(name, tool_name, tool_args, get_all_tools())
                print(f"  [{name}] {tool_name}: {str(output)[:120]}")
                
                results.append(
                    ToolMessage(
                        content=str(output),
                        tool_call_id=block.get("id", ""),
                        name=tool_name,
                    )
                )
            
            messages.extend(results)
        
        # 更新状态为空闲
        member = self._find_member(name)
        if member and member["status"] != "shutdown":
            member["status"] = "idle"
            self._save_config()
    
    def _exec(
        self,
        sender: str,
        tool_name: str,
        args: dict,
        base_tools: list,
    ) -> str:
        """执行队友的工具调用"""
        # 基础工具执行
        if tool_name == "bash":
            return self._run_bash(args["command"])
        if tool_name == "read_file":
            return self._run_read(args["path"])
        if tool_name == "write_file":
            return self._run_write(args["path"], args["content"])
        if tool_name == "edit_file":
            return self._run_edit(args["path"], args["old_text"], args["new_text"])
        if tool_name == "send_message":
            return BUS.send(
                sender,
                args["to"],
                args["content"],
                args.get("msg_type", "message"),
            )
        if tool_name == "read_inbox":
            return json.dumps(BUS.read_inbox(sender), indent=2, ensure_ascii=False)
        
        return f"Unknown tool: {tool_name}"
    
    def _teammate_tools(self) -> list:
        """获取队友可用工具"""
        return [
            {
                "name": "bash",
                "description": "Run a shell command.",
                "input_schema": {
                    "type": "object",
                    "properties": {"command": {"type": "string"}},
                    "required": ["command"],
                },
            },
            {
                "name": "read_file",
                "description": "Read file contents.",
                "input_schema": {
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"],
                },
            },
            {
                "name": "write_file",
                "description": "Write content to file.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                    },
                    "required": ["path", "content"],
                },
            },
            {
                "name": "edit_file",
                "description": "Replace exact text in file.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "old_text": {"type": "string"},
                        "new_text": {"type": "string"},
                    },
                    "required": ["path", "old_text", "new_text"],
                },
            },
            {
                "name": "send_message",
                "description": "Send message to a teammate.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string"},
                        "content": {"type": "string"},
                        "msg_type": {
                            "type": "string",
                            "enum": list(VALID_MSG_TYPES),
                        },
                    },
                    "required": ["to", "content"],
                },
            },
            {
                "name": "read_inbox",
                "description": "Read and drain your inbox.",
                "input_schema": {"type": "object", "properties": {}},
            },
        ]
    
    def list_all(self) -> str:
        """列出所有队友"""
        if not self.config["members"]:
            return "No teammates."
        
        lines = [f"Team: {self.config['team_name']}"]
        for m in self.config["members"]:
            lines.append(f"  {m['name']} ({m['role']}): {m['status']}")
        return "\n".join(lines)
    
    def member_names(self) -> List[str]:
        """获取所有队友名称"""
        return [m["name"] for m in self.config["members"]]
    
    def _run_bash(self, command: str) -> str:
        """运行 shell 命令"""
        dangerous = ["rm -rf /", "sudo", "shutdown", "reboot"]
        if any(d in command for d in dangerous):
            return "Error: Dangerous command blocked"
        
        try:
            r = subprocess.run(
                command,
                shell=True,
                cwd=os.getcwd(),
                capture_output=True,
                text=True,
                timeout=120,
            )
            out = (r.stdout + r.stderr).strip()
            return out[:50000] if out else "(no output)"
        except subprocess.TimeoutExpired:
            return "Error: Timeout (120s)"
    
    def _run_read(self, path: str, limit: int = None) -> str:
        """读取文件"""
        try:
            abs_path = os.path.abspath(path)
            if not abs_path.startswith(os.getcwd()):
                return f"Error: Path escapes workspace: {path}"
            
            with open(abs_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if limit and limit < len(lines):
                    lines = lines[:limit]
                    lines.append(f"\n... ({len(lines) - limit} more lines)")
            
            content = ''.join(lines)
            return content[:50000] if len(content) > 50000 else content
        except Exception as e:
            return f"Error: {type(e).__name__}: {str(e)}"
    
    def _run_write(self, path: str, content: str) -> str:
        """写入文件"""
        try:
            abs_path = os.path.abspath(path)
            if not abs_path.startswith(os.getcwd()):
                return f"Error: Path escapes workspace: {path}"
            
            os.makedirs(os.path.dirname(abs_path) or '.', exist_ok=True)
            
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"Successfully wrote {len(content)} characters to {path}"
        except Exception as e:
            return f"Error: {type(e).__name__}: {str(e)}"
    
    def _run_edit(self, path: str, old_text: str, new_text: str) -> str:
        """编辑文件"""
        try:
            abs_path = os.path.abspath(path)
            if not abs_path.startswith(os.getcwd()):
                return f"Error: Path escapes workspace: {path}"
            
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if old_text not in content:
                return f"Error: Text not found in {path}"
            
            content = content.replace(old_text, new_text, 1)
            
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"Edited {path}"
        except Exception as e:
            return f"Error: {type(e).__name__}: {str(e)}"


# 全局消息总线实例
BUS: Optional[MessageBus] = None

# 全局队友管理器实例
_team_manager: Optional[TeammateManager] = None


def get_bus() -> MessageBus:
    """获取全局消息总线"""
    global BUS
    if BUS is None:
        inbox_dir = Path.cwd() / ".team" / "inbox"
        BUS = MessageBus(inbox_dir)
    return BUS


def get_teammate_manager() -> TeammateManager:
    """获取全局队友管理器"""
    global _team_manager
    if _team_manager is None:
        team_dir = Path.cwd() / ".team"
        _team_manager = TeammateManager(team_dir)
    return _team_manager


@tool
def spawn_teammate(name: str, role: str, prompt: str) -> str:
    """
    创建持久化队友代理
    
    Args:
        name: 队友名称
        role: 角色描述
        prompt: 任务提示
        
    Returns:
        创建结果
    """
    manager = get_teammate_manager()
    return manager.spawn(name, role, prompt)


@tool
def list_teammates() -> str:
    """
    列出所有队友
    
    Returns:
        队友列表
    """
    manager = get_teammate_manager()
    return manager.list_all()


@tool
def send_message(to: str, content: str, msg_type: str = "message") -> str:
    """
    发送消息给队友
    
    Args:
        to: 接收者名称
        content: 消息内容
        msg_type: 消息类型（可选，默认 message）
        
    Returns:
        发送结果
    """
    bus = get_bus()
    return bus.send("lead", to, content, msg_type)


@tool
def read_inbox() -> str:
    """
    读取 lead 的收件箱
    
    Returns:
        消息列表
    """
    bus = get_bus()
    return json.dumps(bus.read_inbox("lead"), indent=2, ensure_ascii=False)


@tool
def broadcast(content: str) -> str:
    """
    广播消息给所有队友
    
    Args:
        content: 消息内容
        
    Returns:
        广播结果
    """
    bus = get_bus()
    manager = get_teammate_manager()
    return bus.broadcast("lead", content, manager.member_names())


def reset_teams():
    """重置团队管理器"""
    global _team_manager, BUS
    team_dir = Path.cwd() / ".team"
    if team_dir.exists():
        import shutil
        shutil.rmtree(team_dir)
    _team_manager = TeammateManager(team_dir)
    BUS = None


def get_team_tools():
    """获取所有团队相关工具"""
    return [
        spawn_teammate,
        list_teammates,
        send_message,
        read_inbox,
        broadcast,
    ]
