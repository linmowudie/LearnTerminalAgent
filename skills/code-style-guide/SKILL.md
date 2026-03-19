---
name: code-style-guide
description: Python 代码规范检查器，提供格式化、命名和最佳实践建议
tags: 代码规范，格式化，最佳实践，审查
---

# Code Style Guide - 代码规范检查器

## 🎯 功能描述

提供 Python 代码规范检查和最佳实践建议，帮助编写一致、可读、高质量的代码。

## ✨ 核心功能

1. **代码格式化**: Black、autopep8 格式化建议
2. **命名规范**: 变量、函数、类命名检查
3. **代码质量**: 复杂度分析、重复代码检测
4. **最佳实践**: PEP 8 规范、类型提示、文档字符串
5. **自动化修复**: 一键修复常见问题

## 📋 支持的检查项

### 1. 代码格式检查

- [ ] 缩进是否正确（4 个空格）
- [ ] 行宽是否超过 88 字符（Black 标准）
- [ ] 空行使用是否恰当
- [ ] 导入语句顺序和分组
- [ ] 空白字符使用

### 2. 命名规范检查

- [ ] 变量名：小写 + 下划线（snake_case）
- [ ] 常量名：全大写 + 下划线
- [ ] 函数名：小写 + 下划线
- [ ] 类名：大驼峰（PascalCase）
- [ ] 模块名：简短、小写、无下划线
- [ ] 私有成员：单下划线前缀
- [ ] 魔术方法：双下划线前后缀

### 3. 代码质量检查

- [ ] 函数复杂度（圈复杂度 < 10）
- [ ] 参数数量（< 5 个）
- [ ] 嵌套层级（< 4 层）
- [ ] 函数长度（< 50 行）
- [ ] 类长度（< 500 行）

### 4. 文档和规范

- [ ] 模块 docstring
- [ ] 函数/方法 docstring
- [ ] 类 docstring
- [ ] 类型注解（Type Hints）
- [ ] TODO/FIXME 注释

## 🛠️ 使用示例

### 示例 1: 检查单个文件

```bash
# 使用脚本检查
python check_style.py src/my_module.py

# 或使用 Agent 命令
LearnAgent >> 检查这个文件的代码规范
```

### 示例 2: 检查整个项目

```bash
# 递归检查所有 Python 文件
python check_style.py src/ --recursive

# 生成报告
python check_style.py src/ --report style_report.md
```

### 示例 3: 自动修复问题

```bash
# 自动格式化
python check_style.py src/ --fix

# 仅应用 Black 格式化
python check_style.py src/ --black-only
```

### 示例 4: 自定义规则

```bash
# 使用自定义配置文件
python check_style.py src/ --config .mypy.ini

# 忽略某些规则
python check_style.py src/ --ignore E501,W391
```

## 🔧 配套工具

### 推荐使用的工具链

1. **Black**: 代码格式化
   ```bash
   pip install black
   black src/
   ```

2. **Ruff**: 快速 linting（替代 flake8）
   ```bash
   pip install ruff
   ruff check src/
   ```

3. **Mypy**: 类型检查
   ```bash
   pip install mypy
   mypy src/
   ```

4. **isort**: 导入排序
   ```bash
   pip install isort
   isort src/
   ```

5. **PyLint**: 全面代码分析
   ```bash
   pip install pylint
   pylint src/my_module.py
   ```

## 📊 配置文件示例

### pyproject.toml (推荐)

```toml
[tool.black]
line-length = 88
target-version = ['py38', 'py39', 'py310']
include = '\.pyi?$'
extend-exclude = '''
/(
  # 目录
  | migrations
  | __pycache__
  | .*\.egg-info
)/
'''

[tool.ruff]
line-length = 88
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
]
ignore = [
    "E501",   # line too long (Black 处理)
    "B008",   # do not perform function calls in argument defaults
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]  # 允许未使用的导入

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
```

### .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.9

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]
```

## 💻 代码示例

### 好的代码风格

```python
"""
用户管理模块

提供用户创建、查询、更新等功能。
"""

from typing import Optional, List
from dataclasses import dataclass


@dataclass
class User:
    """用户数据类"""
    
    user_id: int
    username: str
    email: str
    is_active: bool = True
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "id": self.user_id,
            "username": self.username,
            "email": self.email,
            "active": self.is_active,
        }


class UserManager:
    """用户管理器"""
    
    def __init__(self, database_url: str):
        """
        初始化用户管理器
        
        Args:
            database_url: 数据库连接 URL
        """
        self.database_url = database_url
        self._cache: dict = {}
    
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
    ) -> User:
        """
        创建新用户
        
        Args:
            username: 用户名
            email: 邮箱地址
            password: 密码
            
        Returns:
            创建的 User 对象
            
        Raises:
            ValueError: 当用户名已存在时
        """
        if self._user_exists(username):
            raise ValueError(f"用户 '{username}' 已存在")
        
        user = User(
            user_id=self._get_next_id(),
            username=username,
            email=email,
        )
        
        self._save_user(user, password)
        return user
    
    def _user_exists(self, username: str) -> bool:
        """检查用户是否存在"""
        return username in self._cache
    
    def _get_next_id(self) -> int:
        """获取下一个用户 ID"""
        return len(self._cache) + 1
    
    def _save_user(self, user: User, password: str) -> None:
        """保存用户到数据库"""
        # 实现细节...
        pass
```

### 不好的代码风格 ❌

```python
# 错误示例：命名不规范、缺少文档、复杂度过高

def proc_data(d):  # 函数名不明确，参数名单字母
    x = []
    for i in range(len(d)):
        if d[i] > 0:
            x.append(d[i] * 2)
        else:
            x.append(0)
    return x

class user:  # 类名应该用大驼峰
    def __init__(self, n, e):
        self.n = n  # 属性名不明确
        self.e = e
    
    def get_data(self):
        return {"name": self.n, "email": self.e}
```

## 📚 最佳实践指南

### 1. 代码格式化

**原则**:
- 使用 Black 进行自动化格式化
- 行宽限制为 88 字符
- 使用 4 个空格缩进
- 顶部级别定义之间留 2 个空行
- 方法之间留 1 个空行

**示例**:
```python
# ✅ 好的格式
def calculate_total(items: List[float], tax_rate: float) -> float:
    """计算总金额"""
    subtotal = sum(items)
    tax = subtotal * tax_rate
    return subtotal + tax


class ShoppingCart:
    """购物车类"""
    
    def __init__(self):
        self.items: List[str] = []
    
    def add_item(self, item: str) -> None:
        """添加商品"""
        self.items.append(item)
```

### 2. 命名规范

**变量和函数名**:
```python
# ✅ 好的命名
user_count = 0
max_retries = 3
def calculate_average(numbers: List[float]) -> float:
    pass

# ❌ 不好的命名
cnt = 0  # 缩写不明确
n = 3
def calc(nums):
    pass
```

**类名**:
```python
# ✅ 好的命名
class DataProcessor:
    pass

class HTTPClient:
    pass

# ❌ 不好的命名
class data_processor:  # 应该用大驼峰
    pass

class Http_client:  # 不一致
    pass
```

### 3. 类型注解

**推荐做法**:
```python
from typing import Optional, List, Dict, Union

def greet(name: str, greeting: str = "Hello") -> str:
    """打招呼"""
    return f"{greeting}, {name}!"

def process_items(
    items: List[str],
    config: Optional[Dict[str, any]] = None,
) -> List[str]:
    """处理项目列表"""
    return [item.upper() for item in items]

def get_value(key: str) -> Union[int, str]:
    """获取值"""
    return 42
```

### 4. 文档字符串

**Google 风格**:
```python
def fetch_data(url: str, timeout: int = 30) -> dict:
    """
    从 URL 获取数据
    
    Args:
        url: API 端点 URL
        timeout: 超时时间（秒），默认 30
        
    Returns:
        包含响应数据的字典
        
    Raises:
        requests.Timeout: 当请求超时时
        requests.HTTPError: 当 HTTP 请求失败时
        
    Example:
        >>> data = fetch_data("https://api.example.com/users")
        >>> print(data["count"])
        100
    """
    pass
```

### 5. 错误处理

**最佳实践**:
```python
# ✅ 好的错误处理
def divide(a: float, b: float) -> float:
    """
    除法运算
    
    Raises:
        ValueError: 当除数为零时
    """
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b

# ❌ 不好的错误处理
def divide_bad(a, b):
    try:
        return a / b
    except Exception:  # 捕获所有异常
        return None
```

## 🎓 学习资源

1. **PEP 8 官方文档**: https://pep8.org/
2. **Black 文档**: https://black.readthedocs.io/
3. **Real Python**: https://realpython.com/
4. **Python 最佳实践**: https://docs.python-guide.org/

## 🔄 持续改进

定期检查代码规范并持续改进：

1. **集成到 CI/CD**: 在流水线中运行检查
2. **Pre-commit Hooks**: 提交前自动格式化
3. **定期 Code Review**: 团队互相审查代码
4. **技术债务跟踪**: 记录并逐步修复问题

## 📝 相关技能

- **test-generator**: 生成单元测试
- **doc-generator**: 自动生成文档
- **project-scaffold**: 创建新项目结构
