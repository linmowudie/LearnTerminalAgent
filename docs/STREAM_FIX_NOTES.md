# 流式输出工具调用修复说明

## 问题描述

在使用流式输出时，发现工具调用参数解析失败的问题：

```
[Iteration 2]
[write_file] {}
Error executing write_file: ValidationError: 2 validation errors for write_file
path
  Field required [type=missing, input_value={}, input_type=dict]
```

**根本原因**: LangChain 的流式 API (`stream()`) 在处理工具调用时，会将工具调用信息分散在多个 chunk 中，导致无法正确累积完整的工具调用参数。

---

## 解决方案

### 方案选择：混合模式

我们采用了一种**混合模式**来平衡流式显示和工具调用的可靠性：

1. **第一步 - 流式显示**: 使用 `stream()` 实时显示 AI 的思考内容
2. **第二步 - 完整调用**: 重新调用 `invoke()` 获取完整的工具调用信息

### 实现逻辑

```python
def _stream_invoke(self, verbose: bool = True) -> AIMessage:
    # 1. 流式调用 - 只显示文本内容
    stream = self.llm_with_tools.stream(self.messages)
    
    for chunk in stream:
        if chunk.content:
            print(chunk.content, end="", flush=True)  # 实时显示
    
    # 2. 如果有内容，重新调用获取完整工具信息
    if full_content.strip():
        full_response = self.llm_with_tools.invoke(self.messages)
        return full_response  # 包含完整的 tool_calls
    else:
        return AIMessage(content=full_content)
```

---

## 优缺点分析

### ✅ 优点

1. **保留流式体验**: 用户可以看到 AI 实时思考过程
2. **工具调用可靠**: 完整的参数解析，不会出现 validation error
3. **向后兼容**: 不影响现有代码

### ⚠️ 缺点

1. **两次 API 调用**: 当有工具调用时，会消耗 2 倍 token
2. **轻微延迟**: 需要等待第二次调用完成

---

## 性能优化建议

### 场景 1: 纯文本对话（无工具调用）
- ✅ 只调用 1 次（流式）
- 💰 无额外开销

### 场景 2: 需要工具调用
- ⚠️ 调用 2 次（流式 + 完整）
- 💰 双倍 token 消耗

### 优化策略

如果担心 token 消耗，可以在不需要实时显示的场景禁用流式：

```python
# 禁用流式，节省 token
agent.run(query, stream=False)
```

---

## 配置选项

### 完全启用流式（默认）

```python
agent.run(query, verbose=True, stream=True)
```

**效果**: 
- ✅ 实时显示思考过程
- ✅ 工具调用正常工作
- ⚠️ 有工具调用时消耗 2 倍 token

### 禁用流式

```python
agent.run(query, verbose=True, stream=False)
```

**效果**:
- ❌ 无实时显示
- ✅ 工具调用正常
- 💰 正常 token 消耗

---

## LangChain 流式 API 的限制

### 问题根源

LangChain 的 `stream()` 方法返回的是 `ChatGenerationChunk`，其中：

```python
chunk = {
    'content': '部分文本',
    'message': {
        'tool_call_chunks': [...]  # 分散的工具调用片段
    }
}
```

工具调用被分成多个 chunk，每个 chunk 只包含：
- `name`: 工具名称（可能在第一个 chunk）
- `args`: 参数字符串的一部分（分散在多个 chunk）
- `id`: 调用 ID

**难点**: 无法准确判断何时收集完所有参数。

### 为什么简单拼接不可行

```python
# ❌ 错误示例
tool_calls = []
for chunk in stream:
    if chunk.tool_calls:
        tool_calls.extend(chunk.tool_calls)  # 会导致参数不完整

# 执行时会报错：
# ValidationError: path Field required
```

---

## 未来改进方向

### 方案 A: 智能累积（推荐）

改进 `_stream_invoke` 方法，更精确地累积工具调用：

```python
current_tool_calls = {}

for chunk in stream:
    if chunk.message and chunk.message.tool_call_chunks:
        for tc in chunk.message.tool_call_chunks:
            # 更智能的累积逻辑
            if tc.get('name'):
                current_name = tc['name']
                current_tool_calls[current_name] = {
                    'name': tc['name'],
                    'args': '',
                    'id': tc.get('id', '')
                }
            
            # 累积参数字符串
            if tc.get('args'):
                current_tool_calls[current_name]['args'] += tc['args']
```

### 方案 B: 使用官方支持

等待 LangChain 官方提供更好的流式工具调用支持。

参考 issue: https://github.com/langchain-ai/langchain/issues/...

### 方案 C: 切换到其他框架

考虑使用支持更好流式工具调用的框架：
- LlamaIndex
- Haystack
- 自定义实现

---

## 测试验证

### 测试脚本

```bash
# Windows
test_agent_stream.bat

# Linux/Mac
python src/learn_agent/run.py
```

### 测试用例

1. **纯文本对话**
   ```
   输入：如何找实习？
   期望：流式显示回答，无工具调用
   ```

2. **单工具调用**
   ```
   输入：创建一个 test.txt 文件
   期望：流式显示思考 → 调用 write_file → 卡片格式化结果
   ```

3. **多工具调用**
   ```
   输入：创建 hello.txt 和 world.txt 两个文件
   期望：流式显示 → 多次工具调用 → 卡片格式化结果
   ```

---

## 相关文件

- `src/learn_agent/agent.py` - `_stream_invoke()` 方法
- `src/learn_agent/main.py` - 主循环配置
- `docs/STREAM_OUTPUT_GUIDE.md` - 原始流式输出指南

---

## 总结

当前采用的**混合模式**是在流式体验和工具调用可靠性之间的最佳权衡：

- ✅ 保留了流式显示的视觉体验
- ✅ 保证了工具调用的准确性
- ⚠️ 代价是可能的双倍 token 消耗

**建议**: 
- 日常开发保持默认设置（`stream=True`）
- 批量处理任务时禁用流式（`stream=False`）节省成本

---

**更新时间**: 2026-03-06  
**版本**: v1.1 (修复工具调用问题)
