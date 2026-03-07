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
from ..tools.tools import get_all_tools
from ..infrastructure.workspace import get_workspace
from ..tools.todo import get_todo_manager, reset_todo
from ..agents.subagent import SubAgent, spawn_subagent
from ..infrastructure.logger import logger_agent
from ..tools.skills import get_skill_loader, reload_skills
from ..services.context import (
    get_compactor,
    ContextCompactor,
    estimate_tokens,
    reset_compactor,
)
from ..tools.task_system import get_task_tools, reset_tasks
from ..services.background import get_background_tools, drain_bg_notifications
from ..agents.teams import get_team_tools, reset_teams
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
        workspace_path: Optional[str] = None,  # 新增参数：工作空间路径
    ):
        """
        初始化 Agent
        
        Args:
            config: Agent 配置（可选，默认使用全局配置）
            system_prompt: 系统提示词（可选）
            workspace_path: 工作空间路径（可选，默认当前目录）
        """
        # 初始化工作空间（在所有其他初始化之前）
        workspace = get_workspace()
        # 只有当工作空间未初始化时才初始化
        if workspace.root is None:
            logger_agent.info(f"Agent 初始化工作空间：{workspace_path or '当前目录'}")
            if workspace_path:
                workspace.initialize(workspace_path)
            else:
                workspace.initialize()
        else:
            logger_agent.debug(f"工作空间已初始化，复用：{workspace.root}")
        
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
        
        # 系统提示 - 强调工作空间限制和工具使用
        if system_prompt:
            self.system_prompt = system_prompt
        else:
           self.system_prompt = (
                    f"You are a helpful coding agent working in the directory: {workspace.root}\n"
                    f"ALL file operations MUST be within this workspace.\n"
                    f"You CANNOT access files outside this directory.\n"
                    f"\n"
                    f"CRITICAL MINDSET:\n"
                    f"1. **Verify Before Acting**: Never assume a file's purpose based solely on its filename. "
                    f"If a task involves judging file relevance (e.g., 'delete unrelated files'), you MUST first "
                    f"use `read_file` to inspect the content before making a decision.\n"
                    f"2. **Ambiguity Handling**: If a user request is vague (e.g., 'clean up', 'delete unused'), "
                    f"DO NOT guess. List the potential targets and your reasoning, then ask for specific confirmation.\n"
                    f"3. **Safety First**: Destructive actions are irreversible. When in doubt, ASK.\n"
                    f"\n"
                    f"OPERATIONAL RULES:\n"
                    f"1. ALWAYS respond with SUBSTANTIVE content - NEVER just say '思考完成' or empty phrases.\n"
                    f"2. TOOL USAGE STRATEGY:\n"
                    f"   - **Simple Greetings/Chat** (你好，hello, 谢谢): You can respond DIRECTLY without tools.\n"
                    f"   - **Information Gathering** (查看，检查，读取代码): Use `read_file` or `list_directory` IMMEDIATELY.\n"
                    f"   - **Execution Tasks** (创建，删除，修改，运行): Call the appropriate tool WITHOUT delay.\n"
                    f"   - CRITICAL: If user request IMPLIES needing to check files/directories, USE TOOLS FIRST before responding.\n"
                    f"   - DO NOT describe what you will do in text; just execute the tool.\n"
                    f"3. CRITICAL SAFETY PROTOCOL - File Modification Confirmation:\n"
                    f"   BEFORE executing ANY destructive operation (delete, edit, overwrite):\n"
                    f"   - STEP 1: Verify the target (read content if necessary to ensure it matches user intent).\n"
                    f"   - STEP 2: Present your finding and the proposed action to the user.\n"
                    f"   - STEP 3: Wait for EXPLICIT confirmation ('yes', 'confirm', '确定', '是的').\n"
                    f"   - STEP 4: ONLY THEN execute the destructive tool.\n"
                    f"\n"
                    f"   DESTRUCTIVE operations requiring this protocol:\n"
                    f"   - Deleting files\n"
                    f"   - Editing/modifying existing files\n"
                    f"   - Overwriting files\n"
                    f"\n"
                    f"   SAFE operations (NO confirmation needed):\n"
                    f"   - Reading files, Listing directories, Creating NEW files, Running safe read-only commands.\n"
                    f"\n"
                    f"AVAILABLE TOOLS:\n"
                    f"- `bash`: Run commands, scripts, system info.\n"
                    f"- `read_file`: Read file contents (CRITICAL for verifying file purpose).\n"
                    f"- `write_file`: Create or write files.\n"
                    f"- `edit_file`: Modify existing files.\n"
                    f"- `list_directory`: View directory contents.\n"
                    f"\n"
                    f"EXAMPLE BEHAVIOR SCENARIOS:\n"
                    f"\n"
                    f"[Scenario 0: Simple Greeting - NO Tool Needed]\n"
                    f"User: '你好' or 'Hello'\n"
                    f"Agent: [Responds directly with a friendly greeting, NO tool calls]\n"
                    f"\n"
                    f"[Scenario 1: Simple Task]\n"
                    f"User: '查看当前文件夹内容'\n"
                    f"Agent: [Calls list_directory() IMMEDIATELY]\n"
                    f"\n"
                    f"[Scenario 2: Dangerous Task with Ambiguity - THE KEY FIX]\n"
                    f"User: '删除与该文件夹名无关的文件'\n"
                    f"Agent Thought: I see 'snake_game.py' and 'logistic_regression.ipynb'. Folder is 'LogisticRegression'. "
                    f"'snake_game.py' might be unrelated, BUT it could be a dataset generator. I must check content first.\n"
                    f"Agent Action: [Calls read_file('snake_game.py')]\n"
                    f"Agent Response (after reading): '我检查了 snake_game.py，发现它是一个纯游戏脚本，确实与逻辑回归算法无关。' + "
                    f"'我计划删除它。请确认是否继续？(Yes/No)'\n"
                    f"User: '确定'\n"
                    f"Agent: [Calls bash('del snake_game.py')]\n"
                    f"\n"
                    f"[Scenario 3: Direct Deletion Request]\n"
                    f"User: '删除 test.txt'\n"
                    f"Agent: '确定要删除 test.txt 吗？此操作不可恢复。'\n"
                    f"User: '确定'\n"
                    f"Agent: [Calls bash('del test.txt')]\n"
                    f"\n"
                    f"Remember: **Reading a file to verify safety IS an action.** Do not skip verification steps even if you want to be fast."
                )
        
        # 消息历史
        self.messages: List = [
            SystemMessage(content=self.system_prompt)
        ]
        
        # 迭代计数器
        self.iteration_count = 0
        
        # 空响应重试计数器（避免无限循环）
        self._empty_retry_count = 0
        
        # 上下文压缩器
        self.compactor = get_compactor()
        
        # 启用自动压缩
        self.auto_compact_enabled = True
        
        # 工具调用标志（用于主循环判断是否显示卡片）
        self._has_tool_calls = False
        
        # 后台任务通知
        self._process_background_notifications()
    
    def run(self, query: str, verbose: bool = True, stream: bool = True) -> str:
        """
        运行 Agent 循环处理用户查询
        
        Args:
            query: 用户查询
            verbose: 是否打印详细日志
            stream: 是否使用流式输出
            
        Returns:
            Agent 的最终响应
        """
        # 重置工具调用标志
        self._has_tool_calls = False
        
        # 添加工具使用关键词检测
        action_keywords = {
            '查看': ['list_directory', 'read_file'],
            '创建': ['write_file'],
            '编辑': ['edit_file'],
            '运行': ['bash'],
            '执行': ['bash'],
            '读取': ['read_file'],
            '列出': ['list_directory'],
            'delete': ['bash'],  # 需要谨慎处理
            'create': ['write_file'],
            'run': ['bash'],
            'execute': ['bash'],
            'read': ['read_file'],
            'list': ['list_directory'],
            'view': ['list_directory', 'read_file'],
        }
        
        # 检测用户 query 中是否包含行动关键词
        needs_tool = False
        suggested_tools = []
        for keyword, tools in action_keywords.items():
            if keyword in query or keyword.lower() in query.lower():
                needs_tool = True
                suggested_tools.extend(tools)
        
        # 添加用户消息
        self.messages.append(HumanMessage(content=query))
        
        # 如果是前几次对话或检测到行动关键词，添加强化提醒
        if len(self.messages) <= 10 or needs_tool:
            reminder = (
                "\n\n[SYSTEM REMINDER - CRITICAL]\n"
                "⚠️ YOU MUST USE TOOLS TO TAKE ACTION!\n"
            )
            
            if suggested_tools:
                reminder += (
                    f"🎯 Your query suggests you need: {', '.join(set(suggested_tools))}\n"
                )
            
            reminder += (
                "❌ FORBIDDEN: Empty responses like '思考完成' or just talking\n"
                "✅ REQUIRED: Call appropriate tools IMMEDIATELY\n"
                "[/SYSTEM REMINDER]"
            )
            
            # 将提醒添加到用户消息末尾
            self.messages[-1] = HumanMessage(
                content=self.messages[-1].content + reminder
            )
        
        # 循环调用 LLM 直到不需要使用工具
        while True:
            self.iteration_count += 1
            
            # 检查最大迭代次数
            if self.iteration_count > self.config.max_iterations:
                return (
                    f"Error: Reached maximum iterations "
                    f"({self.config.max_iterations})"
                )
            
            # 调用 LLM（支持流式）
            if stream:
                response = self._stream_invoke(verbose)
            else:
                response = self.llm_with_tools.invoke(self.messages)
            
            # ========== 详细日志：模型响应分析 ==========
            logger_agent.info(f"[Iteration {self.iteration_count}] LLM 响应分析:")
            
            # 1. 记录原始响应内容
            response_content = response.content[:500] if response.content else "(空内容)"
            logger_agent.debug(f"  - 响应内容预览：{response_content}")
            
            # 2. 记录工具调用信息
            if response.tool_calls:
                tool_call_info = []
                for tc in response.tool_calls:
                    tool_call_info.append(f"{tc['name']}({tc['args']})")
                logger_agent.info(f"  - 工具调用：{', '.join(tool_call_info)}")
            else:
                logger_agent.warning(f"  - ⚠️ 无工具调用")
            
            # 3. 分析响应质量
            has_content = bool(response.content and response.content.strip())
            has_tool_calls = bool(response.tool_calls)
            
            if not has_content and not has_tool_calls:
                logger_agent.error(f"  - ❌ 严重问题：既无响应内容也无工具调用！")
            elif not has_tool_calls and needs_tool:
                logger_agent.warning(f"  - ⚠️ 警告：用户请求需要工具，但模型未调用")
                
                # 检查系统提示词是否被正确传递
                system_msg = next((m for m in self.messages if isinstance(m, SystemMessage)), None)
                if system_msg:
                    logger_agent.debug(f"  - 系统提示词长度：{len(system_msg.content)} 字符")
                    if "CRITICAL RULES" in system_msg.content:
                        logger_agent.debug(f"  - ✅ 系统提示词包含 CRITICAL RULES")
                    else:
                        logger_agent.error(f"  - ❌ 系统提示词缺少 CRITICAL RULES！")
                        
                    if "USE TOOLS" in system_msg.content or "USE THE APPROPRIATE TOOL" in system_msg.content:
                        logger_agent.debug(f"  - ✅ 系统提示词包含工具使用说明")
                    else:
                        logger_agent.error(f"  - ❌ 系统提示词缺少工具使用说明！")
            
            # 4. 记录用户消息中的提醒
            last_human_msg = next((m for m in reversed(self.messages) if isinstance(m, HumanMessage)), None)
            if last_human_msg and "[SYSTEM REMINDER" in last_human_msg.content:
                logger_agent.debug(f"  - ✅ 用户消息包含 SYSTEM REMINDER")
                if "list_directory" in last_human_msg.content or "write_file" in last_human_msg.content:
                    logger_agent.debug(f"  - ✅ 提醒中包含具体工具名称")
            # ==========================================
            
            # 添加 AI 响应到历史
            self.messages.append(response)
            
            # ========== 详细日志：消息历史统计 ==========
            logger_agent.debug(f"[消息历史统计]")
            logger_agent.debug(f"  - 总消息数：{len(self.messages)}")
            
            # 统计工具调用历史
            tool_call_history = []
            for i, msg in enumerate(self.messages):
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tc in msg.tool_calls:
                        tool_call_history.append(f"#{i}: {tc['name']}")
            
            if tool_call_history:
                logger_agent.info(f"  - 历史工具调用：{', '.join(tool_call_history)}")
            else:
                logger_agent.warning(f"  - ⚠️ 历史消息中无任何工具调用")
            # ============================================
            
            # 检查是否有工具调用
            if not response.tool_calls:
                # 没有工具调用，检查是否应该调用
                last_human_msg = None
                for msg in reversed(self.messages):
                    if isinstance(msg, HumanMessage):
                        last_human_msg = msg
                        break
                
                # 如果最后一条人类消息包含行动关键词，但 AI 没有调用工具
                if last_human_msg:
                    action_words = ['查看', '创建', '编辑', '运行', '执行', '读取', '列出',
                                   'view', 'create', 'edit', 'run', 'execute', 'read', 'list']
                    has_action = any(word in last_human_msg.content for word in action_words)
                    
                    if has_action:
                        # 限制重试次数，避免无限循环
                        if self._empty_retry_count < 2:
                            logger_agent.warning(
                                f"检测到行动请求但未调用工具，添加提醒并重试 (第{self._empty_retry_count + 1}次)"
                            )
                            # 添加提醒并重试一次
                            self._add_forced_reminder()
                            self._empty_retry_count += 1
                            continue  # 继续循环，再次调用 LLM
                        else:
                            logger_agent.warning(
                                f"已达到最大重试次数，放弃工具调用尝试"
                            )
                
                # 重置重试计数器
                self._empty_retry_count = 0
                
                # 确实不需要工具调用时，返回文本响应
                if not response.content or response.content.strip() == "思考完成":
                    return "我已收到您的请求。请告诉我具体需要做什么？"
                
                return response.content
            
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
    
    def _add_forced_reminder(self):
        """在最后一条 HumanMessage 后添加强制行动提醒"""
        reminder = (
            "\n\n[FORCED REMINDER]\n"
            "⚠️ YOUR LAST RESPONSE WAS EMPTY!\n"
            "You MUST:\n"
            "1. Call appropriate tools to take action\n"
            "2. Provide substantive response\n"
            "3. NEVER say '思考完成' or similar empty phrases\n"
            "[/FORCED REMINDER]"
        )
        
        # 查找最后一条 HumanMessage
        for i in range(len(self.messages) - 1, -1, -1):
            if isinstance(self.messages[i], HumanMessage):
                self.messages[i] = HumanMessage(
                    content=self.messages[i].content + reminder
                )
                break
    
    def _stream_invoke(self, verbose: bool = True) -> AIMessage:
        """
        流式调用 LLM 并实时打印输出
        
        采用混合模式：
        1. 流式显示文本内容（实时体验）
        2. 重新调用获取完整工具调用（可靠性保证）
        3. 空响应检测与强制重试
        """
        from langchain_core.messages import AIMessage
        import sys
        import time
        import threading
        
        # ANSI 颜色代码
        STYLE_CYAN = "\033[36m"
        STYLE_YELLOW = "\033[33m"
        STYLE_RESET = "\033[0m"
        
        # 加载动画控制标志
        loading_stop_event = threading.Event()
        
        def show_loading():
            """在后台显示加载动画"""
            loading_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
            idx = 0
            while not loading_stop_event.is_set():
                # 使用 \r 回到行首，然后重新打印文字和动画
                print(f"\r{STYLE_CYAN}🤖 Agent 思考中:{STYLE_RESET} {loading_chars[idx % len(loading_chars)]}", end="", flush=True)
                idx += 1
                time.sleep(0.1)
            # 清除动画，显示思考完毕并换行
            print(f"\r{STYLE_CYAN}🤖 Agent 思考中:{STYLE_RESET} 思考完毕{STYLE_RESET}\n", end="", flush=True)
        
        try:
            # ========== 详细日志：流式调用开始 ==========
            logger_agent.debug(f"[流式调用] 开始流式调用 LLM")
            logger_agent.debug(f"  - 消息历史长度：{len(self.messages)}")
            
            # 记录最后一条消息的内容类型
            last_msg = self.messages[-1] if self.messages else None
            if last_msg:
                msg_type = type(last_msg).__name__
                content_preview = str(last_msg.content)[:200]
                logger_agent.debug(f"  - 最后消息类型：{msg_type}")
                logger_agent.debug(f"  - 最后内容预览：{content_preview}...")
            # ==========================================
            
            # 流式调用 - 只用于显示文本
            stream = self.llm_with_tools.stream(self.messages)
            
            if verbose:
                # 启动加载动画线程（动画中会包含"🤖 Agent 思考中:"文字）
                loading_thread = threading.Thread(target=show_loading, daemon=True)
                loading_thread.start()
            
            full_content = ""
            has_tool_calls = False
            chunk_count = 0
            first_chunk_received = False
            
            for chunk in stream:
                chunk_count += 1
                
                # 第一个 chunk 到达时，停止加载动画
                if verbose and not first_chunk_received:
                    first_chunk_received = True
                    loading_stop_event.set()  # 停止动画
                    loading_thread.join(timeout=0.2)  # 等待线程结束
                
                # 收集文本内容用于显示
                if hasattr(chunk, 'content') and chunk.content:
                    full_content += chunk.content
                    if verbose:
                        # 逐块打印，模拟打字机效果
                        print(chunk.content, end="", flush=True)
                
                # 检测是否有工具调用片段
                if hasattr(chunk, 'tool_calls') and chunk.tool_calls:
                    has_tool_calls = True
                    # ========== 详细日志：检测到工具调用片段 ==========
                    for tc in chunk.tool_calls:
                        logger_agent.info(f"[流式 chunk #{chunk_count}] 检测到工具调用片段:")
                        logger_agent.info(f"  - 工具名称：{tc.get('name', '未知')}")
                        logger_agent.info(f"  - 参数预览：{str(tc.get('args', '{}'))[:100]}")
                        logger_agent.info(f"  - ID: {tc.get('id', '无')}")
                    # ================================================
            
            if verbose:
                print()  # 换行
            
            # ========== 详细日志：流式调用结束统计 ==========
            logger_agent.info(f"[流式调用] 完成统计:")
            logger_agent.info(f"  - 总 chunk 数：{chunk_count}")
            logger_agent.info(f"  - 收集文本长度：{len(full_content)} 字符")
            logger_agent.info(f"  - 检测到工具调用：{'是' if has_tool_calls else '否'}")
            # ============================================
            
            # 关键改进：如果有工具调用或内容为空，必须重新调用
            if has_tool_calls or not full_content.strip():
                # 标记有工具调用（用于主循环判断是否显示卡片）
                self._has_tool_calls = True
                
                # 重新调用获取完整的工具调用信息
                full_response = self.llm_with_tools.invoke(self.messages)
                
                # 验证响应质量
                if not full_response.tool_calls and not full_response.content:
                    # 如果仍然为空，添加强制提醒并重试
                    logger_agent.warning("LLM 返回空响应，添加强制提醒并重试")
                    self._add_forced_reminder()
                    full_response = self.llm_with_tools.invoke(self.messages)
                
                return full_response
            else:
                # 纯文本回答，直接使用流式结果
                return AIMessage(content=full_content)
                
        except Exception as e:
            # 流式失败，降级到普通调用
            if verbose:
                print(f"\n{STYLE_YELLOW}⚠️ 流式输出失败，切换到普通模式：{e}{STYLE_RESET}")
            return self.llm_with_tools.invoke(self.messages)
    
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
        self._empty_retry_count = 0
        # self.compactor.reset()  # ContextCompactor 没有 reset 方法
    
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
        from ..tools.task_system import get_task_manager
        manager = get_task_manager()
        return manager.create(subject, description)
    
    def task_get(self, task_id: int) -> str:
        """获取任务详情"""
        from ..tools.task_system import get_task_manager
        return get_task_manager().get(task_id)
    
    def task_update(
        self,
        task_id: int,
        status: Optional[str] = None,
        add_blocked_by: Optional[List[int]] = None,
        add_blocks: Optional[List[int]] = None,
    ) -> str:
        """更新任务状态或依赖关系"""
        from ..tools.task_system import get_task_manager
        return get_task_manager().update(task_id, status, add_blocked_by, add_blocks)
    
    def task_list(self) -> str:
        """列出所有任务"""
        from ..tools.task_system import get_task_manager
        return get_task_manager().list_all()
    
    def reset_tasks(self):
        """重置任务管理器"""
        reset_tasks()
    
    # ========== s08: Background Tasks 功能 ==========
    
    def background_run(self, command: str) -> str:
        """在后台运行命令"""
        from ..services.background import get_bg_manager
        return get_bg_manager().run(command)
    
    def check_background(self, task_id: Optional[str] = None) -> str:
        """检查后台任务状态"""
        from ..services.background import get_bg_manager
        return get_bg_manager().check(task_id)
    
    def reset_background(self):
        """重置后台管理器"""
        reset_background()
    
    # ========== s09: Agent Teams 功能 ==========
    
    def spawn_teammate(self, name: str, role: str, prompt: str) -> str:
        """创建持久化队友代理"""
        from .agents.teams import get_teammate_manager
        return get_teammate_manager().spawn(name, role, prompt)
    
    def list_teammates(self) -> str:
        """列出所有队友"""
        from .agents.teams import get_teammate_manager
        return get_teammate_manager().list_all()
    
    def send_message(self, to: str, content: str, msg_type: str = "message") -> str:
        """发送消息给队友"""
        from .agents.teams import get_bus
        return get_bus().send("lead", to, content, msg_type)
    
    def read_inbox(self) -> str:
        """读取 lead 的收件箱"""
        from .agents.teams import get_bus
        import json
        return json.dumps(get_bus().read_inbox("lead"), indent=2, ensure_ascii=False)
    
    def broadcast(self, content: str) -> str:
        """广播消息给所有队友"""
        from .agents.teams import get_bus, get_teammate_manager
        bus = get_bus()
        manager = get_teammate_manager()
        return bus.broadcast("lead", content, manager.member_names())
    
    def reset_teams(self):
        """重置团队管理器"""
        reset_teams()
