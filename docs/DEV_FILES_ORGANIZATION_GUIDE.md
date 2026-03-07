# 📁 开发文件整理指南

## 🎯 目的

保持项目结构清晰，将开发过程中生成的文档和测试文件分类存放。

---

## 📂 目录结构说明

### docs/ - 正式文档

**包含**: 用户指南、配置说明、项目概述等正式文档

```
docs/
├── README.md                      # 文档导航
├── PROJECT_OVERVIEW.md            # 项目概览
├── QUICK_START.md                 # 快速开始
├── CONFIG_FILE_GUIDE.md           # 配置文件指南
├── LOG_FILE_GUIDE.md              # 日志文件指南
├── help.md                        # 帮助信息
├── guides/                        # 指南系列
│   └── [用户指南]
└── learn/                         # 学习系列
    └── [教程]
```

### docs/dev/ - 开发过程文档

**包含**: 问题修复记录、优化总结、实施计划等开发文档

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

### tests/ - 正式测试

**包含**: 端到端测试、集成测试、单元测试

```
tests/
├── test_workspace.py              # 工作空间测试
├── test_workspace_e2e.py          # 端到端测试
└── test_workspace_integration.py  # 集成测试
```

### dev_tests/ - 开发测试

**包含**: 功能验证测试、调试测试、场景测试

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
├── verify_workspace.py            # 工作空间验证
└── temp/                          # 临时测试
    └── test.txt                   # 临时测试文件
```

### scripts/ - 工具脚本

**包含**: 辅助工具、查看脚本、实用程序

```
scripts/
└── view_logs.py                   # 日志查看脚本
```

### logs/ - 日志文件

**包含**: 系统运行生成的日志文件

```
logs/
├── Agent_*.log                    # Agent 日志
├── Tools_*.log                    # 工具日志
├── Workspace_*.log                # 工作空间日志
└── Config_*.log                   # 配置日志
```

---

## 🚀 快速使用

### 运行开发测试

```bash
# 运行单个测试
python dev_tests/test_responsiveness.py

# 运行所有开发测试
for file in dev_tests/test_*.py; do python $file; done

# Windows PowerShell
Get-ChildItem dev_tests\test_*.py | ForEach-Object { python $_.FullName }
```

### 查看开发文档

```bash
# 打开开发文档目录
explorer docs\dev  # Windows
xdg-open docs/dev  # Linux/Mac

# 查看特定文档
cat docs/dev/OPTIMIZATION_SUMMARY.md
```

### 使用工具脚本

```bash
# 查看最新日志
python scripts/view_logs.py

# 查看特定模块日志
python scripts/view_logs.py Agent 100
```

---

## 📝 文件分类规则

### 移动到 docs/dev/ 的文件

- ✅ 问题修复记录（*_FIX.md）
- ✅ 优化总结（*_SUMMARY.md）
- ✅ 实施计划（*_PLAN.md）
- ✅ 诊断指南（DIAGNOSTIC*.md）
- ✅ 示例和实现说明（EXAMPLES*, IMPLEMENTATION*.md）

### 移动到 dev_tests/ 的文件

- ✅ 功能验证测试（test_*.py）
- ✅ 调试测试
- ✅ 场景测试
- ✅ 诊断测试
- ✅ 验证脚本（verify_*.py）

### 移动到 dev_tests/temp/ 的文件

- ✅ 一次性测试文件
- ✅ 实验性脚本
- ✅ 临时生成的文件

### 移动到 scripts/ 的文件

- ✅ 辅助工具（view_*.py）
- ✅ 实用程序
- ✅ 自动化脚本

---

## 🔄 维护指南

### 新增文件时

**问自己**:
1. 这是正式文档还是开发文档？
   - 正式 → docs/
   - 开发 → docs/dev/

2. 这是正式测试还是开发测试？
   - 正式 → tests/
   - 开发 → dev_tests/
   - 临时 → dev_tests/temp/

3. 这是工具脚本吗？
   - 是 → scripts/

### 定期清理

**建议每月清理**:
- 删除 dev_tests/temp/ 中的临时文件
- 归档不再需要的开发文档
- 将成熟的开发测试转为正式测试

---

## 📊 整理效果对比

### 整理前 ❌

```
根目录:
- 20+ 个 test_*.py 文件散落各处
- docs/ 包含 20+ 个混合文档
- 难以区分正式/临时文档
- 视觉混乱，找不到文件
```

### 整理后 ✅

```
根目录:
- 只有核心文件和目录
- 测试文件集中在 dev_tests/
- 文档分类清晰（docs/ vs docs/dev/）
- 视觉清爽，易于维护
```

---

## 💡 最佳实践

### ✅ 推荐做法

1. **及时归类** - 创建文件时就放到正确位置
2. **命名规范** - 使用有意义的文件名
3. **定期清理** - 每月清理临时文件
4. **文档更新** - 更新本指南反映实际结构

### ❌ 避免的做法

1. **不要乱放** - 不要把测试文件放在根目录
2. **不要混放** - 正式和开发文档要分开
3. **不要堆积** - 定期清理不需要的文件

---

## 🎯 文件定位速查

| 要找什么 | 去哪里找 |
|---------|---------|
| 用户指南 | docs/ 或 docs/guides/ |
| 开发文档 | docs/dev/ |
| 正式测试 | tests/ |
| 开发测试 | dev_tests/ |
| 临时测试 | dev_tests/temp/ |
| 工具脚本 | scripts/ |
| 日志文件 | logs/ |
| 教程 | docs/learn/ |

---

## 📖 相关文档

- [`DEV_FILES_ORGANIZATION_PLAN.md`](DEV_FILES_ORGANIZATION_PLAN.md) - 原始整理计划
- [`README.md`](../README.md) - 项目主文档

---

## ✨ 总结

通过本次整理：

✅ **根目录更清爽** - 移除了 20+ 个散乱文件  
✅ **分类更清晰** - 正式/开发文档分离  
✅ **查找更容易** - 按类别组织，快速定位  
✅ **维护更方便** - 结构清晰，便于管理  

**开发体验提升**: ⭐⭐⭐⭐⭐

---

**整理完成日期**: 2026-03-07  
**版本**: v1.0
