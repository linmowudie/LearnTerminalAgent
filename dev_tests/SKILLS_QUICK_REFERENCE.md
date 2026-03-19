# Skills 快速参考指南

## 📦 已安装的 Skills

| Skill | 功能 | 脚本 |
|-------|------|------|
| **project-scaffold** | 项目脚手架生成 | `scaffold.py` |
| **code-style-guide** | 代码规范检查 | `check_style.py` |
| **git-workflow** | Git 工作流管理 | `git_helpers.py` |
| **test-generator** | 测试用例生成 | `generate_tests.py` |
| **doc-generator** | 文档自动生成 | `generate_docs.py` |

---

## ⚡ 快速开始

### 1. 创建新项目

```bash
# Python 项目
python skills/project-scaffold/scaffold.py create python my_project

# React 项目
python skills/project-scaffold/scaffold.py create react my_app

# 查看帮助
python skills/project-scaffold/scaffold.py --help
```

### 2. 代码开发

```bash
# 创建功能分支
python skills/git-workflow/git_helpers.py branch create feature my-feature

# 编写代码后检查规范
python skills/code-style-guide/check_style.py src/

# 生成测试
python skills/test-generator/generate_tests.py src/my_module.py

# 交互式提交
python skills/git-workflow/git_helpers.py commit -i
```

### 3. 生成文档

```bash
# 生成 README
python skills/doc-generator/generate_docs.py src/ --readme

# 生成 API 文档
python skills/doc-generator/generate_docs.py src/ --api -o docs/api/
```

---

## 🔧 常用命令

### Project Scaffold

```bash
# 创建 Python 项目
python skills/project-scaffold/scaffold.py create python my_project

# 创建 TypeScript 项目
python skills/project-scaffold/scaffold.py create typescript my_lib

# 自定义目录
python skills/project-scaffold/scaffold.py create python my_project --dirs "src,tests,docs,examples"

# 强制覆盖
python skills/project-scaffold/scaffold.py create python existing_project --force
```

### Code Style Guide

```bash
# 检查单个文件
python skills/code-style-guide/check_style.py src/module.py

# 递归检查目录
python skills/code-style-guide/check_style.py src/ -r

# 生成报告
python skills/code-style-guide/check_style.py src/ --report style_report.md

# 忽略某些规则
python skills/code-style-guide/check_style.py src/ --ignore E002,E003

# 静默模式（仅显示总数）
python skills/code-style-guide/check_style.py src/ --quiet
```

### Git Workflow

```bash
# 列出分支
python skills/git-workflow/git_helpers.py branch list

# 创建功能分支
python skills/git-workflow/git_helpers.py branch create feature user-login

# 创建 bugfix 分支
python skills/git-workflow/git_helpers.py branch create bugfix issue-123

# 删除分支
python skills/git-workflow/git_helpers.py branch delete feature/old-feature

# 清理已合并分支
python skills/git-workflow/git_helpers.py branch cleanup

# 交互式提交
python skills/git-workflow/git_helpers.py commit -i

# 规范提交
python skills/git-workflow/git_helpers.py commit feat auth "add user login functionality"

# 查看历史
python skills/git-workflow/git_helpers.py log --author "John" -n 10

# 统计信息
python skills/git-workflow/git_helpers.py stats

# 查看冲突
python skills/git-workflow/git_helpers.py conflicts show
```

### Test Generator

```bash
# 为单个文件生成测试
python skills/test-generator/generate_tests.py src/calculator.py

# 为整个目录生成测试
python skills/test-generator/generate_tests.py src/ -r

# 包含 Mock 对象
python skills/test-generator/generate_tests.py src/service.py --with-mock

# 跳过已存在的测试
python skills/test-generator/generate_tests.py src/ --skip-existing

# 指定输出目录
python skills/test-generator/generate_tests.py src/ -o tests/
```

### Doc Generator

```bash
# 生成 README
python skills/doc-generator/generate_docs.py src/ --readme -o README.md

# 生成 API 文档（Markdown）
python skills/doc-generator/generate_docs.py src/ --api --format markdown

# 生成 API 文档（RST）
python skills/doc-generator/generate_docs.py src/ --api --format rst

# 添加 docstring 建议
python skills/doc-generator/generate_docs.py src/module.py --add-docstrings

# 原地修改文件
python skills/doc-generator/generate_docs.py src/module.py --add-docstrings --inplace
```

---

## 💡 使用场景

### 场景 1: 从零开始新项目

```bash
# 1. 创建项目结构
python skills/project-scaffold/scaffold.py create python data_processor

# 2. 初始化 Git
cd data_processor
git init

# 3. 首次提交
git add .
python skills/git-workflow/git_helpers.py commit chore project "initial project structure"

# 4. 开始开发
python skills/git-workflow/git_helpers.py branch create feature data-loading

# ... 编写代码 ...

# 5. 检查代码质量
python skills/code-style-guide/check_style.py src/

# 6. 生成测试
python skills/test-generator/generate_tests.py src/data_loader.py

# 7. 运行测试并完善
pytest tests/test_data_loader.py

# 8. 提交代码
python skills/git-workflow/git_helpers.py commit -i
```

### 场景 2: 代码重构

```bash
# 1. 检查当前代码规范
python skills/code-style-guide/check_style.py src/ --report before_refactor.md

# ... 进行重构 ...

# 2. 再次检查
python skills/code-style-guide/check_style.py src/ --report after_refactor.md

# 3. 比较报告
diff before_refactor.md after_refactor.md
```

### 场景 3: 准备发布

```bash
# 1. 生成完整文档
python skills/doc-generator/generate_docs.py src/ --readme --api --with-examples

# 2. 确保测试覆盖
python skills/test-generator/generate_tests.py src/ --skip-existing

# 3. 运行所有测试
pytest tests/ --cov=src --cov-report=html

# 4. 创建发布分支
python skills/git-workflow/git_helpers.py branch create release v1.0.0

# 5. 提交文档更新
git add .
python skills/git-workflow/git_helpers.py commit docs release "prepare v1.0.0 release"
```

---

## 🎯 最佳实践

### 1. 项目初始化

✅ 使用脚手架工具创建标准结构
✅ 立即初始化 Git 版本控制
✅ 创建第一个规范提交

### 2. 日常开发

✅ 使用功能分支开发
✅ 遵循 Conventional Commits
✅ 及时生成和运行测试
✅ 定期检查代码规范

### 3. 代码审查

✅ 提交前运行代码规范检查
✅ 确保测试覆盖率
✅ 更新文档

### 4. 发布流程

✅ 生成完整 API 文档
✅ 更新 README
✅ 运行所有测试
✅ 创建 release 分支

---

## 📊 输出示例

### Code Style Check 输出

```
============================================================
代码规范检查结果
============================================================

📄 src/calculator.py
------------------------------------------------------------
  ⚠️  第   5 行 [E003 ] 缺少模块 docstring
  ⚠️  第  12 行 [N002 ] 函数名应该使用小写 + 下划线命名：'MyFunction'
  ❌  第  25 行 [E002 ] 行宽超过 88 字符

============================================================
总计：1 个错误，2 个警告
============================================================
```

### Git Stats 输出

```
============================================================
Git 统计信息
============================================================
总提交数：156
文件变更：42
新增行数：3245
删除行数：1123

作者贡献:
  Alice: 89 次提交
  Bob: 45 次提交
  Charlie: 22 次提交
============================================================
```

### Test Generator 输出

```
📝 正在为 calculator.py 生成测试...
✅ 测试文件已生成：tests/test_calculator.py

下一步:
  1. 打开 tests/test_calculator.py
  2. 完善 TODO 标记的测试用例
  3. 运行 pytest tests/test_calculator.py
```

---

## 🐛 常见问题

### Q: 脚本无法执行？

A: 确保 Python 在 PATH 中，或使用完整路径：
```bash
python /full/path/to/script.py
```

### Q: 技能未被加载？

A: 检查 SKILL.md 文件格式，确保包含 YAML frontmatter：
```markdown
---
name: skill-name
description: 技能描述
tags: 标签 1，标签 2
---
```

### Q: 如何自定义模板？

A: 编辑对应技能的脚本文件，修改模板字典或添加新的模板类。

---

## 🔗 相关资源

- [Skills 完整文档](../skills/) - 每个技能的详细说明
- [LearnTerminalAgent](../README.md) - 主项目文档
- [开发规范](../docs/guides/tools.md) - 工具和开发指南

---

## 📞 获取帮助

```bash
# 任何脚本都可以通过 --help 查看帮助
python skills/<skill-name>/<script>.py --help

# 例如
python skills/project-scaffold/scaffold.py --help
python skills/git-workflow/git_helpers.py --help
```
