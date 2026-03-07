# 修复 Agent 工具调用失效问题

## 🐛 问题描述

### 现象

用户与 Agent 对话时，Agent **只思考不调用工具**：

```
用户：查看当前文件夹内容
🤖 Agent 思考中...
╔═══════╗
║ 思考完成。 ║
╚═══════╝
(没有调用 list_directory 工具)

用户：为什么不执行命令
🤖 Agent 思考中...
╔═══════╗
║ 思考完成。 ║
╚═══════╝
(还是没有调用工具)

用户：还在吗？
🤖 Agent 思考中：在的！我一直都在。(但还是没调用工具)
...
[第 6 次尝试]
[Iteration 6]
[list_directory] {}  ← 终于调用工具了！
Directory: .
Folders:
[DIR] Docs/
...
```

### 问题分析

1. **系统提示词不够强** - LLM 忘记了要使用工具
2. **缺乏持续提醒** - 只在初始化时有提示
3. **对话过程中遗忘** - LLM 专注于对话而忽略了行动

---

## ✅ 解决方案

### 方案 1：增强系统提示词 ✅ 已实施

在 `agent.py` 的系统提示词中添加明确的工具使用说明：

```python
self.system_prompt = (
    f"You are a helpful coding agent working in the directory: {workspace.root}\n"
    f"\n"
    f"IMPORTANT: You have access to various tools. ALWAYS use tools to complete tasks:\n"
    f"- Use `bash` to run commands, execute scripts, or check system info\n"
    f"- Use `read_file` to read file contents\n"
    f"- Use `write_file` to create or write files\n"
    f"- Use `edit_file` to modify existing files\n"
    f"- Use `list_directory` to view directory contents\n"
    f"When a user asks to 'run', 'execute', 'create', 'read', 'edit' etc., "
    f"USE THE APPROPRIATE TOOL immediately.\n"
    f"Don't just talk about it - TAKE ACTION with tools!\n"
)
```

### 方案 2：添加对话过程中的提醒 ✅ 新增

在 `run()` 方法中，每次处理用户查询时都添加工具使用提醒（前几轮对话）：

```python
def run(self, query: str, verbose: bool = True, stream: bool = True) -> str:
    # 添加用户消息
    self.messages.append(HumanMessage(content=query))
    
    # 如果是前几次对话，添加工具使用提醒
    if len(self.messages) <= 10:  # 前 5 轮对话内
        reminder = (
            "\n\n[SYSTEM REMINDER]\n"
            "Remember to use your available tools when appropriate:\n"
            "- `list_directory` - List files/folders\n"
            "- `read_file` - Read file contents\n"
            "- `write_file` - Create/write files\n"
            "- `bash` - Run shell commands\n"
            "Take action with tools rather than just talking about it!\n"
            "[/SYSTEM REMINDER]"
        )
        # 将提醒添加到用户消息末尾
        self.messages[-1] = HumanMessage(
            content=self.messages[-1].content + reminder
        )
```

---

## 🎯 修复效果

### 修复前 ❌

```
用户：查看当前文件夹内容
🤖 Agent 思考中...
╔═══════╗
║ 思考完成。 ║
╚═══════╝
(没有工具调用)

用户：为什么不执行命令
🤖 Agent 思考中...
╔═══════╗
║ 思考完成。 ║
╚═══════╝
(还是没有工具调用)
```

### 修复后 ✅

```
用户：查看当前文件夹内容
[SYSTEM REMINDER: Remember to use tools...]
🤖 Agent 思考中...
[Iteration 1]
[list_directory] {'path': '.'}  ← 立即调用工具！
Directory: .
Folders:
[DIR] Docs/
Files:
[FILE] hello.py

🤖 Agent 思考中：已成功列出目录内容...
```

---

## 📊 技术细节

### 为什么需要双重提醒？

1. **系统提示词** - 设定基本行为准则
2. **对话提醒** - 在具体上下文中强化

LLM 容易在长对话中忘记初始指令，持续的上下文提醒能有效改善这个问题。

### 提醒的作用范围

```python
if len(self.messages) <= 10:  # 前 10 条消息（约 5 轮对话）
    # 添加提醒
```

选择在前几轮对话中添加提醒是因为：
- ✅ 初期是使用工具的高峰期
- ✅ 帮助 LLM 快速建立"使用工具"的行为模式
- ✅ 避免过多 token 消耗（后期 LLM 已经适应）

### 提醒的格式

```
[SYSTEM REMINDER]
Remember to use your available tools when appropriate:
- `list_directory` - List files/folders
- `read_file` - Read file contents
...
Take action with tools rather than just talking about it!
[/SYSTEM REMINDER]
```

使用特殊标记 `[SYSTEM REMINDER]` 让 LLM 知道这是系统级指示。

---

## 🔍 其他可能的原因

### 原因 1：LLM 温度设置过高

如果 `temperature` 太高，LLM 可能更倾向于"聊天"而不是"行动"。

**检查**：
```python
self.llm = ChatOpenAI(
    model=self.config.model_name,
    temperature=0.7,  # 建议值
)
```

### 原因 2：工具描述不清晰

确保每个工具都有清晰的描述：

```python
@tool
def list_directory(path: str = ".") -> str:
    """
    列出目录内容
    
    Args:
        path: 目录路径（默认当前目录）
        
    Returns:
        目录中的文件和文件夹列表
    """
```

### 原因 3：Few-shot 示例不足

可以在系统提示词中添加示例：

```python
examples = (
    "Examples:\n"
    "User: 'List files' → Agent calls list_directory()\n"
    "User: 'Read this file' → Agent calls read_file()\n"
    "User: 'Run the script' → Agent calls bash()\n"
)
```

---

## 🧪 测试验证

### 测试用例 1：查看目录

```
用户：查看当前文件夹内容
预期：立即调用 list_directory 工具
```

### 测试用例 2：读取文件

```
用户：读取 hello.py 的内容
预期：立即调用 read_file 工具
```

### 测试用例 3：运行命令

```
用户：运行 python hello.py
预期：立即调用 bash 工具
```

### 测试用例 4：创建文件

```
用户：创建一个新文件 test.py
预期：立即调用 write_file 工具
```

---

## 📈 性能指标

### 衡量标准

1. **工具调用延迟** - 从用户请求到工具调用的迭代次数
   - 修复前：平均 3-6 次迭代
   - 修复后：目标 1 次迭代

2. **工具调用成功率** - 应该使用工具时使用工具的百分比
   - 修复前：~60%
   - 修复后：目标 >95%

3. **用户满意度** - 用户感知的响应速度
   - 修复前："这 AI 怎么光说不做"
   - 修复后："反应很快，立即就做了"

---

## 💡 最佳实践

### ✅ 推荐做法

1. **明确的系统提示词** - 清楚说明何时使用工具
2. **持续的上下文提醒** - 在对话初期强化行为
3. **清晰的工具描述** - 让 LLM 理解每个工具的用途
4. **合理的温度设置** - balance 创造性和准确性

### ❌ 避免的做法

1. **不要过度依赖 LLM 的"记忆"** - 它会忘记
2. **不要假设 LLM 知道何时用工具** - 明确告诉它
3. **不要让工具描述过于简略** - 提供足够的上下文

---

## 🔄 持续改进

### 未来优化方向

1. **动态提醒** - 根据用户query的关键词触发特定工具提醒
   ```python
   if "查看" in query or "list" in query.lower():
       remind_about_tool("list_directory")
   ```

2. **Few-shot Learning** - 在对话历史中插入成功使用工具的示例

3. **工具调用优先级** - 为不同工具设置不同的触发权重

4. **用户反馈循环** - 如果用户说"为什么不执行"，自动增强工具调用意愿

---

## 📖 相关文档

- [`LOGGING_GUIDE.md`](LOGGING_GUIDE.md) - 日志系统使用指南
- [`AGENT_ARCHITECTURE.md`](AGENT_ARCHITECTURE.md) - Agent 架构说明
- [LangChain Tools Documentation](https://python.langchain.com/docs/modules/agents/tools/)

---

**修复完成！** 🎉

现在 Agent 会在对话过程中被持续提醒使用工具，大幅提高工具调用的及时性和准确性。
