# LearnTerminalAgent Skills 目录

本目录用于存放自定义技能和知识模块。

## 📁 目录说明

Skills（技能）是 LearnTerminalAgent 的扩展机制，允许你：

- 加载外部知识库
- 添加特定领域的专业知识
- 扩展 Agent 的能力边界
- 按需加载/卸载技能模块

## 🎯 技能类型

### 1. 文档类技能

包含特定领域的文档和知识：

```
skills/
└── pdf-processing/
    ├── knowledge.md       # PDF 处理知识
    ├── examples.py        # 示例代码
    └── best-practices.md  # 最佳实践
```

### 2. 代码类技能

提供代码模板和工具函数：

```
skills/
└── web-scraping/
    ├── templates/         # 爬虫模板
    ├── utils.py          # 工具函数
    └── README.md         # 使用说明
```

### 3. 配置类技能

定义特定的工作流和配置：

```
skills/
└── data-analysis/
    ├── workflow.json      # 工作流程配置
    └── parameters.yaml    # 参数设置
```

## 🔧 使用技能

### 在 CLI 中加载技能

```bash
LearnAgent >> /skills
LearnAgent >> 加载 pdf 技能
```

### 在代码中使用

```python
from learn_agent.skills import SkillManager

skills = SkillManager()

# 加载技能
skills.load_skill("pdf-processing")

# 使用技能
result = skills.execute("pdf-processing", "分析这个 PDF 文件")
```

## 📝 创建新技能

### 技能结构

每个技能应该包含：

1. **README.md** - 技能说明和使用方法
2. **knowledge/** - 知识库文件
3. **examples/** - 示例代码
4. **tests/** - 技能测试（可选）

### 示例：创建 Python 技能

```
skills/
└── python-expert/
    ├── README.md
    ├── knowledge/
    │   ├── syntax.md
    │   ├── best-practices.md
    │   └── common-patterns.md
    ├── examples/
    │   ├── basic.py
    │   └── advanced.py
    └── tests/
        └── test_python_skill.py
```

### README.md 模板

```markdown
# Python Expert Skill

## 功能描述
提供 Python 编程相关的专业知识和建议。

## 适用场景
- 代码审查
- 最佳实践建议
- 性能优化
- 调试帮助

## 使用示例
LearnAgent >> 请帮我 review 这段 Python 代码

## 依赖项
- Python 3.8+
- 相关库...
```

## 🎯 技能管理

### 列出可用技能

```bash
LearnAgent >> /skills
```

### 加载技能

```bash
LearnAgent >> 加载 python-expert 技能
```

### 卸载技能

```bash
LearnAgent >> 卸载 python-expert 技能
```

## 📚 内置技能（计划中）

未来可能包含的技能：

- [ ] **PDF Processing** - PDF 文档处理
- [ ] **Data Analysis** - 数据分析技能
- [ ] **Web Development** - Web 开发技能
- [ ] **Database Design** - 数据库设计
- [ ] **API Design** - API 设计最佳实践
- [ ] **Security Review** - 代码安全审查
- [ ] **Performance Optimization** - 性能优化

## 🤝 贡献技能

欢迎分享你创建的技能！

1. 在 GitHub 创建 Issue 描述你的技能
2. 提交 Pull Request 到 `skills/` 目录
3. 包含完整的文档和测试

仓库地址：https://github.com/linmowudie/LearnTerminalAgent

## 🔗 相关文档

- [s05 - Skill Loading](../learn/s05-skill-loading.md) - 技能加载机制
- [工具说明](guides/tools.md) - 可用工具列表
- [项目概述](PROJECT_OVERVIEW.md) - 整体架构说明
