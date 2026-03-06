# 流式输出与 HTML 格式化功能说明

## 概述

本次更新为 LearnTerminalAgent 添加了流式输出功能和 HTML 风格的格式化显示，提升用户体验。

## 新增功能

### 1. 流式输出 (Streaming)

**位置**: `src/learn_agent/agent.py`

**核心方法**: `_stream_invoke()`

**功能特点**:
- ✅ 实时显示 AI 的思考过程，类似打字机效果
- ✅ 逐块接收并打印 LLM 的响应
- ✅ 支持工具调用的收集和显示
- ✅ 失败时自动降级到普通模式

**使用方式**:
```python
# 在 agent.run() 中启用流式
response = agent.run(query, verbose=True, stream=True)
```

**实现细节**:
```python
def _stream_invoke(self, verbose: bool = True) -> AIMessage:
    # 使用 LangChain 的 stream 方法
    stream = self.llm_with_tools.stream(self.messages)
    
    for chunk in stream:
        # 实时打印每个 chunk
        if chunk.content:
            print(chunk.content, end="", flush=True)
```

---

### 2. HTML 风格卡片格式化

**位置**: `src/learn_agent/main.py`

**核心方法**: `_format_response_card()`

**功能特点**:
- ✅ 使用 ANSI 转义码模拟 HTML 卡片边框
- ✅ 智能识别内容类型并应用不同颜色
  - 📝 代码块 → 黄色
  - ✅ 成功消息 → 绿色加粗
  - ⚠️ 警告错误 → 红色
  - 📄 普通文本 → 绿色
- ✅ 自适应卡片宽度
- ✅ 防止终端内容折叠

**样式示例**:
```
╔══════════════════════════════════════╗
║ 我已经完成了你的任务。文件已成功创建 ║
║ 并保存到指定目录。                   ║
╚══════════════════════════════════════╝
```

**代码块高亮**:
```
╔══════════════════════════════════════╗
║ ```python                            ║
║ def hello():                         ║
║     print("Hello, World!")           ║
║ ```                                  ║
╚══════════════════════════════════════╝
```

---

### 3. HTML 格式化工具

**位置**: `src/learn_agent/tools.py`

**工具名称**: `format_html_output`

**功能**: AI 可以主动调用此工具来格式化输出

**支持的样式**:
- `default` - 默认样式
- `code` - 代码块样式
- `success` - 成功消息样式
- `warning` - 警告消息样式
- `error` - 错误消息样式
- `info` - 信息提示样式

**使用示例**:
```python
format_html_output(
    content="任务完成！",
    style="success"
)
# 返回：<div style="color: #22863a; background: #dcffe4; ...">任务完成！</div>
```

---

## 技术实现

### 流式输出流程

```
用户输入
  ↓
Agent.run(query, stream=True)
  ↓
_stream_invoke()
  ↓
llm_with_tools.stream(messages)  ← LangChain 流式 API
  ↓
for chunk in stream:             ← 逐块处理
  - 收集内容
  - 实时打印 (flush=True)
  - 收集工具调用
  ↓
构建完整 AIMessage
  ↓
返回响应
```

### 卡片格式化算法

1. **分析内容**: 找出最长行确定卡片宽度
2. **构建边框**: 使用 Unicode 框线字符 (╔═╗║╚╝)
3. **样式检测**: 识别每行的内容类型
   - 代码关键词 (`import`, `def`, `class`, ```)`
   - 成功标记 (`✅`, `✓`, `✔`)
   - 警告标记 (`⚠️`, `❗`, `Error`)
4. **应用颜色**: 根据类型使用对应的 ANSI 颜色码
5. **输出渲染**: 组合所有元素形成最终卡片

---

## 配置说明

### 启用/禁用流式

在 `agent.run()` 调用时控制:
```python
# 启用流式 (默认)
agent.run(query, stream=True)

# 禁用流式
agent.run(query, stream=False)
```

### 调整 verbosity

```python
# 详细模式 (显示思考过程和工具调用)
agent.run(query, verbose=True)

# 简洁模式 (只显示最终结果)
agent.run(query, verbose=False)
```

---

## 兼容性

### 终端支持

✅ **完美支持**:
- Windows Terminal
- PowerShell (现代版本)
- Linux 终端 (GNOME Terminal, Konsole)
- macOS Terminal (iTerm2)

⚠️ **部分支持**:
- 传统 cmd.exe (可能颜色显示异常)
- 某些 SSH 客户端 (可能不支持 Unicode 框线)

### Python 版本

- Python 3.8+
- 依赖：LangChain >= 0.1.0

---

## 测试验证

运行测试脚本查看效果:
```bash
python test_stream_output.py
```

测试内容包括:
1. 普通文本响应的卡片格式化
2. 包含代码块的响应格式化
3. 包含成功标记的响应格式化
4. 多行混合内容的响应格式化

---

## 优势对比

### Before (传统输出)
```
我已经完成了你的任务。文件已成功创建并保存到指定目录。
```

### After (流式 + 卡片格式化)
```
╔══════════════════════════════════════╗
║ 我已经完成了你的任务。文件已成功创建 ║
║ 并保存到指定目录。                   ║
╚══════════════════════════════════════╝
```

**改进点**:
- ✅ 视觉上更加醒目，不易被忽略
- ✅ 结构化展示，防止终端折叠
- ✅ 颜色编码提升可读性
- ✅ 流式输出减少等待焦虑

---

## 未来优化方向

1. **Markdown 渲染**: 支持更丰富的 Markdown 格式
2. **语法高亮**: 集成 pygments 进行代码高亮
3. **进度条**: 为长时间任务添加进度指示
4. **可配置主题**: 允许用户自定义颜色主题
5. **导出功能**: 支持将会话记录导出为 HTML

---

## 相关文件

- `src/learn_agent/agent.py` - 流式调用实现
- `src/learn_agent/main.py` - 卡片格式化函数
- `src/learn_agent/tools.py` - HTML 格式化工具
- `test_stream_output.py` - 测试脚本

---

**更新时间**: 2026-03-06  
**版本**: v1.0
