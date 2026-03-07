# 日志系统实施总结

## 📋 完成的工作

### 1. 创建核心日志模块 ✅

**文件**: `src/learn_agent/logger.py`

**功能**:
- ✅ 多级别日志（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- ✅ 彩色终端输出（不同级别不同颜色）
- ✅ 文件日志支持（可选启用）
- ✅ 结构化日志格式
- ✅ 便捷函数（debug, info, warning, error）
- ✅ 上下文管理器（log_context）
- ✅ 性能计时装饰器（@timing）

**预定义的 Logger**:
```python
logger_agent      # Agent 核心日志
logger_tools      # 工具执行日志
logger_workspace  # 工作空间日志
logger_config     # 配置日志
```

### 2. 集成到工作空间模块 ✅

**文件**: `src/learn_agent/workspace.py`

**添加的日志点**:
```python
# 初始化工作空间
with log_context(f"初始化工作空间：{workspace_path or '当前目录'}", 'workspace'):
    logger_workspace.info(f"工作空间已设置：{self._workspace_root}")

# 路径解析
logger_workspace.debug(f"解析路径：{path}")
logger_workspace.debug(f"相对路径，解析为：{abs_path}")
logger_workspace.debug(f"路径验证通过")

# 错误追踪
logger_workspace.error(f"路径越界：{path} -> {abs_path}")
```

**效果**:
```
[INFO] Workspace: 开始：初始化工作空间：F:\ProjectCode\PersionalProject
[DEBUG] Workspace: 解析路径：hello.py
[DEBUG] Workspace: 相对路径，解析为：F:\ProjectCode\PersionalProject\hello.py
[DEBUG] Workspace: 路径验证通过
[INFO] Workspace: 工作空间已设置：F:\ProjectCode\PersionalProject
```

### 3. 工具模块集成示例 ✅

**文件**: `src/learn_agent/tools.py`

**导入日志模块**:
```python
from .logger import logger_tools, timing
```

**bash 工具示例**:
```python
@tool
@timing  # 性能计时
def bash(command: str) -> str:
    logger_tools.debug(f"执行 bash 命令：{command}")
    
    try:
        result = subprocess.run(...)
        logger_tools.info(f"bash 命令执行完成，输出 {len(output)} 字符")
        return output
    except subprocess.TimeoutExpired:
        logger_tools.error(f"bash 命令超时：{command}")
        return f"Error: Command timed out"
    except Exception as e:
        logger_tools.error(f"bash 命令执行失败：{e}")
        raise
```

### 4. 创建完整文档 ✅

**文件**: `docs/LOGGING_GUIDE.md`

**内容**:
- ✅ 快速开始指南
- ✅ 详细用法说明
- ✅ 实际应用场景
- ✅ 最佳实践
- ✅ 调试技巧
- ✅ 配置选项

### 5. 测试验证 ✅

**文件**: `test_logging.py`

**测试结果**:
```
✅ 基本日志输出 - 通过
✅ 不同模块日志 - 通过
✅ 上下文管理器 - 通过
✅ 性能计时装饰器 - 通过
✅ 文件日志启用 - 通过
✅ 日志级别设置 - 通过
✅ 工作空间操作日志 - 通过
```

## 🎯 使用示例

### 场景 1：追踪 Agent 执行流程

```python
from learn_agent.logger import logger_agent, log_context

def run(self, query: str):
    with log_context(f"处理用户查询：{query}"):
        logger_agent.info(f"开始 Agent 循环")
        
        while True:
            logger_agent.debug(f"迭代次数：{self.iteration_count}")
            
            response = self.llm_with_tools.invoke(self.messages)
            logger_agent.debug(f"LLM 响应：{response.content[:100]}...")
            
            if not response.tool_calls:
                logger_agent.info("无工具调用，返回最终响应")
                return response.content
            
            for tool_call in response.tool_calls:
                logger_agent.info(f"执行工具：{tool_call['name']}")
                result = self._execute_tool(tool_call)
                logger_agent.debug(f"工具结果：{result[:100]}...")
```

### 场景 2：监控工具性能

```python
from learn_agent.logger import timing, logger_tools

@timing
def execute_tool(tool_name, args):
    logger_tools.info(f"开始执行工具：{tool_name}")
    try:
        result = tool.invoke(args)
        logger_tools.debug(f"工具执行成功")
        return result
    except Exception as e:
        logger_tools.error(f"工具执行失败：{e}")
        raise

# 输出示例:
# [INFO] Tools: 开始执行工具：bash
# [DEBUG] Tools: 工具执行成功
# [INFO] Agent: execute_tool 执行耗时：0.523s
```

### 场景 3：调试路径问题

```python
from learn_agent.logger import logger_workspace

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
        logger_workspace.debug("✓ 路径验证通过")
        return abs_path
    except ValueError:
        logger_workspace.error(f"✗ 路径越界：{path}")
        raise
```

## 📊 日志输出示例

### 完整会话日志

```
2026-03-07 01:00:00 [INFO] Workspace: 开始：初始化工作空间：F:\ProjectCode\PersionalProject
2026-03-07 01:00:00 [INFO] Workspace: 工作空间已设置：F:\ProjectCode\PersionalProject
2026-03-07 01:00:01 [INFO] Agent: 收到用户查询：运行 hello.py
2026-03-07 01:00:01 [DEBUG] Agent: 开始 Agent 循环
2026-03-07 01:00:02 [INFO] Agent: 执行工具：bash
2026-03-07 01:00:02 [DEBUG] Tools: 执行 bash 命令：python hello.py
2026-03-07 01:00:03 [INFO] Tools: bash 命令执行完成，输出 15 字符
2026-03-07 01:00:03 [DEBUG] Agent: 工具结果：Hello, World!
2026-03-07 01:00:03 [INFO] Agent: execute_tool 执行耗时：1.234s
2026-03-07 01:00:04 [INFO] Agent: 无工具调用，返回最终响应
2026-03-07 01:00:04 [INFO] Workspace: 完成：初始化工作空间：F:\ProjectCode\PersionalProject
```

### 错误追踪日志

```
2026-03-07 01:00:00 [DEBUG] Workspace: 解析路径：C:/Windows/System32/drivers/etc/hosts
2026-03-07 01:00:00 [DEBUG] Workspace: 绝对路径 -> C:\Windows\System32\drivers\etc\hosts
2026-03-07 01:00:00 [ERROR] Workspace: 路径越界：C:/Windows/System32/drivers/etc/hosts
2026-03-07 01:00:01 [ERROR] Tools: 读取文件失败：路径越界
2026-03-07 01:00:01 [WARNING] Agent: 用户请求被拒绝 - 访问受限路径
```

## 🔧 配置选项

### 1. 启用文件日志

```python
from learn_agent.logger import enable_file_logging

# 在程序启动时调用
enable_file_logging(log_dir="logs")
```

### 2. 设置日志级别

```python
from learn_agent.logger import set_log_level
import logging

# 开发环境 - 显示所有日志
set_log_level(logging.DEBUG)

# 生产环境 - 只显示重要日志
set_log_level(logging.INFO)

# 静默模式 - 只显示错误
set_log_level(logging.ERROR)
```

### 3. 自定义 Logger

```python
from learn_agent.logger import get_logger

# 创建自定义 logger
my_logger = get_logger('MyModule', logging.DEBUG)

my_logger.debug("调试信息")
my_logger.info("普通信息")
```

## 💡 最佳实践

### ✅ 推荐做法

1. **关键操作使用上下文管理器**
   ```python
   with log_context("加载配置文件"):
       load_config()
   ```

2. **耗时函数使用性能计时**
   ```python
   @timing
   def slow_function():
       ...
   ```

3. **异常处记录错误日志**
   ```python
   try:
       risky_operation()
   except Exception as e:
       logger.error(f"操作失败：{e}", exc_info=True)
       raise
   ```

4. **提供有意义的日志消息**
   ```python
   # ✅ 好
   logger.info(f"读取文件：{path}, 大小：{size} bytes")
   
   # ❌ 不好
   logger.info("读取文件")
   ```

### ❌ 避免的做法

1. **不要在循环中记录大量 DEBUG 日志**
   ```python
   # ❌ 会导致日志文件过大
   for item in large_list:
       logger.debug(f"处理：{item}")
   ```

2. **不要记录敏感信息**
   ```python
   # ❌ 禁止
   logger.debug(f"API Key: {api_key}")
   ```

3. **不要过度日志**
   ```python
   # ❌ 冗余
   logger.info("开始")
   do_something()
   logger.info("完成")
   
   # ✅ 更好
   with log_context("do_something"):
       do_something()
   ```

## 📁 文件结构

```
src/learn_agent/
├── logger.py              # 日志系统核心模块 ✨ NEW
├── workspace.py           # 已集成日志
├── tools.py              # 已集成日志（部分）
├── agent.py              # 待集成
└── config.py             # 待集成

docs/
├── LOGGING_GUIDE.md      # 完整使用指南 ✨ NEW
└── LOGGING_SUMMARY.md    # 本文档

tests/
└── test_logging.py       # 日志系统测试 ✨ NEW
```

## 🎯 下一步计划

### 已完成 ✅
- [x] 创建 logger.py 核心模块
- [x] 集成到 workspace.py
- [x] 创建文档和示例
- [x] 编写测试验证

### 待完成 📝
- [ ] 集成到所有工具函数（tools.py）
- [ ] 集成到 Agent 循环（agent.py）
- [ ] 集成到配置管理（config.py）
- [ ] 添加日志轮转（防止日志文件过大）
- [ ] 添加日志分析工具

## 📖 相关文档

- [`LOGGING_GUIDE.md`](LOGGING_GUIDE.md) - 详细使用指南
- [`test_logging.py`](../test_logging.py) - 测试示例
- [`logger.py`](../src/learn_agent/logger.py) - 源码

---

**日志系统已就绪！** 🎉

现在可以轻松地：
- ✅ 追踪程序执行流程
- ✅ 定位问题和错误
- ✅ 分析性能瓶颈
- ✅ 理解系统行为

让调试变得前所未有的简单！
