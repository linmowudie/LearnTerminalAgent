# LearnTerminalAgent 命令行工具

本目录包含 LearnTerminalAgent 的可执行脚本。

## 📁 文件说明

### learn-agent

可执行的 Python 脚本，用于启动 LearnTerminalAgent CLI。

```bash
# 直接运行脚本
./bin/learn-agent
```

或添加到系统 PATH 后直接运行：

```bash
# 使用命令
learn-agent
```

## 🔧 安装方式

### 👍 方法 1：使用 pip 安装（推荐）

```bash
# 在项目根目录执行
pip install -e .
```

安装后会自动创建 `learn-agent` 命令。

### 💻 方法 2：直接运行脚本

```bash
python bin/learn-agent
```

### 🚀 方法 3：使用 python -m

```bash
python -m learn_agent.main
```

## 💡 使用示例

```bash
# 启动交互式会话
learn-agent

# 或直接运行 Python 脚本
python src/learn_agent/main.py
```

**说明**：推荐使用 `learn-agent` 命令，它会自动配置好所有环境变量和路径。

## 📝 说明

- 该脚本通过 [pyproject.toml](../pyproject.toml) 中的 `[project.scripts]` 配置自动安装
- 指向的入口函数是 `learn_agent.main:main`
- 在 Windows 上可能需要使用 PowerShell 或 CMD 运行

## 🔗 相关文档

- **[快速入门](../docs/guides/quickstart.md)** - 5 分钟上手指南
- **[使用指南](../docs/guides/README.md)** - 详细使用说明
- **[工具说明](../docs/guides/tools.md)** - 所有工具完整手册
