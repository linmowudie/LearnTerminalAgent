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

API 密钥**不建议**直接写在配置文件中，推荐使用以下方式：

### 方法 1：环境变量（推荐）

```bash
# Linux/macOS
export QWEN_API_KEY="sk-xxxxx"

# Windows PowerShell
$env:QWEN_API_KEY="sk-xxxxx"
```

### 方法 2：.env 文件

在项目根目录创建 `.env` 文件：

```
QWEN_API_KEY=sk-xxxxx
```

### 方法 3：系统环境变量

永久添加到系统环境变量（推荐用于生产环境）。

## 📋 配置加载优先级

LearnTerminalAgent 按以下优先级加载配置：

1. **环境变量**（最高优先级）
2. **config.json 文件**
3. **默认值**（最低优先级）

## 🛠️ 自定义配置

你可以复制 `config.json` 并修改参数：

```bash
cp config/config.json config/my-config.json
```

然后在代码中指定配置文件路径。

## 🔗 相关文档

- [配置指南](../docs/guides/config-guide.md)
- [快速入门](../docs/QUICK_START.md)
- [项目概述](../docs/PROJECT_OVERVIEW.md)
