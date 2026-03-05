"""
LearnTerminalAgent Agent 循环核心实现

实现完整的 Agent 循环逻辑
"""

from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
)

from .config import get_config, AgentConfig
from .tools import get_all_tools
from .todo import get_todo_manager, reset_todo
from .subagent import SubAgent, spawn_subagent
from .skills import get_skill_loader, reload_skills
from .context import (
    get_compactor,
    ContextCompactor,
    estimate_tokens,
    reset_compactor,
)
from .task_system import get_task_tools, reset_tasks
from .background import get_background_tools, drain_bg_notifications
from .teams import get_team_tools, reset_teams
import os

class AgentLoop:
    """
    Agent 循环实现
    
    核心模式:
        while 有工具调用:
            response = LLM(messages, tools)
            execute tools
            append results
    """
    
    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        system_prompt: Optional[str] = None,
    ):
        """
        初始化 Agent
        
        Args:
            config: Agent 配置（可选，默认使用全局配置）
            system_prompt: 系统提示词（可选）
        """
        # 加载配置
        self.config = config or get_config()
        
        # 初始化 LLM
        self.llm = ChatOpenAI(
            model=self.config.model_name,
            base_url=self.config.base_url,
            api_key=self.config.api_key,
            max_tokens=self.config.max_tokens,
        )
        
        # 获取工具并绑定到 LLM
        self.tools = get_all_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # 系统提示
        if system_prompt:
            self.system_prompt = system_prompt
        else:
            self.system_prompt = (
                f"You are a helpful coding agent at {os.getcwd()}. "
                f"Use the provided tools to solve tasks. "
                f"Act efficiently and don't explain too much."
            )
        
        # 消息历史
        self.messages: List = [
            SystemMessage(content=self.system_prompt)
        ]
        
        # 迭代计数器
        self.iteration_count = 0
        
        # 上下文压缩器
        self.compactor = get_compactor()
        
        # 启用自动压缩
        self.auto_compact_enabled = True
        
        # 后台任务通知
        self._process_background_notifications()
    
    def run(self, query: str, verbose: bool = True) -> str:
        """
        运行 Agent 循环处理用户查询
        
        Args:
            query: 用户查询
            verbose: 是否打印详细日志
            
        Returns:
            Agent 的最终响应
        """
        # 添加用户消息
        self.messages.append(HumanMessage(content=query))
        
        # 循环调用 LLM 直到不需要使用工具
        while True:
            self.iteration_count += 1
            
            # 检查最大迭代次数
            if self.iteration_count > self.config.max_iterations:
                return (
                    f"Error: Reached maximum iterations "
                    f"({self.config.max_iterations})"
                )
            
            # 调用 LLM
            response = self.llm_with_tools.invoke(self.messages)
            
            # 添加 AI 响应到历史
            self.messages.append(response)
            
            # 检查是否有工具调用
            if not response.tool_calls:
                # 没有工具调用，返回最终响应
                return response.content or "思考完成。"
            
            # 执行工具调用
            if verbose:
                print(f"\n[Iteration {self.iteration_count}]")
            
            tool_results = []
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                # 打印工具调用
                if verbose:
                    if tool_name == "bash":
                        cmd = tool_args.get('command', str(tool_args))
                        print(f"\033[33m$ {cmd}\033[0m")
                    else:
                        print(f"\033[33m[{tool_name}] {tool_args}\033[0m")
                
                # 执行工具
                result = self._execute_tool(tool_name, tool_args)
                
                # 打印结果
                if verbose and result:
                    preview = result[:200]
                    if len(result) > 200:
                        preview += "..."
                    print(preview)
                
                # 记录工具结果
                tool_results.append({
                    "name": tool_name,
                    "content": result,
                    "tool_call_id": tool_call.get("id", ""),
                })
            
            # 添加工具结果到消息历史
            for tool_result in tool_results:
                self.messages.append(
                    ToolMessage(
                        content=tool_result["content"],
                        tool_call_id=tool_result["tool_call_id"],
                        name=tool_result["name"],
                    )
                )
            
            # Layer 1: micro_compact - 每次迭代后压缩旧的工具结果
            self.messages = self.compactor.micro_compact(self.messages)
            
            # Layer 2: auto_compact - 检查是否需要自动压缩
            if self.auto_compact_enabled:
                token_count = estimate_tokens(self.messages)
                if token_count > self.compactor.threshold:
                    self.messages = self.compactor.auto_compact(
                        self.messages, self.llm
                    )
        
        # 理论上不会到这里
        return ""
    
    def _process_background_notifications(self):
        """处理后台任务通知并注入到消息历史"""
        notifs = drain_bg_notifications()
        if notifs and len(self.messages) > 1:
            notif_text = "\n".join(
                f"[bg:{n['task_id']}] {n['status']}: {n['result']}" 
                for n in notifs
            )
            self.messages.append(
                HumanMessage(
                    content=f"<background-results>\n{notif_text}\n</background-results>"
                )
            )
            self.messages.append(
                AIMessage(content="Noted background results.")
            )
    
    def _execute_tool(self, tool_name: str, tool_args: dict) -> str:
        """
        执行工具调用
        
        Args:
            tool_name: 工具名称
            tool_args: 工具参数
            
        Returns:
            工具执行结果
        """
        # 查找工具
        tool = None
        for t in self.tools:
            if t.name == tool_name:
                tool = t
                break
        
        if not tool:
            return f"Error: Unknown tool '{tool_name}'"
        
        # 执行工具
        try:
            return tool.invoke(tool_args)
        except Exception as e:
            return f"Error executing {tool_name}: {type(e).__name__}: {str(e)}"
    
    def reset(self):
        """重置 Agent 状态"""
        self.messages = [SystemMessage(content=self.system_prompt)]
        self.iteration_count = 0
        self.compactor.reset()
    
    def get_history(self) -> List:
        """获取消息历史"""
        return self.messages.copy()
    
    def set_system_prompt(self, prompt: str):
        """设置新的系统提示"""
        self.system_prompt = prompt
        # 更新第一条消息
        if self.messages and isinstance(self.messages[0], SystemMessage):
            self.messages[0] = SystemMessage(content=prompt)
    
    # ========== s03: TodoWrite 功能 ==========
    
    def get_todo_progress(self) -> str:
        """获取任务进度"""
        manager = get_todo_manager()
        return manager.render()
    
    def reset_todo(self):
        """重置任务管理器"""
        reset_todo()
    
    # ========== s04: SubAgent 功能 ==========
    
    def spawn_subagent(
        self,
        task: str,
        system_prompt: Optional[str] = None,
        verbose: bool = True,
    ) -> str:
        """
        创建子代理执行任务
        
        Args:
            task: 任务描述
            system_prompt: 子代理系统提示（可选）
            verbose: 是否详细输出
            
        Returns:
            子代理的任务摘要
        """
        return spawn_subagent(
            task=task,
            config=self.config,
            system_prompt=system_prompt,
            verbose=verbose,
        )
    
    # ========== s05: Skill Loading 功能 ==========
    
    def list_skills(self) -> str:
        """列出所有可用技能"""
        loader = get_skill_loader()
        return loader.get_descriptions()
    
    def load_skill(self, name: str) -> str:
        """加载指定技能"""
        loader = get_skill_loader()
        content = loader.get_content(name)
        if content:
            return f"<skill name=\"{name}\">\n{content}\n</skill>"
        else:
            return f"Error: Skill '{name}' not found"
    
    def reload_skills(self) -> str:
        """重新加载技能"""
        return reload_skills.invoke({})
    
    # ========== s06: Context Compaction 功能 ==========
    
    def compact_context(self, manual: bool = True) -> str:
        """
        压缩上下文
        
        Args:
            manual: 是否手动触发
            
        Returns:
            压缩结果
        """
        self.messages = self.compactor.compact(self.messages, self.llm)
        return "Context compressed successfully"
    
    def get_context_stats(self) -> dict:
        """获取上下文统计信息"""
        token_count = estimate_tokens(self.messages)
        compactor_stats = self.compactor.get_stats()
        
        return {
            "current_tokens": token_count,
            "threshold": self.compactor.threshold,
            "compactions": compactor_stats,
            "message_count": len(self.messages),
        }
    
    def enable_auto_compact(self, enabled: bool = True):
        """启用/禁用自动压缩"""
        self.auto_compact_enabled = enabled
    
    # ========== s07: Task System 功能 ==========
    
    def task_create(self, subject: str, description: str = "") -> str:
        """创建新任务"""
        from .task_system import get_task_manager
        manager = get_task_manager()
        return manager.create(subject, description)
    
    def task_get(self, task_id: int) -> str:
        """获取任务详情"""
        from .task_system import get_task_manager
        return get_task_manager().get(task_id)
    
    def task_update(
        self,
        task_id: int,
        status: Optional[str] = None,
        add_blocked_by: Optional[List[int]] = None,
        add_blocks: Optional[List[int]] = None,
    ) -> str:
        """更新任务状态或依赖关系"""
        from .task_system import get_task_manager
        return get_task_manager().update(task_id, status, add_blocked_by, add_blocks)
    
    def task_list(self) -> str:
        """列出所有任务"""
        from .task_system import get_task_manager
        return get_task_manager().list_all()
    
    def reset_tasks(self):
        """重置任务管理器"""
        reset_tasks()
    
    # ========== s08: Background Tasks 功能 ==========
    
    def background_run(self, command: str) -> str:
        """在后台运行命令"""
        from .background import get_bg_manager
        return get_bg_manager().run(command)
    
    def check_background(self, task_id: Optional[str] = None) -> str:
        """检查后台任务状态"""
        from .background import get_bg_manager
        return get_bg_manager().check(task_id)
    
    def reset_background(self):
        """重置后台管理器"""
        reset_background()
    
    # ========== s09: Agent Teams 功能 ==========
    
    def spawn_teammate(self, name: str, role: str, prompt: str) -> str:
        """创建持久化队友代理"""
        from .teams import get_teammate_manager
        return get_teammate_manager().spawn(name, role, prompt)
    
    def list_teammates(self) -> str:
        """列出所有队友"""
        from .teams import get_teammate_manager
        return get_teammate_manager().list_all()
    
    def send_message(self, to: str, content: str, msg_type: str = "message") -> str:
        """发送消息给队友"""
        from .teams import get_bus
        return get_bus().send("lead", to, content, msg_type)
    
    def read_inbox(self) -> str:
        """读取 lead 的收件箱"""
        from .teams import get_bus
        import json
        return json.dumps(get_bus().read_inbox("lead"), indent=2, ensure_ascii=False)
    
    def broadcast(self, content: str) -> str:
        """广播消息给所有队友"""
        from .teams import get_bus, get_teammate_manager
        bus = get_bus()
        manager = get_teammate_manager()
        return bus.broadcast("lead", content, manager.member_names())
    
    def reset_teams(self):
        """重置团队管理器"""
        reset_teams()
