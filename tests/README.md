# LearnTerminalAgent 测试目录

本目录用于存放项目的测试用例。

## 📁 目录结构

```
tests/
├── test_agent.py          # Agent 主循环测试
├── test_tools.py          # 工具系统测试
├── test_todo.py           # TodoWrite 测试
├── test_subagent.py       # SubAgent 测试
├── test_skills.py         # Skills 系统测试
├── test_context.py        # Context 管理测试
├── test_teams.py          # Agent Teams 测试
├── test_config.py         # 配置管理测试
└── ...
```

## 🧪 运行测试

### 运行所有测试

```bash
pytest tests/
```

### 运行特定测试文件

```bash
pytest tests/test_agent.py
```

### 运行特定测试函数

```bash
pytest tests/test_agent.py::test_agent_initialization
```

### 显示覆盖率

```bash
pytest --cov=src/learn_agent tests/
```

### 详细输出

```bash
pytest -v tests/
```

## 📝 测试规范

### 测试文件命名

- 以 `test_` 开头
- 对应源代码模块名
- 例如：`agent.py` → `test_agent.py`

### 测试函数命名

- 以 `test_` 开头
- 描述测试内容
- 使用下划线分隔
- 例如：`test_agent_creates_file()`

### 测试结构示例

```python
import pytest
from learn_agent.agent import AgentLoop

def test_agent_initialization():
    """测试 Agent 初始化"""
    agent = AgentLoop()
    assert agent is not None

def test_agent_run_basic_task():
    """测试 Agent 执行基本任务"""
    agent = AgentLoop()
    response = agent.run("创建一个测试文件")
    assert "成功" in response or "完成" in response

@pytest.mark.asyncio
async def test_agent_async_operation():
    """测试 Agent 异步操作"""
    # 异步测试代码
    pass
```

## 🔧 测试配置

### pytest.ini（可选）

可以在项目根目录创建 `pytest.ini`：

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --tb=short
```

### conftest.py

创建共享的测试夹具：

```python
# tests/conftest.py
import pytest
from learn_agent.config import get_config

@pytest.fixture
def sample_config():
    """提供测试配置"""
    return get_config()

@pytest.fixture
def agent_instance():
    """提供 Agent 实例"""
    return AgentLoop()
```

## 📚 测试范围

### 单元测试

针对单个函数或方法的测试：

```python
def test_read_file_success():
    """测试读取文件成功的情况"""
    content = read_file("test.txt")
    assert isinstance(content, str)
```

### 集成测试

测试多个组件的协作：

```python
def test_agent_with_tool_use():
    """测试 Agent 使用工具的完整流程"""
    agent = AgentLoop()
    response = agent.run("列出当前目录的文件")
    assert response is not None
```

### 边界测试

测试边界条件和异常情况：

```python
def test_read_nonexistent_file():
    """测试读取不存在的文件"""
    with pytest.raises(FileNotFoundError):
        read_file("nonexistent.txt")
```

## 🎯 测试最佳实践

1. **保持独立** - 每个测试应该独立运行，不依赖其他测试
2. **可重复性** - 测试结果应该是确定的，不受环境影响
3. **快速执行** - 单元测试应该快速执行
4. **清晰命名** - 测试名称应该清楚表达测试目的
5. **覆盖全面** - 包括正常情况、边界情况和异常情况

## 📊 持续改进

- 定期查看测试覆盖率报告
- 为关键功能添加测试
- 修复 Bug 时先写测试用例
- 重构代码时保持测试同步更新

## 🔗 相关文档

- [项目开发](../docs/guides/)
- [贡献指南](../README.md#贡献)
- [GitHub Actions](https://github.com/linmowudie/LearnTerminalAgent/actions)
