# 配置文件查找逻辑说明

## 📁 配置文件位置

LearnTerminalAgent 现在支持**多个配置文件位置**，按优先级查找：

### 优先级顺序

1. **命令行指定的路径**（如果通过参数传递）
2. **`./config/config.json`** (项目根目录的 config 文件夹) ✨ **推荐**
3. **`src/learn_agent/config.json`** (源代码目录)

## 🔍 查找逻辑

```python
possible_paths = [
    Path(__file__).parent.parent.parent / "config" / "config.json",  # ./config/config.json
    Path(__file__).parent / "config.json",  # src/learn_agent/config.json
]

for path in possible_paths:
    if path.exists():
        config_path = path
        break
```

## 📂 项目结构示例

```
LearnTerminalAgent/
├── config/                          # ✨ 推荐的配置文件位置
│   └── config.json                  # 主配置文件
├── src/
│   └── learn_agent/
│       ├── config.py                # 配置加载代码
│       └── config.json              # 备选配置文件（通常不需要）
├── run_agent.py                     # 启动脚本
└── ...
```

## 🎯 日志输出示例

### 成功找到配置文件

```
2026-03-07 01:10:25 [INFO] Config: 找到配置文件：F:\ProjectCode\LearnTerminalAgent\config\config.json
2026-03-07 01:10:25 [INFO] Config: 从 JSON 加载配置：F:\ProjectCode\LearnTerminalAgent\config\config.json
2026-03-07 01:10:25 [INFO] Config: 配置加载成功：F:\ProjectCode\LearnTerminalAgent\config\config.json
[OK] Loaded config from: F:\ProjectCode\LearnTerminalAgent\config\config.json
```

### 未找到配置文件（回退到环境变量）

```
2026-03-07 01:10:25 [DEBUG] Config: 所有可能的配置文件都不存在
Warning: Config file not found in common locations.
Falling back to environment variables.
```

## ⚙️ 配置文件格式

```json
{
  "agent": {
    "api_key": "sk-your-api-key-here",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model_name": "qwen3.5-flash",
    "max_tokens": 8000,
    "timeout": 120,
    "max_iterations": 50
  },
  "security": {
    "dangerous_patterns": [
      "rm -rf /",
      "sudo",
      "shutdown",
      "reboot",
      "> /dev/",
      "mkfs",
      "dd if="
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

## 🔧 最小配置文件

最简单的配置只需要 API Key：

```json
{
  "agent": {
    "api_key": "sk-your-api-key-here"
  }
}
```

其他配置项都会使用默认值。

## 🛠️ 使用环境变量覆盖

即使使用了 JSON 配置文件，仍然可以用环境变量覆盖特定值：

```bash
# PowerShell
$env:QWEN_API_KEY="sk-another-key"
python run_agent.py

# 这会覆盖 config.json 中的 api_key
```

## 📝 最佳实践

### ✅ 推荐做法

1. **将 `config/config.json` 添加到 `.gitignore`**
   ```bash
   # .gitignore
   config/config.json
   ```

2. **保留 `config.json.example` 作为模板**
   ```json
   {
     "agent": {
       "api_key": "your-api-key-here"
     }
   }
   ```

3. **在团队文档中说明配置方法**
   ```markdown
   ## 配置步骤
   
   1. 复制 `config/config.json.example` 为 `config/config.json`
   2. 填入你的 API Key
   3. 运行 `python run_agent.py`
   ```

### ❌ 避免的做法

1. **不要将包含真实 API Key 的配置文件提交到 Git**
2. **不要硬编码敏感信息在源代码中**

## 🐛 故障排查

### 问题 1：配置文件未被找到

**检查清单**：
- [ ] 确认文件路径：`config/config.json`
- [ ] 确认文件存在：`ls config/config.json`
- [ ] 检查文件名：是 `config.json` 不是 `Config.json`（区分大小写）

### 问题 2：加载了错误的配置文件

**解决方法**：
查看日志输出，确认找到的配置文件路径：
```
[INFO] Config: 找到配置文件：...
```

如果想强制使用特定路径，可以修改代码或移动配置文件位置。

### 问题 3：API Key 无效

**检查步骤**：
1. 确认 JSON 格式正确
2. 确认 API Key 没有多余的空格或引号
3. 尝试使用环境变量测试

## 📖 相关文档

- [`LOGGING_GUIDE.md`](LOGGING_GUIDE.md) - 日志系统使用指南
- [`QUICK_START.md`](QUICK_START.md) - 快速入门
- [`.env.example`](../.env.example) - 环境变量示例

---

**配置文件查找功能已完善！** 🎉

现在 LearnTerminalAgent 会自动在合理的位置查找配置文件，无需手动指定路径。
