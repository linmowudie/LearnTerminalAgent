# Agent 响应优化计划书

## 📋 项目概述

### 1.1 问题背景

当前 Agent 系统存在以下关键问题：

1. **空响应问题** - LLM 偶尔返回"思考完成"等无实质内容的回复
2. **工具调用延迟** - 用户明确要求操作时，Agent 只思考不行动
3. **回应冗长** - 过度解释即将执行的操作，而非直接执行
4. **流式输出不可靠** - 工具调用参数解析失败

### 1.2 优化目标

| 目标 | 描述 | 衡量指标 |
|------|------|----------|
| ✅ 零空响应 | 禁止"思考完成"类回复 | 空响应率 < 1% |
| ✅ 即时工具调用 | 隐含操作请求时立即调用工具 | 工具调用延迟 ≤ 1 次迭代 |
| ✅ 简洁回应 | 回应简洁直接，聚焦结果 | 平均响应长度减少 30% |
| ✅ 可靠流式输出 | 保持实时性的同时确保工具调用准确 | 工具调用成功率 > 98% |

---

## 🎯 核心策略

### 2.1 三重提醒机制

通过三个层面强化 LLM 的工具使用行为：

```
┌─────────────────────────────────────────┐
│  Layer 1: 系统提示词（初始化）           │
│  - 设定基本行为准则                     │
│  - 明确工具使用说明                     │
│  - 禁止空响应                           │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  Layer 2: 对话过程提醒（前 5 轮）          │
│  - 持续强化工具使用意识                 │
│  - 关键词触发针对性提醒                │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  Layer 3: 强制重试机制（空响应时）       │
│  - 检测空响应并自动重试                 │
│  - 添加强制行动提醒                     │
└─────────────────────────────────────────┘
```

### 2.2 智能关键词触发

建立行动关键词映射表，自动识别需要工具调用的场景：

```python
行动关键词 → 推荐工具
├─ 查看/列出/view/list → list_directory, read_file
├─ 创建/create → write_file
├─ 编辑/修改/edit/update → edit_file
├─ 运行/执行/run/execute → bash
└─ 读取/read → read_file
```

### 2.3 混合流式调用模式

平衡实时显示和工具调用可靠性：

```
流式阶段（实时显示）
    ↓
检测工具调用片段？
    ├─ YES → 重新 invoke（获取完整工具信息）
    └─ NO → 直接使用流式结果
        ↓
    验证响应质量
        ├─ 空响应 → 强制提醒 + 重试
        └─ 正常 → 返回结果
```

---

## 📝 实施步骤

### 阶段一：系统提示词增强

**文件**: `src/learn_agent/agent.py`  
**优先级**: P0（最高）  
**预计工时**: 30 分钟

#### 修改内容

在 `AgentLoop.__init__()` 方法中，将系统提示词替换为：

```python
self.system_prompt = (
    f"You are a helpful coding agent working in the directory: {workspace.root}\n"
    f"ALL file operations MUST be within this workspace.\n"
    f"You CANNOT access files outside this directory. If a user requests a file "
    f"outside the workspace, explain that you can only access files within "
    f"{workspace.root}.\n"
    f"\n"
    f"CRITICAL RULES:\n"
    f"1. ALWAYS respond with SUBSTANTIVE content - NEVER just say '思考完成' or empty phrases\n"
    f"2. When user asks to DO something (view, create, edit, run, etc.), YOU MUST:\n"
    f"   - IMMEDIATELY call the appropriate tool\n"
    f"   - DO NOT just talk about it - TAKE ACTION\n"
    f"3. Keep responses concise and direct - avoid lengthy explanations\n"
    f"4. NEVER repeat what you're about to do - just do it with tools\n"
    f"\n"
    f"AVAILABLE TOOLS - USE THEM:\n"
    f"- `bash` - Run commands, execute scripts, check system info\n"
    f"- `read_file` - Read file contents (when user asks to view/read)\n"
    f"- `write_file` - Create or write files (when user asks to create)\n"
    f"- `edit_file` - Modify existing files (when user asks to edit/update)\n"
    f"- `list_directory` - View directory contents (when user asks to list/view files)\n"
    f"\n"
    f"EXAMPLE BEHAVIOR:\n"
    f"User: '查看当前文件夹内容' → Agent calls list_directory() IMMEDIATELY\n"
    f"User: '创建一个 test.txt 文件' → Agent calls write_file() IMMEDIATELY\n"
    f"User: '运行 python hello.py' → Agent calls bash() IMMEDIATELY\n"
    f"\n"
    f"Remember: ACTIONS speak louder than words - USE TOOLS!"
)
```

#### 验收标准

- [ ] Agent 初始化时使用新提示词
- [ ] 提示词包含明确的禁止事项
- [ ] 提示词包含具体的行为示例

---

### 阶段二：智能关键词触发机制

**文件**: `src/learn_agent/agent.py`  
**优先级**: P0  
**预计工时**: 45 分钟

#### 修改内容

在 `AgentLoop.run()` 方法中添加关键词检测和针对性提醒：

```python
def run(self, query: str, verbose: bool = True, stream: bool = True) -> str:
    # 添加工具使用关键词检测
    action_keywords = {
        '查看': ['list_directory', 'read_file'],
        '创建': ['write_file'],
        '编辑': ['edit_file'],
        '运行': ['bash'],
        '执行': ['bash'],
        '读取': ['read_file'],
        '列出': ['list_directory'],
        'delete': ['bash'],  # 需要谨慎处理
        'create': ['write_file'],
        'run': ['bash'],
        'execute': ['bash'],
        'read': ['read_file'],
        'list': ['list_directory'],
        'view': ['list_directory', 'read_file'],
    }
    
    # 检测用户 query 中是否包含行动关键词
    needs_tool = False
    suggested_tools = []
    for keyword, tools in action_keywords.items():
        if keyword in query or keyword.lower() in query.lower():
            needs_tool = True
            suggested_tools.extend(tools)
    
    # 添加用户消息
    self.messages.append(HumanMessage(content=query))
    
    # 如果是前几次对话或检测到行动关键词，添加强化提醒
    if len(self.messages) <= 10 or needs_tool:
        reminder = (
            "\n\n[SYSTEM REMINDER - CRITICAL]\n"
            "⚠️ YOU MUST USE TOOLS TO TAKE ACTION!\n"
        )
        
        if suggested_tools:
            reminder += (
                f"🎯 Your query suggests you need: {', '.join(set(suggested_tools))}\n"
            )
        
        reminder += (
            "❌ FORBIDDEN: Empty responses like '思考完成' or just talking\n"
            "✅ REQUIRED: Call appropriate tools IMMEDIATELY\n"
            "[/SYSTEM REMINDER]"
        )
        
        # 将提醒添加到用户消息末尾
        self.messages[-1] = HumanMessage(
            content=self.messages[-1].content + reminder
        )
```

#### 验收标准

- [ ] 能准确识别中英文行动关键词
- [ ] 针对性提醒包含推荐工具列表
- [ ] 前 5 轮对话内持续提醒

---

### 阶段三：流式输出优化

**文件**: `src/learn_agent/agent.py`  
**优先级**: P0  
**预计工时**: 60 分钟

#### 修改内容

重构 `_stream_invoke()` 方法，实现混合调用模式：

```python
def _stream_invoke(self, verbose: bool = True) -> AIMessage:
    """
    流式调用 LLM 并实时打印输出
    
    采用混合模式：
    1. 流式显示文本内容（实时体验）
    2. 重新调用获取完整工具调用（可靠性保证）
    3. 空响应检测与强制重试
    """
    from langchain_core.messages import AIMessage
    
    # ANSI 颜色代码
    STYLE_CYAN = "\033[36m"
    STYLE_YELLOW = "\033[33m"
    STYLE_RESET = "\033[0m"
    
    try:
        # 流式调用 - 只用于显示文本
        stream = self.llm_with_tools.stream(self.messages)
        
        if verbose:
            print(f"\n{STYLE_CYAN}🤖 Agent 思考中:{STYLE_RESET}", end=" ", flush=True)
        
        full_content = ""
        has_tool_calls = False
        
        for chunk in stream:
            # 收集文本内容用于显示
            if hasattr(chunk, 'content') and chunk.content:
                full_content += chunk.content
                if verbose:
                    print(chunk.content, end="", flush=True)
            
            # 检测是否有工具调用片段
            if hasattr(chunk, 'tool_calls') and chunk.tool_calls:
                has_tool_calls = True
        
        if verbose:
            print()  # 换行
        
        # 关键改进：如果有工具调用或内容为空，必须重新调用
        if has_tool_calls or not full_content.strip():
            # 重新调用获取完整的工具调用信息
            full_response = self.llm_with_tools.invoke(self.messages)
            
            # 验证响应质量
            if not full_response.tool_calls and not full_response.content:
                # 如果仍然为空，添加强制提醒并重试
                logger_agent.warning("LLM 返回空响应，添加强制提醒并重试")
                self._add_forced_reminder()
                full_response = self.llm_with_tools.invoke(self.messages)
            
            return full_response
        else:
            # 纯文本回答，直接使用流式结果
            return AIMessage(content=full_content)
            
    except Exception as e:
        # 流式失败，降级到普通调用
        if verbose:
            print(f"\n{STYLE_YELLOW}⚠️ 流式输出失败，切换到普通模式：{e}{STYLE_RESET}")
        return self.llm_with_tools.invoke(self.messages)
```

#### 验收标准

- [ ] 流式显示文本内容正常
- [ ] 检测到工具调用时自动切换完整模式
- [ ] 空响应触发强制重试机制

---

### 阶段四：空响应检测与重试

**文件**: `src/learn_agent/agent.py`  
**优先级**: P1  
**预计工时**: 30 分钟

#### 新增方法

在 `AgentLoop` 类中添加 `_add_forced_reminder()` 方法：

```python
def _add_forced_reminder(self):
    """在最后一条 HumanMessage 后添加强制行动提醒"""
    reminder = (
        "\n\n[FORCED REMINDER]\n"
        "⚠️ YOUR LAST RESPONSE WAS EMPTY!\n"
        "You MUST:\n"
        "1. Call appropriate tools to take action\n"
        "2. Provide substantive response\n"
        "3. NEVER say '思考完成' or similar empty phrases\n"
        "[/FORCED REMINDER]"
    )
    
    # 查找最后一条 HumanMessage
    for i in range(len(self.messages) - 1, -1, -1):
        if isinstance(self.messages[i], HumanMessage):
            self.messages[i] = HumanMessage(
                content=self.messages[i].content + reminder
            )
            break
```

#### 修改 `run()` 方法

在工具调用检查部分添加验证逻辑：

```python
# 检查是否有工具调用
if not response.tool_calls:
    # 没有工具调用，检查是否应该调用
    last_human_msg = None
    for msg in reversed(self.messages):
        if isinstance(msg, HumanMessage):
            last_human_msg = msg
            break
    
    # 如果最后一条人类消息包含行动关键词，但 AI 没有调用工具
    if last_human_msg:
        action_words = ['查看', '创建', '编辑', '运行', '执行', '读取', '列出',
                       'view', 'create', 'edit', 'run', 'execute', 'read', 'list']
        has_action = any(word in last_human_msg.content for word in action_words)
        
        if has_action:
            logger_agent.warning(
                f"检测到行动请求但未调用工具，添加提醒并重试"
            )
            # 添加提醒并重试一次
            self._add_forced_reminder()
            continue  # 继续循环，再次调用 LLM
    
    # 确实不需要工具调用时，返回文本响应
    if not response.content or response.content.strip() == "思考完成":
        return "我已收到您的请求。请告诉我具体需要做什么？"
    
    return response.content
```

#### 验收标准

- [ ] 空响应自动触发重试
- [ ] 检测到应调用工具但未调用时自动重试
- [ ] 重试次数限制为 1 次（避免无限循环）

---

### 阶段五：工具描述增强

**文件**: `src/learn_agent/tools.py`  
**优先级**: P1  
**预计工时**: 20 分钟

#### 修改内容

为每个核心工具添加 USAGE TRIGGER 说明：

```python
@tool
def list_directory(path: str = ".") -> str:
    """
    列出目录内容 - 当用户要求"查看"、"列出"文件或文件夹时使用
    
    Args:
        path: 目录路径（默认当前目录）
        
    Returns:
        目录中的文件和文件夹列表
    
    USAGE TRIGGER: User says "查看...", "列出...", "show files", "list directory"
    """
    # ... 实现保持不变

@tool
def read_file(path: str, limit: Optional[int] = None) -> str:
    """
    读取文件内容 - 当用户要求"读取"、"查看...内容"时使用
    
    Args:
        path: 文件路径
        limit: 最大读取行数（可选）
        
    Returns:
        文件内容
    
    USAGE TRIGGER: User says "读取...", "查看...的内容", "read file", "show me..."
    """
    # ... 实现保持不变

@tool
def write_file(path: str, content: str) -> str:
    """
    写入文件内容 - 当用户要求"创建"、"新建"、"写入"文件时使用
    
    Args:
        path: 文件路径
        content: 要写入的内容
        
    Returns:
        操作结果
    
    USAGE TRIGGER: User says "创建...文件", "新建...", "write to file", "create..."
    """
    # ... 实现保持不变

@tool
def bash(command: str) -> str:
    """
    运行 shell 命令 - 当用户要求"运行"、"执行"命令或脚本时使用
    
    Args:
        command: 要执行的 shell 命令
        
    Returns:
        命令的输出结果
    
    USAGE TRIGGER: User says "运行...", "执行...", "run command", "execute..."
    """
    # ... 实现保持不变
```

#### 验收标准

- [ ] 所有核心工具都有 USAGE TRIGGER 说明
- [ ] 说明包含中英文触发词示例

---

## 🧪 测试验证计划

### 测试用例设计

创建测试脚本 `test_responsiveness.py`：

```python
#!/usr/bin/env python
"""
Agent 响应优化验证测试
"""

from learn_agent.agent import AgentLoop

def test_list_directory():
    """测试：查看目录"""
    agent = AgentLoop()
    response = agent.run("查看当前文件夹内容", verbose=False)
    assert "list_directory" in str(agent.messages), "应调用 list_directory 工具"
    assert "思考完成" not in response, "不应返回空响应"

def test_create_file():
    """测试：创建文件"""
    agent = AgentLoop()
    response = agent.run("创建一个 test.txt 文件，写入 hello", verbose=False)
    assert "write_file" in str(agent.messages), "应调用 write_file 工具"
    assert "我会创建" not in response, "不应只说不做"

def test_run_command():
    """测试：运行命令"""
    agent = AgentLoop()
    response = agent.run("运行 python --version", verbose=False)
    assert "bash" in str(agent.messages), "应调用 bash 工具"
    assert "让我想想" not in response, "不应冗长解释"

def test_read_file():
    """测试：读取文件"""
    agent = AgentLoop()
    response = agent.run("读取 README.md 的内容", verbose=False)
    assert "read_file" in str(agent.messages), "应调用 read_file 工具"

def test_no_empty_response():
    """测试：禁止空响应"""
    agent = AgentLoop()
    response = agent.run("你好", verbose=False)
    assert response.strip() not in ["思考完成", "", " "], "禁止空响应"
```

### 测试执行

```bash
# 运行单元测试
python test_responsiveness.py

# 手动测试
python src/learn_agent/main.py
```

### 验收标准

| 测试项 | 通过率目标 | 实际通过率 |
|--------|-----------|-----------|
| 查看目录 → 立即调用工具 | 100% | ⬜ |
| 创建文件 → 立即调用工具 | 100% | ⬜ |
| 运行命令 → 立即调用工具 | 100% | ⬜ |
| 读取文件 → 立即调用工具 | 100% | ⬜ |
| 禁止空响应 | 100% | ⬜ |
| 简洁回应（<100 字） | 90% | ⬜ |

---

## 📊 效果评估

### 性能指标对比

| 指标 | 优化前 | 优化后目标 | 测量方法 |
|------|--------|-----------|---------|
| 空响应率 | ~5% | < 1% | 日志统计 |
| 工具调用延迟 | 3-6 次迭代 | ≤ 1 次迭代 | 测试脚本 |
| 工具调用成功率 | ~60% | > 98% | 测试脚本 |
| 平均响应长度 | 150 字 | < 100 字 | 抽样统计 |
| 用户满意度 | 3.5/5 | > 4.5/5 | 用户反馈 |

### 用户体验改进

**优化前场景**：
```
用户：查看当前文件夹内容
🤖 Agent 思考中...
╔═══════╗
║ 思考完成。 ║
╚═══════╝
(无工具调用) ❌

用户：为什么不执行命令
🤖 Agent 思考中...
我来帮你查看目录内容...
(还是没调用工具) ❌
```

**优化后场景**：
```
用户：查看当前文件夹内容
[SYSTEM REMINDER: Use tools...]
🤖 Agent 思考中...
[Iteration 1]
[list_directory] {'path': '.'}  ← 立即调用工具！✅
Directory: .
Folders:
[DIR] Docs/
Files:
[FILE] README.md

✅ 已成功列出目录内容
```

---

## ⚠️ 风险评估

### 风险 1：Token 消耗增加

**原因**：混合模式可能导致双倍 API 调用  
**影响**：成本上升  
**缓解措施**：
- 纯文本对话仍使用单次流式调用
- 提供配置选项禁用流式：`agent.run(query, stream=False)`
- 批量处理任务时建议禁用流式

### 风险 2：响应延迟

**原因**：重试机制增加等待时间  
**影响**：用户体验下降  
**缓解措施**：
- 限制重试次数为 1 次
- 流式显示思考过程，减少感知延迟
- 优化 LLM 温度设置（建议 0.7）

### 风险 3：过度提醒

**原因**：频繁 SYSTEM REMINDER 可能干扰对话  
**影响**：Token 浪费和视觉干扰  
**缓解措施**：
- 前 5 轮对话后停止常规提醒
- 仅在有行动关键词时触发针对性提醒
- 使用简洁的提醒格式

---

## 📅 实施时间表

| 阶段 | 任务 | 预计工时 | 负责人 | 状态 |
|------|------|---------|--------|------|
| 阶段一 | 系统提示词增强 | 30 分钟 | ⬜ | ⬜ 未开始 |
| 阶段二 | 智能关键词触发 | 45 分钟 | ⬜ | ⬜ 未开始 |
| 阶段三 | 流式输出优化 | 60 分钟 | ⬜ | ⬜ 未开始 |
| 阶段四 | 空响应检测重试 | 30 分钟 | ⬜ | ⬜ 未开始 |
| 阶段五 | 工具描述增强 | 20 分钟 | ⬜ | ⬜ 未开始 |
| 测试 | 测试验证 | 30 分钟 | ⬜ | ⬜ 未开始 |
| **总计** | | **3 小时 35 分钟** | | |

---

## 🔧 技术依赖

### 必需组件

- LangChain >= 0.1.0
- ChatOpenAI API
- Python >= 3.8

### 相关文件

- `src/learn_agent/agent.py` - 主要修改文件
- `src/learn_agent/tools.py` - 工具描述增强
- `src/learn_agent/logger.py` - 日志记录
- `test_responsiveness.py` - 新建测试文件

---

## 📖 维护指南

### 日常监控

1. **日志审查** - 每日检查 `test_logs/` 中的错误日志
2. **用户反馈** - 收集用户对响应速度的反馈
3. **性能指标** - 每周统计工具调用成功率

### 持续改进方向

1. **动态提醒** - 根据上下文智能调整提醒频率
2. **Few-shot 学习** - 插入成功工具调用示例
3. **工具优先级** - 为不同工具设置触发权重
4. **用户反馈循环** - 用户说"为什么不执行"时自动增强

---

## ✅ 验收清单

### 功能验收

- [ ] 零空响应（连续测试 100 次无空响应）
- [ ] 工具调用延迟 ≤ 1 次迭代（测试 10 个用例）
- [ ] 工具调用成功率 > 98%（测试 100 个用例）
- [ ] 流式输出正常工作
- [ ] 所有测试用例通过

### 文档验收

- [ ] 更新 `README.md` 说明优化效果
- [ ] 更新 `docs/QUICK_START.md` 使用示例
- [ ] 编写 `CHANGELOG.md` 版本更新记录

### 代码质量

- [ ] 通过所有单元测试
- [ ] 代码审查通过
- [ ] 无破坏性变更

---

## 📞 联系方式

如有问题或建议，请联系：

- 项目负责人：待分配
- 技术支持：查看 `docs/help.md`
- Bug 报告：提交 Issue

---

**批准人**: _______________  
**日期**: 2026-03-07  
**版本**: v1.0  

---

## 附录 A：相关文件索引

| 文件 | 说明 |
|------|------|
| [`docs/AGENT_TOOL_CALLING_FIX.md`](AGENT_TOOL_CALLING_FIX.md) | 工具调用修复方案 |
| [`docs/STREAM_FIX_NOTES.md`](STREAM_FIX_NOTES.md) | 流式输出修复说明 |
| [`src/learn_agent/agent.py`](../src/learn_agent/agent.py) | Agent 核心实现 |
| [`src/learn_agent/tools.py`](../src/learn_agent/tools.py) | 工具定义 |
| [`src/learn_agent/main.py`](../src/learn_agent/main.py) | 主程序入口 |

---

## 附录 B：配置示例

### 环境变量配置

```bash
# API 配置
export QWEN_API_KEY="sk-xxxxx"
export QWEN_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"

# 可选：调整 Agent 行为
export AGENT_MAX_ITERATIONS=10
export AGENT_TEMPERATURE=0.7
```

### 运行时配置

```python
# 启用流式（默认）
agent.run(query, stream=True)

# 禁用流式（节省 token）
agent.run(query, stream=False)

# 禁用详细输出
agent.run(query, verbose=False)
```

---

**计划书编制完成！** 📋
