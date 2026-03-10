# 环境配置指南

本文档详细介绍 LearnTerminalAgent 的环境配置和虚拟环境管理。

## 📦 为什么使用虚拟环境？

### 优势

1. **项目隔离** - 避免不同项目间的依赖冲突
2. **环境清洁** - 不污染全局 Python 环境
3. **版本控制** - 精确控制项目所需的 Python 和包版本
4. **易于部署** - 方便团队协作和生产环境部署
5. **快速重建** - 可随时删除重建，确保环境一致性

### 虚拟环境 vs 全局安装

| 特性 | 虚拟环境 | 全局安装 |
|------|----------|----------|
| 项目隔离 | ✅ 完全隔离 | ❌ 所有项目共享 |
| 依赖冲突 | ✅ 无冲突 | ⚠️ 可能冲突 |
| 版本控制 | ✅ 精确控制 | ❌ 难以控制 |
| 环境清洁 | ✅ 保持清洁 | ❌ 污染全局 |
| 团队协作 | ✅ 易于同步 | ❌ 配置复杂 |
| **推荐度** | ⭐⭐⭐⭐⭐ | ⭐ |

---

## 🚀 快速开始

### 1. 创建虚拟环境

在项目根目录执行：

```bash
# Windows PowerShell
cd f:\ProjectCode\LearnTerminalAgent
python -m venv .venv

# Linux/Mac
cd /path/to/LearnTerminalAgent
python3 -m venv .venv
```

**说明**：
- `.venv` 是约定俗成的命名（也有用 `venv/`）
- 已添加到 `.gitignore`，不会被提交到仓库
- 包含完整的 Python 解释器和包管理工具

### 2. 激活虚拟环境

#### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

**如果提示执行策略错误**：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Windows CMD

```cmd
.venv\Scripts\activate.bat
```

#### Linux/Mac

```bash
source.venv/bin/activate
```

**激活成功标志**：命令行前缀出现 `(.venv)` 标识

```bash
(.venv) PS F:\ProjectCode\LearnTerminalAgent>
```

### 3. 安装项目依赖

#### 方式 A：使用 uv（推荐 ⭐）

[uv](https://github.com/astral-sh/uv) 是一个超快的 Python 包管理器，比 pip 快 10-100 倍。

```bash
# 安装 uv（如果尚未安装）
pip install uv

# 使用 uv 安装依赖
uv pip install -e .
```

**优势**：
- 🚀 极快的安装速度（Rust 实现）
- 📦 智能缓存管理
- 🔒 可靠的依赖解析
- 🎯 支持多种 Python 版本

#### 方式 B：使用 pip

```bash
pip install -e .
```

#### 方式 C：从 requirements.txt 安装

```bash
pip install-r requirements.txt
```

### 4. 验证安装

```bash
python -c "import learn_agent; print(f'✓ LearnTerminalAgent 已安装: {learn_agent.__version__ if hasattr(learn_agent, \"__version__\") else \"latest\"}')"
```

预期输出：
```
✓ LearnTerminalAgent 已安装：latest
```

---

## 💻 使用启动脚本

项目提供了便捷的 PowerShell 启动脚本 `agent.ps1`，会自动检测并激活虚拟环境。

### 使用方法

```powershell
# 在当前目录启动
.\agent.ps1

# 指定工作空间
.\agent.ps1 F:\Project\MyApp
```

### 自动激活逻辑

脚本会自动执行以下检查：

1. **检测虚拟环境** - 查找 `.venv/Scripts/Activate.ps1`
2. **激活虚拟环境** - 如果存在则自动激活
3. **优雅降级** - 如果不存在，使用系统 Python 并显示警告
4. **彩色反馈** - 提供清晰的终端输出

**示例输出**：

```
[INFO] Virtual environment activated: f:\ProjectCode\LearnTerminalAgent\.venv
============================================================
LearnAgent 配置
============================================================
✓ 模型：qwen3.5-plus
...
```

**虚拟环境缺失时**：

```
[WARNING] Virtual environment not found at f:\ProjectCode\LearnTerminalAgent\.venv
[INFO] Continuing with system Python...
============================================================
LearnAgent 配置
============================================================
...
```

---

## 🔧 高级配置

### 环境变量管理

#### 创建 .env 文件

在项目根目录创建 `.env` 文件：

```bash
QWEN_API_KEY=sk-your-api-key-here
```

**支持的 API Key 类型**：
- `QWEN_API_KEY` - 通义千问（推荐）
- `ANTHROPIC_API_KEY` - Anthropic Claude
- `OPENAI_API_KEY` - OpenAI GPT

#### 环境变量优先级

配置加载优先级：**环境变量 > 配置文件 > 默认值**

```bash
# 环境变量覆盖（最高优先级）
$env:MODEL_ID="qwen-max"
$env:MAX_TOKENS="16000"

# 运行 Agent
.\agent.ps1
```

### 多 Python 版本管理

如果需要特定 Python 版本：

```bash
# 使用 pyenv 管理多版本（Linux/Mac）
pyenv install 3.11.0
pyenv local 3.11.0
python -m venv .venv

# Windows 使用多个 Python 安装
C:\Python311\python.exe -m venv .venv
```

---

## 🐛 常见问题

### Q1: PowerShell 无法运行脚本

**错误信息**：
```
无法加载文件，因为在此系统上禁止运行脚本。
```

**解决方案**：
```powershell
# 为当前用户设置执行策略
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 或临时绕过限制
PowerShell -ExecutionPolicy Bypass -File .\agent.ps1
```

### Q2: 虚拟环境占用过大

**查看大小**：
```bash
# Windows PowerShell
Get-ChildItem .venv -Recurse | Measure-Object -Property Length -Sum

# Linux/Mac
du -sh .venv
```

**清理方案**：
1. 删除虚拟环境重建
2. 使用 `uv` 的共享缓存减少重复

```bash
# 删除虚拟环境
Remove-Item -Recurse -Force .venv  # Windows
rm -rf .venv                        # Linux/Mac

# 重新创建
python -m venv .venv
uv pip install -e .
```

### Q3: 依赖安装失败

**常见原因**：
- 网络连接问题
- Python 版本不兼容
- 缺少编译工具（Windows）

**解决方案**：

```bash
# 使用国内镜像（推荐）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用 uv（自动选择最优镜像）
uv pip install -e .
```

### Q4: 如何退出虚拟环境？

```bash
# 方法 1：使用命令
deactivate

# 方法 2：直接关闭终端窗口
```

---

## 📋 最佳实践

### 1. 始终使用虚拟环境

```bash
# ✅ 好的做法
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .

# ❌ 不好的做法
pip install-e .  # 直接安装到全局
```

### 2. 定期更新依赖

```bash
# 激活虚拟环境后
pip list --outdated
pip install --upgrade package-name

# 或使用 uv
uv pip install --upgrade package-name
```

### 3. 锁定依赖版本

生成精确的依赖列表：

```bash
pip freeze > requirements.lock.txt
```

### 4. 团队同步

确保团队成员使用相同的依赖版本：

```bash
# 提交锁定的依赖文件
git add requirements.lock.txt

# 团队安装
pip install -r requirements.lock.txt
```

### 5. 使用 .gitignore

确保虚拟环境不被提交：

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
env/
```

---

## 🔄 迁移指南

### 从全局安装迁移到虚拟环境

1. **记录全局安装的包**
   ```bash
   pip freeze > global-requirements.txt
   ```

2. **创建虚拟环境**
   ```bash
  python -m venv .venv
   ```

3. **激活虚拟环境**
   ```bash
   .\.venv\Scripts\Activate.ps1  # Windows
   source .venv/bin/activate      # Linux/Mac
   ```

4. **安装包到虚拟环境**
   ```bash
   pip install -e .
   ```

5. **验证功能正常**
   ```bash
   .\agent.ps1
   ```

6. **可选：卸载全局包**
   ```bash
   pip uninstall -y package-name
   ```

---

## 📊 性能对比

### 安装速度对比（45 个包）

| 工具 | 时间 | 相对速度 |
|------|------|----------|
| **uv** | ~10 秒 | ⭐⭐⭐⭐⭐ (基准) |
| pip | ~60 秒 | ⭐ (慢 6 倍) |

### 磁盘占用

| 项目 | 大小 |
|------|------|
| 虚拟环境 (.venv) | ~300 MB |
| 项目源码 | ~50 MB |
| 总计 | ~350 MB |

---

## 🎯 总结

### 标准工作流程

```bash
# 1. 克隆项目
git clone https://github.com/linmowudie/LearnTerminalAgent.git
cd LearnTerminalAgent

# 2. 创建虚拟环境
python -m venv .venv

# 3. 激活虚拟环境
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate      # Linux/Mac

# 4. 安装依赖
uv pip install -e .

# 5. 配置 API Key
echo "QWEN_API_KEY=sk-xxx" > .env

# 6. 启动 Agent
.\agent.ps1
```

### 关键要点

✅ **必须使用虚拟环境** - 避免依赖冲突  
✅ **推荐使用 uv** - 速度快 10-100 倍  
✅ **使用 agent.ps1** - 自动激活虚拟环境  
✅ **配置 .env 文件** - 管理 API Key  
✅ **遵循 .gitignore** - 不提交虚拟环境  

---

**Happy Coding!** 🚀

如有问题，请查阅 [QUICK_START.md](QUICK_START.md) 或提交 Issue。
