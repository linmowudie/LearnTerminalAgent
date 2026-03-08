"""
LearnTerminalAgent SubAgent 模块 - s04
实现子代理功能，支持任务委派和上下文隔离
"""

import os
from pathlib import Path
from typing import Optional, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from ..core.config import get_config, AgentConfig
from ..tools.tools import get_all_tools
from ..infrastructure.workspace import get_workspace


# 子代理提示词模板路径
DEFAULT_SUBAGENT_PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "prompts" / "subagent_prompt_zh.md"


def load_subagent_prompt(
    prompt_path: Optional[Path] = None,
    workspace_root: str = "",
    task_description: str = "",
) -> str:
    """
    加载子代理提示词模板
    
    Args:
        prompt_path: 提示词文件路径，None 则使用默认路径
        workspace_root: 工作空间根目录
        task_description: 任务描述
        
    Returns:
        渲染后的提示词字符串
    """
    path = prompt_path if prompt_path else DEFAULT_SUBAGENT_PROMPT_PATH
    
    if not path.exists():
        # 如果提示词文件不存在，返回简化的默认提示词
        return (
            f"你是由主代理委派的专属子代理，工作目录：{workspace_root}\n"
            f"高效完成指定任务，并返回清晰的摘要。\n"
            f"当前任务：{task_description}"
        )
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 替换占位符
        rendered = template.replace("{workspace_root}", workspace_root)
        rendered = rendered.replace("{task_description}", task_description)
        
        return rendered
    except Exception as e:
        # 加载失败时返回简化版本
        return (
            f"你是由主代理委派的专属子代理，工作目录：{workspace_root}\n"
            f"高效完成指定任务，并返回清晰的摘要。\n"
            f"当前任务：{task_description}"
        )


class SubAgent:
    """
    子代理类
    
    子代理在独立的上下文中工作，共享文件系统但不共享消息历史。
    完成任务后只返回摘要给父代理。
    """
    
    def __init__(
        self,
        parent_config: Optional[AgentConfig] = None,
        system_prompt: Optional[str] = None,
        prompt_path: Optional[Path] = None,
    ):
        """
        初始化子代理
        
        Args:
            parent_config: 父代理配置
            system_prompt: 系统提示词（优先级高于文件加载）
            prompt_path: 提示词文件路径（可选，默认使用 prompts/subagent_prompt_zh.md）
        """
        # 继承主代理的工作空间（关键！）
        self.workspace = get_workspace()
        
        # 使用父代理的配置或默认配置
        self.config = parent_config or get_config()
        
        # 初始化 LLM
        self.llm = ChatOpenAI(
            model=self.config.model_name,
            base_url=self.config.base_url,
            api_key=self.config.api_key,
            max_tokens=self.config.max_tokens,
        )
        
        # 获取工具并绑定
        self.tools = get_all_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # 系统提示 - 优先级：自定义 > 文件加载 > 默认
        if system_prompt:
            self.system_prompt = system_prompt
        else:
            # 从文件加载提示词
            self.system_prompt = load_subagent_prompt(
                prompt_path=prompt_path,
                workspace_root=self.workspace.root,
                task_description="等待分配任务..."
            )
        
        # 独立的消息历史（与父代理隔离）
        self.messages: List = [
            SystemMessage(content=self.system_prompt)
        ]
        
        # 迭代计数器
        self.iteration_count = 0
    
    def run(self, task: str, verbose: bool = False) -> str:
        """
        运行子代理完成任务
        
        Args:
            task: 任务描述
            verbose: 是否打印详细日志
            
        Returns:
            任务完成的摘要
        """
        # 添加任务到消息历史
        self.messages.append(HumanMessage(content=task))
        
        if verbose:
            print(f"\n[SubAgent Starting Task]")
            print(f"Task: {task[:100]}...")
        
        # 循环调用 LLM 直到不需要使用工具
        while True:
            self.iteration_count += 1
            
            # 检查最大迭代次数
            if self.iteration_count > self.config.max_iterations:
                return (
                    f"Error: SubAgent reached maximum iterations "
                    f"({self.config.max_iterations})"
                )
            
            # 调用 LLM
            response = self.llm_with_tools.invoke(self.messages)
            
            # 添加响应到历史
            self.messages.append(response)
            
            # 检查是否有工具调用
            if not response.tool_calls:
                # 没有工具调用，任务完成，返回摘要
                summary = response.content or "Task completed."
                if verbose:
                    print(f"\n[SubAgent Task Complete]")
                    print(f"Summary: {summary}")
                return summary
            
            # 执行工具调用
            if verbose:
                print(f"\n[SubAgent Iteration {self.iteration_count}]")
            
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                if verbose:
                    print(f"  Using {tool_name}: {tool_args}")
                
                # 执行工具
                result = self._execute_tool(tool_name, tool_args)
                
                if verbose and result:
                    preview = result[:100]
                    if len(result) > 100:
                        preview += "..."
                    print(f"  Result: {preview}")
                
                # 添加结果到消息历史
                from langchain_core.messages import ToolMessage
                self.messages.append(
                    ToolMessage(
                        content=result,
                        tool_call_id=tool_call.get("id", ""),
                        name=tool_name,
                    )
                )
        
        return ""
    
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
        """重置子代理状态"""
        self.messages = [SystemMessage(content=self.system_prompt)]
        self.iteration_count = 0
    
    def get_message_count(self) -> int:
        """获取消息数量"""
        return len(self.messages)


def spawn_subagent(
    task: str,
    config: Optional[AgentConfig] = None,
    system_prompt: Optional[str] = None,
    prompt_path: Optional[Path] = None,
    verbose: bool = True,
) -> str:
    """
    创建并运行子代理
    
    Args:
        task: 任务描述
        config: 配置（可选）
        system_prompt: 系统提示（可选，优先级高于文件加载）
        prompt_path: 提示词文件路径（可选，默认使用 prompts/subagent_prompt_zh.md）
        verbose: 是否详细输出
        
    Returns:
        子代理的任务摘要
    """
    agent = SubAgent(
        parent_config=config,
        system_prompt=system_prompt,
        prompt_path=prompt_path,
    )
    return agent.run(task, verbose=verbose)
