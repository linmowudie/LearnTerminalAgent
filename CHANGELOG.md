# 变更日志 (Changelog)

本文件记录了 LearnTerminalAgent 项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [1.0.0] - 2026-03-05

### 新增 ✨
- **核心功能**
  - Agent 主循环实现（基于 LangChain）
  - 工具使用系统（bash、文件读写、目录列表等）
  - TodoWrite 任务管理系统
  - SubAgent 子代理委派机制
  - Skills 技能加载系统
  - Context 上下文自动压缩
  - Background 后台任务支持
  - Team Protocols 多代理协作协议
  - Autonomous Agents 自主代理功能
  - Worktree Isolation 工作树隔离

- **CLI 功能**
  - 交互式命令行界面
  - 特殊命令系统（`/help`, `/quit`, `/reset` 等）
  - 配置管理和回退机制
  - 帮助文档系统集成

- **文档系统**
  - 完整的学习教程（s01-s12）
  - 快速入门指南
  - 项目概述文档
  - 工具使用说明
  - 配置指南

- **开发工具**
  - pyproject.toml 配置
  - Black 代码格式化
  - Ruff 代码检查
  - Pytest 测试框架

### 技术栈 🛠️
- Python >= 3.8
- LangChain >= 0.1.0
- LangChain-OpenAI >= 0.0.5
- python-dotenv >= 1.0.0
- Anthropic >= 0.8.0

### 项目结构 📁
```
LearnTerminalAgent/
├── src/learn_agent/      # 源代码
│   ├── agent.py          # Agent 主循环
│   ├── tools.py          # 工具实现
│   ├── todo.py           # 任务管理
│   ├── subagent.py       # 子代理
│   ├── skills.py         # 技能系统
│   ├── context.py        # 上下文管理
│   ├── team_protocols.py # 团队协作
│   └── main.py           # 程序入口
├── docs/                 # 文档
│   ├── learn/            # 学习教程
│   └── guides/           # 使用指南
├── config/               # 配置文件
└── tests/                # 测试用例
```

---

## 版本说明

### 版本号规则
- **主版本号 (Major)**: 不兼容的 API 修改
- **次版本号 (Minor)**: 向下兼容的功能性新增
- **修订号 (Patch)**: 向下兼容的问题修正

### 更新类型
- `新增` - 新功能
- `优化` - 性能改进或体验优化
- `修复` - Bug 修复
- `弃用` - 即将移除的功能
- `移除` - 已移除的功能
- `安全` - 安全性修复

---

## 未来计划 🚀

### v1.1.0 (计划中)
- [ ] 增加更多内置工具
- [ ] 改进上下文压缩算法
- [ ] 添加单元测试覆盖
- [ ] 完善错误处理机制

### v1.2.0 (计划中)
- [ ] 支持多种 LLM 后端
- [ ] 添加 Web UI 界面
- [ ] 实现插件系统
- [ ] 提供 Docker 部署方案

---

## 贡献指南

欢迎提交 Issue 和 Pull Request！

请访问 GitHub 仓库：https://github.com/linmowudie/LearnTerminalAgent

---

**最后更新**: 2026-03-05
