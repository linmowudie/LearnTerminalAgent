---
name: test-generator
description: 测试用例生成器，自动创建单元测试模板和 pytest 测试代码
tags: 单元测试，pytest,测试覆盖，TDD
---

# Test Generator - 测试用例生成器

## 🎯 功能描述

自动分析 Python 代码并生成对应的单元测试模板，支持 pytest 框架，帮助快速编写高质量的测试用例。

## ✨ 核心功能

1. **自动生成**: 分析函数/类自动生成测试模板
2. **边界测试**: 自动包含边界条件和异常场景
3. **参数化测试**: 生成 pytest 参数化测试用例
4. **Mock 辅助**: 提供外部依赖的 Mock 方案
5. **覆盖率检查**: 分析测试覆盖率并提供改进建议

## 📋 支持的测试类型

### 1. 单元测试 (Unit Tests)

- 函数级别测试
- 方法级别测试
- 类行为测试

### 2. 集成测试 (Integration Tests)

- 模块间交互
- API 端点测试
- 数据库操作

### 3. 参数化测试 (Parametric Tests)

- 多组输入数据
- 边界值测试
- 等价类划分

### 4. 异常测试 (Exception Tests)

- 错误输入处理
- 边界条件验证
- 异常情况捕获

## 🛠️ 使用示例

### 示例 1: 为函数生成测试

```python
# 源代码：src/calculator.py
def add(a: float, b: float) -> float:
    """两数相加"""
    return a + b

def divide(a: float, b: float) -> float:
    """两数相除"""
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b
```

```bash
# 生成测试
python generate_tests.py src/calculator.py

# 生成的测试文件：tests/test_calculator.py
```

### 示例 2: 为类生成测试

```python
# 源代码：src/user_service.py
class UserService:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def create_user(self, username: str, email: str) -> User:
        pass
    
    def get_user(self, user_id: int) -> Optional[User]:
        pass
    
    def delete_user(self, user_id: int) -> bool:
        pass
```

```bash
# 生成测试（包含 Mock）
python generate_tests.py src/user_service.py --with-mock
```

### 示例 3: 批量生成测试

```bash
# 为整个目录生成测试
python generate_tests.py src/ --recursive --output tests/

# 仅生成缺失的测试文件
python generate_tests.py src/ --skip-existing
```

### 示例 4: 自定义测试模板

```bash
# 使用自定义模板
python generate_tests.py src/module.py --template custom_template.py

# 指定测试前缀
python generate_tests.py src/module.py --prefix test_
```

## 🔧 配套脚本

### generate_tests.py 使用方法

```bash
# 查看帮助
python generate_tests.py --help

# 为单个文件生成测试
python generate_tests.py src/my_module.py

# 为整个目录生成测试
python generate_tests.py src/ -r

# 生成测试并包含 Mock
python generate_tests.py src/service.py --with-mock

# 使用自定义配置
python generate_tests.py src/ --config .test_config.yaml
```

## 📊 生成的测试示例

### 简单函数测试

**源代码**:
```python
def calculate_discount(price: float, discount: float) -> float:
    """计算折扣价格"""
    if price < 0:
        raise ValueError("价格不能为负")
    if not 0 <= discount <= 100:
        raise ValueError("折扣必须在 0-100 之间")
    
    return price * (1 - discount / 100)
```

**生成的测试**:
```python
"""
calculate_discount 函数的测试套件
"""

import pytest
from src.calculator import calculate_discount


class TestCalculateDiscount:
    """calculate_discount 函数测试类"""
    
    def test_normal_discount(self):
        """测试正常折扣场景"""
        assert calculate_discount(100, 10) == 90.0
        assert calculate_discount(200, 25) == 150.0
    
    @pytest.mark.parametrize(
        "price,discount,expected",
        [
            (100, 0, 100),      # 无折扣
            (100, 50, 50),      # 50% 折扣
            (100, 100, 0),      # 全额折扣
            (50, 20, 40),       # 小额价格
        ],
    )
    def test_parametrized_cases(self, price, discount, expected):
        """参数化测试多个场景"""
        assert calculate_discount(price, discount) == expected
    
    def test_invalid_price(self):
        """测试无效价格输入"""
        with pytest.raises(ValueError, match="价格不能为负"):
            calculate_discount(-100, 10)
        
        with pytest.raises(ValueError):
            calculate_discount(-1, 0)
    
    def test_invalid_discount(self):
        """测试无效折扣输入"""
        with pytest.raises(ValueError, match="折扣必须在 0-100 之间"):
            calculate_discount(100, -10)
        
        with pytest.raises(ValueError):
            calculate_discount(100, 150)
    
    def test_boundary_values(self):
        """测试边界值"""
        # 折扣边界
        assert calculate_discount(100, 0) == 100
        assert calculate_discount(100, 100) == 0
        
        # 价格边界
        assert calculate_discount(0, 50) == 0
```

### 带 Mock 的类测试

**源代码**:
```python
class EmailService:
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """发送邮件"""
        pass

class UserService:
    def __init__(self, email_service: EmailService):
        self.email_service = email_service
    
    def register_user(self, username: str, email: str) -> User:
        user = User(username, email)
        self.email_service.send_email(
            email,
            "欢迎注册",
            f"欢迎 {username}!"
        )
        return user
```

**生成的测试**:
```python
"""
UserService 类的测试套件
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.user_service import UserService
from src.email_service import EmailService


class TestUserService:
    """UserService 类测试类"""
    
    @pytest.fixture
    def mock_email_service(self):
        """创建 EmailService 的 Mock 对象"""
        return Mock(spec=EmailService)
    
    @pytest.fixture
    def user_service(self, mock_email_service):
        """创建 UserService 实例（使用 Mock）"""
        return UserService(mock_email_service)
    
    def test_register_user_success(self, user_service, mock_email_service):
        """测试用户注册成功场景"""
        # Arrange
        username = "testuser"
        email = "test@example.com"
        
        # Act
        user = user_service.register_user(username, email)
        
        # Assert
        assert user.username == username
        assert user.email == email
        mock_email_service.send_email.assert_called_once_with(
            email,
            "欢迎注册",
            f"欢迎 {username}!"
        )
    
    def test_register_user_sends_email(self, user_service, mock_email_service):
        """测试注册时发送邮件"""
        # Act
        user_service.register_user("user1", "user1@example.com")
        
        # Assert
        assert mock_email_service.send_email.called
    
    def test_register_user_with_invalid_email(
        self, user_service, mock_email_service
    ):
        """测试无效邮箱处理"""
        # Arrange
        mock_email_service.send_email.side_effect = Exception("邮件发送失败")
        
        # Act & Assert
        with pytest.raises(Exception, match="邮件发送失败"):
            user_service.register_user("user1", "invalid-email")
```

## 🎯 最佳实践

### 1. 测试命名规范

```python
# ✅ 好的命名
def test_login_with_valid_credentials():
    pass

def test_login_with_invalid_password_raises_error():
    pass

def test_calculate_discount_given_negative_price_then_raises_error():
    pass

# ❌ 不好的命名
def test1():
    pass

def test_login():  # 太模糊
    pass
```

### 2. AAA 模式 (Arrange-Act-Assert)

```python
def test_user_creation():
    # Arrange (准备)
    username = "testuser"
    email = "test@example.com"
    
    # Act (执行)
    user = user_service.create_user(username, email)
    
    # Assert (断言)
    assert user.username == username
    assert user.email == email
```

### 3. 测试覆盖策略

```python
# 正常路径测试
def test_happy_path():
    pass

# 边界值测试
def test_boundary_conditions():
    pass

# 异常路径测试
def test_error_handling():
    pass

# 回归测试
def test_previously_fixed_bugs():
    pass
```

### 4. Fixture 使用

```python
@pytest.fixture
def database_connection():
    """创建测试数据库连接"""
    conn = create_test_db()
    yield conn
    cleanup_test_db(conn)

@pytest.fixture
def sample_user():
    """创建示例用户"""
    return User("testuser", "test@example.com")

def test_user_in_db(database_connection, sample_user):
    """使用 fixture 进行测试"""
    database_connection.save(sample_user)
    assert database_connection.exists(sample_user.id)
```

## 📚 Pytest 使用指南

### 安装和配置

```bash
# 安装 pytest
pip install pytest pytest-cov pytest-mock

# 运行测试
pytest

# 显示覆盖率
pytest --cov=src --cov-report=html

# 运行特定测试
pytest tests/test_calculator.py::TestAddition
```

### pyproject.toml 配置

```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = [
    "-ra",
    "-q",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html:htmlcov",
]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/__init__.py",
]
```

### 常用 Pytest 命令

```bash
# 基本运行
pytest
pytest tests/

# 详细输出
pytest -v
pytest -vv

# 显示打印内容
pytest -s

# 遇到第一个失败就停止
pytest -x

# 运行上次失败的测试
pytest --lf

# 显示最慢的 10 个测试
pytest --durations=10

# 并行执行测试
pytest -n auto
```

## 🔍 测试覆盖率

### 查看覆盖率

```bash
# 终端显示
pytest --cov=src --cov-report=term-missing

# HTML 报告
pytest --cov=src --cov-report=html

# XML 报告 (CI/CD)
pytest --cov=src --cov-report=xml
```

### 覆盖率目标

```toml
[tool.coverage.report]
fail_under = 80
show_missing = true
skip_covered = true

exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
]
```

## 🎓 学习资源

- [pytest 官方文档](https://docs.pytest.org/)
- [测试金字塔](https://martinfowler.com/bliki/TestPyramid.html)
- [TDD 入门](https://www.agilealliance.org/glossary/tdd/)
