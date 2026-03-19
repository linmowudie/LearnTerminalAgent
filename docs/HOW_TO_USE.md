# LearnTerminalAgent 启动指南

## 🚀 在任意目录启动的三种方法

### 方法 1：使用启动脚本（推荐）✅

```bash
# 在任何目录都可以运行
python F:\ProjectCode\LearnTerminalAgent\run_agent.py [工作空间路径]

# 示例 1：在当前目录启动
cd F:\ProjectCode\MemoryWords
python F:\ProjectCode\LearnTerminalAgent\run_agent.py

# 示例 2：指定工作空间
python F:\ProjectCode\LearnTerminalAgent\run_agent.py F:\ProjectCode\LearnTerminalAgent
```

**为什么用这个方法？**
- ✅ 自动处理 Python 路径
- ✅ 无需配置环境变量
- ✅ 在任何目录都能运行
- ✅ 最简单，不容易出错

---

### 方法 2：直接运行 main.py

```bash
python F:\ProjectCode\LearnTerminalAgent\src\learn_agent\main.py [工作空间路径]

# 示例
cd F:\ProjectCode\MemoryWords
python F:\ProjectCode\LearnTerminalAgent\src\learn_agent\main.py F:\ProjectCode\LearnTerminalAgent
```

---

### 方法 3：安装为系统包（长期使用）

```bash
# 进入项目根目录
cd F:\ProjectCode\LearnTerminalAgent

# 可编辑安装
pip install -e .

# 之后可以在任意位置使用
learn-agent  # 命令行工具
# 或
python -m learn_agent.main  # 模块方式
```

---

## 💡 解决常见问题

### 问题 1：ModuleNotFoundError

**错误信息**：
```
ModuleNotFoundError: No module named 'learn_agent'
```

**原因**：Python 找不到 `learn_agent` 模块

**解决方法**：使用启动脚本
```bash
python F:\ProjectCode\LearnTerminalAgent\run_agent.py
```

---

### 问题 2：UnicodeEncodeError（Windows）

**错误信息**：
```
UnicodeEncodeError: 'gbk' codec can't encode character
```

**原因**：Windows PowerShell 默认使用 GBK 编码

**解决方法**：已自动在代码中处理，设置 UTF-8 编码

---

### 问题 3：配置文件找不到

**错误信息**：
```
Warning: Config file not found
```

**解决方法**：
1. 在项目目录创建 `.env` 文件
2. 添加 API Key：
   ```
   QWEN_API_KEY=sk-your-api-key-here
   ```

---

## 📋 完整使用流程

### 步骤 1：准备项目

```bash
# 创建或进入你的项目目录
cd F:\ProjectCode\MyProject

# 确保有一些文件
mkdir src
echo "print('Hello')" > src/main.py
```

### 步骤 2：配置 API Key

在项目目录创建 `.env` 文件：

```bash
# .env 文件内容
QWEN_API_KEY=sk-your-api-key-here
```

### 步骤 3：启动 Agent

```bash
# 在项目目录内
python F:\ProjectCode\LearnTerminalAgent\run_agent.py

# 或在其他目录
python F:\ProjectCode\LearnTerminalAgent\run_agent.py F:\ProjectCode\MyProject
```

### 步骤 4：开始工作

```
============================================================
LearnAgent 配置
============================================================
✓ 模型：qwen3.5-flash
✓ Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
✓ API Key: sk-xxxxx...xxxxx
============================================================

[WORKSPACE] 使用工作空间：F:\ProjectCode\MyProject

LearnTerminalAgent >> 创建一个 README.md 文件
```

---

## 🔒 工作空间说明

### 什么是工作空间？

工作空间是 LLM 可以访问的唯一目录范围。

**例如**：
```bash
python run_agent.py F:\ProjectCode\MyProject
```

此时工作空间 = `F:\ProjectCode\MyProject`

### 允许的操作 ✅

```python
# 读取工作空间内的文件
read_file("src/main.py")
read_file("README.md")

# 写入工作空间内的文件
write_file("new_file.txt", "content")

# 列出工作空间内的目录
list_directory("src")

# 在工作空间执行命令
bash "python src/main.py"
```

### 禁止的操作 ❌

```python
# 访问工作空间外的文件
read_file("C:/Windows/System32/drivers/etc/hosts")
# Error: 路径越界

read_file("../OtherProject/file.txt")
# Error: 路径越界

# 写入工作空间外
write_file("C:/tmp/evil.txt", "content")
# Error: 路径越界
```

---

## 🎯 实际使用场景

### 场景 1：项目开发

```bash
cd F:\ProjectCode\WebApp
python F:\ProjectCode\LearnTerminalAgent\run_agent.py

# 现在可以让 Agent：
# - "创建 Flask 路由"
# - "修改数据库配置"  
# - "运行测试"
# - "查看依赖"
```

### 场景 2：学习练习

```bash
mkdir F:\LearnPython\exercise_01
cd F:\LearnPython\exercise_01
python F:\ProjectCode\LearnTerminalAgent\run_agent.py

# Agent 只能在这个练习目录内操作
# 不会影响其他文件或项目
```

### 场景 3：代码审查

```bash
cd F:\CodeReview\project-a
python F:\ProjectCode\LearnTerminalAgent\run_agent.py

# 让 Agent 分析代码：
# - "分析代码结构"
# - "找出所有 Python 文件"
# - "检查是否有安全问题"
```

---

## 🛠️ 快捷方式

### Windows 批处理脚本

创建了 `run.bat` 后：

```batch
REM 复制 run.bat 到方便的位置
copy F:\ProjectCode\LearnTerminalAgent\run.bat C:\Tools\

# 然后在任意位置使用
run.bat F:\ProjectCode\MyProject
```

### PowerShell 别名

在 PowerShell 配置文件添加：

```powershell
Set-Alias la "python F:\ProjectCode\LearnTerminalAgent\run_agent.py"

# 之后可以直接使用
la F:\ProjectCode\MyProject
```

---

## 📖 更多资源

- [工具使用指南](docs/guides/tools.md) - 所有工具的详细说明
- [快速入门](docs/QUICK_START.md) - 5 分钟上手
- [工作空间示例](docs/WORKSPACE_EXAMPLES.md) - 实际使用例子
- [实施总结](docs/WORKSPACE_IMPLEMENTATION_SUMMARY.md) - 技术细节

---

## ❓ 快速问答

**Q: 必须在项目目录才能启动吗？**  
A: 不！可以在任何目录使用 `run_agent.py` 指定工作空间路径。

**Q: 如何切换工作空间？**  
A: 重启 Agent，传入新的工作空间路径。

**Q: 可以同时操作多个项目吗？**  
A: 每次启动只能有一个工作空间。需要开多个终端窗口。

**Q: 为什么我的文件访问被拒绝？**  
A: 文件可能在工作空间外。这是安全特性，不是 bug。

**Q: 如何临时访问外部文件？**  
A: 将文件复制到工作空间内，或使用绝对路径启动。

---

## ✅ 验证清单

使用前确认：

- [ ] Python 3.8+ 已安装
- [ ] API Key 已配置（`.env` 文件或环境变量）
- [ ] 知道要工作的项目目录路径
- [ ] 使用 `run_agent.py` 启动（推荐）

启动后确认：

- [ ] 看到 "✓ 工作空间已设置：xxx" 提示
- [ ] 确认工作空间路径正确
- [ ] 可以正常输入命令
- [ ] 工具调用成功

---

**祝使用愉快！** 🎉

如有问题，请查看错误信息并参考本文档的"解决常见问题"部分。
