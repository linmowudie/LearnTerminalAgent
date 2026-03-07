# 工作空间沙箱使用示例

## 🎯 核心功能

工作空间沙箱确保 LLM 只能访问指定目录及其子目录，就像代码编辑器打开特定文件夹一样。

## 📖 使用方式

### 方式 1：在当前目录运行（最常用）

```bash
# 进入你的项目目录
cd F:\ProjectCode\MyProject

# 启动 Agent
python -m learn_agent.main

# 此时工作空间自动设置为 F:\ProjectCode\MyProject
```

**输出示例**：
```
✓ 工作空间已设置：F:\ProjectCode\MyProject

============================================================
LearnTerminalAgent - LangChain 实现的智能 Agent
============================================================

LearnTerminalAgent >> 
```

### 方式 2：直接指定工作空间路径

```bash
# 在任意位置启动，指定工作空间
python -m learn_agent.main F:\ProjectCode\AnotherProject

# 输出会显示：
📁 使用工作空间：F:\ProjectCode\AnotherProject

✓ 工作空间已设置：F:\ProjectCode\AnotherProject
```

## ✅ 允许的操作

以下操作在工作空间内是允许的：

### 1. 读取文件
```python
# 读取当前目录的文件
agent.run("读取 README.md 的内容")
# ✅ 成功

# 读取子目录的文件
agent.run("读取 src/main.py 的内容")
# ✅ 成功
```

### 2. 写入文件
```python
# 创建新文件
agent.run("创建一个 test.txt 文件，写入 Hello World")
# ✅ 成功

# 创建嵌套目录结构
agent.run("创建 src/utils/helpers.py 文件")
# ✅ 成功（自动创建父目录）
```

### 3. 列出目录
```python
agent.run("列出当前目录的所有文件")
# ✅ 显示工作空间根目录内容

agent.run("查看 src 目录下有哪些文件")
# ✅ 显示 src 子目录内容
```

### 4. 执行命令
```python
# 所有命令都在工作空间根目录执行
agent.run("运行 python --version")
# ✅ 成功

agent.run("运行 pip list")
# ✅ 成功
```

## ❌ 禁止的操作

以下操作会被阻止并返回错误：

### 1. 访问工作空间外的文件
```python
# 尝试读取系统文件
agent.run("读取 C:/Windows/System32/drivers/etc/hosts")
# ❌ 错误：路径越界

# 尝试读取上级目录
agent.run("读取 ../secret.txt 的内容")
# ❌ 错误：路径越界
```

**错误信息示例**：
```
Error: 路径越界：C:/Windows/System32/drivers/etc/hosts
工作空间：F:\ProjectCode\MyProject
目标路径：C:\Windows\System32\drivers\etc\hosts
```

### 2. 写入工作空间外
```python
# 尝试写入临时目录
agent.run("在 C:/tmp/evil.txt 写入恶意内容")
# ❌ 错误：路径越界
```

### 3. 危险命令
```python
# 即使在工作空间内，危险命令也会被阻止
agent.run("运行 sudo rm -rf /")
# ❌ 错误：Dangerous command 'sudo' blocked
```

## 🔍 实际使用场景

### 场景 1：项目开发
```bash
# 在项目目录启动
cd F:\ProjectCode\WebApp
python -m learn_agent.main

# 现在可以让 Agent 帮你：
- "创建一个新的 Flask 路由"
- "修改 app.py 中的数据库配置"
- "运行测试用例"
- "查看 requirements.txt 的依赖"

# 所有这些操作都限制在 WebApp 目录内
```

### 场景 2：学习练习
```bash
# 为每个练习创建独立目录
mkdir F:\LearnPython\exercise_01
cd F:\LearnPython\exercise_01
python -m learn_agent.main

# Agent 只能在这个练习目录内操作
# 不会影响其他练习或系统文件
```

### 场景 3：代码审查
```bash
# 只让 Agent 查看特定项目
cd F:\CodeReview\project-a
python -m learn_agent.main

# 让 Agent 分析代码：
- "分析 src 目录的代码结构"
- "找出所有的 Python 文件"
- "检查是否有硬编码的密码"

# Agent 无法访问项目外的任何文件
```

## 🛡️ 安全机制

### 1. 路径验证
所有文件路径都会经过以下验证：
1. 转换为绝对路径
2. 检查是否在工作空间内
3. 解析符号链接防止绕过

### 2. 命令执行隔离
所有 shell 命令都在工作空间根目录执行：
```python
# 即使用户说 "cd .."，命令仍然在工作空间根目录执行
agent.run("cd .. && ls")
# 实际上还是在原工作空间根目录
```

### 3. 清晰的错误提示
越界操作会返回详细的错误信息：
- 请求的路径
- 工作空间范围
- 解析后的实际路径

这有助于理解为什么操作被拒绝。

## 📝 注意事项

1. **工作空间一旦设置就不可更改**
   - 需要重启 Agent 来切换工作空间
   
2. **相对路径基于启动时的目录**
   - 建议使用绝对路径避免混淆
   
3. **符号链接会被解析**
   - 通过符号链接访问工作空间外也会被阻止

4. **不影响系统命令**
   - 可以正常运行 python、pip 等命令
   - 只是工作目录被限制

## 🎓 总结

工作空间沙箱提供了：
- ✅ **安全性**：防止意外修改系统文件
- ✅ **隔离性**：每个项目独立操作
- ✅ **可控性**：清晰的边界和错误提示
- ✅ **便利性**：像 IDE 一样打开文件夹即可工作

使用非常简单：
```bash
cd 你的项目目录
python -m learn_agent.main
```

就这么简单！LLM 现在只能在你的项目目录内工作了。
