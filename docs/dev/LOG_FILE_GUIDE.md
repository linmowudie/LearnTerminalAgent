# 日志系统使用指南

## 📋 概述

日志系统已升级为 **DEBUG 级别**，支持灵活的配置化管理。所有日志自动输出到 `logs` 目录，不在终端显示。

### 🎉 最新版本特性（2026-03-10）

- ✅ **默认 DEBUG 级别** - 所有 logger 默认输出详细调试信息
- ✅ **配置化支持** - 可通过 `config/config.json` 自定义各模块日志级别
- ✅ **动态调整** - 支持运行时动态修改日志级别
- ✅ **增强日志覆盖** - Agent 核心、工具调用等关键路径添加详细日志

---

## 🎯 核心特性

### ✅ 自动文件日志

- **无需手动启用** - 初始化时自动创建日志文件
- **安静模式** - 终端无任何日志输出，保持界面清爽
- **自动分类** - 不同模块输出到不同的日志文件
- **时间戳命名** - 日志文件名包含时间戳，便于查找

### 📁 日志文件结构

```
logs/
├── agent_20260307_120000.log      # Agent 核心日志
├── tools_20260307_120000.log      # 工具执行日志
├── workspace_20260307_120000.log  # 工作空间日志
└── config_20260307_120000.log     # 配置日志
```

---

## 🚀 使用方法

### 默认使用（推荐）

```python
from src.learn_agent.logger import logger_agent, logger_tools

# 直接使用，日志自动输出到 logs 目录
logger_agent.info("Agent 启动")
logger_tools.warning("工具调用警告")
```

### 查看日志文件

```bash
# Windows PowerShell
Get-ChildItem logs\*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 5

# 或使用资源管理器直接打开
explorer logs
```

---

## 📝 日志格式

### 文件格式

```plaintext
2026-03-10 15:18:56 [DEBUG] Agent: [工具执行] 开始执行：list_directory
2026-03-10 15:18:56 [DEBUG] Agent:   - 参数：{'path': '.'}
2026-03-10 15:18:57 [INFO] Agent: [工具执行] 完成：list_directory
2026-03-10 15:18:57 [DEBUG] Agent:   - 结果预览：['file1.txt', 'file2.py']
2026-03-10 15:18:58 [INFO] Workspace: 工作空间已设置：F:\ProjectCode\LearnTerminalAgent
2026-03-10 15:19:00 [WARNING] Agent: ⚠️ 无工具调用
2026-03-10 15:19:01 [ERROR] Tools: 文件未找到：test.txt
```

**说明**：
- DEBUG 日志包含详细的函数调用、参数和返回值
- INFO 日志记录关键业务流程节点
- WARNING 日志提示潜在问题
- ERROR 日志记录错误信息和异常堆栈

### 日志级别

| 级别 | 说明 | 使用场景 |
|------|------|---------|
| DEBUG | 调试信息 | 详细调试数据 |
| INFO | 一般信息 | 正常流程记录 |
| WARNING | 警告信息 | 潜在问题提示 |
| ERROR | 错误信息 | 错误发生记录 |

---

## 🔧 便捷函数

### 按模块记录日志

```python
from src.learn_agent.logger import info, warning, error, debug

# Agent 模块
info("Agent 初始化完成", module='agent')
warning("工具调用失败", module='agent')
error("严重错误", module='agent')

# Tools 模块
info("工具执行成功", module='tools')
error("工具执行失败", module='tools')

# Workspace 模块
info("工作空间已设置", module='workspace')
```

### 日志上下文管理器

```python
from src.learn_agent.logger import log_context

with log_context("加载配置文件"):
    # 自动记录开始和完成
    load_config()
    
# 如果发生异常，会自动记录错误
```

### 性能计时装饰器

```python
from src.learn_agent.logger import timing

@timing
def slow_function():
    time.sleep(1)
    
# 自动记录函数执行耗时
# 输出：slow_function 执行耗时：1.000s
```

---

## ⚙️ 配置选项

### 1. 通过配置文件设置（推荐）

在 `config/config.json` 中添加或修改 `logging` 配置节：

```json
{
  "logging": {
    "default_level": "DEBUG",
    "modules": {
      "agent": "DEBUG",
      "tools": "INFO",
      "workspace": "DEBUG",
      "config": "INFO"
    }
  }
}
```

**配置说明**：
- `default_level`: 全局默认日志级别（DEBUG/INFO/WARNING/ERROR）
- `modules`: 各模块单独配置，支持差异化日志级别
- 配置会在 Agent 启动时自动应用

**示例场景**：
```json
// 开发调试模式 - 所有模块 DEBUG
"logging": {
  "default_level": "DEBUG",
  "modules": {
    "agent": "DEBUG",
    "tools": "DEBUG",
    "workspace": "DEBUG",
    "config": "DEBUG"
  }
}

// 生产运行模式 - 只记录重要信息
"logging": {
  "default_level": "INFO",
  "modules": {
    "agent": "INFO",
    "tools": "WARNING",
    "workspace": "INFO",
    "config": "INFO"
  }
}
```

### 2. 运行时动态调整

```python
import logging
from src.learn_agent.logger import set_log_level

# 设置为 DEBUG 级别（记录更详细）
set_log_level(logging.DEBUG)

# 设置为 WARNING 级别（只记录警告和错误）
set_log_level(logging.WARNING)
```

**注意**：运行时调整的优先级高于配置文件，会立即生效。

### 自定义日志文件路径

```python
from src.learn_agent.logger import setup_logger

# 指定日志文件路径
custom_logger = setup_logger('MyModule', logging.INFO, log_file='custom/my_custom.log')

custom_logger.info("这条日志会输出到 custom/my_custom.log")
```

---

## 📊 日志管理

### 清理旧日志

```bash
# Windows PowerShell - 删除 7 天前的日志
Get-ChildItem logs\*.log | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } | Remove-Item

# Linux/Mac - 删除 7 天前的日志
find logs -name "*.log" -mtime +7 -delete
```

### 查看最新日志

```bash
# Windows PowerShell - 查看最新的日志文件
Get-ChildItem logs\*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content

# Linux/Mac - 实时查看最新日志
tail -f logs/agent_*.log
```

---

## 🐛 故障排查

### 问题 1: 找不到日志文件

**检查 logs 目录**:
```bash
# Windows
dir logs

# Linux/Mac
ls -la logs
```

**预期结果**: 应该看到多个 `.log` 文件

### 问题 2: 日志内容为空

**可能原因**: 日志级别设置过高  
**解决方法**: 
```python
set_log_level(logging.DEBUG)  # 降低级别查看更多内容
```

### 问题 3: 终端有日志输出

**原因**: 可能有其他地方配置了控制台处理器  
**解决**: 检查代码中是否有 `StreamHandler` 的使用

---

## 💡 最佳实践

### ✅ 推荐做法

1. **使用便捷函数** - `info()`, `warning()`, `error()`
2. **合理选择日志级别** - 不要全部用 INFO
3. **提供足够的上下文** - 包含操作、对象、结果
4. **定期清理旧日志** - 避免占用过多磁盘空间

### ❌ 避免的做法

1. **不要在终端打印日志** - 使用 logger 而不是 print
2. **不要记录敏感信息** - 如 API Key、密码等
3. **不要过度日志** - 避免日志文件过大
4. **不要忽略 ERROR** - 及时处理错误日志

---

## 📖 示例代码

### 完整示例

```python
from src.learn_agent.logger import (
    logger_agent, 
    logger_tools,
    info, 
    warning, 
    error,
    log_context,
    timing
)

# 直接使用 logger 对象
logger_agent.info("Agent 启动")

# 使用便捷函数
info("配置加载成功", module='agent')
warning("工具调用延迟", module='tools')

# 使用上下文管理器
with log_context("处理用户请求"):
    process_request()

# 使用性能计时
@timing
def analyze_data():
    # 自动记录执行时间
    pass
```

---

## 🔗 相关文档

- [`LOGGING_GUIDE.md`](LOGGING_GUIDE.md) - 原始日志指南
- [`LOGGING_SUMMARY.md`](LOGGING_SUMMARY.md) - 日志系统总结
- [`src/learn_agent/logger.py`](../src/learn_agent/logger.py) - 源码实现

---

## 📞 常见问题

### Q: 为什么终端看不到日志了？

A: 这是设计决策。所有日志输出到 `logs` 目录，保持终端清爽。如需查看日志：
```bash
# 打开日志目录
explorer logs  # Windows
open logs      # Mac
xdg-open logs  # Linux
```

### Q: 如何实时查看日志？

A: 使用以下命令：
```bash
# Linux/Mac
tail -f logs/agent_*.log

# Windows PowerShell
Get-Content logs\agent_*.log -Wait -Tail 50
```

### Q: 日志文件太大怎么办？

A: 建议：
1. 调整日志级别：`set_log_level(logging.WARNING)`
2. 定期清理旧日志
3. 使用日志轮转（需额外配置）

---

**版本**: v3.0 (安静模式)  
**更新日期**: 2026-03-07
