# 日志系统使用指南

## 📋 概述

LearnTerminalAgent 现在配备了完善的日志系统，支持：

- ✅ **多级别日志**：DEBUG, INFO, WARNING, ERROR, CRITICAL
- ✅ **彩色终端输出**：不同级别不同颜色，便于识别
- ✅ **文件日志**（可选）：持久化保存日志
- ✅ **性能计时**：自动记录函数执行时间
- ✅ **上下文追踪**：记录操作开始/完成/失败

## 🚀 快速开始

### 1. 导入日志模块

```python
from learn_agent.logger import (
    logger_agent,      # Agent 核心日志
    logger_tools,      # 工具执行日志
    logger_workspace,  # 工作空间日志
    logger_config,     # 配置日志
    
    # 便捷函数
    debug, info, warning, error,
    
    # 高级功能
    log_context, timing,
    enable_file_logging
)
```

### 2. 基本使用

```python
from learn_agent.logger import info, error

# 记录信息
info("程序启动成功")

# 记录错误
error("发生了一个错误")
```

### 3. 指定模块

```python
info("工具加载完成", module='tools')
error("路径验证失败", module='workspace')
```

## 📖 详细用法

### 3.1 直接使用 Logger

```python
from learn_agent.logger import logger_agent, logger_tools

# Agent 日志
logger_agent.info("Agent 初始化完成")
logger_agent.debug("调试信息")
logger_agent.warning("警告信息")
logger_agent.error("错误信息")

# 工具日志
logger_tools.info("工具执行开始")
```

### 3.2 使用便捷函数

```python
from learn_agent.logger import debug, info, warning, error

# 默认记录到 agent 模块
info("用户请求已处理")

# 指定模块
info("配置文件已加载", module='config')
debug("路径解析中...", module='workspace')
```

### 3.3 日志上下文管理器

自动记录操作的开始、完成和失败：

```python
from learn_agent.logger import log_context

with log_context("加载配置文件"):
    # 这里执行加载配置的代码
    load_config()
    
# 输出:
# [INFO] Agent: 开始：加载配置文件
# [INFO] Agent: 完成：加载配置文件

# 如果发生异常:
# [ERROR] Agent: 失败：加载配置文件 - FileNotFoundError
```

### 3.4 性能计时装饰器

自动记录函数执行时间：

```python
from learn_agent.logger import timing

@timing
def slow_function():
    import time
    time.sleep(2)
    
slow_function()
# 输出：[INFO] Agent: slow_function 执行耗时：2.001s
```

## 🔧 配置

### 启用文件日志

```python
from learn_agent.logger import enable_file_logging

# 启用文件日志（默认保存到 logs/ 目录）
enable_file_logging()

# 指定日志目录
enable_file_logging(log_dir="my_logs")
```

文件命名格式：`agent_YYYYMMDD_HHMMSS.log`

### 设置日志级别

```python
from learn_agent.logger import set_log_level
import logging

# 设置为 DEBUG 级别（显示所有日志）
set_log_level(logging.DEBUG)

# 设置为 WARNING 级别（只显示警告和错误）
set_log_level(logging.WARNING)
```

## 📊 日志输出示例

### 终端彩色输出

```
2026-03-07 01:00:00 [INFO] Workspace: 工作空间已设置：F:\ProjectCode\PersionalProject
2026-03-07 01:00:01 [DEBUG] Workspace: 解析路径：hello.py
2026-03-07 01:00:01 [DEBUG] Workspace: 相对路径，解析为：F:\ProjectCode\PersionalProject\hello.py
2026-03-07 01:00:01 [DEBUG] Workspace: 路径验证通过
2026-03-07 01:00:02 [INFO] Tools: 执行 bash 命令：python hello.py
2026-03-07 01:00:03 [INFO] Tools: bash 命令执行完成，输出 15 字符
2026-03-07 01:00:03 [INFO] Agent: 任务完成
```

### 错误日志

```
2026-03-07 01:00:00 [ERROR] Workspace: 路径越界：C:/Windows/System32/drivers/etc/hosts -> C:\Windows\System32\drivers\etc\hosts
2026-03-07 01:00:01 [ERROR] Tools: bash 命令执行失败：TimeoutExpired
```

## 🎯 实际应用场景

### 场景 1：追踪工具调用

```python
# 在 tools.py 中
from .logger import logger_tools

@tool
def read_file(path: str, limit: Optional[int] = None) -> str:
    logger_tools.info(f"读取文件：{path}")
    try:
        # ... 文件读取逻辑
        logger_tools.debug(f"成功读取 {len(content)} 字符")
        return content
    except Exception as e:
        logger_tools.error(f"读取文件失败：{e}")
        raise
```

### 场景 2：调试 Agent 循环

```python
# 在 agent.py 中
from .logger import logger_agent

def run(self, query: str, verbose: bool = True):
    logger_agent.info(f"收到用户查询：{query}")
    
    while True:
        logger_agent.debug(f"迭代次数：{self.iteration_count}")
        
        # LLM 调用
        response = self.llm_with_tools.invoke(self.messages)
        logger_agent.debug(f"LLM 响应：{response.content[:100]}...")
        
        if not response.tool_calls:
            logger_agent.info("无工具调用，返回最终响应")
            return response.content
        
        # 工具执行
        for tool_call in response.tool_calls:
            logger_agent.info(f"执行工具：{tool_call['name']}")
            result = self._execute_tool(tool_call)
            logger_agent.debug(f"工具结果：{result[:100]}...")
```

### 场景 3：工作空间路径追踪

```python
# 在 workspace.py 中
from .logger import logger_workspace

def resolve_path(self, path: str) -> Path:
    logger_workspace.debug(f"解析路径：{path}")
    
    path_obj = Path(path)
    
    if not path_obj.is_absolute():
        abs_path = self.root / path_obj
        logger_workspace.debug(f"相对路径 -> {abs_path}")
    else:
        abs_path = path_obj.resolve()
        logger_workspace.debug(f"绝对路径 -> {abs_path}")
    
    try:
        abs_path.relative_to(self.root)
        logger_workspace.debug("路径验证通过")
        return abs_path
    except ValueError:
        logger_workspace.error(f"路径越界：{path}")
        raise
```

## 📁 日志文件位置

默认情况下，日志文件保存在：

```
logs/
├── agent_20260307_010000.log
├── agent_20260307_011500.log
└── agent_20260307_023000.log
```

每个日志文件包含完整的会话记录。

## 🎨 颜色说明

- **青色 (DEBUG)**: 详细调试信息
- **绿色 (INFO)**: 正常流程信息
- **黄色 (WARNING)**: 警告信息
- **红色 (ERROR)**: 错误信息
- **紫色 (CRITICAL)**: 严重错误

## 💡 最佳实践

### 1. 选择合适的日志级别

```python
# 详细调试信息 → DEBUG
logger.debug(f"变量值：x={x}, y={y}")

# 正常流程信息 → INFO
logger.info("配置文件加载成功")

# 潜在问题 → WARNING  
logger.warning("配置文件不存在，使用默认值")

# 错误情况 → ERROR
logger.error(f"数据库连接失败：{e}")

# 严重故障 → CRITICAL
logger.critical("系统资源耗尽，无法继续运行")
```

### 2. 提供有意义的日志消息

```python
# ❌ 不好的日志
logger.info("开始处理")
logger.info("完成")

# ✅ 好的日志
logger.info(f"开始处理用户请求：user_id={user_id}")
logger.info(f"完成用户数据处理，共 {count} 条记录")
```

### 3. 记录异常堆栈

```python
# ❌ 只记录错误消息
try:
    risky_operation()
except Exception as e:
    logger.error(f"操作失败：{e}")

# ✅ 记录完整堆栈
try:
    risky_operation()
except Exception as e:
    logger.exception(f"操作失败：{e}")  # 自动包含堆栈跟踪
```

## 🔍 调试技巧

### 1. 查看实时日志

```bash
# PowerShell
Get-Content logs/agent_*.log -Tail 50 -Wait

# Linux/Mac
tail -f logs/agent_*.log
```

### 2. 搜索特定错误

```bash
# 查找所有 ERROR 日志
Select-String "ERROR" logs/*.log

# 查找特定模块的日志
Select-String "Workspace:" logs/*.log
```

### 3. 分析性能问题

```bash
# 查找所有耗时记录
Select-String "执行耗时" logs/*.log

# 找出最慢的操作
Select-String "执行耗时" logs/*.log | Sort-Object -Descending
```

## 📝 总结

日志系统是调试和监控的利器：

- ✅ **开发阶段**：使用 DEBUG 级别，详细追踪
- ✅ **生产环境**：使用 INFO 或 WARNING 级别
- ✅ **问题排查**：启用文件日志，保留完整记录
- ✅ **性能优化**：使用 @timing 装饰器找出瓶颈

善用日志，让调试不再困难！🎉
