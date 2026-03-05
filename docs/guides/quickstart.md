# LearnTerminalAgent 快速入门

5 分钟快速开始使用 LearnAgent。

## 📋 前置要求

- ✅ Python 3.8+
- ✅ API Key（通义千问/Anthropic/OpenAI）
- ✅ pip 或 poetry

## 🚀 安装步骤

### 1. 克隆项目

```bash
cd your-project-directory
git clone <repository-url>
cd learn-agent
```

### 2. 安装依赖

**方法一：使用 pip**

```bash
pip install -e .
```

**方法二：手动安装依赖**

```bash
pip install langchain langchain-openai python-dotenv anthropic
```

### 3. 配置 API Key

**推荐：使用 .env 文件**

在项目根目录创建 `.env` 文件：

```bash
QWEN_API_KEY=sk-your-api-key-here
```

**或使用环境变量**

```bash
# PowerShell
$env:QWEN_API_KEY="sk-your-api-key-here"

# Linux/Mac
export QWEN_API_KEY="sk-your-api-key-here"
```

### 4. 验证安装

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

## 💻 基础使用

### 第一个任务

```
LearnAgent >> 创建一个 hello.txt 文件，写入 "Hello, LearnAgent!"
```

Agent 会执行：

```
[Iteration 1]
🟡 [write_file] {'path': 'hello.txt', 'content': 'Hello, LearnAgent!'}
Successfully wrote 20 characters to hello.txt

Done! File created successfully.
```

### 查看文件内容

```
LearnAgent >> 读取 hello.txt 的内容
```

```
[Iteration 1]
🟡 [read_file] {'path': 'hello.txt'}
Hello, LearnAgent!

File contents: Hello, LearnAgent!
```

### 运行命令

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
📁 src/

Files:
📄 .env
📄 README.md
...

Directory listing complete.
```

## 🔧 常用命令

### 内置斜杠命令

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

### 自然语言调用工具

直接描述你的需求，Agent 会自动选择工具：

```
LearnAgent >> 创建一个 test.py 文件
LearnAgent >> 运行 python test.py
LearnAgent >> 查看 src 目录下有哪些文件
LearnAgent >> 添加一个任务：完成项目文档
LearnAgent >> 把任务 1 标记为进行中
```

## 📊 进阶功能

### 1. 任务管理

#### TodoWrite (短期任务)

```
LearnAgent >> 添加任务：完成项目文档
Added task #1. Current list:
[ ] #1: 完成项目文档

LearnAgent >> 更新任务 1 为进行中
Updated task #1. Current list:
[>] #1: 完成项目文档

LearnAgent >> 完成任务 1
Updated task #1. Current list:
[x] #1: 完成项目文档
(1/1 completed)
```

#### Task System (持久化任务)

```
LearnAgent >> 创建一个任务，主题是"重构代码"，描述"优化性能"
Created task: {
  "id": 1,
  "subject": "重构代码",
  "description": "优化性能",
  "status": "pending"
}

LearnAgent >> 列出所有任务
[ ] #1: 重构代码
```

### 2. 子代理委派

```
LearnAgent >> 用子代理探索项目结构

[SubAgent Starting Task]
Task: Explore project structure...

[SubAgent Iteration 1]
  Using list_directory: {'path': '.'}
  
[SubAgent Task Complete]
Summary: Project has 5 directories and 20 files.

Done! I've delegated the task. Here's what it found...
```

### 3. 后台任务

```
LearnAgent >> 在后台运行 npm install
Background task a1b2c3d4 started: npm install

LearnAgent >> 检查后台任务状态
a1b2c3d4: [completed] npm install
```

### 4. 上下文管理

查看统计：
```
LearnAgent >> /stats
上下文统计:
  Token 数：15000
  阈值：50000
  消息数：45
  压缩次数：2
```

手动压缩：
```
LearnAgent >> /compact
Context compressed successfully
```

## ⚙️ 自定义配置

### 修改配置文件

编辑 `config/config.json`:

```json
{
  "agent": {
    "model_name": "qwen-max",
    "max_tokens": 16000,
    "timeout": 300,
    "max_iterations": 100
  },
  "context": {
    "threshold": 80000,
    "keep_recent": 5
  }
}
```

### 使用环境变量

```bash
export MODEL_ID=qwen-max
export MAX_TOKENS=16000
export TIMEOUT=300
```

## 🐛 常见问题

### Q1: 启动失败，提示 API Key 错误

**解决**:
1. 检查 `.env` 文件是否存在
2. 确认 API Key 格式正确
3. 重启 Python 进程

### Q2: 工具调用失败

**解决**:
- 检查工作目录权限
- 避免危险命令
- 检查文件路径是否正确

### Q3: 达到最大迭代次数

**解决**:
- 增加 `max_iterations` 配置
- 将复杂任务拆分为多个小任务
- 使用子代理委派

### Q4: 上下文过长警告

**解决**:
- 使用 `/compact` 手动压缩
- 等待自动压缩触发
- 增加 `threshold` 配置

## 📚 下一步学习

完成快速入门后，建议深入学习：

1. **[配置指南](config-guide.md)** - 详细配置说明
2. **[工具使用](tools.md)** - 所有内置工具文档
3. **[Learn 系列](../INDEX.md)** - 深入理解各模块原理

## 🎯 最佳实践

### 1. 任务分解

将大任务拆分为小步骤：
```
❌ "完成整个项目"
✅ "1. 创建项目结构 → 2. 实现核心功能 → 3. 编写测试"
```

### 2. 及时更新状态

保持任务状态准确反映进度。

### 3. 合理使用子代理

独立子任务委派给子代理，减少主代理负担。

### 4. 定期压缩上下文

长对话后主动压缩，节省 token。

### 5. 安全优先

审查 Agent 行为，避免危险操作。

---

**Happy Coding!** 🚀

遇到问题？查看 [完整文档索引](../INDEX.md)
