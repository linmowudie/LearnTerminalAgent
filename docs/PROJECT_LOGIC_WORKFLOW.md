# LearnTerminalAgent 项目逻辑工作流程

## 1. 项目概述

### 1.1 项目定位和技术栈

**LearnTerminalAgent** 是一个基于 LangChain 实现的终端智能 Agent 框架，专为编程辅助任务设计。它通过自然语言交互，帮助用户完成代码编写、文件操作、命令执行等开发任务。

**技术栈**：
- **编程语言**: Python 3.8+
- **核心框架**: LangChain
- **LLM 集成**: langchain-openai, Anthropic
- **环境变量**: python-dotenv
- **代码工具**: Black (格式化), Ruff (linting), pytest (测试)
- **打包工具**: setuptools, wheel

### 1.2 核心特性

| 特性编号 | 特性名称 | 说明 |
|---------|---------|------|
| s03 | TodoWrite | 内存级任务管理，支持任务添加、更新、删除和进度追踪 |
| s04 | SubAgent | 子代理委派机制，实现上下文隔离的任务分解 |
| s05 | SkillLoader | 两层技能注入系统，支持外部知识加载 |
| s06 | ContextCompactor | 三层上下文压缩策略，防止 token 超限 |
| s07 | TaskSystem | 持久化任务管理系统，支持跨会话任务追踪 |
| s08 | BackgroundTasks | 后台任务执行器，非阻塞命令运行 |
| s09 | AgentTeams | 多代理协作系统，基于消息总线的异步通信 |
| s12 | WorktreeIsolation | Git Worktree 隔离机制，支持并行开发分支 |

### 1.3 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      用户交互层                              │
│                    run_agent.py / main()                     │
│                  交互式 CLI + 命令处理                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      核心层 (Core)                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   AgentLoop     │  │   AgentConfig   │  │   Workspace  │ │
│  │  主代理循环      │  │   配置管理       │  │   工作空间    │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      工具层 (Tools)                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 基础工具：bash, read_file, write_file, edit_file,    │    │
│  │ list_directory, format_html_output                   │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │ TodoWrite    │ │ TaskSystem   │ │ Skills       │        │
│  │ (s03)        │ │ (s07)        │ │ (s05)        │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      服务层 (Services)                       │
│  ┌─────────────────────────┐  ┌─────────────────────────┐  │
│  │ ContextCompactor (s06)  │  │ BackgroundManager (s08) │  │
│  │ 三层压缩策略             │  │ 后台任务执行             │  │
│  └─────────────────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      代理层 (Agents)                         │
│  ┌─────────────────────────┐  ┌─────────────────────────┐  │
│  │ SubAgent (s04)          │  │ TeammateManager (s09)   │  │
│  │ 子代理委派               │  │ 团队协作和消息总线        │  │
│  └─────────────────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   基础设施层 (Infrastructure)                 │
│  ┌─────────────────────────┐  ┌─────────────────────────┐  │
│  │ WorkspaceManager         │  │ Logger                  │  │
│  │ 路径验证和沙箱           │  │ 日志记录                 │  │
│  └─────────────────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 系统启动流程

### 2.1 启动入口和初始化序列

**启动方式**：

```bash
# 方式 1: 快速启动脚本
python run_agent.py [工作空间路径]

# 方式 2: CLI 命令（安装后）
learn-agent

# 方式 3: Windows 批处理
agent.bat
```

**初始化序列图**：

```
run_agent.py
    │
    ├─ ① 添加 src 目录到 Python 路径
    │
    ├─ ② 导入 learn_agent.core.main
    │
    └─ ③ 调用 main()
            │
            ├─ ④ 设置 UTF-8 编码（Windows）
            │
            ├─ ⑤ 解析命令行参数获取工作空间路径
            │
            ├─ ⑥ 初始化工作空间单例
            │     get_workspace().initialize(workspace_root)
            │
            ├─ ⑦ 加载配置单例
            │     get_config()
            │
            ├─ ⑧ 创建 AgentLoop 实例
            │     AgentLoop(workspace, config)
            │
            ├─ ⑨ 打印欢迎横幅和配置信息
            │
            └─ ⑩ 进入主循环
                  while True:
                      query = input("LearnTerminalAgent >> ")
                      agent.run(query)
```

### 2.2 配置加载机制

**配置文件**: `config/config.json`

**加载流程**：

```python
get_config()
    │
    ├─ 检查全局 _config 单例是否存在
    │
    ├─ 如果不存在 → 创建 Config 实例
    │       │
    │       ├─ 从环境变量读取配置
    │       │   os.getenv('AGENT_API_KEY', ...)
    │       │
    │       ├─ 加载 JSON 配置文件
    │       │   json.load(open('config/config.json'))
    │       │
    │       └─ 合并环境变量和文件配置
    │
    └─ 返回配置单例
```

**配置项说明**：

| 配置组 | 字段 | 默认值 | 说明 |
|-------|------|--------|------|
| agent | api_key | "" | LLM API 密钥 |
| agent | base_url | 阿里云百炼端点 | API 基础 URL |
| agent | model_name | qwen3.5-plus | 使用的模型 |
| agent | max_tokens | 8000 | 最大生成 token 数 |
| agent | timeout | 120 | 请求超时时间（秒） |
| agent | max_iterations | 50 | 单次任务最大迭代次数 |
| security | dangerous_patterns | [rm -rf /, sudo, ...] | 危险命令过滤模式 |
| context | threshold | 50000 | 上下文压缩阈值（字符数） |
| context | keep_recent | 3 | 保留的最近工具结果数 |
| context | auto_compact_enabled | true | 启用自动压缩 |
| tasks | max_items | 20 | 任务列表最大条目数 |
| background | timeout | 300 | 后台任务超时（秒） |
| team | poll_interval | 5 | 团队轮询间隔（秒） |
| team | idle_timeout | 60 | 空闲超时（秒） |
| worktree | enabled | true | 启用 Git worktree |
| worktree | base_ref | HEAD | Git 基础引用 |

### 2.3 工作空间初始化

**工作空间管理**: `src/learn_agent/infrastructure/workspace.py`

**初始化流程**：

```python
get_workspace().initialize(workspace_root=None)
    │
    ├─ 如果 workspace_root 为 None → 使用当前目录
    │
    ├─ 创建 WorkspaceManager 实例
    │
    ├─ 验证路径存在性和可访问性
    │
    ├─ 存储根路径到 self.root
    │
    └─ 返回单例实例
```

**核心方法**：

```python
resolve_path(path: str) -> Path
    │
    ├─ 如果是绝对路径 → 直接使用
    │
    ├─ 如果是相对路径 → 拼接 root + path
    │
    ├─ 安全检查：验证路径在 root 范围内
    │       realpath 规范化 → 检查是否以 root 开头
    │
    ├─ 如果越界 → 抛出 ValueError
    │
    └─ 返回 Path 对象
```

### 2.4 AgentLoop 创建过程

**初始化代码位置**: `src/learn_agent/core/agent.py:55-109`

```python
AgentLoop.__init__(workspace, config)
    │
    ├─ ① 存储 workspace
    │
    ├─ ② 加载或创建 config
    │
    ├─ ③ 初始化 LLM
    │     ChatOpenAI(
    │         model=config.model_name,
    │         api_key=config.api_key,
    │         base_url=config.base_url,
    │         max_tokens=config.max_tokens,
    │         timeout=config.timeout
    │     )
    │
    ├─ ④ 获取所有工具并绑定
    │     self.tools = get_all_tools()
    │     self.llm_with_tools = llm.bind_tools(self.tools)
    │
    ├─ ⑤ 加载系统提示词
    │     _load_system_prompt() → 从 prompts/agent_prompt_zh.md 读取
    │
    ├─ ⑥ 初始化消息历史
    │     self.messages = [SystemMessage(content=system_prompt)]
    │
    ├─ ⑦ 重置计数器
    │     self.iteration_count = 0
    │     self._empty_retry_count = 0
    │
    └─ ⑧ 获取上下文压缩器单例
          self.compactor = get_compactor()
          self.compactor.enable_auto_compact(config.context.auto_compact_enabled)
```

---

## 3. 核心运行循环

### 3.1 主循环架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     main() 主循环                            │
│                                                              │
│  while True:                                                 │
│      │                                                       │
│      ├─ 获取用户输入                                         │
│      │   query = input("LearnTerminalAgent >> ")            │
│      │                                                       │
│      ├─ 命令检测（以'/'开头）                                │
│      │   /help, /reset, /config, /quit, ...                 │
│      │                                                       │
│      ├─ 空输入检查                                           │
│      │   if not query: continue                             │
│      │                                                       │
│      ├─ 运行 Agent                                           │
│      │   response = agent.run(query, verbose=True, stream=True) │
│      │                                                       │
│      ├─ 格式化输出                                           │
│      │   print(_format_response_card(response))             │
│      │                                                       │
│      └─ 异常处理                                             │
│          KeyboardInterrupt, EOFError, Exception             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 用户输入处理流程

**行动关键词检测** (`agent.py:132-156`)：

```python
action_keywords = {
    '查看': ['list_directory', 'read_file'],
    '创建': ['write_file'],
    '编辑': ['edit_file'],
    '运行': ['bash'],
    '删除': ['bash(rm/del)'],
    '搜索': ['bash(grep/find)'],
}

检测流程：
    │
    ├─ 遍历 action_keywords 字典
    │
    ├─ 如果 query 包含某个关键词
    │   │
    │   └─ 构建强化工具提醒
    │       "注意：用户要求'{query}'，请务必调用相关工具！"
    │
    └─ 将提醒附加到 query 末尾
```

**强化提醒规则**：
- 前 10 条消息：始终添加提醒
- 检测到行动关键词：添加对应工具提醒
- 其他情况：不添加

### 3.3 LLM 调用和响应解析

**流式调用流程** (`_stream_invoke()`, `agent.py:485-567`)：

```
_stream_invoke(query)
    │
    ├─ ① 启动加载动画线程
    │     显示旋转 Braille 字符：⠋→⠙→⠹→⠸→⠼→⠴→⠦→⠧→⠇→⠏
    │
    ├─ ② 调用 LLM 流式接口
    │     for chunk in llm.stream(messages):
    │         - 第一个 chunk 到达 → 停止动画
    │         - 累积内容到 response_content
    │         - 收集 tool_calls 片段
    │
    ├─ ③ 检查是否有工具调用
    │     │
    │     ├─ 有工具调用 → 重新调用普通 invoke
    │     │       (因为流式无法可靠获取 tool_calls)
    │     │
    │     └─ 无工具调用 → 使用流式结果
    │
    └─ ④ 返回 AIMessage
```

**普通调用流程**：

```python
llm_with_tools.invoke(messages)
    │
    ├─ 发送完整消息历史给 LLM
    │
    ├─ 接收 AIMessage 响应
    │     content: str
    │     tool_calls: List[ToolCall]
    │
    └─ 返回 AIMessage 对象
```

### 3.4 工具执行机制

**工具执行流程** (`_execute_tool()`, `agent.py:365-380`)：

```
_execute_tool(tool_name, tool_args)
    │
    ├─ ① 查找工具
    │     tool = next(t for t in self.tools if t.name == tool_name)
    │
    ├─ ② 调用工具
    │     result = tool.invoke(tool_args)
    │
    ├─ ③ 异常处理
    │     except Exception as e:
    │         return f"Error executing {tool_name}: {type(e).__name__}: {str(e)}"
    │
    └─ ④ 返回结果
```

**工具注册机制**：

```python
get_all_tools()
    │
    ├─ 基础工具
    │   bash, read_file, write_file, edit_file, list_directory, format_html_output
    │
    ├─ Todo 工具 (s03)
    │   *get_todo_tools()
    │
    ├─ Task System 工具 (s07)
    │   *get_task_tools()
    │
    ├─ Background 工具 (s08)
    │   *get_background_tools()
    │
    ├─ Team 工具 (s09)
    │   *get_team_tools()
    │
    └─ Skill 工具 (s05)
        *get_skill_tools()
```

### 3.5 上下文管理策略

**三层压缩架构**：

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: micro_compact() - 微压缩（每次迭代自动执行）         │
│                                                              │
│ 功能：压缩旧的工具结果                                        │
│ 策略：保留最近 3 个工具结果，旧的替换为占位符                   │
│ 触发：每次迭代完成后                                          │
│ 示例："[Previous: used bash]"                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: auto_compact() - 自动压缩（超过阈值时触发）          │
│                                                              │
│ 功能：使用 LLM 总结对话历史                                    │
│ 触发：token 数 > 50000（可配置）                              │
│ 策略：                                                       │
│   ① 保存完整记录到 .transcripts/transcript_{timestamp}.json │
│   ② 提取最近 20 条消息发送给 LLM 总结                          │
│   ③ 替换所有消息为：[摘要] + [Previous conversation...]    │
│   ④ 记录压缩历史                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: compact() - 手动压缩（用户主动触发）                 │
│                                                              │
│ 功能：与 auto_compact 相同，但不检查阈值                      │
│ 触发：用户输入 /compact 命令                                  │
│ 用途：主动清理上下文，节省 token                             │
└─────────────────────────────────────────────────────────────┘
```

**压缩数据流**：

```
原始消息列表 (100 条)
    │
    ├─ micro_compact()
    │     识别所有 ToolMessage → 保留最近 3 个 → 旧的替换为占位符
    │
    ├─ 估算 token 数
    │     len(str(messages)) // 4
    │
    ├─ 检查是否超过阈值
    │     │
    │     ├─ 未超过 → 返回
    │     │
    │     └─ 超过 → auto_compact()
    │           │
    │           ├─ 保存到 JSON 文件
    │           │
    │           ├─ 调用 LLM 总结
    │           │
    │           └─ 替换为 2 条消息：
    │                 [SystemMessage, HumanMessage(摘要)]
    │
    └─ 返回压缩后消息列表 (2-10 条)
```

---

## 4. 模块详细工作流程

### 4.1 TodoWrite 任务管理（s03）

**核心类**: `TodoManager` (`src/learn_agent/tools/todo.py`)

**数据结构**：

```python
@dataclass
class TodoItem:
    id: str              # 自增 ID（字符串）
    text: str            # 任务描述
    status: str          # pending | in_progress | completed
```

**工作流程**：

```
todo_add(text)
    │
    ├─ _counter += 1
    │
    ├─ 创建 TodoItem(id=str(_counter), text=text, status='pending')
    │
    ├─ items.append(item)
    │
    ├─ _validate()
    │     - 检查总数 <= max_items (20)
    │     - 检查 in_progress 任务 <= 1 个
    │     - 检查 text 非空
    │
    └─ 返回 item

todo_update(item_id, status, text=None)
    │
    ├─ 遍历 items 查找匹配 id
    │
    ├─ 更新 status 和/或 text
    │
    ├─ 如果 status == 'in_progress'
    │     将所有其他任务的 status 改为 'pending'
    │
    ├─ _validate()
    │
    └─ 返回 item

todo_list()
    │
    ├─ render() 渲染
    │     遍历 items → 根据状态选择标记:
    │       - pending → [ ]
    │       - in_progress → [>]
    │       - completed → [x]
    │
    ├─ 添加进度统计
    │     总计：X, 已完成：Y, 进行中：Z, 待处理：W
    │
    └─ 返回格式化字符串
```

**渲染示例**：

```
Todo List:
[1] [>] 实现用户认证功能
[2] [ ] 添加单元测试
[3] [x] 设计数据库模型
[4] [ ] 编写 API 文档

进度：总计：4, 已完成：1, 进行中：1, 待处理：2, 完成率：25.0%
```

### 4.2 SubAgent 子代理委派（s04）

**核心类**: `SubAgent` (`src/learn_agent/agents/subagent.py`)

**设计目标**: 实现任务委派和上下文隔离

**初始化流程**：

```python
SubAgent.__init__(workspace, config, task)
    │
    ├─ 继承 workspace（共享文件系统）
    │
    ├─ 加载 config
    │
    ├─ 初始化 LLM（与父代理相同配置）
    │
    ├─ 绑定工具（与父代理相同工具集）
    │
    ├─ 设置系统提示
    │     包含工作空间路径信息
    │
    └─ 创建独立消息历史
          messages = [SystemMessage(...)]
          （与父代理完全隔离）
```

**执行流程**：

```
spawn_subagent(task)
    │
    ├─ 创建 SubAgent 实例
    │
    ├─ 调用 sub_agent.run(task)
    │     │
    │     ├─ while True 循环:
    │     │     │
    │     │     ├─ 检查最大迭代次数
    │     │     │
    │     │     ├─ LLM 调用
    │     │     │
    │     │     ├─ 添加工具调用结果
    │     │     │
    │     │     ├─ 判断是否有工具调用
    │     │     │     │
    │     │     │     ├─ 无工具调用 → 返回摘要，结束
    │     │     │     │
    │     │     │     └─ 有工具调用 → 执行工具 → 继续循环
    │     │
    │     └─ 返回任务摘要
    │
    └─ 返回摘要给父代理
```

**父子代理关系**：

```
父代理 (AgentLoop)
    │
    ├─ messages: [父代理的完整历史]
    │
    ├─ 调用 spawn_subagent("实现登录功能")
    │     │
    │     └─ 子代理 (SubAgent)
    │           │
    │           ├─ messages: [独立的子任务历史]
    │           │
    │           ├─ 执行：读取文件 → 编写代码 → 运行测试
    │           │
    │           └─ 返回："已完成登录功能实现，包括..."
    │
    └─ 接收摘要，添加到自己的消息历史
```

### 4.3 SkillLoader 技能加载（s05）

**核心类**: `SkillLoader` (`src/learn_agent/tools/skills.py`)

**技能文件格式** (`skills/*/SKILL.md`):

```markdown
---
name: skill-name
description: 技能描述
tags: 可选标签
---
技能正文内容...
完整的说明文档
```

**两层注入机制**：

```
Layer 1: 系统提示中的技能列表
    │
    ├─ 主代理初始化时调用
    │     skills_desc = loader.get_descriptions()
    │
    ├─ 遍历所有技能
    │     提取 name, description, tags
    │
    ├─ 生成格式化列表
    │     "- skill-name: description (tags)"
    │
    └─ 添加到系统提示词
          system_prompt += f"\nAvailable skills:\n{skills_desc}"

Layer 2: 按需加载完整技能
    │
    ├─ AI 决定学习某个技能
    │     load_skill.invoke({"name": "skill-name"})
    │
    ├─ 读取完整 SKILL.md 文件
    │
    └─ 返回：<skill name="skill-name">完整内容</skill>
```

**技能加载流程**：

```python
_load_all()
    │
    ├─ 遍历 skills_dir/**/*.md
    │
    ├─ 查找所有 SKILL.md 文件
    │
    ├─ 对每个文件调用 _parse_frontmatter()
    │     使用正则匹配：^---\n(.*?)\n---\n(.*)
    │     解析 YAML frontmatter → meta 信息
    │     提取正文 → body 内容
    │
    ├─ 存储到 self.skills 字典
    │     {
    │       "skill-name": {
    │         "meta": {"name": "...", "description": "...", "tags": "..."},
    │         "body": "技能正文",
    │         "path": "/absolute/path",
    │         "dir": "/absolute/path/to/skill"
    │       }
    │     }
    │
    └─ 返回加载的技能数量
```

### 4.4 ContextCompactor 上下文压缩（s06）

**核心类**: `ContextCompactor` (`src/learn_agent/services/context.py`)

**micro_compact() 详细流程**：

```python
micro_compact(messages, keep_recent=3)
    │
    ├─ 收集所有 ToolMessage
    │     tool_messages = [(i, msg) for i, msg in enumerate(messages) 
    │                      if isinstance(msg, ToolMessage)]
    │
    ├─ 如果数量 <= keep_recent → 直接返回
    │
    ├─ 保留最近的 keep_recent 个
    │     to_keep = tool_messages[-keep_recent:]
    │
    ├─ 替换旧的为占位符
    │     for index, msg in tool_messages[:-keep_recent]:
    │         messages[index] = HumanMessage(
    │             content=f"[Previous: used {msg.name}]"
    │         )
    │
    └─ 返回压缩后列表
```

**auto_compact() 详细流程**：

```python
auto_compact(messages)
    │
    ├─ 估算 token 数
    │     token_estimate = estimate_tokens(messages)
    │
    ├─ 如果 token_estimate <= threshold → 直接返回
    │
    ├─ 保存完整记录
    │     _save_transcript(messages)
    │     → .transcripts/transcript_{timestamp}.json
    │
    ├─ 调用 LLM 总结
    │     _summarize_with_llm(messages)
    │     │
    │     ├─ 提取最近 20 条消息
    │     │
    │     ├─ 构建总结提示词
    │     │     "请总结以下对话历史，保留关键信息和决策..."
    │     │
    │     └─ 调用 llm.invoke()
    │
    ├─ 替换所有消息
    │     new_messages = [
    │         SystemMessage(original_system_content),
    │         HumanMessage(f"{summary.content}\n\n[Previous conversation compressed...]")
    │     ]
    │
    ├─ 记录压缩历史
    │     self.compaction_history.append({
    │         "type": "auto",
    │         "timestamp": time.time(),
    │         "tokens_saved": token_estimate
    │     })
    │
    └─ 返回压缩后列表
```

### 4.5 TaskSystem 持久化任务（s07）

**核心类**: `TaskManager` (`src/learn_agent/tools/task_system.py`)

**任务存储结构**：

```python
@dataclass
class Task:
    id: str              # UUID
    title: str           # 任务标题
    description: str     # 详细描述
    status: str          # pending | in_progress | completed | cancelled
    created_at: float    # 创建时间戳
    updated_at: float    # 更新时间戳
    completed_at: Optional[float]  # 完成时间戳
```

**持久化机制**：

```
任务创建
    │
    ├─ 生成 UUID
    │
    ├─ 创建 Task 对象
    │
    ├─ 添加到内存列表
    │
    └─ 保存到 JSON 文件
          data/.tasks/{task_id}.json

任务更新
    │
    ├─ 查找内存中的 Task
    │
    ├─ 更新字段
    │
    ├─ 更新 updated_at
    │
    └─ 同步到 JSON 文件

任务列表
    │
    ├─ 扫描 data/.tasks/*.json
    │
    ├─ 加载所有任务
    │
    ├─ 按状态/时间排序
    │
    └─ 返回格式化列表
```

### 4.6 BackgroundTasks 后台任务（s08）

**核心类**: `BackgroundManager` (`src/learn_agent/services/background.py`)

**后台执行流程**：

```python
background_run(command)
    │
    ├─ 创建 subprocess.Popen()
    │     - stdout=PIPE, stderr=PIPE
    │     - 非阻塞模式
    │
    ├─ 生成任务 ID
    │
    ├─ 存储到 self.running_tasks
    │     {
    │       task_id: {
    │         "process": Popen 对象,
    │         "command": command,
    │         "start_time": time.time()
    │       }
    │     }
    │
    └─ 返回任务 ID

后台监控线程
    │
    ├─ 定期轮询 running_tasks
    │
    ├─ 检查进程状态
    │     process.poll()
    │
    ├─ 如果已完成
    │     - 读取输出
    │     - 移动到 completed_tasks
    │     - 通知主代理
    │
    └─ 检查超时
          if time.time() - start_time > timeout:
              process.kill()
```

### 4.7 Teams 团队协作（s09）

**核心组件**:

```
┌─────────────────┐      ┌──────────────────┐
│  MessageBus     │◄────►│ TeammateManager  │
│  (消息总线)      │      │ (队友管理器)      │
│  - send()       │      │ - spawn()        │
│  - read_inbox() │      │ - _teammate_loop │
│  - broadcast()  │      │ - _exec()        │
└─────────────────┘      └──────────────────┘
         │                        │
         └──────────┬─────────────┘
                    │
         ┌──────────▼──────────┐
         │   队友线程池         │
         │  Thread per Agent   │
         └─────────────────────┘
```

**消息总线工作原理**：

```python
MessageBus.send(to, from, msg_type, content)
    │
    ├─ 验证 msg_type 合法性
    │
    ├─ 构建消息对象
    │     {
    │       "type": msg_type,
    │       "from": from,
    │       "content": content,
    │       "timestamp": time.time()
    │     }
    │
    ├─ 追加到收件箱文件
    │     data/.inbox/{to}.jsonl
    │     (JSON Lines 格式，每行一个 JSON)
    │
    └─ 返回成功

MessageBus.read_inbox(name)
    │
    ├─ 读取 name.jsonl 文件
    │
    ├─ 逐行解析 JSON
    │
    ├─ 清空文件内容
    │
    └─ 返回消息列表
```

**队友生命周期**：

```
spawn_teammate(name, role, prompt)
    │
    ├─ 检查是否已存在
    │
    ├─ 更新/创建成员配置
    │     config.json:
    │     {
    │       "team_name": "default",
    │       "members": [
    │         {"name": "reviewer", "role": "Code Reviewer", "status": "idle"}
    │       ]
    │     }
    │
    ├─ 保存配置
    │
    ├─ 启动独立线程
    │     Thread(target=_teammate_loop, args=(name, ...))
    │
    └─ 返回队友信息

_teammate_loop(name)
    │
    ├─ 初始化阶段
    │     - 获取工作空间
    │     - 构建系统提示
    │     - 初始化 LLM 和工具
    │
    ├─ 主循环 (最多 50 次迭代)
    │     │
    │     ├─ 检查收件箱
    │     │     messages = BUS.read_inbox(name)
    │     │
    │     ├─ 添加收件箱消息到消息历史
    │     │
    │     ├─ LLM 调用
    │     │
    │     ├─ 执行工具（受限工具集）
    │     │     - bash (带安全检查)
    │     │     - read_file, write_file, edit_file
    │     │     - send_message, read_inbox
    │     │
    │     └─ 无工具调用 → 退出循环
    │
    └─ 清理阶段
          - 更新状态为 idle
          - 保存配置
```

### 4.8 Worktree 隔离机制（s12）

**核心类**: `WorktreeManager` (`src/learn_agent/protocols/worktree_isolation.py`)

**Git Worktree 工作流程**：

```
创建工作树
    │
    ├─ 验证 Git 仓库存在
    │
    ├─ 检查分支是否已被占用
    │
    ├─ 执行 git worktree add
    │     git worktree add -b feature-branch ../worktrees/feature-branch
    │
    ├─ 创建独立工作空间
    │     worktrees/feature-branch/
    │
    └─ 返回工作树路径

切换工作树
    │
    ├─ 验证工作树存在
    │
    ├─ 在主代理中切换工作空间
    │     workspace.root = worktree_path
    │
    └─ 后续操作在此工作树中进行

清理工作树
    │
    ├─ 执行 git worktree remove
    │
    ├─ 删除本地目录
    │
    └─ 恢复主工作空间
```

---

## 5. 数据流转全景

### 5.1 消息历史结构

**典型消息序列**：

```python
messages = [
    # 索引 0: 系统提示
    SystemMessage(content="你是一个专业的编程助手..."),
    
    # 索引 1: 用户查询
    HumanMessage(content="创建一个 Hello World 的 Python 文件"),
    
    # 索引 2: AI 思考（可能包含工具调用）
    AIMessage(
        content="我将创建一个 Python 文件...",
        tool_calls=[
            {
                "id": "call_abc123",
                "name": "write_file",
                "args": {"path": "hello.py", "content": "print('Hello World')"}
            }
        ]
    ),
    
    # 索引 3: 工具执行结果
    ToolMessage(
        content="Successfully created hello.py",
        name="write_file",
        tool_call_id="call_abc123"
    ),
    
    # 索引 4: 用户后续查询
    HumanMessage(content="运行这个文件"),
    
    # 索引 5: AI 再次调用工具
    AIMessage(
        content="",
        tool_calls=[
            {
                "id": "call_def456",
                "name": "bash",
                "args": {"command": "python hello.py"}
            }
        ]
    ),
    
    # 索引 6: 工具结果
    ToolMessage(
        content="Hello World\n",
        name="bash",
        tool_call_id="call_def456"
    ),
    
    # 索引 7: 最终响应
    AIMessage(content="文件已成功运行，输出：Hello World")
]
```

### 5.2 工具调用数据流

**完整数据流图**：

```
用户输入："创建一个测试文件"
    │
    ▼
HumanMessage 添加到 messages[]
    │
    ▼
AgentLoop.run()
    │
    ├─ 检测关键词"创建" → 添加强化提醒
    │
    ▼
LLM 调用 (invoke/stream)
    │
    ├─ 输入：messages[] (包含系统提示和历史)
    │
    └─ 输出：AIMessage
            - content: "我将创建文件..."
            - tool_calls: [{name: "write_file", args: {...}}]
    │
    ▼
添加 AIMessage 到 messages[]
    │
    ▼
检测 tool_calls
    │
    ├─ 遍历每个 tool_call
    │     │
    │     ├─ 查找工具对象
    │     │     tool = next(t for t in tools if t.name == "write_file")
    │     │
    │     ├─ 执行工具
    │     │     result = tool.invoke(args)
    │     │     │
    │     │     ├─ resolve_path(path) → 验证路径安全
    │     │     ├─ makedirs(parent_dir) → 创建父目录
    │     │     ├─ open(path, 'w').write(content) → 写入文件
    │     │     └─ 返回："Successfully created ..."
    │     │
    │     └─ 添加 ToolMessage 到 messages[]
    │
    ▼
micro_compact() 压缩旧工具结果
    │
    ▼
auto_compact() 检查 token 阈值
    │
    ▼
循环继续或返回响应
    │
    ▼
main() 格式化输出
    │
    └─ ANSI 卡片样式显示
```

### 5.3 跨模块数据传递

**模块间数据流**：

```
┌─────────────────────────────────────────────────────────────┐
│ 主代理 (AgentLoop)                                          │
│                                                              │
│  messages: [System, Human, AI, Tool, ...]                   │
│       │                                                      │
│       │ 调用                                                 │
│       ▼                                                      │
│  ┌─────────────────┐                                        │
│  │ SubAgent.run()  │ ← 独立 messages 副本                    │
│  │                 │   返回：摘要字符串                       │
│  └─────────────────┘                                        │
│       │                                                      │
│       │ 调用                                                 │
│       ▼                                                      │
│  ┌─────────────────┐                                        │
│  │ TodoManager     │ ← 共享 items 列表                        │
│  │                 │   返回：渲染字符串                       │
│  └─────────────────┘                                        │
│       │                                                      │
│       │ 调用                                                 │
│       ▼                                                      │
│  ┌─────────────────┐                                        │
│  │ ContextCompactor│ ← 修改 messages 原地压缩                │
│  │                 │   返回：压缩后列表                       │
│  └─────────────────┘                                        │
│       │                                                      │
│       │ 调用                                                 │
│       ▼                                                      │
│  ┌─────────────────┐                                        │
│  │ MessageBus.send │ → 写入 JSONL 文件                        │
│  │                 │   返回：成功                            │
│  └─────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. 错误处理和安全机制

### 6.1 多层异常捕获

**四层错误处理架构**：

```
┌─────────────────────────────────────────────────────────────┐
│ L4: main() 全局异常捕获                                     │
│                                                              │
│  try:                                                        │
│      agent.run(query)                                        │
│  except KeyboardInterrupt: break  # 优雅退出                 │
│  except EOFError: break           # 输入流结束               │
│  except Exception as e:           # 未知错误                 │
│      print(f"❌ 错误：{e}")                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ L3: AgentLoop.run() 迭代保护                                │
│                                                              │
│  while iteration_count < max_iterations:                     │
│      try:                                                    │
│          llm.invoke()                                        │
│          _execute_tool()                                     │
│      except Exception as e:                                  │
│          return f"Error: {type(e).__name__}: {str(e)}"      │
│                                                              │
│  if iteration_count > max_iterations:                        │
│      return "Error: Reached maximum iterations"              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ L2: _execute_tool() 工具执行保护                            │
│                                                              │
│  try:                                                        │
│      tool = next(t for t in tools if t.name == tool_name)   │
│      result = tool.invoke(args)                              │
│      return result                                           │
│  except StopIteration:                                       │
│      return f"Error: Tool '{tool_name}' not found"          │
│  except Exception as e:                                      │
│      return f"Error executing {tool_name}: {e}"             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ L1: 各工具内部业务逻辑错误处理                              │
│                                                              │
│  @tool                                                       │
│  def read_file(path: str):                                   │
│      try:                                                    │
│          abs_path = workspace.resolve_path(path)             │
│          with open(abs_path) as f: return f.read()           │
│      except FileNotFoundError:                               │
│          return "Error: File not found"                      │
│      except ValueError as e:  # 路径越界                     │
│          return f"Error: {str(e)}"                           │
│      except Exception as e:                                  │
│          return f"Error: {type(e).__name__}: {str(e)}"      │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 危险命令过滤

**bash 工具安全检查** (`tools/tools.py:38-48`)：

```python
@tool
def bash(command: str) -> str:
    config = get_config()
    workspace = get_workspace()
    
    # 安全检查
    for pattern in config.dangerous_patterns:
        if pattern in command:
            return f"Error: Command blocked by security policy: {pattern}"
    
    # 执行命令
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=workspace.root,  # 限制在工作空间内
            capture_output=True,
            text=True,
            timeout=config.timeout  # 超时保护
        )
        return result.stdout + result.stderr
    except TimeoutExpired:
        return f"Error: Command timed out after {config.timeout}s"
    except Exception as e:
        return f"Error: {type(e).__name__}: {str(e)}"
```

**默认危险模式**：

```json
{
  "dangerous_patterns": [
    "rm -rf /",      # 删除根目录
    "sudo",          # 提权命令
    "shutdown",      # 关机命令
    "reboot",        # 重启命令
    "> /dev/"        # 设备文件写入
  ]
}
```

### 6.3 路径安全验证

**Workspace 路径验证** (`infrastructure/workspace.py:35-52`)：

```python
def resolve_path(self, path: str) -> Path:
    """解析路径并进行安全验证"""
    
    # 步骤 1: 转换为绝对路径
    if os.path.isabs(path):
        abs_path = Path(path)
    else:
        abs_path = self.root / path
    
    # 步骤 2: 规范化路径（解析 .., ., 符号链接）
    real_path = abs_path.resolve()
    real_root = self.root.resolve()
    
    # 步骤 3: 验证路径在工作空间范围内
    try:
        real_path.relative_to(real_root)
    except ValueError:
        raise ValueError(
            f"Path '{path}' is outside workspace. "
            f"Workspace root: {self.root}"
        )
    
    return abs_path
```

**验证示例**：

```
合法路径:
  - workspace: /home/user/project
  - 输入：src/main.py
  - 结果：/home/user/project/src/main.py ✓

非法路径:
  - workspace: /home/user/project
  - 输入：../../etc/passwd
  - 规范化：/etc/passwd
  - 验证失败：抛出 ValueError ✗

非法路径 (绝对路径):
  - workspace: /home/user/project
  - 输入：/etc/passwd
  - 验证失败：抛出 ValueError ✗
```

---

## 7. 关键文件索引

### 7.1 核心文件清单

**Top 10 关键文件**：

| 排名 | 文件路径 | 大小 | 重要性 | 职责 |
|-----|---------|------|--------|------|
| 1 | `src/learn_agent/core/agent.py` | 33KB | ⭐⭐⭐⭐⭐ | Agent 循环核心，LLM 调用、工具执行、流式输出 |
| 2 | `src/learn_agent/core/main.py` | 12KB | ⭐⭐⭐⭐⭐ | 主程序入口，交互式 CLI 界面 |
| 3 | `src/learn_agent/tools/tools.py` | 9KB | ⭐⭐⭐⭐⭐ | 基础工具定义：bash, read_file, write_file 等 |
| 4 | `src/learn_agent/core/config.py` | 11KB | ⭐⭐⭐⭐ | 配置管理，环境变量和 JSON 配置文件 |
| 5 | `src/learn_agent/infrastructure/workspace.py` | 5KB | ⭐⭐⭐⭐ | 工作空间沙箱管理，路径验证 |
| 6 | `src/learn_agent/agents/subagent.py` | 7KB | ⭐⭐⭐⭐ | 子代理实现，任务委派 |
| 7 | `src/learn_agent/services/context.py` | 10KB | ⭐⭐⭐⭐ | 上下文压缩，三层策略 |
| 8 | `src/learn_agent/agents/teams.py` | 19KB | ⭐⭐⭐ | 团队协作，消息总线 |
| 9 | `prompts/agent_prompt_zh.md` | 3KB | ⭐⭐⭐ | 中文系统提示词模板 |
| 10 | `src/learn_agent/__init__.py` | 1KB | ⭐⭐⭐ | 模块导出和版本管理 |

### 7.2 配置文件说明

**项目配置** (`pyproject.toml`):

```toml
[project]
name = "learn-terminal-agent"
version = "1.0.0"
dependencies = [
    "langchain>=0.1.0",
    "langchain-openai>=0.0.5",
    "python-dotenv>=1.0.0",
    "anthropic>=0.8.0",
]

[project.scripts]
learn-agent = "learn_agent.main:main"  # CLI 入口点

[tool.setuptools.packages.find]
where = ["src"]  # 源代码目录
```

**运行时配置** (`config/config.json`):

```json
{
  "agent": {
    "api_key": "",  # 留空，从环境变量读取
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model_name": "qwen3.5-plus",
    "max_tokens": 8000,
    "timeout": 120,
    "max_iterations": 50
  },
  "security": {
    "dangerous_patterns": ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
  },
  "context": {
    "threshold": 50000,
    "keep_recent": 3,
    "auto_compact_enabled": true
  }
}
```

**环境变量** (`.env.example`):

```bash
# LLM API 配置
AGENT_API_KEY=your-api-key-here
AGENT_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
AGENT_MODEL_NAME=qwen3.5-plus

# 可选配置
AGENT_MAX_TOKENS=8000
AGENT_TIMEOUT=120
AGENT_MAX_ITERATIONS=50
```

### 7.3 扩展点说明

**自定义工具**：

在 `src/learn_agent/tools/` 目录下创建新文件：

```python
from langchain.tools import tool
from learn_agent.infrastructure.workspace import get_workspace

@tool
def my_custom_tool(arg1: str, arg2: int = 10) -> str:
    """工具描述"""
    workspace = get_workspace()
    # 工具实现
    return f"Result: {arg1}, {arg2}"
```

然后在 `get_all_tools()` 中注册：

```python
def get_all_tools():
    return [
        # ... 现有工具
        my_custom_tool,
    ]
```

**自定义技能**：

在 `skills/` 目录下创建文件夹和 SKILL.md：

```
skills/my-skill/SKILL.md
```

内容格式：

```markdown
---
name: my-skill
description: 我的自定义技能
tags: python, web
---
技能的详细说明和内容...
```

**自定义配置**：

编辑 `config/config.json` 添加新配置项，然后在代码中通过 `get_config()` 访问。

---

## 附录：快速参考

### A. 常用命令

```bash
# 启动 Agent
python run_agent.py [工作空间]

# 安装为 CLI 工具
pip install -e .

# 运行后使用 learn-agent 命令
learn-agent

# 运行测试
pytest

# 代码格式化
black src/ tests/

# Linting
ruff check src/ tests/
```

### B. 特殊命令

```
/help     - 显示帮助信息
/reset    - 重置对话历史
/config   - 显示配置信息
/history  - 显示最近 10 条消息
/todo     - 显示任务进度
/skills   - 列出可用技能
/compact  - 手动压缩上下文
/stats    - 显示上下文统计
/quit     - 退出程序
```

### C. 数据目录结构

```
data/
├── .tasks/          # 持久化任务文件
│   └── {task_id}.json
├── .team/           # 团队配置
│   └── config.json
├── .inbox/          # 消息收件箱（JSONL 格式）
│   ├── lead.jsonl
│   └── reviewer.jsonl
├── .transcripts/    # 压缩前的对话记录
│   └── transcript_{timestamp}.json
└── .worktrees/      # Git worktree 索引
    └── index.json
```

---

*文档版本：1.0*  
*最后更新：2026-03-08*  
*基于 LearnTerminalAgent v2.1.0*
