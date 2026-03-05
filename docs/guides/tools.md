# LearnTerminalAgent 工具使用指南

所有内置工具的详细说明和使用示例。

## 🛠️ 基础工具 (s02)

### bash

执行 shell 命令。

**签名**:
```python
bash(command: str) -> str
```

**示例**:
```python
# 简单命令
agent.run("运行 python --version")

# 复杂命令
agent.run("创建一个目录并初始化 git 仓库")
# 自动执行：mkdir project && cd project && git init

# 查看文件权限
agent.run("ls -la src/")
```

**安全限制**:
- 阻止危险命令（`rm -rf /`, `sudo` 等）
- 超时限制（默认 120 秒）
- 输出长度限制（50000 字符）

---

### read_file

读取文件内容。

**签名**:
```python
read_file(path: str, limit: Optional[int] = None) -> str
```

**示例**:
```python
# 读取整个文件
agent.run("读取 README.md 的内容")

# 只读前 10 行
agent.run("读取 config.py 的前 10 行")
# 或
result = read_file.invoke({"path": "config.py", "limit": 10})

# 查看日志文件末尾
agent.run("查看 app.log 的最后 50 行")
```

**安全限制**:
- 只能访问工作目录内的文件
- 输出长度限制（50000 字符）

---

### write_file

写入文件内容。

**签名**:
```python
write_file(path: str, content: str) -> str
```

**示例**:
```python
# 创建新文件
agent.run("创建一个 test.txt 文件，写入 Hello World")

# 覆盖现有文件
agent.run("更新 config.json，清空所有内容")

# 创建嵌套目录结构
agent.run("创建 src/utils/helpers.py 文件")
# 自动创建父目录
```

**安全限制**:
- 只能写入工作目录内
- 自动创建不存在的父目录

---

### list_directory

列出目录内容。

**签名**:
```python
list_directory(path: str = ".") -> str
```

**示例**:
```python
# 列出当前目录
agent.run("列出当前目录的所有文件")

# 查看指定目录
agent.run("src 目录下有哪些文件夹？")

# 递归查看（需要多次调用）
agent.run("先列出根目录，然后分别查看每个子目录")
```

**输出格式**:
```
Directory: /path/to/dir

Folders:
📁 config/
📁 src/

Files:
📄 README.md
📄 config.json
```

---

## 📝 任务管理工具

### TodoWrite 工具 (s03)

#### todo_add

添加新任务。

**签名**:
```python
todo_add(text: str) -> str
```

**示例**:
```python
agent.run("添加一个任务：完成项目文档")
# 输出：Added task #1. Current list:
#       [ ] #1: 完成项目文档
```

---

#### todo_update

更新任务状态或内容。

**签名**:
```python
todo_update(item_id: str, status: str, text: Optional[str] = None) -> str
```

**状态值**:
- `pending` - 待处理
- `in_progress` - 进行中
- `completed` - 已完成

**示例**:
```python
# 开始任务
agent.run("把任务 1 标记为进行中")

# 完成任务
agent.run("完成任务 1")

# 修改任务描述
agent.run("把任务 1 的描述改为'完成项目文档 - 修订版'")
```

---

#### todo_remove

删除任务。

**签名**:
```python
todo_remove(item_id: str) -> str
```

**示例**:
```python
agent.run("删除任务 3")
```

---

#### todo_list

列出所有任务。

**签名**:
```python
todo_list() -> str
```

**示例**:
```python
agent.run("显示我的任务列表")
# 输出：
# [ ] #1: 任务 1
# [>] #2: 任务 2 (进行中)
# [x] #3: 任务 3
# (1/3 completed)
```

---

#### todo_progress

显示任务进度统计。

**签名**:
```python
todo_progress() -> str
```

**示例**:
```python
agent.run("显示任务进度")
# 输出：
# Total: 3 tasks
# Completed: 1
# In Progress: 1
# Pending: 1
# Progress: 33.3%
```

---

### Task System 工具 (s07)

#### task_create

创建持久化任务。

**签名**:
```python
task_create(subject: str, description: str = "") -> str
```

**示例**:
```python
agent.task_create(
    subject="重构代码",
    description="优化性能和提高可维护性"
)
# 输出：
# {
#   "id": 1,
#   "subject": "重构代码",
#   "description": "优化性能和提高可维护性",
#   "status": "pending"
# }
```

---

#### task_get

获取任务详情。

**签名**:
```python
task_get(task_id: int) -> str
```

**示例**:
```python
agent.task_get(1)
# 返回任务完整信息，包括依赖关系
```

---

#### task_update

更新任务状态和依赖。

**签名**:
```python
task_update(
    task_id: int,
    status: Optional[str] = None,
    addBlockedBy: Optional[List[int]] = None,
    addBlocks: Optional[List[int]] = None
) -> str
```

**示例**:
```python
# 更新状态
agent.task_update(1, status="in_progress")

# 设置依赖：任务 2 阻塞任务 1
agent.task_update(1, addBlocks=[2])
# 任务 1 的 blockedBy 会添加 [2]
# 任务 2 的 blocks 会添加 [1]

# 完成任务（自动清除依赖）
agent.task_update(1, status="completed")
```

---

#### task_list

列出所有任务。

**签名**:
```python
task_list() -> str
```

**示例**:
```python
agent.task_list()
# 输出：
# [ ] #1: 任务 1
# [>] #2: 任务 2 (blocked by: [1])
# [x] #3: 任务 3
```

---

## 🎯 高级功能工具

### Skill Loading 工具 (s05)

#### list_skills

列出可用技能。

```python
agent.list_skills()
# 输出：
# Available skills:
#   - pdf-processing: Process PDF files
#   - code-review: Code review best practices
```

---

#### load_skill

加载技能完整内容。

```python
skill_content = agent.load_skill("code-review")
print(skill_content)
# <skill name="code-review">
# ---
# name: code-review
# description: ...
# ---
# 完整内容...
# </skill>
```

---

#### reload_skills

重新加载技能（技能文件更新后）。

```python
agent.reload_skills()
# Reloaded 3 skills: pdf-processing, code-review, testing
```

---

### Background Tasks 工具 (s08)

#### background_run

在后台运行命令（非阻塞）。

```python
agent.background_run("npm install")
# 输出：Background task a1b2c3d4 started: npm install
```

---

#### check_background

检查后台任务状态。

```python
# 检查特定任务
agent.check_background("a1b2c3d4")

# 列出所有任务
agent.check_background()
```

---

### Team Collaboration 工具 (s09)

#### spawn_teammate

创建持久化队友代理。

```python
agent.spawn_teammate(
    name="reviewer",
    role="代码审查员",
    prompt="Review all code changes for quality"
)
```

---

#### send_message

发送消息给队友。

```python
agent.send_message(
    to="reviewer",
    content="请审查 src/main.py",
    msg_type="message"
)
```

---

#### read_inbox

读取收件箱。

```python
inbox = agent.read_inbox()
# 返回 JSON 格式的消息列表
```

---

#### broadcast

广播消息给所有队友。

```python
agent.broadcast("所有人注意：下午 3 点开会")
```

---

### Worktree 工具 (s12)

#### worktree_create

创建 worktree。

```python
agent.worktree_create(
    name="feature-a",
    task_id=1,
    base_ref="main"
)
```

---

#### worktree_list

列出所有 worktree。

```python
agent.worktree_list()
```

---

#### worktree_status

查看 worktree 状态。

```python
agent.worktree_status("feature-a")
```

---

#### worktree_run

在 worktree 中运行命令。

```python
agent.worktree_run(
    name="feature-a",
    command="npm test"
)
```

---

#### worktree_remove

删除 worktree。

```python
agent.worktree_remove(
    name="feature-a",
    force=False,
    complete_task=True
)
```

---

#### worktree_keep

保留 worktree（不移除）。

```python
agent.worktree_keep("feature-a")
```

---

#### worktree_events

查看最近事件。

```python
agent.worktree_events(limit=20)
```

---

## 🔍 工具使用技巧

### 1. 自然语言组合

Agent 会自动组合多个工具：

```
用户：创建一个 test.py 文件并运行它

Agent 执行:
1. write_file → 创建文件
2. bash → 运行 python test.py
```

### 2. 明确指定工具

需要时可以明确指定：

```
用户：用 bash 工具运行 ls -la
```

### 3. 查看工具结果

详细模式下可以看到每个工具的结果：

```python
agent.run("任务", verbose=True)
```

### 4. 错误处理

工具失败时会返回清晰的错误信息：

```
Error: File not found: nonexistent.txt
Error: Path escapes workspace: /etc/passwd
Error: Command timeout after 120s
```

---

## 📊 工具分类总结

| 类别 | 工具数量 | 模块 |
|------|---------|------|
| 基础工具 | 4 | s02 |
| Todo 工具 | 5 | s03 |
| Task System | 4 | s07 |
| Skills | 4 | s05 |
| Background | 2 | s08 |
| Teams | 5 | s09 |
| Worktree | 7 | s12 |
| **总计** | **31** | - |

---

**下一步**: [任务管理指南](task-management.md) →
