# LearnTerminalAgent 核心包

LearnTerminalAgent 的主要 Python 包，实现了智能 Agent 的所有核心功能。

## 📦 包结构

### 核心组件

| 模块 | 描述 |
|------|------|
| [`agent.py`](agent.py) | Agent 主循环，负责任务处理、工具调用和决策制定 |
| [`tools.py`](tools.py) | 提供 bash 命令执行、文件操作、目录管理等工具 |
| [`main.py`](main.py) | CLI 命令行界面入口，处理用户交互 |

### 任务与上下文管理

| 模块 | 描述 |
|------|------|
| [`todo.py`](todo.py) | TodoWrite 系统，管理和跟踪任务进度 |
| [`context.py`](context.py) | 上下文 token 管理，实现自动压缩机制 |
| [`task_system.py`](task_system.py) | 复杂任务的分解、规划和执行系统 |

### 代理与协作

| 模块 | 描述 |
|------|------|
| [`subagent.py`](subagent.py) | SubAgent 子代理委派机制 |
| [`teams.py`](teams.py) | Agent Teams 多代理团队协作 |
| [`team_protocols.py`](team_protocols.py) | Agent 间通信协议和消息传递 |
| [`autonomous_agents.py`](autonomous_agents.py) | 自主代理行为和决策逻辑 |

### 技能与扩展

| 模块 | 描述 |
|------|------|
| [`skills.py`](skills.py) | Skills 系统，加载和管理外部技能模块 |
| [`background.py`](background.py) | 后台异步任务处理 |
| [`worktree_isolation.py`](worktree_isolation.py) | Git Worktree 隔离，支持并行开发 |

### 配置与管理

| 模块 | 描述 |
|------|------|
| [`config.py`](config.py) | API 密钥、模型配置和运行时设置 |
| [`project_config.py`](project_config.py) | 项目级配置管理 |
| [`run.py`](run.py) | 运行辅助脚本 |
| [`__init__.py`](__init__.py) | 包初始化和版本信息 |

## 🎯 主要功能

### 1. Agent 主循环
- 接收用户输入
- 分析任务需求
- 调用相应工具
- 返回执行结果

### 2. 工具使用
- **bash** - 执行 shell 命令
- **read_file** - 读取文件内容
- **write_file** - 写入文件内容
- **list_directory** - 列出目录内容
- 更多工具可扩展添加

### 3. 任务管理
- 自动分解复杂任务
- 跟踪任务进度
- 更新任务状态

### 4. 上下文优化
- 实时监控 token 使用
- 自动压缩长对话
- 保持关键信息

### 5. 多代理协作
- 创建 Agent 团队
- 定义角色和职责
- 实现团队协议

## 🔧 使用示例

### 基本使用

```python
from learn_agent.agent import AgentLoop

# 创建 Agent 实例
agent = AgentLoop()

# 运行任务
response = agent.run("创建一个 hello.txt 文件")
print(response)
```

### 使用任务系统

```python
from learn_agent.todo import TodoManager

# 创建任务管理器
todos = TodoManager()

# 添加任务
todos.add_task("创建项目结构")
todos.update_task(1, status="completed")
```

### 配置管理

```python
from learn_agent.config import get_config

# 获取配置
config = get_config()
print(f"当前模型：{config.model_name}")
```

## 📚 学习资源

- [s01 - Agent 循环](../../docs/learn/s01-the-agent-loop.md)
- [s02 - 工具使用](../../docs/learn/s02-tool-use.md)
- [s03 - TodoWrite](../../docs/learn/s03-todo-write.md)
- [s04 - SubAgent](../../docs/learn/s04-subagent.md)
- [完整教程](../../docs/learn/)

## 🧪 测试

```bash
# 运行所有测试
pytest tests/

# 运行特定模块测试
pytest tests/test_agent.py
```

## 🤝 贡献

查看源代码或提交改进：
https://github.com/linmowudie/LearnTerminalAgent
