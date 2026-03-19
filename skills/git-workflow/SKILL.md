---
name: git-workflow
description: Git 工作流助手，提供分支管理、提交规范和合并冲突解决方案
tags: Git,版本控制，工作流，最佳实践
---

# Git Workflow - Git 工作流助手

## 🎯 功能描述

提供 Git 操作的最佳实践指导、自动化脚本和常见问题解决方案，帮助团队高效协作。

## ✨ 核心功能

1. **分支管理**: 创建、删除、清理分支
2. **提交规范**: Conventional Commits 检查
3. **合并协助**: 解决合并冲突指南
4. **历史记录**: 查看和分析提交历史
5. **工作流模板**: Git Flow、GitHub Flow、Trunk Based

## 📋 支持的 Git 工作流

### 1. Git Flow (推荐用于发布周期明确的项目)

```
main (production)
  │
  ├── develop (integration)
  │     │
  │     ├── feature/login
  │     ├── feature/dashboard
  │     └── bugfix/issue-123
  │
  ├── release/v1.0.0
  └── hotfix/critical-bug
```

**分支类型**:
- `main`: 生产环境代码
- `develop`: 开发集成分支
- `feature/*`: 新功能开发
- `release/*`: 发布准备
- `hotfix/*`: 紧急修复

### 2. GitHub Flow (推荐用于持续部署项目)

```
main
  │
  ├── feature/login
  ├── feature/dashboard
  └── bugfix/issue-123
```

**简单流程**:
1. 从 `main` 创建功能分支
2. 开发并提交
3. 创建 Pull Request
4. Review 后合并到 `main`
5. 立即部署

### 3. Trunk Based Development (推荐用于敏捷团队)

```
trunk (main)
  │
  ├── short-lived-branch-1
  ├── short-lived-branch-2
  └── feature-flag-development
```

**核心原则**:
- 所有开发者在主干上协作
- 短生命周期分支（< 1 天）
- 使用功能开关
- 频繁小步提交

## 🛠️ 使用示例

### 示例 1: 创建功能分支

```bash
# 使用脚本创建标准化的功能分支
python git_helpers.py branch create feature user-authentication

# 手动操作
git checkout develop
git pull origin develop
git checkout -b feature/user-authentication
```

### 示例 2: 提交代码

```bash
# 使用 Conventional Commits 规范
git add .
git commit -m "feat(auth): add user login functionality"

# 或使用交互式工具
python git_helpers.py commit
```

### 示例 3: 合并分支

```bash
# 合并功能分支到 develop
git checkout develop
git pull origin develop
git merge --no-ff feature/user-authentication
git push origin develop
```

### 示例 4: 解决冲突

```bash
# 当遇到合并冲突时
git merge develop
# 出现冲突提示

# 使用工具查看冲突
python git_helpers.py conflicts show

# 解决后标记为已解决
git add conflicted_file.py
git commit
```

## 🔧 配套脚本

### git_helpers.py 使用方法

```bash
# 查看帮助
python git_helpers.py --help

# 分支管理
python git_helpers.py branch list
python git_helpers.py branch create feature my-feature
python git_helpers.py branch cleanup

# 提交辅助
python git_helpers.py commit
python git_helpers.py commit "feat: add new feature"

# 查看历史
python git_helpers.py log --author "John" --since "2024-01-01"

# 统计信息
python git_helpers.py stats
```

## 📝 提交规范 (Conventional Commits)

### 格式

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### 类型说明

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档变更
- `style`: 代码格式（不影响代码运行）
- `refactor`: 重构（既不是新功能也不是 bug 修复）
- `test`: 添加或修改测试
- `chore`: 构建过程或辅助工具变更

### 示例

```bash
# 新功能
git commit -m "feat(auth): add user registration"

# 修复 bug
git commit -m "fix(api): resolve null pointer in user service"

# 文档更新
git commit -m "docs(readme): update installation instructions"

# 重构
git commit -m "refactor(core): simplify validation logic"

# 多个变更范围
git commit -m """feat(ui): add dark mode support

- Add theme toggle component
- Implement theme switching logic
- Update CSS variables for dark theme

Closes #123"""
```

## 💻 Git 命令速查表

### 基础操作

```bash
# 克隆仓库
git clone <repository-url>

# 查看状态
git status

# 添加文件
git add file.py
git add .  # 添加所有文件

# 提交
git commit -m "message"

# 推送
git push origin branch-name
```

### 分支操作

```bash
# 创建分支
git checkout -b feature/new-feature
git switch -c feature/new-feature

# 切换分支
git checkout develop
git switch develop

# 查看分支
git branch
git branch -a  # 查看所有分支

# 删除分支
git branch -d feature/old-feature
git branch -D feature/old-feature  # 强制删除

# 合并分支
git checkout main
git merge feature/new-feature
```

### 远程操作

```bash
# 拉取最新代码
git pull origin develop

# 仅获取不合并
git fetch origin

# 推送到远程
git push origin feature-branch

# 跟踪远程分支
git checkout -b local-branch origin/remote-branch
```

### 查看历史

```bash
# 查看日志
git log
git log --oneline
git log --graph --oneline --all

# 查看特定文件历史
git log --follow file.py

# 查看作者贡献
git log --author="John"
git shortlog -sn
```

### 撤销操作

```bash
# 撤销工作区修改
git checkout -- file.py
git restore file.py

# 撤销暂存
git reset HEAD file.py
git restore --staged file.py

# 修改最后一次提交
git commit --amend

# 回退提交
git revert HEAD
git revert HEAD~3..HEAD
```

## 🚨 常见问题解决

### 1. 解决合并冲突

**步骤**:

```bash
# 1. 开始合并
git merge develop

# 2. 查看冲突文件
git status

# 3. 编辑冲突文件，找到冲突标记：
<<<<<<< HEAD
你的修改
=======
其他人的修改
>>>>>>> develop

# 4. 解决冲突后标记为已解决
git add conflicted_file.py

# 5. 完成合并
git commit
```

**使用工具辅助**:
```bash
# 使用 mergetool
git mergetool

# 使用脚本查看冲突
python git_helpers.py conflicts show
```

### 2. 误删分支恢复

```bash
# 查看 reflog
git reflog

# 找到删除前的 commit hash
# 重新创建分支
git branch recovered-branch <commit-hash>
```

### 3. 清理本地分支

```bash
# 删除已合并的本地分支
git branch --merged | grep -v "\*\|main\|develop" | xargs git branch -d

# 删除已经不存在的远程分支的本地跟踪分支
git fetch -p && for branch in $(git for-each-ref --format '%(refname) %(upstream:track)' refs/heads | awk '$2 == "[gone]" {sub("refs/heads/", "", $1); print $1}'); do git branch -D $branch; done
```

### 4. 重置提交历史

```bash
# 软重置（保留更改）
git reset --soft HEAD~3

# 混合重置（默认）
git reset HEAD~3

# 硬重置（丢弃更改）
git reset --hard HEAD~3

# 推送到远程（谨慎使用）
git push origin --force
```

## 🎯 最佳实践

### 1. 提交频率

- ✅ 频繁提交，小步快跑
- ✅ 每个提交完成一个小的功能点
- ❌ 避免超大提交（> 500 行）
- ❌ 避免多天不提交

### 2. 提交信息

- ✅ 清晰描述变更内容
- ✅ 使用祈使句语气
- ✅ 首字母不大写，结尾不加句号
- ❌ 避免模糊的描述（如 "fix bug", "update"）

### 3. 分支命名

- ✅ 使用小写字母和连字符
- ✅ 添加类型前缀（feature/, bugfix/, hotfix/）
- ✅ 使用 JIRA issue 号或简短描述
- ❌ 避免使用特殊字符和空格
- ❌ 避免过长的分支名

### 4. Code Review

- ✅ 创建 Pull Request 时提供清晰描述
- ✅ 关联相关的 Issue
- ✅ 及时响应 Review 意见
- ✅ Review 他人代码时保持尊重
- ❌ 避免超大 PR（> 400 行）

## 📊 团队协作建议

### Git 工作流选择

| 项目类型 | 推荐工作流 | 原因 |
|---------|-----------|------|
| 企业级应用 | Git Flow | 明确的发布周期 |
| SaaS/云服务 | GitHub Flow | 持续部署 |
| 开源项目 | GitHub Flow + Fork | 社区协作 |
| 快速迭代产品 | Trunk Based | 快速反馈 |

### 权限管理

```
main (保护分支)
  ├── 只能通过 PR 合并
  ├── 需要至少 1 人 review
  └── CI 必须通过

develop (保护分支)
  ├── 只能通过 PR 合并
  └── 建议有 review

feature/* (自由分支)
  └── 开发者自由创建
```

## 🔗 相关工具

1. **Git 客户端**:
   - GitKraken (图形化界面)
   - SourceTree (免费图形化工具)
   - VSCode Git 插件

2. **CI/CD 集成**:
   - GitHub Actions
   - GitLab CI
   - Jenkins

3. **代码质量**:
   - SonarQube
   - CodeClimate

## 📚 学习资源

- [Pro Git 书籍](https://git-scm.com/book/en/v2)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
