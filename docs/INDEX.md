# LearnAgent 文档索引

完整的文档导航和索引。

## 📖 Learn 系列 - 模块原理及实现

### 基础模块 (s01-s06)

#### [s01 - The Agent Loop](learn/s01-the-agent-loop.md)
**原理**: Agent 核心循环机制  
**实现**: 
- `while` 循环 + 工具调用驱动
- 消息历史管理
- 迭代次数控制
- 三层上下文压缩策略

**相关文件**: 
- [`src/learn_agent/agent.py`](../src/learn_agent/agent.py#L97-L189) - AgentLoop.run()
- [`src/learn_agent/context.py`](../src/learn_agent/context.py) - 上下文压缩

---

#### [s02 - Tool Use](learn/s02-tool-use.md)
**原理**: 基于 LangChain 的工具绑定和执行机制  
**实现**:
- `@tool` 装饰器定义
- LLM 工具绑定 (`llm.bind_tools()`)
- 工具执行器 (`_execute_tool()`)
- 安全检查机制

**相关文件**:
- [`src/learn_agent/tools.py`](../src/learn_agent/tools.py) - 基础工具定义
- [`src/learn_agent/agent.py`](../src/learn_agent/agent.py#L208-L233) - 工具执行逻辑

---

#### [s03 - TodoWrite](learn/s03-todo-write.md)
**原理**: 内存级任务管理，支持状态追踪  
**实现**:
- `TodoManager` 管理类
- `TodoItem` 数据结构
- 状态验证（pending/in_progress/completed）
- 唯一 in_progress 约束

**相关文件**:
- [`src/learn_agent/todo.py`](../src/learn_agent/todo.py) - 完整实现
- [`src/learn_agent/agent.py`](../src/learn_agent/agent.py#L254-L262) - Agent 集成

---

#### [s04 - SubAgent](learn/s04-subagent.md)
**原理**: 任务委派与上下文隔离  
**实现**:
- `SubAgent` 类独立运行
- 独立消息历史
- 任务完成后返回摘要
- 共享文件系统但不共享上下文

**相关文件**:
- [`src/learn_agent/subagent.py`](../src/learn_agent/subagent.py) - 完整实现
- [`src/learn_agent/agent.py`](../src/learn_agent/agent.py#L265-L287) - spawn_subagent()

---

#### [s05 - Skill Loading](learn/s05-skill-loading.md)
**原理**: 两层技能注入机制  
**实现**:
- Layer 1: 技能名称 + 描述（系统提示）
- Layer 2: 完整内容（按需加载到 tool_result）
- YAML frontmatter 解析
- SKILL.md 文件格式

**相关文件**:
- [`src/learn_agent/skills.py`](../src/learn_agent/skills.py) - SkillLoader 类
- [`skills/`](../skills/) - 技能文件目录

---

#### [s06 - Context Compaction](learn/s06-context-compaction.md)
**原理**: 三层压缩策略管理 token 使用  
**实现**:
- **Layer 1 (micro_compact)**: 每次迭代后静默替换旧工具结果为占位符
- **Layer 2 (auto_compact)**: 超过阈值时保存记录并总结
- **Layer 3 (compact tool)**: 手动触发立即压缩
- 对话记录持久化到 `.transcripts/`

**相关文件**:
- [`src/learn_agent/context.py`](../src/learn_agent/context.py) - ContextCompactor 类
- [`src/learn_agent/agent.py`](../src/learn_agent/agent.py#L177-L186) - 集成到循环

---

### 高级模块 (s07-s12)

#### [s07 - Task System](learn/s07-task-system.md)
**原理**: 基于 JSON 文件的持久化任务管理系统  
**实现**:
- `.tasks/` 目录存储 task_*.json 文件
- `TaskManager` CRUD 操作
- 依赖关系图（blockedBy/blocks）
- 完成任务自动清除依赖

**相关文件**:
- [`src/learn_agent/task_system.py`](../src/learn_agent/task_system.py) - 完整实现
- [`src/learn_agent/agent.py`](../src/learn_agent/agent.py#L342-L372) - Agent 集成

---

#### [s08 - Background Tasks](learn/s08-background-tasks.md)
**原理**: 后台线程执行 + 通知队列注入  
**实现**:
- `BackgroundManager` 管理类
- 线程池执行命令
- `_notification_queue` 传递结果
- `drain_notifications()` 在 LLM 调用前注入

**相关文件**:
- [`src/learn_agent/background.py`](../src/learn_agent/background.py) - 完整实现
- [`src/learn_agent/agent.py`](../src/learn_agent/agent.py#L191-L206) - 通知处理

---

#### [s09 - Agent Teams](learn/s09-agent-teams.md)
**原理**: 持久化命名代理 + 异步通信  
**实现**:
- `TeammateManager` 管理队友生命周期
- `MessageBus` 基于 JSONL 收件箱
- 每个队友独立线程运行
- 有效消息类型控制

**相关文件**:
- [`src/learn_agent/teams.py`](../src/learn_agent/teams.py) - 完整实现
- [`src/learn_agent/agent.py`](../src/learn_agent/agent.py#L391-L421) - Agent 集成

---

#### [s10 - Team Protocols](learn/s10-team-protocols.md)
**原理**: 团队通信协议规范  
**实现**:
- 消息类型：message/broadcast/shutdown_request/plan_approval_response
- send_message / read_inbox / broadcast API
- 收件箱轮询机制
- 消息时间戳排序

**相关文件**:
- [`src/learn_agent/teams.py`](../src/learn_agent/teams.py#L38-L130) - MessageBus 实现

---

#### [s11 - Autonomous Agents](learn/s11-autonomous-agents.md)
**原理**: 自主代理 Idle 周期 + 任务认领  
**实现**:
- `scan_unclaimed_tasks()` 扫描未分配任务
- `claim_task()` 认领任务（带锁保护）
- `make_identity_block()` 身份重新注入
- Idle 状态轮询

**相关文件**:
- [`src/learn_agent/autonomous_agents.py`](../src/learn_agent/autonomous_agents.py) - 完整实现

---

#### [s12 - Worktree Isolation](learn/s12-worktree-isolation.md)
**原理**: Git worktree + 任务隔离  
**实现**:
- `WorktreeManager` 管理 worktree 生命周期
- 任务与 worktree 绑定
- `EventBus` 记录生命周期事件
- worktree 内运行命令隔离

**相关文件**:
- [`src/learn_agent/worktree_isolation.py`](../src/learn_agent/worktree_isolation.py) - 完整实现
- [`src/learn_agent/task_system.py`](../src/learn_agent/task_system.py#L100-L110) - 任务 owner 字段

---

## 🛠️ Guides 系列 - 用途及用法

### 配置与环境

#### [配置指南](guides/config-guide.md)
**用途**: 管理所有配置项  
**用法**:
```python
from learn_agent.config import get_config, AgentConfig

# 从 JSON 加载（默认）
config = get_config(from_json=True)

# 从环境变量加载
config = AgentConfig.from_env()

# 保存到 JSON
config.save_to_json("path/to/config.json")
```

**配置文件位置**: `config/config.json`  
**环境变量**: QWEN_API_KEY, ANTHROPIC_BASE_URL, MODEL_ID 等

---

#### [快速入门](guides/quickstart.md)
**用途**: 快速开始使用 LearnAgent  
**用法**:
```bash
# 安装依赖
pip install -e .

# 设置 API Key
export QWEN_API_KEY="sk-xxxxx"

# 运行
python -m learn_agent.main
```

---

### 工具使用

#### [内置工具](guides/tools.md)
**基础工具**:
- `bash(command)` - 执行 shell 命令
- `read_file(path, limit)` - 读取文件
- `write_file(path, content)` - 写入文件
- `list_directory(path)` - 列出目录

**使用方法**:
```python
# 在 Agent 中自然语言调用
agent.run("创建一个 test.txt 文件，写入 Hello World")
```

---

#### [任务管理工具](guides/task-management.md)
**Todo 工具** (s03):
- `todo_add(text)` - 添加任务
- `todo_update(id, status, text)` - 更新任务
- `todo_remove(id)` - 删除任务
- `todo_list()` - 列出任务
- `todo_progress()` - 显示进度

**Task System 工具** (s07):
- `task_create(subject, description)` - 创建任务
- `task_get(task_id)` - 获取详情
- `task_update(task_id, status, addBlockedBy, addBlocks)` - 更新
- `task_list()` - 列出所有

**使用示例**:
```python
# Todo（内存级）
agent.run("添加任务：完成项目文档")
agent.todo_update("1", "in_progress")

# Task System（持久化）
agent.task_create("重构代码", "优化性能")
agent.task_update(1, "in_progress", addBlocks=[2, 3])
```

---

#### [团队协作工具](guides/team-collaboration.md)
**工具**:
- `spawn_teammate(name, role, prompt)` - 创建队友
- `list_teammates()` - 列出队友
- `send_message(to, content, msg_type)` - 发送消息
- `read_inbox()` - 读取收件箱
- `broadcast(content)` - 广播消息

**使用示例**:
```python
# 创建队友
agent.spawn_teammate("reviewer", "代码审查员", "Review all code changes")

# 发送消息
agent.send_message("reviewer", "请审查 src/main.py")

# 读取回复
inbox = agent.read_inbox()
```

---

#### [技能开发](guides/skill-development.md)
**用途**: 自定义技能和知识加载  
**格式**:
```markdown
---
name: skill-name
description: 简短描述
tags: tag1,tag2
---

# 技能完整内容

这里是详细的教学内容...
```

**使用方法**:
```python
# 列出技能
skills = agent.list_skills()

# 加载技能
content = agent.load_skill("pdf-processing")

# 重新加载
agent.reload_skills()
```

**存放位置**: `skills/*/SKILL.md`

---

## 📊 统计信息

| 模块 | 代码行数 | 工具数量 | 复杂度 |
|------|---------|---------|--------|
| s01 Agent | 422 | 0 | ⭐⭐⭐ |
| s02 Tools | 193 | 4 | ⭐⭐ |
| s03 Todo | 233 | 5 | ⭐⭐ |
| s04 SubAgent | 203 | 0 | ⭐⭐ |
| s05 Skills | 266 | 4 | ⭐⭐⭐ |
| s06 Context | 319 | 0 | ⭐⭐⭐⭐ |
| s07 Task | 264 | 4 | ⭐⭐⭐ |
| s08 Background | 198 | 2 | ⭐⭐⭐ |
| s09 Teams | 584 | 5 | ⭐⭐⭐⭐⭐ |
| s10 Protocols | (包含在 teams.py) | - | ⭐⭐⭐ |
| s11 Autonomous | 115 | 2 | ⭐⭐⭐ |
| s12 Worktree | 431 | 7 | ⭐⭐⭐⭐⭐ |

---

## 🔗 交叉引用

### 配置相关
- [`config.py`](../src/learn_agent/config.py) → 所有模块使用
- [`project_config.py`](../src/learn_agent/project_config.py) → 路径管理

### 工具集成
- [`tools.py`](../src/learn_agent/tools.py) → 基础工具
- 各模块的 `get_*_tools()` → 工具注册

### 数据持久化
- `.tasks/` → 任务系统 (s07)
- `.team/` → 团队配置 (s09)
- `.transcripts/` → 对话记录 (s06)
- `.worktrees/` → Worktree 索引 (s12)

---

**最后更新**: 2026-03-05  
**维护者**: LearnAgent Team
