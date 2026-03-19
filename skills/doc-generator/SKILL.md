---
name: doc-generator
description: 文档生成助手，自动生成 API 文档、README 和代码注释
tags: 文档，API 文档，README,自动化
---

# Doc Generator - 文档生成助手

## 🎯 功能描述

自动分析 Python 代码并生成完整的文档，包括 API 文档、README 文件、函数注释等，帮助维护高质量的项目文档。

## ✨ 核心功能

1. **API 文档生成**: 从代码生成 API 参考文档
2. **README 生成**: 创建项目说明文档
3. **Docstring 补充**: 为函数/类添加文档字符串
4. **类型推断**: 自动推断并添加类型注解
5. **示例提取**: 从代码中提取使用示例

## 📋 支持的文档类型

### 1. API 参考文档

- 模块说明
- 类和方法文档
- 函数签名和参数说明
- 返回值类型

### 2. 项目文档

- README.md
- INSTALL.md
- CONTRIBUTING.md
- CHANGELOG.md

### 3. 代码内文档

- 模块 docstring
- 函数 docstring
- 类 docstring
- 复杂逻辑注释

## 🛠️ 使用示例

### 示例 1: 生成 API 文档

```bash
# 为整个项目生成 API 文档
python generate_docs.py src/ --output docs/api/

# 生成 Markdown 格式
python generate_docs.py src/ --format markdown

# 生成 reStructuredText 格式
python generate_docs.py src/ --format rst
```

### 示例 2: 生成 README

```bash
# 基于项目结构生成 README
python generate_docs.py --readme --output README.md

# 包含使用示例
python generate_docs.py --readme --with-examples
```

### 示例 3: 补充 Docstring

```bash
# 为缺少文档的代码添加 docstring
python generate_docs.py src/ --add-docstrings

# 仅添加到特定文件
python generate_docs.py src/module.py --add-docstrings --inplace
```

### 示例 4: 生成使用示例

```bash
# 从测试文件提取示例
python generate_docs.py src/ --extract-examples tests/

# 生成示例代码片段
python generate_docs.py src/utils.py --examples-only
```

## 🔧 配套脚本

### generate_docs.py 使用方法

```bash
# 查看帮助
python generate_docs.py --help

# 生成完整文档
python generate_docs.py src/ -o docs/

# 仅生成 README
python generate_docs.py --readme

# 添加 docstring
python generate_docs.py src/module.py --add-docstrings --inplace

# 生成 API 文档
python generate_docs.py src/ --api --format markdown
```

## 📊 生成的文档示例

### README.md 示例

```markdown
# Project Name

简短的项目描述。

## 📦 安装

```bash
pip install project-name
```

## 🚀 快速开始

```python
from project_name import main_function

result = main_function(param1, param2)
print(result)
```

## 📖 API 文档

### 核心模块

#### `module_name`

模块的简短说明。

**主要功能**:
- 功能点 1
- 功能点 2
- 功能点 3

**使用示例**:
```python
from project_name import module_name

# 示例代码
obj = module_name.ClassName()
result = obj.method()
```

#### `module_name.ClassName`

类的说明。

**方法**:
- `method1()` - 方法说明
- `method2(params)` - 方法说明

### 工具函数

#### `function_name(params)`

函数说明。

**参数**:
- `param1` (str): 参数说明
- `param2` (int, optional): 参数说明，默认值为 10

**返回值**:
- `return_type`: 返回值说明

**异常**:
- `ValueError`: 当参数无效时抛出

**示例**:
```python
result = function_name("value", 20)
```

## 📁 项目结构

```
project-name/
├── src/
│   ├── module1.py
│   ├── module2.py
│   └── utils/
├── tests/
├── docs/
└── README.md
```

## 🧪 测试

```bash
pytest tests/
```

## 🤝 贡献

详见 [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 许可证

MIT License
```

### API 文档示例 (Markdown)

```markdown
# API 参考文档

## 模块：calculator

计算器模块，提供基本数学运算。

---

### 类：Calculator

计算器类，支持加减乘除运算。

#### 方法

##### `__init__(self, precision: int = 2)`

初始化计算器。

**参数**:
- `precision` (int): 小数精度，默认为 2

**示例**:
```python
calc = Calculator(precision=4)
```

---

##### `add(self, a: float, b: float) -> float`

两数相加。

**参数**:
- `a` (float): 第一个数
- `b` (float): 第二个数

**返回值**:
- `float`: 两数之和

**异常**:
- `TypeError`: 当参数不是数字时

**示例**:
```python
calc = Calculator()
result = calc.add(10, 20)
print(result)  # 输出：30.0
```

---

##### `divide(self, a: float, b: float) -> float`

两数相除。

**参数**:
- `a` (float): 被除数
- `b` (float): 除数

**返回值**:
- `float`: 商

**异常**:
- `ValueError`: 当除数为零时

**示例**:
```python
calc = Calculator()
result = calc.divide(100, 5)
print(result)  # 输出：20.0
```

---

## 函数

### `calculate_average(numbers: List[float]) -> float`

计算平均值。

**参数**:
- `numbers` (List[float]): 数字列表

**返回值**:
- `float`: 平均值

**异常**:
- `ValueError`: 当列表为空时

**示例**:
```python
from calculator import calculate_average

avg = calculate_average([1, 2, 3, 4, 5])
print(avg)  # 输出：3.0
```
```

### Docstring 补充示例

**补充前**:
```python
def process_data(data, threshold):
    result = []
    for item in data:
        if item.value > threshold:
            result.append(item)
    return result
```

**补充后**:
```python
def process_data(
    data: List[DataItem],
    threshold: float,
) -> List[DataItem]:
    """
    处理数据并过滤超过阈值的项
    
    遍历数据列表，筛选出值大于指定阈值的数据项。
    
    Args:
        data: 待处理的数据列表
        threshold: 过滤阈值
        
    Returns:
        过滤后的数据列表
        
    Raises:
        TypeError: 当输入数据类型不正确时
        
    Example:
        >>> items = [DataItem(10), DataItem(20), DataItem(5)]
        >>> result = process_data(items, 15)
        >>> len(result)
        1
    """
    result = []
    for item in data:
        if item.value > threshold:
            result.append(item)
    return result
```

## 🎯 最佳实践

### 1. Docstring 规范

**Google 风格**:
```python
def function_name(param1, param2):
    """
    函数的简短描述
    
    详细描述（可选），可以跨多行。
    
    Args:
        param1 (type): 参数 1 的描述
        param2 (type): 参数 2 的描述
        
    Returns:
        type: 返回值的描述
        
    Raises:
        ExceptionType: 异常情况的描述
        
    Example:
        >>> function_name(value1, value2)
        expected_result
    """
```

**NumPy 风格**:
```python
def function_name(param1, param2):
    """
    函数的简短描述
    
    详细描述。
    
    Parameters
    ----------
    param1 : type
        参数 1 的描述
    param2 : type
        参数 2 的描述
        
    Returns
    -------
    type
        返回值的描述
        
    Raises
    ------
    ExceptionType
        异常情况的描述
    """
```

### 2. README 结构

```markdown
# 项目名称

[![Build Status](badge-url)]()
[![Coverage Status](badge-url)]()

## 简介

一句话描述项目。

## 特性

- 特性 1
- 特性 2
- 特性 3

## 安装

安装说明。

## 使用指南

### 快速开始

基本使用示例。

### 高级用法

更复杂的示例。

## API 文档

API 链接或简要说明。

## 开发

### 环境设置

```bash
git clone <repository>
cd project
pip install -r requirements-dev.txt
```

### 运行测试

```bash
pytest
```

## 贡献

如何参与项目贡献。

## 变更历史

主要版本变更记录。

## 许可证

License 信息。

## 联系方式

维护者信息和联系方式。
```

### 3. 文档维护

- ✅ 保持文档与代码同步更新
- ✅ 使用自动化工具生成文档
- ✅ 定期审查文档质量
- ✅ 包含实际可运行的示例
- ❌ 避免过时或不准确的文档

## 🔗 相关工具

### 文档生成工具

1. **Sphinx**: Python 文档生成器
   ```bash
   pip install sphinx
   sphinx-quickstart
   ```

2. **MkDocs**: Markdown 文档站点
   ```bash
   pip install mkdocs
   mkdocs new my-project
   ```

3. **pydoc**: Python 内置文档工具
   ```bash
   pydoc module_name
   pydoc -w module_name  # 生成 HTML
   ```

4. **pdoc**: 现代 Python 文档工具
   ```bash
   pip install pdoc
   pdoc module_name
   ```

### 文档检查工具

```bash
# 检查 docstring 完整性
pip install interrogate
interrogate src/

# 检查文档拼写
pip install pyspelling
pyspelling -c .spelling.yaml
```

## 📚 学习资源

- [Sphinx 官方文档](https://www.sphinx-doc.org/)
- [PEP 257 - Docstring 约定](https://peps.python.org/pep-0257/)
- [Google Python 风格指南](https://google.github.io/styleguide/pyguide.html)
- [reStructuredText 语法](https://docutils.sourceforge.io/rst.html)
