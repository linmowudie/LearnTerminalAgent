# 📁 项目文件组织说明

## 🎯 快速导航

### 📄 文档

- **正式文档** → [`docs/`](docs/) - 用户指南、配置说明
- **开发文档** → [`docs/dev/`](docs/dev/) - 问题修复、优化总结
- **学习教程** → [`docs/learn/`](docs/learn/) - 系列教程

### 🧪 测试

- **正式测试** → [`tests/`](tests/) - 端到端、集成测试
- **开发测试** → [`dev_tests/`](dev_tests/) - 功能验证、调试测试
- **临时测试** → [`dev_tests/temp/`](dev_tests/temp/) - 一次性测试

### 🛠️ 工具

- **脚本工具** → [`scripts/`](scripts/) - 辅助工具、查看脚本
- **日志文件** → [`logs/`](logs/) - 系统日志

---

## 📂 完整目录结构

```
LearnTerminalAgent/
├── docs/                          # 正式文档
│   ├── README.md                  # 文档导航
│   ├── PROJECT_OVERVIEW.md        # 项目概览
│   ├── QUICK_START.md             # 快速开始
│   ├── CONFIG_FILE_GUIDE.md       # 配置文件指南
│   ├── LOG_FILE_GUIDE.md          # 日志文件指南
│   ├── help.md                    # 帮助信息
│   ├── guides/                    # 指南系列
│   ├── learn/                     # 学习系列
│   └── dev/                       # 开发过程文档
│       ├── AGENT_TOOL_CALLING_FIX.md
│       ├── OPTIMIZATION_SUMMARY.md
│       └── [更多...]
│
├── tests/                         # 正式测试
│   ├── test_workspace.py
│   ├── test_workspace_e2e.py
│   └── test_workspace_integration.py
│
├── dev_tests/                     # 开发测试
│   ├── test_agent_tools.py
│   ├── test_bash_tool.py
│   ├── test_responsiveness.py
│   ├── test_model_diagnostic.py
│   ├── [更多...]
│   └── temp/                      # 临时测试
│       └── test.txt
│
├── scripts/                       # 工具脚本
│   └── view_logs.py               # 日志查看
│
├── logs/                          # 日志文件
│   ├── Agent_*.log
│   ├── Tools_*.log
│   └── [更多...]
│
├── src/                           # 源代码
│   └── learn_agent/               # Agent 核心代码
│
├── config/                        # 配置文件
├── data/                          # 数据文件
├── skills/                        # 技能定义
└── workspace/                     # 工作空间
```

---

## 🚀 常用命令

### 运行测试

```bash
# 运行正式测试
python -m pytest tests/

# 运行开发测试
python dev_tests/test_responsiveness.py

# 运行所有开发测试
for file in dev_tests/test_*.py; do python $file; done
```

### 查看日志

```bash
# 使用脚本查看
python scripts/view_logs.py

# 直接查看（Windows）
Get-Content logs\Agent_*.log -Tail 50

# 直接查看（Linux/Mac）
tail -n 50 logs/Agent_*.log
```

### 查看文档

```bash
# 打开正式文档
start docs\README.md  # Windows
open docs/README.md   # Mac

# 打开开发文档
start docs\dev\OPTIMIZATION_SUMMARY.md
```

---

## 📝 文件分类速查

| 文件类型 | 存放位置 | 示例 |
|---------|---------|------|
| 用户指南 | `docs/` | `CONFIG_FILE_GUIDE.md` |
| 开发文档 | `docs/dev/` | `OPTIMIZATION_SUMMARY.md` |
| 正式测试 | `tests/` | `test_workspace.py` |
| 开发测试 | `dev_tests/` | `test_responsiveness.py` |
| 临时测试 | `dev_tests/temp/` | `test.txt` |
| 工具脚本 | `scripts/` | `view_logs.py` |
| 日志文件 | `logs/` | `Agent_20260307_*.log` |

---

## 💡 为什么要这样组织？

### ✅ 好处

1. **清晰的视觉** - 根目录只有核心文件
2. **快速的查找** - 按类别组织，一目了然
3. **方便的维护** - 同类文件在一起
4. **灵活的管理** - 正式/开发分离

### 🎯 分类原则

- **正式 vs 开发** - 用户看的放 docs/，开发者看的放 docs/dev/
- **稳定 vs 临时** - 稳定的测试放 tests/，临时的放 dev_tests/
- **使用 vs 工具** - 主要代码放 src/，辅助工具放 scripts/

---

## 🔄 如何贡献文件

### 新增文档时

1. **判断类型**:
   - 用户指南 → `docs/`
   - 开发记录 → `docs/dev/`

2. **命名规范**:
   - 使用英文大写字母和下划线
   - 例如：`FEATURE_DESCRIPTION.md`

3. **更新索引**:
   - 在相应 README 中添加链接

### 新增测试时

1. **判断类型**:
   - 正式测试 → `tests/`
   - 开发测试 → `dev_tests/`
   - 临时测试 → `dev_tests/temp/`

2. **命名规范**:
   - 测试文件以 `test_` 开头
   - 例如：`test_new_feature.py`

---

## 📖 详细指南

- **整理计划**: [`docs/DEV_FILES_ORGANIZATION_PLAN.md`](docs/DEV_FILES_ORGANIZATION_PLAN.md)
- **使用指南**: [`docs/DEV_FILES_ORGANIZATION_GUIDE.md`](docs/DEV_FILES_ORGANIZATION_GUIDE.md)
- **主文档**: [`README.md`](README.md)

---

## ✨ 整理效果

**整理前**: 
- ❌ 根目录 20+ 个散乱文件
- ❌ 文档和测试混在一起
- ❌ 难以查找和维护

**整理后**:
- ✅ 根目录清爽整洁
- ✅ 文档分类清晰
- ✅ 测试集中管理
- ✅ 查找快速方便

**开发体验提升**: ⭐⭐⭐⭐⭐

---

**更新日期**: 2026-03-07  
**版本**: v1.0
