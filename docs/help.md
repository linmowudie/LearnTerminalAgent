# LearnAgent 使用指南

## 快速开始

### 1. 基本用法

直接输入自然语言描述你的任务，例如：

```
LearnAgent >> 创建一个 hello.txt 文件
LearnAgent >> 列出当前目录的所有文件
LearnAgent >> 查看 README.md 的内容
LearnAgent >> 运行 python --version
```

### 2. 特殊命令

以下命令需要以 `/` 开头，由程序直接处理：

| 命令 | 说明 |
|------|------|
| `/help` | 显示此帮助信息 |
| `/reset` | 清除对话历史，开始新对话 |
| `/config` | 显示当前配置信息 |
| `/history` | 显示当前对话历史 |
| `/todo` | 显示任务进度 |
| `/skills` | 列出可用技能 |
| `/compact` | 手动压缩上下文 |
| `/stats` | 显示上下文统计 |
| `/quit` | 退出程序 |

**注意：** 不带 `/` 的文本会被视为普通对话，由大模型处理。

### 3. 可用工具

Agent 可以使用以下工具：

- **bash** - 运行 shell 命令
- **read_file** - 读取文件内容
- **write_file** - 写入文件内容
- **list_directory** - 列出目录内容
- **todo_add** - 添加任务
- **todo_update** - 更新任务
- **load_skill** - 加载技能

### 4. 高级功能

#### TodoWrite - 任务管理
Agent 会自动管理任务进度，适合复杂的多步骤任务。

#### SubAgent - 子代理委派
可以将特定任务委派给子代理执行。

示例：
```
LearnAgent >> 用子代理探索项目结构
```

#### Skills - 技能加载
按需加载外部知识和技能模块。

示例：
```
LearnAgent >> 加载 pdf 技能
```

#### Context - 上下文压缩
自动或手动压缩长对话，节省 token。

### 5. 使用示例

#### 示例 1：创建文件
```
LearnAgent >> 创建一个 test.py 文件，包含 print("Hello")
```

#### 示例 2：多步骤任务
```
LearnAgent >> 帮我重构这个项目的代码结构
```
Agent 会自动使用 TodoWrite 管理任务进度。

#### 示例 3：使用子代理
```
LearnAgent >> 分析 docs 目录下所有文档的结构
```

#### 示例 4：加载技能
```
LearnAgent >> 我需要处理 PDF 文档，请加载相关技能
```

### 6. 最佳实践

1. **清晰描述任务**：尽可能详细地描述你的需求
2. **利用任务系统**：复杂任务会让 Agent 自动分解步骤
3. **合理使用命令**：区分 `/command`（系统命令）和普通对话
4. **定期检查进度**：使用 `/todo` 查看任务完成情况
5. **管理上下文**：长对话时使用 `/compact` 或 `/stats` 监控 token 使用

### 7. 常见问题

**Q: 如何退出程序？**
A: 输入 `/quit` 或按 Ctrl+D

**Q: 如何清除对话历史？**
A: 输入 `/reset` 开始新的对话

**Q: 如何查看配置？**
A: 输入 `/config` 查看当前配置信息

**Q: 命令不生效怎么办？**
A: 确保命令以 `/` 开头，如 `/help` 而不是 `help`

---

**更多信息请参考：**
- [快速入门](./QUICK_START.md)
- [项目概述](./PROJECT_OVERVIEW.md)
- [学习文档](./learn/)
