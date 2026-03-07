"""
LearnTerminalAgent SubAgent 模块 - s04
实现子代理功能，支持任务委派和上下文隔离
"""

import os
from typing import Optional, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from .config import get_config, AgentConfig
from .tools import get_all_tools
from .workspace import get_workspace


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
    ):
        """
        初始化子代理
        
        Args:
            parent_config: 父代理配置
            system_prompt: 系统提示词
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
        
        # 系统提示 - 包含工作空间信息
        if system_prompt:
            self.system_prompt = system_prompt
        else:
            self.system_prompt = (
                f"You are a coding subagent working on a task.\n"
                f"Your workspace is: {self.workspace.root}\n"
                f"All file operations must be within this workspace.\n"
                f"Complete the given task efficiently. "
                f"When done, provide a concise summary of what you accomplished."
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
    verbose: bool = True,
) -> str:
    """
    创建并运行子代理
    
    Args:
        task: 任务描述
        config: 配置（可选）
        system_prompt: 系统提示（可选）
        verbose: 是否详细输出
        
    Returns:
        子代理的任务摘要
    """
    agent = SubAgent(parent_config=config, system_prompt=system_prompt)
    return agent.run(task, verbose=verbose)
