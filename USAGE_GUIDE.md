# LearnTerminalAgent 使用指南

## 🚀 快速启动方法

### 方法 1：使用启动脚本（最简单）✅

在项目根目录运行：

```bash
# Windows PowerShell / CMD
python run_agent.py

# 或指定工作空间
python run_agent.py F:\ProjectCode\MyProject
```

**优点**：
- ✅ 无需配置环境变量
- ✅ 在任何目录都能运行
- ✅ 自动处理路径问题

### 方法 2：直接运行 Python 文件

```bash
python F:\ProjectCode\LearnTerminalAgent\src\learn_agent\main.py [工作空间路径]
```

**示例**：
```bash
# 在 MemoryWords 目录
cd F:\ProjectCode\MemoryWords
python F:\ProjectCode\LearnTerminalAgent\src\learn_agent\main.py F:\ProjectCode\LearnTerminalAgent
```

### 方法 3：安装为系统包（推荐长期使用）

```bash
# 进入项目目录
cd F:\ProjectCode\LearnTerminalAgent

# 可编辑安装
pip install -e .

# 安装后可以在任意位置运行
learn-agent  # 使用命令行工具
# 或
python -m learn_agent.main  # 使用模块方式
```

### 方法 4：设置 PYTHONPATH（临时）

```powershell
# PowerShell
$env:PYTHONPATH = "F:\ProjectCode\LearnTerminalAgent\src"
python -m learn_agent.main F:\ProjectCode\LearnTerminalAgent
```

```bash
# Linux/Mac
export PYTHONPATH=/path/to/LearnTerminalAgent/src
python -m learn_agent.main /path/to/workspace
```

## 💡 常见错误解决

### 错误 1：ModuleNotFoundError: No module named 'learn_agent'

**原因**：Python 找不到 `learn_agent` 模块

**解决方法**：

1. **使用启动脚本**（推荐）：
   ```bash
   python run_agent.py
   ```

2. **或者添加路径到 PYTHONPATH**：
   ```powershell
   $env:PYTHONPATH = "F:\ProjectCode\LearnTerminalAgent\src"
   ```

3. **或者直接运行 main.py**：
   ```bash
   python F:\ProjectCode\LearnTerminalAgent\src\learn_agent\main.py
   ```

### 错误 2：配置文件找不到

**原因**：在非项目目录运行时，配置文件路径不对

**解决方法**：
- 使用启动脚本会自动处理
- 或者确保 config.json 在正确位置

## 📝 使用示例

### 示例 1：在当前目录工作

```bash
# 假设你在 F:\ProjectCode\MemoryWords
cd F:\ProjectCode\MemoryWords

# 运行启动脚本
python F:\ProjectCode\LearnTerminalAgent\run_agent.py

# 现在工作空间就是 F:\ProjectCode\MemoryWords
# LLM 只能访问这个目录的文件
```

### 示例 2：指定工作空间

```bash
# 在任意位置
python F:\ProjectCode\LearnTerminalAgent\run_agent.py F:\ProjectCode\AnotherProject

# 工作空间设置为 AnotherProject
```

### 示例 3：使用批处理脚本

```batch
REM 创建快捷方式
copy F:\ProjectCode\LearnTerminalAgent\run.bat C:\Tools\

REM 然后在任意位置使用
run.bat F:\ProjectCode\MyProject
```

## 🔧 配置说明

### API Key 配置

在项目目录创建 `.env` 文件：

```bash
QWEN_API_KEY=sk-your-api-key-here
```

或者修改配置文件 `src/learn_agent/config.json`：

```json
{
  "agent": {
    "api_key": "your-api-key",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model_name": "qwen3.5-flash"
  }
}
```

### 工作空间说明

工作空间是 LLM 可以访问的唯一目录范围：

- ✅ LLM 可以读取/写入工作空间内的任何文件
- ❌ LLM 无法访问工作空间外的文件
- ✅ 所有命令都在工作空间根目录执行
- ❌ 尝试访问外部文件会返回清晰的错误

## 📋 完整工作流程

1. **准备项目目录**
   ```bash
   cd F:\ProjectCode\MyProject
   ```

2. **启动 Agent**
   ```bash
   python F:\ProjectCode\LearnTerminalAgent\run_agent.py
   ```

3. **开始工作**
   ```
   ✓ 工作空间已设置：F:\ProjectCode\MyProject
   
   LearnTerminalAgent >> 创建一个 hello.txt 文件
   ```

4. **LLM 在工作空间内操作**
   - 可以：创建、读取、修改项目文件
   - 不可以：访问系统文件或其他项目

## 🎯 最佳实践

### 1. 为每个项目创建独立的工作空间

```bash
# 项目 A
python run_agent.py F:\ProjectA

# 项目 B  
python run_agent.py F:\ProjectB
```

### 2. 使用启动脚本

始终使用 `run_agent.py` 而不是直接调用模块，避免路径问题。

### 3. 检查工作空间

启动时会显示：
```
✓ 工作空间已设置：F:\ProjectCode\MyProject
```

确认这是你想要工作的目录。

### 4. 理解限制

记住 LLM 只能在工作空间内操作，这是安全特性，不是 bug。

## 🆘 获取帮助

```bash
# 启动后输入
/help

# 查看可用命令
```

## 📖 更多信息

- [工具使用指南](docs/guides/tools.md)
- [快速入门](docs/QUICK_START.md)
- [工作空间示例](docs/WORKSPACE_EXAMPLES.md)
