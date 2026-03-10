# LearnAgent 快速启动指南

5 分钟快速开始使用 LearnAgent。

## 📋 前置要求

- Python 3.8+
- API Key（通义千问/Anthropic/OpenAI）
- Git（可选，用于 worktree 功能）

## 🚀 安装步骤

### 📦 环境配置（首次使用）

#### 方法 1：使用虚拟环境（推荐）

**1. 创建虚拟环境**
```bash
cd f:\ProjectCode\LearnTerminalAgent
python -m venv .venv
```

**2. 激活虚拟环境**
```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux/Mac
source.venv/bin/activate
```

**3. 安装项目依赖**
```bash
# 使用 uv（推荐，更快）
uv pip install -e .

# 或使用 pip
pip install-e .
```

**4. 验证安装**
```bash
python -m learn_agent.main
```

#### 方法 2：全局安装（不推荐）

```bash
pip install -e .
```

**注意**: 此方法会污染全局 Python 环境，建议使用虚拟环境。

---

### 1. 克隆项目

```bash
cd f:\ProjectCode\learn-claude-code\learn-agent
```

### 2. 安装依赖

**如果已按上述配置虚拟环境，此步骤可跳过**

```bash
pip install -e .
```

或者手动安装：

```bash
pip install langchain langchain-openai python-dotenv anthropic
```

### 3. 配置 API Key

**方法一：使用 .env 文件（推荐）**

在项目根目录创建 `.env` 文件：

```bash
QWEN_API_KEY=sk-your-api-key-here
```

**方法二：环境变量**

```bash
# PowerShell
$env:QWEN_API_KEY="sk-your-api-key-here"

# Linux/Mac
export QWEN_API_KEY="sk-your-api-key-here"
```

**支持的 API Key 类型**:
- `QWEN_API_KEY` - 通义千问（推荐）
- `ANTHROPIC_API_KEY` - Anthropic Claude
- `OPENAI_API_KEY` - OpenAI GPT

### 5. 模型配置

如果你想使用其它平台的API或者其它模型，你必须登录相关平台获取API_KEY,填入配置文件并修改相关的模型名和基础路由，具体详情可以询问大模型，相关技术应用已经很成熟了

### 6. 验证安装

```bash
python -m learn_agent.main
```

看到以下输出表示成功：

```
============================================================
LearnAgent 配置
============================================================
✓ 模型：qwen3.5-flash
✓ Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
✓ API Key: sk-xxxxx...xxxxx
✓ Max Tokens: 8000
✓ Timeout: 120s
============================================================

LearnAgent >>
```

## 🚀 选择工作空间

### 方法 1：在当前目录运行

```bash
cd 你的项目目录
python -m learn_agent.main
```

### 方法 2：指定工作空间路径

```bash
python -m learn_agent.main /path/to/your/project
```

**示例：**
```bash
# 方式 1：进入项目目录
cd F:\ProjectCode\MyApp
python -m learn_agent.main

# 方式 2：直接指定路径
python -m learn_agent.main F:\ProjectCode\MyApp
```

两种方式效果相同：LLM 只能访问该目录下的文件。

**重要提示**：工作空间限制了 LLM 的文件访问范围，确保安全性。就像代码编辑器打开特定文件夹一样，LLM 无法访问工作空间外的文件。

## 💻 第一个任务

### 示例 1：创建文件

```
LearnAgent >> 创建一个 hello.txt 文件，写入 "Hello, LearnAgent!"
```

Agent 会调用 `write_file` 工具完成：

```
[Iteration 1]
🟡 [write_file] {'path': 'hello.txt', 'content': 'Hello, LearnAgent!'}
Successfully wrote 20 characters to hello.txt

Done! File created successfully.
```

### 示例 2：查看文件内容

```
LearnAgent >> 读取 hello.txt 的内容
```

```
[Iteration 1]
🟡 [read_file] {'path': 'hello.txt'}
Hello, LearnAgent!

File contents: Hello, LearnAgent!
```

### 示例 3：运行命令

```
LearnAgent >> 列出当前目录的所有文件
```

```
[Iteration 1]
🟡 $ ls
Directory: F:\ProjectCode\learn-claude-code\learn-agent

Folders:
📁 config/
📁 data/
📁 docs/
📁 skills/
📁 src/

Files:
📄 .env
📄 .gitignore
📄 README.md
...

Directory listing complete.
```

### 示例 4：任务管理

```
LearnAgent >> 添加一个任务：完成项目文档
```

```
Added task #1. Current list:
[ ] #1: 完成项目文档

(0/1 completed)
```

```
LearnAgent >> 更新任务 1 为进行中
```

```
Updated task #1. Current list:
[>] #1: 完成项目文档

(0/1 completed)
```

### 示例 5：使用子代理

```
LearnAgent >> 用子代理探索项目结构
```

```
[SubAgent Starting Task]
Task: Explore project structure...

[SubAgent Iteration 1]
  Using list_directory: {'path': '.'}
  Result: Directory structure...

[SubAgent Task Complete]
Summary: Project has 5 directories and 20 files.
```

## 🔧 常用命令

### 内置命令

```
/help      - 显示帮助信息
/reset     - 重置对话历史
/config    - 显示配置信息
/history   - 显示最近 10 条消息
/todo      - 显示任务进度
/skills    - 列出可用技能
/compact   - 手动压缩上下文
/stats     - 显示上下文统计
/quit      - 退出程序
```

### 工具调用

直接在自然语言中描述即可，Agent 会自动选择工具：

```
LearnAgent >> 创建一个 test.py 文件
LearnAgent >> 运行 python test.py
LearnAgent >> 查看 src 目录有什么文件
LearnAgent >> 添加一个任务：修复 bug
```

## 📊 进阶功能

### 1. 上下文压缩

当对话过长时，自动触发压缩：

```
[Auto Compact] Token count (52000) exceeds threshold (50000)
[Transcript Saved] data/.transcripts/transcript_1709600000.json
[Auto Compact] Saved transcript and compressed context
```

手动压缩：

```
LearnAgent >> /compact
```

### 2. 后台任务

运行长时间任务：

```
LearnAgent >> 在后台运行 npm install
Background task a1b2c3d4 started: npm install

LearnAgent >> 检查后台任务
a1b2c3d4: [completed] npm install
```

### 3. 团队协作

创建队友：

```
LearnAgent >> 创建一个队友叫 reviewer，角色是代码审查员
Spawned 'reviewer' (role: 代码审查员)

LearnAgent >> 发送消息给 reviewer：请审查最新的代码
Sent message to reviewer
```

### 4. Worktree 隔离

创建隔离的工作树：

```
LearnAgent >> 创建 worktree feature-a，绑定到任务 1
Created worktree: {"name": "feature-a", "path": "...", "branch": "wt/feature-a"}
```

## ⚙️ 配置选项

### 修改配置

编辑 `config/config.json`：

```json
{
  "agent": {
    "model_name": "qwen3.5-flash",
    "max_tokens": 8000,
    "timeout": 120,
    "max_iterations": 50
  },
  "context": {
    "threshold": 50000,
    "auto_compact_enabled": true
  },
  "tasks": {
    "max_items": 20
  }
}
```

### 环境变量

所有配置项都支持环境变量覆盖：

```bash
export MODEL_ID=qwen-max
export MAX_TOKENS=16000
export TIMEOUT=300
```

## 🐛 常见问题

### 问题 1：API Key 错误

```
❌ 配置错误：未找到 API Key！
```

**解决**: 确保 `.env` 文件存在且 API Key 正确

### 问题 2：工具调用失败

```
Error executing tool: Permission denied
```

**解决**: 检查工作目录权限，避免危险操作

### 问题 3：上下文过长

```
Warning: Context approaching token limit
```

**解决**: 使用 `/compact` 手动压缩或等待自动压缩

### 问题 4：后台任务超时

```
Error: Timeout (300s)
```

**解决**: 增加超时时间或优化任务

## 📚 下一步

完成快速启动后，建议阅读：

1. [配置指南](guides/config-guide.md) - 详细配置说明
2. [工具使用](guides/tools.md) - 所有内置工具
3. [Learn 系列](learn/s01-the-agent-loop.md) - 深入理解原理

## 🎯 最佳实践

1. **任务分解**: 复杂任务拆分为多个小任务
2. **及时压缩**: 长对话后主动压缩上下文
3. **合理使用子代理**: 独立子任务委派给子代理
4. **持久化任务**: 重要任务使用 Task System 而非 Todo
5. **安全优先**: 避免危险命令，审查 Agent 行为

---

**Happy Coding!** 🚀

如有问题，请查阅 [完整文档](INDEX.md) 或提交 Issue。
