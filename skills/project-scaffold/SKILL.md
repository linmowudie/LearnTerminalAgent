---
name: project-scaffold
description: 项目脚手架生成器，快速创建标准项目目录结构
tags: 项目初始化，目录结构，脚手架
---

# Project Scaffold - 项目脚手架生成器

## 🎯 功能描述

提供标准化的项目目录结构生成功能，支持多种项目类型的脚手架模板。

## ✨ 核心特性

1. **快速初始化**: 一键生成标准项目结构
2. **可定制化**: 支持自定义项目名称和配置
3. **最佳实践**: 遵循业界标准目录布局
4. **多语言支持**: Python、JavaScript、TypeScript 等

## 📁 支持的脚手架类型

### Python 项目模板

```
project-name/
├── src/
│   └── project_name/
│       ├── __init__.py
│       ├── main.py
│       └── core/
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── docs/
├── scripts/
├── config/
├── .gitignore
├── README.md
├── requirements.txt
├── pyproject.toml
└── setup.py
```

### Web 项目模板 (React/Vue)

```
project-name/
├── public/
├── src/
│   ├── components/
│   ├── pages/
│   ├── utils/
│   ├── styles/
│   ├── App.jsx
│   └── index.js
├── package.json
├── vite.config.js
└── README.md
```

### 通用库模板

```
project-name/
├── lib/
├── examples/
├── tests/
├── docs/
├── .gitignore
├── LICENSE
├── README.md
└── package.json / setup.py
```

## 🛠️ 使用示例

### 示例 1: 创建 Python 项目

```bash
# 使用脚本创建
python scripts/scaffold.py create python my_project

# 或使用 Agent 命令
LearnAgent >> 帮我创建一个名为 my_project 的 Python 项目脚手架
```

### 示例 2: 创建 Web 项目

```bash
# 使用脚本创建
python scripts/scaffold.py create react my_web_app

# 或使用 Agent 命令
LearnAgent >> 为 my_web_app 生成 React 项目结构
```

### 示例 3: 自定义目录结构

```bash
# 指定特定目录
python scripts/scaffold.py create python custom_project --dirs "src,tests,docs,examples"
```

## 📦 配套脚本

### scaffold.py 使用方法

**位置**: `skills/project-scaffold/scaffold.py`

**基本用法**:
```bash
# 查看帮助
python scaffold.py --help

# 创建 Python 项目
python scaffold.py create python my_project

# 创建 TypeScript 项目
python scaffold.py create typescript my_ts_project

# 创建简单目录结构
python scaffold.py create simple my_simple_project
```

**参数说明**:
- `create`: 创建新项目
- `<type>`: 项目类型 (python, react, vue, typescript, simple)
- `<name>`: 项目名称
- `--dirs`: 自定义目录列表（逗号分隔）
- `--force`: 强制覆盖已存在的目录

## 🔧 代码示例

### 在 Python 代码中使用

```python
from skills.project_scaffold.scaffold import create_project

# 创建 Python 项目
create_project(
    name="my_awesome_project",
    project_type="python",
    force=True
)

print("项目创建完成！")
```

### 自定义项目结构

```python
from skills.project_scaffold.scaffold import ProjectScaffold

scaffold = ProjectScaffold()

# 定义自定义结构
structure = {
    "my_project": {
        "src": {"my_package": ["__init__.py", "main.py"]},
        "tests": ["test_main.py"],
        "docs": [],
        "README.md": "",
        "requirements.txt": ""
    }
}

scaffold.create_from_dict(structure)
```

## 📋 生成的文件说明

### Python 项目必选文件

1. **`pyproject.toml`**: 现代 Python 项目配置文件
2. **`requirements.txt`**: 依赖列表
3. **`setup.py`**: 安装配置（可选）
4. **`.gitignore`**: Git 忽略规则
5. **`README.md`**: 项目说明文档
6. **`src/__init__.py`**: 包初始化文件

### 推荐的文件内容

#### `.gitignore` (Python)
```gitignore
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
```

#### `README.md` 模板
```markdown
# Project Name

简短的项目描述。

## 安装

```bash
pip install -e .
```

## 使用方法

```python
from project_name import main
```

## 开发

```bash
pip install -r requirements-dev.txt
pytest
```

## License

MIT
```

## 🎓 最佳实践

### 1. 命名规范

- 项目名称使用小写和下划线：`my_project`
- 包名与项目名称一致
- 避免使用连字符（-）在包名中

### 2. 目录组织

- 源代码放在 `src/` 目录下
- 测试代码放在 `tests/` 目录下
- 文档放在 `docs/` 目录下
- 脚本工具放在 `scripts/` 目录下

### 3. 配置文件

- 优先使用 `pyproject.toml` (现代标准)
- 保留 `setup.py` 用于兼容性
- 使用 `requirements.txt` 锁定依赖版本

### 4. 文档编写

- README 包含：简介、安装、使用示例、开发指南
- 添加 CHANGELOG.md 记录变更历史
- 编写 CONTRIBUTING.md 说明贡献流程

## 🚀 扩展建议

可以进一步扩展此技能：

1. **添加更多模板**: Django, FastAPI, Flask 等框架模板
2. **交互式创建**: 通过问答方式收集项目信息
3. **Git 初始化**: 自动执行 git init 和首次提交
4. **虚拟环境**: 自动创建和激活 venv
5. **依赖安装**: 自动安装 requirements.txt 中的依赖

## 📝 更新日志

- **v1.0.0**: 初始版本，支持 Python/Web 项目脚手架
