# LearnTerminalAgent 配置指南

详细配置说明和环境变量管理。

## 📋 配置文件位置

### JSON 配置文件

默认位置：`config/config.json`

```json
{
  "agent": {
    "api_key": "",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model_name": "qwen3.5-flash",
    "max_tokens": 8000,
    "timeout": 120,
    "max_iterations": 50
  },
  "security": {
    "dangerous_patterns": [
      "rm -rf /", "sudo", "shutdown", 
      "reboot", "> /dev/", "mkfs", "dd if="
    ]
  },
  "context": {
    "threshold": 50000,
    "keep_recent": 3,
    "auto_compact_enabled": true
  },
  "tasks": {
    "max_items": 20
  },
  "background": {
    "timeout": 300
  },
  "team": {
    "poll_interval": 5,
    "idle_timeout": 60
  },
  "worktree": {
    "enabled": true,
    "base_ref": "HEAD"
  }
}
```

### 环境变量文件

`.env` 文件（推荐）：

```bash
# API 配置
QWEN_API_KEY=sk-your-api-key-here

# 可选配置
MODEL_ID=qwen-max
ANTHROPIC_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
MAX_TOKENS=16000
TIMEOUT=300
```

## 🔧 配置项详解

### Agent 配置

#### api_key (必需)

**类型**: `str`  
**来源**: 环境变量或 JSON  
**优先级**: 环境变量 > JSON 文件

支持的 API Key 类型：
- `QWEN_API_KEY` - 通义千问（推荐）
- `ANTHROPIC_API_KEY` - Anthropic Claude
- `OPENAI_API_KEY` - OpenAI GPT

```python
# 从环境变量加载
config = AgentConfig.from_env()

# 从 JSON 加载（API Key 仍建议用环境变量）
config = AgentConfig.from_json()
```

#### base_url

**类型**: `str`  
**默认**: `"https://dashscope.aliyuncs.com/compatible-mode/v1"`

API 端点 URL：

```json
{
  "agent": {
    "base_url": "https://api.openai.com/v1"  # OpenAI
  }
}
```

#### model_name

**类型**: `str`  
**默认**: `"qwen3.5-flash"`

使用的模型名称：

```json
{
  "agent": {
    "model_name": "qwen-max"     // 通义千问最强
  }
}
```

常用模型：
- `qwen3.5-flash` - 快速、经济
- `qwen-max` - 最强能力
- `claude-3-opus` - Claude 最强
- `gpt-4-turbo` - GPT-4 版本

#### max_tokens

**类型**: `int`  
**默认**: `8000`

单次响应最大 token 数：

```json
{
  "agent": {
    "max_tokens": 16000  // 增加输出长度
  }
}
```

#### timeout

**类型**: `int`  
**默认**: `120` (秒)

工具执行超时时间：

```json
{
  "agent": {
    "timeout": 300  // 5 分钟
  }
}
```

#### max_iterations

**类型**: `int`  
**默认**: `50`

Agent 循环最大迭代次数：

```json
{
  "agent": {
    "max_iterations": 100  // 复杂任务
  }
}
```

### 安全配置

#### dangerous_patterns

**类型**: `List[str]`  
**默认**: `["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/", "mkfs", "dd if="]`

阻止的危险命令模式：

```json
{
  "security": {
    "dangerous_patterns": [
      "rm -rf /",
      "sudo",
      "your-custom-pattern"
    ]
  }
}
```

### 上下文压缩配置

#### threshold

**类型**: `int`  
**默认**: `50000`

触发自动压缩的 token 阈值：

```json
{
  "context": {
    "threshold": 80000  // 提高阈值
  }
}
```

#### keep_recent

**类型**: `int`  
**默认**: `3`

保留最近的工具结果数量：

```json
{
  "context": {
    "keep_recent": 5  // 保留更多上下文
  }
}
```

#### auto_compact_enabled

**类型**: `bool`  
**默认**: `true`

是否启用自动压缩：

```json
{
  "context": {
    "auto_compact_enabled": false  // 禁用自动压缩
  }
}
```

### 任务管理配置

#### max_items

**类型**: `int`  
**默认**: `20`

TodoWrite 最大任务数：

```json
{
  "tasks": {
    "max_items": 50  // 增加任务限制
  }
}
```

### 后台任务配置

#### timeout

**类型**: `int`  
**默认**: `300` (秒)

后台任务超时时间：

```json
{
  "background": {
    "timeout": 600  // 10 分钟
  }
}
```

### 团队配置

#### poll_interval

**类型**: `int`  
**默认**: `5` (秒)

队友轮询间隔：

```json
{
  "team": {
    "poll_interval": 10  // 降低频率
  }
}
```

#### idle_timeout

**类型**: `int`  
**默认**: `60` (秒)

队友空闲超时：

```json
{
  "team": {
    "idle_timeout": 120  // 延长等待
  }
}
```

### Worktree 配置

#### enabled

**类型**: `bool`  
**默认**: `true`

是否启用 worktree 功能：

```json
{
  "worktree": {
    "enabled": false  // 禁用 worktree
  }
}
```

#### base_ref

**类型**: `str`  
**默认**: `"HEAD"`

创建 worktree 的基础分支：

```json
{
  "worktree": {
    "base_ref": "main"  // 基于 main 分支
  }
}
```

## 🎯 配置使用示例

### 开发环境配置

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
  }
}
```

### 生产环境配置

```json
{
  "agent": {
    "model_name": "qwen-max",
    "max_tokens": 16000,
    "timeout": 300,
    "max_iterations": 100
  },
  "security": {
    "dangerous_patterns": [
      "rm -rf /", "sudo", "shutdown",
      "reboot", "> /dev/", "mkfs", "dd if=",
      "curl.*\\|.*sh", "wget.*\\|.*sh"
    ]
  },
  "context": {
    "threshold": 80000,
    "keep_recent": 5
  },
  "tasks": {
    "max_items": 50
  }
}
```

### 测试环境配置

```json
{
  "agent": {
    "model_name": "qwen3.5-flash",
    "max_tokens": 4000,
    "timeout": 60,
    "max_iterations": 30
  },
  "context": {
    "threshold": 30000,
    "auto_compact_enabled": false
  }
}
```

## 🔍 配置加载顺序

配置加载优先级（从高到低）：

1. **代码中显式设置**
   ```python
   config = AgentConfig(max_tokens=20000)
   ```

2. **环境变量**
   ```bash
   export QWEN_API_KEY="..."
   ```

3. **JSON 配置文件**
   ```json
   {"agent": {"max_tokens": 8000}}
   ```

4. **默认值**
   ```python
   @dataclass
   class AgentConfig:
       max_tokens: int = 8000  # 默认值
   ```

## 💾 配置管理 API

### 从环境变量加载

```python
from learn_agent.config import AgentConfig

config = AgentConfig.from_env()
```

### 从 JSON 加载

```python
config = AgentConfig.from_json("path/to/config.json")
```

### 保存到 JSON

```python
config.save_to_json("path/to/config.json")
```

### 验证配置

```python
try:
    config.validate()
    print("✓ 配置有效")
except ValueError as e:
    print(f"✗ 配置错误：{e}")
```

### 打印配置信息

```python
config.print_info()
```

输出：
```
============================================================
LearnTerminalAgent 配置
============================================================
✓ 模型：qwen3.5-flash
✓ Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
✓ API Key: sk-xxxxx...xxxxx
✓ Max Tokens: 8000
✓ Timeout: 120s
============================================================
```

## 🐛 常见问题

### Q1: API Key 不生效？

**检查清单**:
1. 确保 `.env` 文件存在
2. 检查 API Key 名称正确（`QWEN_API_KEY`）
3. 重启 Python 进程
4. 检查 API Key 格式（无多余空格）

### Q2: 配置文件找不到？

默认路径是相对于包位置的，建议：
```python
# 使用绝对路径
config = AgentConfig.from_json("/absolute/path/config.json")
```

### Q3: 配置不生效？

检查加载顺序，后加载的配置会覆盖先前的：
```python
# ❌ 错误：from_json 会覆盖 from_env
config = AgentConfig.from_env()
config = AgentConfig.from_json()

# ✅ 正确：JSON 优先
config = AgentConfig.from_json()
```

## 📚 最佳实践

1. **敏感信息用环境变量**: API Key 不要放在 JSON 中
2. **版本控制排除 .env**: 添加到 `.gitignore`
3. **提供配置模板**: `.env.example` 供参考
4. **环境分离**: 开发/测试/生产使用不同配置
5. **定期审查**: 检查和更新安全配置

---

**下一步**: [快速入门](quickstart.md) →
