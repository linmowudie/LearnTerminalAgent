# LearnTerminalAgent 源代码目录

本目录包含 LearnTerminalAgent 项目的核心源代码。

## 📁 目录结构

```
src/
└── learn_agent/          # 主要 Python 包
    ├── agent.py          # Agent 主循环实现
    ├── tools.py          # 工具系统（bash、文件操作等）
    ├── todo.py           # TodoWrite 任务管理
    ├── subagent.py       # SubAgent 子代理委派
    ├── skills.py         # Skills 技能加载系统
    ├── context.py        # Context 上下文管理与压缩
    ├── team_protocols.py # 多代理协作协议
    ├── teams.py          # Agent Teams 团队实现
    ├── autonomous_agents.py # 自主代理功能
    ├── background.py     # 后台任务支持
    ├── worktree_isolation.py # Worktree 隔离机制
    ├── task_system.py    # 任务系统实现
    ├── config.py         # 配置管理
    ├── project_config.py # 项目配置
    ├── main.py           # 程序入口
    └── run.py            # 运行辅助脚本
```

## 🎯 模块说明

### 核心模块

| 文件 | 功能描述 |
|------|----------|
| **agent.py** | Agent 主循环，负责任务处理和决策 |
| **tools.py** | 提供 bash、文件读写、目录列表等工具 |
| **main.py** | CLI 入口，处理用户交互和命令解析 |

### 高级功能模块

| 文件 | 功能描述 |
|------|----------|
| **todo.py** | TodoWrite 任务进度管理 |
| **subagent.py** | SubAgent 子代理委派机制 |
| **skills.py** | 外部技能和知识加载 |
| **context.py** | 上下文 token 管理与自动压缩 |

### 多代理协作模块

| 文件 | 功能描述 |
|------|----------|
| **team_protocols.py** | Agent 团队通信协议 |
| **teams.py** | Agent Teams 团队协作实现 |
| **autonomous_agents.py** | 自主代理行为控制 |

### 系统与配置模块

| 文件 | 功能描述 |
|------|----------|
| **background.py** | 后台异步任务处理 |
| **worktree_isolation.py** | Git Worktree 隔离机制 |
| **task_system.py** | 复杂任务分解与执行 |
| **config.py** | API 密钥和运行时配置 |
| **project_config.py** | 项目级配置管理 |

## 🛠️ 安装与使用

### 开发模式安装

```bash
pip install -e .
```

### 直接运行

```bash
python src/learn_agent/main.py
```

### 使用命令行工具

```bash
learn-agent
```

## 📦 依赖项

主要依赖：
- `langchain>=0.1.0` - AI 框架
- `langchain-openai>=0.0.5` - OpenAI 接口
- `python-dotenv>=1.0.0` - 环境变量管理
- `anthropic>=0.8.0` - Anthropic API

完整依赖列表见 [requirements.txt](../requirements.txt) 或 [pyproject.toml](../pyproject.toml)。

## 🔧 开发指南

### 代码风格

项目使用以下工具保持代码质量：
- **Black** - 代码格式化
- **Ruff** - 代码检查

### 运行测试

```bash
pytest tests/
```

## 📚 相关文档

- [项目概述](../docs/PROJECT_OVERVIEW.md)
- [快速入门](../docs/QUICK_START.md)
- [学习教程](../docs/learn/)
- [使用指南](../docs/guides/)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

仓库地址：https://github.com/linmowudie/LearnTerminalAgent
