# LearnTerminalAgent 配置目录

本目录包含 LearnTerminalAgent 的配置文件。

## 📁 文件说明

### config.json

主配置文件，包含 Agent 运行所需的各项配置。

```json
{
  "model_name": "qwen3.5-flash",
  "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "max_tokens": 8000,
  "timeout": 120
}
```

## ⚙️ 配置项说明

| 配置项 | 描述 | 默认值 |
|--------|------|--------|
| `model_name` | LLM 模型名称 | `qwen3.5-flash` |
| `base_url` | API 基础 URL | 阿里云百炼地址 |
| `max_tokens` | 最大 token 数 | `8000` |
| `timeout` | 请求超时时间（秒） | `120` |

## 🔐 API 密钥配置

⚠️ **重要提示**：API 密钥**不建议**直接写在配置文件中，推荐使用以下方式：

### 👍 方法 1：环境变量（推荐）

```bash
# Linux/macOS
export QWEN_API_KEY="sk-xxxxx"

# Windows PowerShell
$env:QWEN_API_KEY="sk-xxxxx"
```

### 📄 方法 2：.env 文件

在项目根目录创建 `.env` 文件：

```bash
# .env 文件内容
QWEN_API_KEY=sk-xxxxx
```

### 🔧 方法 3：系统环境变量

永久添加到系统环境变量（推荐用于生产环境）。

## 📋 配置加载优先级

LearnTerminalAgent 按以下优先级加载配置（从高到低）：

1. **环境变量** - 最高优先级，覆盖所有其他配置
2. **config.json 文件** - 中等优先级
3. **默认值** - 最低优先级，当上述配置不存在时使用

## 🛠️ 自定义配置

你可以复制 `config.json` 并修改参数：

```bash
# 复制配置文件
cp config/config.json config/my-config.json
```

然后在代码中指定配置文件路径。

**示例**：

```python
from learn_agent.config import load_config

# 加载自定义配置文件
config = load_config("config/my-config.json")
```

## 🔗 相关文档

- **[配置指南](../docs/guides/config-guide.md)** - 详细配置说明
- **[快速入门](../docs/guides/quickstart.md)** - 5 分钟上手
- **[项目概述](../docs/PROJECT_OVERVIEW.md)** - 整体架构
