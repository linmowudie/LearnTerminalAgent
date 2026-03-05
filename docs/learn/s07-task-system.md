# s07 - Task System: 任务管理系统

LearnAgent 的高级任务管理系统，支持持久化存储和依赖关系管理。

## 📖 原理介绍

### 核心思想

Task System 是一个**基于 JSON 文件的持久化任务管理系统**，与 TodoWrite（内存级）不同，它具有以下特点：

1. **持久化存储** - 任务以 JSON 文件形式保存在 `.tasks/` 目录
2. **依赖关系图** - 支持任务间的阻塞关系（blockedBy/blocks）
3. **任务所有者** - 可以指定任务负责人（用于团队协作）
4. **自动依赖清除** - 完成任务时自动从其他任务的 blockedBy 中移除

### 与 TodoWrite 的对比

| 特性 | TodoWrite (s03) | Task System (s07) |
|------|----------------|-------------------|
| 存储方式 | 内存 | JSON 文件 |
| 持久化 | ❌ | ✅ |
| 依赖关系 | ❌ | ✅ blockedBy/blocks |
| 任务所有者 | ❌ | ✅ owner 字段 |
| 复杂度 | 低 | 中 |
| 适用场景 | 短期简单任务 | 长期复杂项目 |

### 数据结构

```python
@dataclass
class Task:
    """任务数据结构"""
    id: int                      # 唯一自增 ID
    subject: str                 # 任务主题
    description: str = ""        # 任务描述
    status: str = "pending"      # pending/in_progress/completed
    blockedBy: List[int] = []    # 被哪些任务阻塞
    blocks: List[int] = []       # 阻塞哪些任务
    owner: str = ""              # 任务所有者
```

### 依赖关系示例

```
任务 1 (未完成) ──blocks──> 任务 2 (blockedBy: [1])
                          └── 等待任务 1 完成才能开始
```

## 💻 实现方法

### TaskManager 类

完整实现位于 [`src/learn_agent/task_system.py`](../src/learn_agent/task_system.py)

```python
class TaskManager:
    """
    任务管理器
    
    CRUD 操作 + 依赖图管理，所有任务持久化为 JSON 文件
    """
    
    def __init__(self, tasks_dir: Path):
        self.dir = tasks_dir
        self.dir.mkdir(exist_ok=True)
        self._next_id = self._max_id() + 1  # 下一个任务 ID
```

### 持久化机制

#### 1. 加载任务

```python
def _load(self, task_id: int) -> Task:
    """加载任务"""
    path = self.dir / f"task_{task_id}.json"
    if not path.exists():
        raise ValueError(f"Task {task_id} not found")
    
    data = json.loads(path.read_text(encoding='utf-8'))
    return Task(**data)
```

#### 2. 保存任务

```python
def _save(self, task: Task):
    """保存任务"""
    path = self.dir / f"task_{task.id}.json"
    path.write_text(
        json.dumps(task.__dict__, indent=2),
        encoding='utf-8'
    )
```

**文件格式示例** (`task_1.json`):
```json
{
  "id": 1,
  "subject": "重构代码",
  "description": "优化性能",
  "status": "in_progress",
  "blockedBy": [],
  "blocks": [2, 3],
  "owner": "developer"
}
```

### CRUD 操作

#### 创建任务 (Create)

```python
def create(self, subject: str, description: str = "") -> str:
    """创建新任务"""
    task = Task(
        id=self._next_id,
        subject=subject,
        description=description,
        status="pending",
        blockedBy=[],
        blocks=[],
        owner="",
    )
    self._save(task)
    self._next_id += 1
    return json.dumps(task.__dict__, indent=2, ensure_ascii=False)
```

**使用示例**:
```python
manager.create("完成项目文档", "编写 README 和使用指南")
# 返回：
# {
#   "id": 1,
#   "subject": "完成项目文档",
#   "description": "编写 README 和使用指南",
#   "status": "pending",
#   "blockedBy": [],
#   "blocks": [],
#   "owner": ""
# }
```

#### 获取任务 (Read)

```python
def get(self, task_id: int) -> str:
    """获取任务详情"""
    task = self._load(task_id)
    return json.dumps(task.__dict__, indent=2, ensure_ascii=False)
```

#### 更新任务 (Update)

```python
def update(
    self,
    task_id: int,
    status: Optional[str] = None,
    add_blocked_by: Optional[List[int]] = None,
    add_blocks: Optional[List[int]] = None,
) -> str:
    """更新任务状态或依赖关系"""
    task = self._load(task_id)
    
    # 1. 更新状态
    if status:
        if status not in ("pending", "in_progress", "completed"):
            raise ValueError(f"Invalid status: {status}")
        task.status = status
        
        # 完成任务时，从所有其他任务的 blockedBy 中移除
        if status == "completed":
            self._clear_dependency(task_id)
    
    # 2. 添加阻塞关系
    if add_blocked_by:
        task.blockedBy = list(set(task.blockedBy + add_blocked_by))
    
    if add_blocks:
        task.blocks = list(set(task.blocks + add_blocks))
        # 双向绑定：更新被阻塞任务的 blockedBy 列表
        for blocked_id in add_blocks:
            try:
                blocked = self._load(blocked_id)
                if task_id not in blocked.blockedBy:
                    blocked.blockedBy.append(task_id)
                    self._save(blocked)
            except ValueError:
                pass
    
    self._save(task)
    return json.dumps(task.__dict__, indent=2, ensure_ascii=False)
```

**使用示例**:
```python
# 更新状态
manager.update(1, status="in_progress")

# 设置依赖：任务 1 阻塞任务 2 和 3
manager.update(1, add_blocks=[2, 3])
# 自动更新任务 2 和 3 的 blockedBy 字段

# 完成任务（自动清除依赖）
manager.update(1, status="completed")
# 任务 2 和 3 的 blockedBy 中的 1 会被移除
```

#### 依赖清除机制

```python
def _clear_dependency(self, completed_id: int):
    """从所有任务中移除已完成的依赖"""
    for f in self.dir.glob("task_*.json"):
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
            if completed_id in data.get("blockedBy", []):
                data["blockedBy"].remove(completed_id)
                f.write_text(json.dumps(data, indent=2), encoding='utf-8')
        except Exception:
            continue
```

#### 列出任务 (List)

```python
def list_all(self) -> str:
    """列出所有任务"""
    tasks = []
    for f in sorted(self.dir.glob("task_*.json")):
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
            tasks.append(data)
        except Exception:
            continue
    
    if not tasks:
        return "No tasks."
    
    lines = []
    for t in tasks:
        marker = {
            "pending": "[ ]",
            "in_progress": "[>]",
            "completed": "[x]"
        }.get(t["status"], "[?]")
        
        blocked = f" (blocked by: {t['blockedBy']})" if t.get("blockedBy") else ""
        lines.append(f"{marker} #{t['id']}: {t['subject']}{blocked}")
    
    return "\n".join(lines)
```

**输出示例**:
```
[ ] #1: 需求分析
[>] #2: 编写代码 (blocked by: [1])
[ ] #3: 测试 (blocked by: [1])
[x] #4: 部署
```

### 工具定义

四个 LangChain 工具：

```python
@tool
def task_create(subject: str, description: str = "") -> str:
    """创建新任务"""
    manager = get_task_manager()
    return manager.create(subject, description)

@tool
def task_get(task_id: int) -> str:
    """获取任务详情"""
    manager = get_task_manager()
    return manager.get(task_id)

@tool
def task_update(
    task_id: int,
    status: Optional[str] = None,
    addBlockedBy: Optional[List[int]] = None,
    addBlocks: Optional[List[int]] = None,
) -> str:
    """更新任务状态或依赖关系"""
    manager = get_task_manager()
    return manager.update(task_id, status, addBlockedBy, addBlocks)

@tool
def task_list() -> str:
    """列出所有任务"""
    manager = get_task_manager()
    return manager.list_all()
```

### Agent 集成

在 `agent.py` 中的方法：

```python
class AgentLoop:
    # ========== s07: Task System 功能 ==========
    
    def task_create(self, subject: str, description: str = "") -> str:
        """创建新任务"""
        from .task_system import get_task_manager
        manager = get_task_manager()
        return manager.create(subject, description)
    
    def task_get(self, task_id: int) -> str:
        """获取任务详情"""
        from .task_system import get_task_manager
        return get_task_manager().get(task_id)
    
    def task_update(
        self,
        task_id: int,
        status: Optional[str] = None,
        add_blocked_by: Optional[List[int]] = None,
        add_blocks: Optional[List[int]] = None,
    ) -> str:
        """更新任务状态或依赖关系"""
        from .task_system import get_task_manager
        return get_task_manager().update(task_id, status, add_blocked_by, add_blocks)
    
    def task_list(self) -> str:
        """列出所有任务"""
        from .task_system import get_task_manager
        return get_task_manager().list_all()
    
    def reset_tasks(self):
        """重置任务管理器"""
        reset_tasks()
```

### 全局实例

```python
# 全局任务管理器实例
_task_manager: Optional[TaskManager] = None

def get_task_manager() -> TaskManager:
    """获取全局任务管理器"""
    global _task_manager
    if _task_manager is None:
        tasks_dir = Path.cwd() / ".tasks"
        _task_manager = TaskManager(tasks_dir)
    return _task_manager

def reset_tasks():
    """重置任务管理器（清空所有任务）"""
    global _task_manager
    if tasks_dir.exists():
        for f in tasks_dir.glob("task_*.json"):
            f.unlink()
    _task_manager = TaskManager(tasks_dir)
```

## 🎯 使用示例

### 基础工作流

```python
# 1. 创建任务
agent.task_create("需求分析", "完成产品需求文档")
# 返回：{"id": 1, "subject": "需求分析", ...}

# 2. 开始任务
agent.task_update(1, status="in_progress")

# 3. 查看任务列表
agent.task_list()
# 输出：[>] #1: 需求分析

# 4. 完成任务
agent.task_update(1, status="completed")
# 输出：[x] #1: 需求分析
```

### 依赖关系管理

```python
# 创建三个有依赖关系的任务
agent.task_create("架构设计")  # 任务 1
agent.task_create("后端开发")  # 任务 2
agent.task_create("前端开发")  # 任务 3

# 设置依赖：任务 1 完成后才能开始任务 2 和 3
agent.task_update(1, add_blocks=[2, 3])
# 自动更新：
# - 任务 1 的 blocks: [2, 3]
# - 任务 2 的 blockedBy: [1]
# - 任务 3 的 blockedBy: [1]

# 查看任务列表
agent.task_list()
# 输出:
# [ ] #1: 架构设计
# [ ] #2: 后端开发 (blocked by: [1])
# [ ] #3: 前端开发 (blocked by: [1])

# 完成任务 1
agent.task_update(1, status="completed")
# 自动从任务 2 和 3 的 blockedBy 中移除 1

# 现在任务 2 和 3 可以开始了
agent.task_list()
# 输出:
# [x] #1: 架构设计
# [ ] #2: 后端开发
# [ ] #3: 前端开发
```

### 复杂项目示例

```
用户：我要开发一个 Web 应用

Agent 创建任务计划:
1. task_create("需求分析")           # 任务 1
2. task_create("技术选型")           # 任务 2
3. task_create("数据库设计")         # 任务 3
4. task_create("API 开发")            # 任务 4
5. task_create("前端开发")           # 任务 5
6. task_create("测试部署")           # 任务 6

# 设置依赖关系
task_update(1, add_blocks=[2])       # 需求 → 选型
task_update(2, add_blocks=[3, 4])    # 选型 → 数据库设计 & API 开发
task_update(3, add_blocks=[4])       # 数据库 → API 开发
task_update(4, add_blocks=[5])       # API → 前端
task_update(5, add_blocks=[6])       # 前端 → 测试

# 任务列表显示:
[ ] #1: 需求分析
[ ] #2: 技术选型 (blocked by: [1])
[ ] #3: 数据库设计 (blocked by: [2])
[ ] #4: API 开发 (blocked by: [2, 3])
[ ] #5: 前端开发 (blocked by: [4])
[ ] #6: 测试部署 (blocked by: [5])

# 按顺序完成任务
task_update(1, "completed")  # 完成需求
task_update(2, "in_progress") # 开始选型
# ... 依次进行
```

## ⚙️ 配置选项

### 数据存储位置

```python
from .project_config import get_project_config
PROJECT = get_project_config()
tasks_dir = PROJECT.data_dir / ".tasks"
```

### 任务 ID 生成

```python
def _max_id(self) -> int:
    """获取当前最大任务 ID"""
    ids = []
    for f in self.dir.glob("task_*.json"):
        try:
            task_id = int(f.stem.split("_")[1])
            ids.append(task_id)
        except (ValueError, IndexError):
            continue
    return max(ids) if ids else 0
```

ID 规则：
- 从 1 开始自增
- 即使删除任务也不会重用 ID
- 通过扫描现有文件确定下一个 ID

## 🐛 错误处理

### 常见错误

1. **任务不存在**
   ```
   ValueError: Task 99 not found
   ```
   **解决**: 检查任务 ID 是否正确

2. **无效状态**
   ```
   ValueError: Invalid status: invalid_status
   ```
   **解决**: 使用有效状态：pending/in_progress/completed

3. **循环依赖**
   ```
   可能导致逻辑错误
   ```
   **解决**: 避免 A→B→A 的循环依赖

4. **文件损坏**
   ```
   JSONDecodeError: Invalid JSON
   ```
   **解决**: 手动修复或删除损坏的 JSON 文件

## 📊 性能考虑

### 优势

✅ **持久化** - 上下文压缩后任务信息不丢失  
✅ **依赖管理** - 清晰的任务先后关系  
✅ **团队协作** - owner 字段支持分工  
✅ **审计追踪** - JSON 文件可版本控制  

### 劣势

⚠️ **文件系统 I/O** - 每次操作都读写文件  
⚠️ **无并发锁** - 多线程环境可能需要锁机制  
⚠️ **查询能力有限** - 不支持复杂筛选和排序  

### 最佳实践

1. **合理分解任务** - 任务粒度适中，不宜过粗或过细
2. **明确依赖关系** - 提前规划任务先后顺序
3. **及时更新状态** - 保持任务状态准确
4. **定期清理** - 归档已完成的任务文件
5. **版本控制** - 将 `.tasks/` 目录纳入 Git 管理（可选）

## 🔗 与相关模块集成

### 与 Worktree 集成 (s12)

```python
# 创建 worktree 并绑定任务
worktree_create(name="feature-a", task_id=1)
# 任务 1 的 owner 字段会自动设置为 "feature-a"
```

### 与团队协作集成 (s09)

```python
# 队友认领任务
agent.send_message("reviewer", "请审查代码")
# reviewer 完成任务后可以更新任务状态
agent.task_update(task_id, status="completed", owner="reviewer")
```

### 与自主代理集成 (s11)

```python
# 自主代理扫描未分配任务
unclaimed = scan_unclaimed_tasks()
# 条件：status=pending, owner 为空，blockedBy 为空

# 认领任务
claim_task(task_id=1, owner="autonomous_agent")
```

## 🔗 相关模块

- [s03 - TodoWrite](s03-todo-write.md) - 轻量级任务管理
- [s09 - Agent Teams](s09-agent-teams.md) - 团队协作
- [s12 - Worktree Isolation](s12-worktree-isolation.md) - 任务与 worktree 绑定

---

**下一步**: 了解 [后台任务机制](s08-background-tasks.md) →
