# 开发文档整理计划

## 📋 目标

整理开发过程中生成的临时文档和测试文件，保持项目结构清晰。

---

## 🎯 分类规则

### 1. 正式文档 (保留在 docs/)

**标准**:
- ✅ 项目核心文档（README, QUICK_START 等）
- ✅ 用户指南（CONFIG_FILE_GUIDE, LOG_FILE_GUIDE 等）
- ✅ 架构说明（PROJECT_OVERVIEW 等）
- ✅ 系列教程（learn/ 目录）

**文件列表**:
```
docs/
├── README.md                      # 保持
├── PROJECT_OVERVIEW.md            # 保持
├── QUICK_START.md                 # 保持
├── CONFIG_FILE_GUIDE.md           # 保持
├── LOG_FILE_GUIDE.md              # 保持
└── help.md                        # 保持
```

### 2. 开发过程文档 (移动到 docs/dev/)

**标准**:
- ⚠️ 问题修复记录
- ⚠️ 优化总结
- ⚠️ 实施计划
- ⚠️ 诊断指南

**文件列表**:
```
docs/dev/
├── AGENT_TOOL_CALLING_FIX.md           # 工具调用修复
├── STREAM_FIX_NOTES.md                 # 流式输出修复
├── RELATIVE_PATH_FIX.md                # 路径修复
├── WORKSPACE_INITIALIZATION_FIX.md     # 工作空间初始化修复
├── AGENT_RESPONSE_OPTIMIZATION_PLAN.md # 响应优化计划
├── OPTIMIZATION_SUMMARY.md             # 优化总结
├── LOGGING_GUIDE.md                    # 日志指南（旧版）
├── LOGGING_SUMMARY.md                  # 日志总结（旧版）
├── LOGGING_OPTIMIZATION_SUMMARY.md     # 日志优化总结
├── LOG_SYSTEM_QUIET_MODE_SUMMARY.md    # 安静模式总结
├── MODEL_RESPONSE_DIAGNOSTIC.md        # 模型诊断指南
├── MODEL_RESPONSE_DIAGNOSTIC_IMPLEMENTATION.md # 诊断实施
├── WORKSPACE_EXAMPLES.md               # 工作空间示例
├── WORKSPACE_IMPLEMENTATION_SUMMARY.md # 工作空间实现总结
└── STREAM_OUTPUT_GUIDE.md              # 流式输出指南（旧版）
```

### 3. 测试文件分类

#### A. 正式测试 (保留在 tests/)

**标准**:
- ✅ 端到端测试
- ✅ 集成测试
- ✅ 单元测试

**文件列表**:
```
tests/
├── test_workspace.py              # 工作空间测试
├── test_workspace_e2e.py          # 端到端测试
└── test_workspace_integration.py  # 集成测试
```

#### B. 开发测试 (移动到 dev_tests/)

**标准**:
- ⚠️ 功能验证测试
- ⚠️ 调试测试
- ⚠️ 场景测试
- ⚠️ 诊断测试

**文件列表**:
```
dev_tests/
├── test_agent_tools.py            # Agent 工具测试
├── test_bash_tool.py              # Bash 工具测试
├── test_cross_directory.py        # 跨目录测试
├── test_e2e_agent.py              # Agent 端到端测试
├── test_import_order.py           # 导入顺序测试
├── test_improved_prompt.py        # 提示词改进测试
├── test_logging.py                # 日志测试
├── test_memorywords.py            # 记忆词测试
├── test_model_diagnostic.py       # 模型诊断测试
├── test_persional.py              # 个人测试
├── test_real_scenario.py          # 真实场景测试
├── test_responsiveness.py         # 响应测试
├── test_startup.py                # 启动测试
└── verify_workspace.py            # 工作空间验证
```

#### C. 临时测试文件 (移动到 dev_tests/temp/)

**标准**:
- 🔧 一次性测试
- 🔧 实验性测试
- 🔧 调试脚本

**文件列表**:
```
dev_tests/temp/
├── test.txt                       # 临时测试文件
└── [未来临时测试]
```

### 4. 工具脚本 (移动到 scripts/)

**标准**:
- 🔧 辅助工具
- 🔧 查看脚本
- 🔧 实用程序

**文件列表**:
```
scripts/
├── view_logs.py                   # 日志查看脚本
└── [其他工具脚本]
```

---

## 📁 新的目录结构

```
ProjectRoot/
├── docs/                          # 正式文档
│   ├── README.md
│   ├── PROJECT_OVERVIEW.md
│   ├── QUICK_START.md
│   ├── CONFIG_FILE_GUIDE.md
│   ├── LOG_FILE_GUIDE.md
│   ├── help.md
│   ├── guides/                    # 指南系列
│   │   ├── README.md
│   │   ├── config-guide.md
│   │   ├── quickstart.md
│   │   └── tools.md
│   └── learn/                     # 学习系列
│       └── [教程文件]
│
├── docs/dev/                      # 开发过程文档
│   ├── AGENT_TOOL_CALLING_FIX.md
│   ├── STREAM_FIX_NOTES.md
│   ├── RELATIVE_PATH_FIX.md
│   ├── WORKSPACE_INITIALIZATION_FIX.md
│   ├── AGENT_RESPONSE_OPTIMIZATION_PLAN.md
│   ├── OPTIMIZATION_SUMMARY.md
│   ├── LOGGING_GUIDE.md
│   ├── LOGGING_SUMMARY.md
│   ├── LOGGING_OPTIMIZATION_SUMMARY.md
│   ├── LOG_SYSTEM_QUIET_MODE_SUMMARY.md
│   ├── MODEL_RESPONSE_DIAGNOSTIC.md
│   ├── MODEL_RESPONSE_DIAGNOSTIC_IMPLEMENTATION.md
│   ├── WORKSPACE_EXAMPLES.md
│   ├── WORKSPACE_IMPLEMENTATION_SUMMARY.md
│   └── STREAM_OUTPUT_GUIDE.md
│
├── tests/                         # 正式测试
│   ├── test_workspace.py
│   ├── test_workspace_e2e.py
│   └── test_workspace_integration.py
│
├── dev_tests/                     # 开发测试
│   ├── test_agent_tools.py
│   ├── test_bash_tool.py
│   ├── test_cross_directory.py
│   ├── test_e2e_agent.py
│   ├── test_import_order.py
│   ├── test_improved_prompt.py
│   ├── test_logging.py
│   ├── test_memorywords.py
│   ├── test_model_diagnostic.py
│   ├── test_persional.py
│   ├── test_real_scenario.py
│   ├── test_responsiveness.py
│   ├── test_startup.py
│   ├── verify_workspace.py
│   └── temp/                      # 临时测试
│       └── test.txt
│
├── scripts/                       # 工具脚本
│   └── view_logs.py
│
└── logs/                          # 日志文件（已存在）
    └── [日志文件]
```

---

## 🚀 执行步骤

### Step 1: 创建目录结构

```bash
# 创建开发文档目录
mkdir docs\dev

# 创建开发测试目录
mkdir dev_tests
mkdir dev_tests\temp

# 创建工具脚本目录
mkdir scripts
```

### Step 2: 移动开发文档

```bash
# 移动开发过程文档
move docs\AGENT_TOOL_CALLING_FIX.md docs\dev\
move docs\STREAM_FIX_NOTES.md docs\dev\
move docs\RELATIVE_PATH_FIX.md docs\dev\
move docs\WORKSPACE_INITIALIZATION_FIX.md docs\dev\
move docs\AGENT_RESPONSE_OPTIMIZATION_PLAN.md docs\dev\
move docs\OPTIMIZATION_SUMMARY.md docs\dev\
move docs\LOGGING_GUIDE.md docs\dev\
move docs\LOGGING_SUMMARY.md docs\dev\
move docs\LOGGING_OPTIMIZATION_SUMMARY.md docs\dev\
move docs\LOG_SYSTEM_QUIET_MODE_SUMMARY.md docs\dev\
move docs\MODEL_RESPONSE_DIAGNOSTIC.md docs\dev\
move docs\MODEL_RESPONSE_DIAGNOSTIC_IMPLEMENTATION.md docs\dev\
move docs\WORKSPACE_EXAMPLES.md docs\dev\
move docs\WORKSPACE_IMPLEMENTATION_SUMMARY.md docs\dev\
move docs\STREAM_OUTPUT_GUIDE.md docs\dev\
```

### Step 3: 移动开发测试

```bash
# 移动测试文件
move test_agent_tools.py dev_tests\
move test_bash_tool.py dev_tests\
move test_cross_directory.py dev_tests\
move test_e2e_agent.py dev_tests\
move test_import_order.py dev_tests\
move test_improved_prompt.py dev_tests\
move test_logging.py dev_tests\
move test_memorywords.py dev_tests\
move test_model_diagnostic.py dev_tests\
move test_persional.py dev_tests\
move test_real_scenario.py dev_tests\
move test_responsiveness.py dev_tests\
move test_startup.py dev_tests\
move verify_workspace.py dev_tests\
```

### Step 4: 移动临时文件

```bash
# 移动临时测试文件
move test.txt dev_tests\temp\
```

### Step 5: 移动工具脚本

```bash
# 移动工具脚本
move view_logs.py scripts\
```

---

## 📝 注意事项

### 1. 更新引用路径

移动文件后，需要更新文档中的相对路径引用：

**检查以下文件**:
- `docs/README.md` - 可能需要更新链接
- `docs/dev/*.md` - 互相引用的链接
- `dev_tests/*.py` - 导入路径

**更新示例**:
```markdown
# 修改前
- [`AGENT_TOOL_CALLING_FIX.md`](AGENT_TOOL_CALLING_FIX.md)

# 修改后
- [`AGENT_TOOL_CALLING_FIX.md`](dev/AGENT_TOOL_CALLING_FIX.md)
```

### 2. 更新 .gitignore

确保新目录被版本控制跟踪：

```bash
# .gitignore 不需要修改
# 所有新目录都应该被 Git 跟踪
```

### 3. 保持可访问性

- ✅ `docs/` - 用户可见的正式文档
- ✅ `docs/dev/` - 开发者参考的开发文档
- ✅ `tests/` - 正式测试套件
- ✅ `dev_tests/` - 开发测试，可选运行
- ✅ `scripts/` - 实用工具

---

## 🎯 预期效果

### 整理前

```
根目录:
- 20+ 个 test_*.py 文件散落各处 ❌
- docs/ 包含 20+ 个混合文档 ❌
- 难以区分正式/临时文档 ❌

开发体验:
- 找不到需要的文件 ❌
- 视觉混乱 ❌
- 难以维护 ❌
```

### 整理后

```
根目录:
- 只有核心文件和目录 ✅
- 测试文件集中在 dev_tests/ ✅
- 文档分类清晰 ✅

开发体验:
- 快速定位文件 ✅
- 视觉清爽 ✅
- 易于维护 ✅
```

---

## 📊 统计信息

| 类别 | 文件数 | 位置 |
|------|--------|------|
| 正式文档 | ~6 | docs/ |
| 开发文档 | ~14 | docs/dev/ |
| 正式测试 | ~3 | tests/ |
| 开发测试 | ~14 | dev_tests/ |
| 临时文件 | ~1 | dev_tests/temp/ |
| 工具脚本 | ~1 | scripts/ |

---

## 🔄 后续维护

### 新增文档时

1. **正式文档** → 放入 `docs/`
   - 用户指南、配置说明等
   
2. **开发文档** → 放入 `docs/dev/`
   - 问题修复记录、优化总结等

### 新增测试时

1. **正式测试** → 放入 `tests/`
   - 单元测试、集成测试等
   
2. **开发测试** → 放入 `dev_tests/`
   - 功能验证、调试测试等
   
3. **临时测试** → 放入 `dev_tests/temp/`
   - 一次性测试、实验脚本等

### 新增脚本时

1. **工具脚本** → 放入 `scripts/`
   - 辅助工具、查看脚本等

---

## ✅ 验收清单

- [ ] 创建 docs/dev/ 目录
- [ ] 创建 dev_tests/ 目录
- [ ] 创建 dev_tests/temp/ 目录
- [ ] 创建 scripts/ 目录
- [ ] 移动所有开发文档到 docs/dev/
- [ ] 移动所有开发测试到 dev_tests/
- [ ] 移动临时文件到 dev_tests/temp/
- [ ] 移动工具脚夲到 scripts/
- [ ] 更新文档中的相对路径引用
- [ ] 验证所有移动的文件可正常访问
- [ ] 更新根目录 README（如需要）

---

**版本**: v1.0  
**日期**: 2026-03-07
