# s10 - Team Protocols: 团队通信协议

LearnAgent 团队协作的通信协议规范，定义了消息类型、格式和通信模式。

## 📖 原理介绍

### 核心思想

**标准化的异步通信协议**：
- 定义有效的消息类型
- 规范消息格式
- 支持多种通信模式（私信/广播）
- 基于 JSONL 文件的持久化队列

### 消息类型系统

有效消息类型（`VALID_MSG_TYPES`）：

```python
VALID_MSG_TYPES: Set[str] = {
    "message",           # 普通消息
    "broadcast",         # 广播消息
    "shutdown_request",  # 关闭请求
    "shutdown_response", # 关闭响应
    "plan_approval_response", # 计划审批
}
```

#### 1. message（普通消息）

一对一通信的基本消息类型：

```json
{
  "type": "message",
  "from": "lead",
  "content": "请审查 src/main.py",
  "timestamp": 1709600000
}
```

**使用场景**:
- 分配任务
- 询问问题
- 提供反馈

#### 2. broadcast（广播消息）

一对多通信的广播类型：

```json
{
  "type": "broadcast",
  "from": "lead",
  "content": "下午 3 点开会",
  "timestamp": 1709600000
}
```

**使用场景**:
- 团队通知
- 紧急公告
- 进度同步

#### 3. shutdown_request（关闭请求）

请求队友停止运行：

```json
{
  "type": "shutdown_request",
  "from": "lead",
  "content": "任务完成，可以停止了",
  "timestamp": 1709600000
}
```

**使用场景**:
- 队友完成任务后
- 团队重组时

#### 4. shutdown_response（关闭响应）

队友对关闭请求的确认：

```json
{
  "type": "shutdown_response",
  "from": "reviewer",
  "content": "已安全关闭",
  "timestamp": 1709600001
}
```

#### 5. plan_approval_response（计划审批）

用于审批队友提交的计划：

```json
{
  "type": "plan_approval_response",
  "from": "lead",
  "content": "计划已批准，开始执行",
  "approved": true,
  "timestamp": 1709600000
}
```

### 消息格式规范

标准消息结构：

```python
msg = {
    "type": str,           # 必需：消息类型
    "from": str,           # 必需：发送者
    "content": str,        # 必需：消息内容
    "timestamp": float,    # 必需：时间戳（Unix 时间戳）
    # 可选：额外字段
    "extra_field": any,
}
```

**必填字段**:
- `type` - 消息类型（必须是 VALID_MSG_TYPES 之一）
- `from` - 发送者名称
- `content` - 消息内容
- `timestamp` - Unix 时间戳（秒）

**可选字段**:
- 任何额外的键值对

## 💻 实现方法

### MessageBus 实现

完整代码位于 [`src/learn_agent/teams.py`](../src/learn_agent/teams.py#L38-L130)

#### 发送消息

```python
def send(
    self,
    sender: str,
    to: str,
    content: str,
    msg_type: str = "message",
    extra: Optional[Dict] = None,
) -> str:
    """发送消息到队友收件箱"""
    # 1. 验证消息类型
    if msg_type not in VALID_MSG_TYPES:
        return f"Error: Invalid type '{msg_type}'. Valid: {VALID_MSG_TYPES}"
    
    # 2. 构建消息
    msg = {
        "type": msg_type,
        "from": sender,
        "content": content,
        "timestamp": time.time(),
    }
    if extra:
        msg.update(extra)
    
    # 3. 写入收件箱（JSONL 格式）
    inbox_path = self.dir / f"{to}.jsonl"
    with open(inbox_path, "a", encoding='utf-8') as f:
        f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    
    return f"Sent {msg_type} to {to}"
```

**特点**:
- ✅ 类型安全检查
- ✅ 支持额外字段
- ✅ JSONL 格式（每行一个 JSON）
- ✅ 追加写入（不会覆盖）

#### 读取收件箱

```python
def read_inbox(self, name: str) -> List[dict]:
    """读取并清空收件箱"""
    inbox_path = self.dir / f"{name}.jsonl"
    if not inbox_path.exists():
        return []
    
    messages = []
    # 逐行解析 JSONL
    for line in inbox_path.read_text(encoding='utf-8').strip().splitlines():
        if line.strip():
            messages.append(json.loads(line))
    
    # 清空收件箱（消费式读取）
    inbox_path.write_text("", encoding='utf-8')
    
    return messages
```

**特点**:
- ✅ 消费式读取（读完后清空）
- ✅ 按时间顺序返回
- ✅ 容错处理（跳过空行）

#### 广播消息

```python
def broadcast(self, sender: str, content: str, teammates: List[str]) -> str:
    """广播消息给所有队友"""
    count = 0
    for name in teammates:
        if name != sender:
            # 给每个队友发送广播消息
            self.send(sender, name, content, "broadcast")
            count += 1
    return f"Broadcast to {count} teammates"
```

### 队友端接收

在 `_teammate_loop()` 中：

```python
def _teammate_loop(self, name: str, role: str, prompt: str):
    """队友代理循环"""
    messages = [HumanMessage(content=prompt)]
    
    for _ in range(50):
        # 检查收件箱
        local_bus = BUS or MessageBus(INBOX_DIR)
        inbox = local_bus.read_inbox(name)
        
        # 将消息添加到对话历史
        for msg in inbox:
            messages.append(
                HumanMessage(
                    content=json.dumps(msg, ensure_ascii=False)
                )
            )
        
        # ... 继续处理
```

## 🎯 使用示例

### 基础通信

```python
# 发送普通消息
agent.send_message(
    to="reviewer",
    content="请审查最新的代码提交",
    msg_type="message"
)
# 输出：Sent message to reviewer

# 查看回复
inbox = agent.read_inbox()
for msg in inbox:
    print(f"[{msg['type']}] From {msg['from']}: {msg['content']}")
# 输出：[message] From reviewer: 已完成审查...
```

### 广播通知

```python
# 广播会议通知
agent.broadcast("所有人注意，下午 3 点开会")
# 输出：Broadcast to 3 teammates
```

### 自定义消息类型

```python
# 使用自定义类型（需要先定义）
bus = get_bus()
bus.send(
    sender="lead",
    to="developer",
    content="紧急任务",
    msg_type="message",
    extra={
        "priority": "high",
        "deadline": "2026-03-06"
    }
)

# 队友收到后可以解析额外字段
msg = inbox[0]
if msg.get('priority') == 'high':
    print("这是高优先级任务！")
```

### 实际工作流

```
场景：代码审查流程

1. Lead → Reviewer (message):
   {
     "type": "message",
     "from": "lead",
     "content": "请审查 PR #42",
     "timestamp": 1709600000,
     "pr_number": 42
   }

2. Reviewer 处理中...

3. Reviewer → Lead (message):
   {
     "type": "message",
     "from": "reviewer",
     "content": "审查完成，发现 3 个问题",
     "timestamp": 1709600300,
     "issues": ["issue1", "issue2", "issue3"]
   }

4. Lead → All (broadcast):
   {
     "type": "broadcast",
     "from": "lead",
     "content": "PR #42 需要修改",
     "timestamp": 1709600400
   }

5. Lead → Reviewer (shutdown_request):
   {
     "type": "shutdown_request",
     "from": "lead",
     "content": "审查任务完成",
     "timestamp": 1709600500
   }

6. Reviewer → Lead (shutdown_response):
   {
     "type": "shutdown_response",
     "from": "reviewer",
     "content": "已关闭",
     "timestamp": 1709600501
   }
```

## ⚙️ 配置选项

### 扩展消息类型

可以在 `teams.py` 中添加自定义类型：

```python
VALID_MSG_TYPES: Set[str] = {
    "message",
    "broadcast",
    "shutdown_request",
    "shutdown_response",
    "plan_approval_response",
    # 添加新类型
    "code_review_request",
    "test_result",
    "build_notification",
}
```

### 收件箱目录

```python
from .project_config import get_project_config
PROJECT = get_project_config()
INBOX_DIR = PROJECT.data_dir / ".team" / "inbox"
```

### 时间戳格式

使用 Unix 时间戳（秒）：

```python
import time
timestamp = time.time()  # 例如：1709600000.123
```

转换为可读格式：

```python
from datetime import datetime
readable = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
```

## 🐛 错误处理

### 常见错误

1. **无效消息类型**
   ```
   Error: Invalid type 'custom'. Valid: {...}
   ```
   **解决**: 使用预定义的类型或扩展 VALID_MSG_TYPES

2. **收件箱不存在**
   ```
   read_inbox 返回空列表
   ```
   **解决**: 队友可能还没创建，先 spawn_teammate

3. **消息丢失**
   ```
   发送了但没收到的感觉
   ```
   **解决**: 检查收件箱是否被其他消费者读取

4. **JSONL 格式错误**
   ```
   JSONDecodeError
   ```
   **解决**: 手动检查 .jsonl 文件格式

## 📊 性能考虑

### 优势

✅ **简单可靠** - 基于文件，无需额外服务  
✅ **持久化** - 消息不会丢失  
✅ **异步非阻塞** - 发送后立即返回  
✅ **易于调试** - 可以直接查看 .jsonl 文件  

### 劣势

⚠️ **文件系统 I/O** - 每次操作都读写文件  
⚠️ **无消息优先级** - FIFO 顺序处理  
⚠️ **单消费者** - 每个消息只能被一个队友读取  

### 最佳实践

1. **简洁消息** - 保持消息内容简短
2. **及时清理** - 定期归档旧的 .jsonl 文件
3. **合理轮询** - 不要过于频繁检查收件箱
4. **错误处理** - 捕获并记录通信异常
5. **消息确认** - 重要消息要求回复确认

## 🔗 相关模块

- [s09 - Agent Teams](s09-agent-teams.md) - 团队协作基础
- [s08 - Background Tasks](s08-background-tasks.md) - 后台通知机制
- [s11 - Autonomous Agents](s11-autonomous-agents.md) - 自主代理通信

---

**下一步**: 了解 [自主代理机制](s11-autonomous-agents.md) →
