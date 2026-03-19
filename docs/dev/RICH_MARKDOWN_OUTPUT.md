# Rich Markdown 输出优化指南

## 概述

LearnTerminalAgent 现已集成 **Rich** 库，用于提供美观的终端富文本输出。AI 返回的 Markdown 格式内容会被自动渲染为带有样式、颜色和边框的富文本，显著提升可读性和视觉体验。

---

## 核心特性

### ✅ 1. Markdown 渲染

自动识别并渲染 Markdown 语法元素：

- **标题** (`#`, `##`, `###`) - 显示为粗体大字
- **列表** (`-`, `1.`) - 带项目符号的列表
- **代码块** (```) - 语法高亮的代码区域
- **引用** (`>`) - 斜体引用块
- **粗体/斜体** (`**text**`, `*text*`) - 相应文本样式

### ✅ 2. 响应卡片

使用圆角边框 Panel 展示 AI 回复，支持多种样式：

| 样式 | 用途 | 边框颜色 | 标题 |
|------|------|----------|------|
| `default` | 常规回复 | 青色 | 无 |
| `success` | 成功消息 | 绿色 | ✅ 成功 |
| `warning` | 警告提示 | 黄色 | ⚠️ 警告 |
| `error` | 错误信息 | 红色 | ❌ 错误 |
| `code` | 代码展示 | 黄色 | 📝 代码 |

### ✅ 3. 代码语法高亮

集成 Pygments 引擎，支持：

- Python、JavaScript、Java 等主流语言
- Monokai 主题配色
- 行号和缩进保持

### ✅ 4. 智能降级

如果 Rich 不可用，自动切换到 ANSI 卡片模式：

```
╔══════════════════════╗
║ 这是 ANSI 模式的卡片 ║
╚══════════════════════╝
```

---

## 技术实现

### 文件结构

```
src/learn_agent/infrastructure/
├── display.py          # 核心显示模块（包含 Rich 集成）
└── ...
```

### 关键类和方法

#### `TerminalDisplay` 类

主要的显示管理接口：

```python
from src.learn_agent.infrastructure.display import TerminalDisplay

display = TerminalDisplay(verbose=True, use_rich=True)
```

**参数说明**：
- `verbose`: 是否启用详细输出
- `use_rich`: 是否使用 Rich（None 时自动检测）

#### 主要方法

##### 1. `render_markdown(markdown_text: str)`

渲染 Markdown 格式的文本：

```python
markdown = """
# 标题

这是 **粗体** 和 `代码`。

```python
def hello():
    print("Hello!")
```
"""

display.render_markdown(markdown)
```

##### 2. `print_response_card(content: str, style: str = "default")`

打印响应卡片：

```python
# 成功消息
display.print_response_card("✅ 任务完成！", style="success")

# 代码展示
display.print_response_card("```python\ncode here\n```", style="code")

# 错误提示
display.print_response_card("❌ 发生错误", style="error")
```

##### 3. `_render_mixed_content(content: str)`

内部方法，渲染混合内容（文本 + 代码块）：

- 自动检测 ` ``` ` 标记
- 分离代码和普通文本
- 分别应用语法高亮和文本样式

---

## 使用示例

### 示例 1：基础 Markdown 渲染

```python
from src.learn_agent.infrastructure.display import TerminalDisplay

display = TerminalDisplay(verbose=True)

response = """
# 项目分析报告

## 概述
已分析你的代码项目，发现以下内容：

### 文件结构
- ✅ 主程序：`main.py`
- ✅ 工具模块：`utils.py`
- ⚠️ 缺少测试文件

### 代码质量
```python
def calculate_score(items):
    total = sum(item.value for item in items)
    return total * 1.2  # 20% 加成
```

建议添加单元测试覆盖边缘情况。
"""

display.render_markdown(response)
```

### 示例 2：不同样式的卡片

```python
display = TerminalDisplay(verbose=True)

# 默认样式
display.print_response_card(
    "这是一个普通的响应。\n包含多行文本。",
    style="default"
)

# 成功样式
display.print_response_card(
    "✅ 文件已成功创建！\n路径：./data/output.txt",
    style="success"
)

# 警告样式
display.print_response_card(
    "⚠️ 注意：此操作不可逆。\n请确认你已备份重要数据。",
    style="warning"
)

# 代码样式
code_response = """
这是生成的代码：

```python
class DataProcessor:
    def __init__(self, data):
        self.data = data
    
    def process(self):
        return [x * 2 for x in self.data]
```

使用方法：`processor = DataProcessor([1, 2, 3])`
"""
display.print_response_card(code_response, style="code")
```

### 示例 3：在 Agent 中使用

在 `main.py` 中，Agent 的响应会自动使用 Rich 卡片：

```python
# agent.run() 返回的响应会自动格式化
response = agent.run(query, verbose=True, stream=True)

# 如果有工具调用，verbose 模式已显示过程
# 纯文本回答会显示为 Rich 卡片
if not agent._has_tool_calls:
    agent.display.print_response_card(response, style="default")
```

---

## 配置选项

### 启用/禁用 Rich

```python
# 自动检测（推荐）
display = TerminalDisplay(verbose=True)

# 强制使用 Rich
display = TerminalDisplay(verbose=True, use_rich=True)

# 强制使用 ANSI 降级模式
display = TerminalDisplay(verbose=True, use_rich=False)
```

### Windows 兼容性

自动处理 Windows 控制台编码问题：

- 检测 UTF-8 支持
- 不支持时使用 ASCII 替代字符
- Colorama 集成确保颜色正常显示

```python
# 无需手动配置，库会自动处理
IS_WINDOWS = sys.platform.startswith('win')
legacy_windows=IS_WINDOWS and not SUPPORTS_UTF8
```

---

## 视觉效果对比

### Before（传统输出）

```
我已经完成了你的任务。文件已成功创建并保存到指定目录。

```python
def hello():
    print("Hello")
```

注意事项：
- 文件权限需要设置
- 记得导入依赖
```

### After（Rich 渲染）

```
╭─────────────────────────────────────────╮
│                                         │
│  我已经完成了你的任务。                 │
│  文件已成功创建并保存到指定目录。       │
│                                         │
│  ```python                              │
│  def hello():                           │
│      print("Hello")                     │
│  ```                                    │
│                                         │
│  注意事项：                             │
│  • 文件权限需要设置                     │
│  • 记得导入依赖                         │
│                                         │
╰─────────────────────────────────────────╯
```

**改进点**：
- ✅ 圆角边框突出显示回复内容
- ✅ 代码块语法高亮更易阅读
- ✅ 列表项使用项目符号
- ✅ 整体布局更加专业美观

---

## 依赖安装

### 必需依赖

已在 `requirements.txt` 中添加：

```txt
rich>=13.0.0
typer>=0.9.0
```

安装命令：

```bash
pip install rich typer
```

### 可选依赖

Pygments（语法高亮，Rich 会自动安装）：

```bash
pip install pygments
```

---

## 测试验证

运行测试脚本查看效果：

```bash
python test_rich_output.py
```

测试内容包括：
1. ✅ 基础 Markdown 渲染
2. ✅ 不同样式的响应卡片
3. ✅ 混合内容（文本 + 代码）渲染
4. ✅ ANSI 降级模式

---

## 最佳实践

### 1. 语义化样式选择

根据内容类型选择合适的卡片样式：

```python
# ✅ 好的做法
if success:
    display.print_response_card("✅ 完成", style="success")
elif has_error:
    display.print_response_card("❌ 错误", style="error")
elif contains_code:
    display.print_response_card(code, style="code")
else:
    display.print_response_card(text, style="default")
```

### 2. 保持内容简洁

卡片宽度自适应，但过长的行会影响可读性：

```python
# ✅ 推荐：每行不超过 60 字符
content = "这是第一行。\n这是第二行。"

# ❌ 避免：超长的单行
long_line = "这是一行非常非常非常非常非常非常非常非常非常非常非常非常长的文本..."
```

### 3. Markdown 格式优化

AI 回复应使用标准 Markdown 格式：

```markdown
# 标题

正文内容。

## 子标题

- 列表项 1
- 列表项 2

```python
# 代码块
code_here
```
```

### 4. 性能考虑

Rich 渲染开销很小，但在极端情况下可禁用：

```python
# 高性能模式（不需要富文本）
display = TerminalDisplay(verbose=True, use_rich=False)
```

---

## 故障排查

### 问题 1：中文显示乱码

**原因**：Windows 控制台编码问题

**解决**：
```bash
# PowerShell
chcp 65001

# 或在代码中设置
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

### 问题 2：颜色不显示

**原因**：旧版 Windows Terminal 或 cmd.exe

**解决**：
```python
# 强制启用颜色
from rich.console import Console
console = Console(force_terminal=True)
```

### 问题 3：边框字符显示异常

**原因**：字体不支持 Unicode 框线字符

**解决**：
- 使用支持 Unicode 的字体（如 Cascadia Code, Consolas）
- 或降级到 ANSI 模式：`use_rich=False`

---

## API 参考

### `TerminalDisplay` 完整方法列表

| 方法 | 描述 | 参数 |
|------|------|------|
| `__init__(verbose, use_rich)` | 初始化显示器 | verbose: bool, use_rich: Optional[bool] |
| `show_loading_animation(prefix)` | 显示加载动画 | prefix: str |
| `stop_loading_animation()` | 停止加载动画 | - |
| `print_tool_call(name, args)` | 打印工具调用 | name: str, args: dict |
| `print_tool_result(result)` | 打印工具结果 | result: str |
| `print_stream_chunk(chunk)` | 打印流式文本块 | chunk: str |
| `print_section_header(text)` | 打印分段标题 | text: str |
| `print_error(message)` | 打印错误信息 | message: str |
| `print_warning(message)` | 打印警告信息 | message: str |
| `render_markdown(text)` | 渲染 Markdown | text: str |
| `print_response_card(content, style)` | 打印响应卡片 | content: str, style: str |

---

## 更新日志

### v1.0 - 2026-03-09

- ✅ 集成 Rich 库到 `display.py`
- ✅ 添加 Markdown 渲染功能
- ✅ 实现 5 种响应卡片样式
- ✅ 支持代码语法高亮
- ✅ 自动降级到 ANSI 模式
- ✅ Windows 兼容性优化
- ✅ 更新 `main.py` 使用新显示系统

---

## 相关文件

- `src/learn_agent/infrastructure/display.py` - 核心实现
- `src/learn_agent/core/main.py` - 主程序入口
- `test_rich_output.py` - 测试脚本
- `requirements.txt` - 依赖配置

---

**更新时间**: 2026-03-09  
**版本**: v1.0  
**作者**: LearnTerminalAgent Team
