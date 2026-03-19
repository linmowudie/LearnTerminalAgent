# 记忆管理和搜索工具使用指南

## 🎯 新功能概览

本次升级为 LearnTerminalAgent 添加了四大核心工具：

1. **🧠 记忆检索** - 从历史会话中查找相关经验
2. **💻 代码搜索** - 在代码文件中搜索特定模式
3. **📁 文件搜索** - 按名称或内容查找文件
4. **💾 自动记忆存储** - 会话结束自动保存（后台运行）

---

## 📚 工具使用说明

### 1. 记忆检索工具 (`search_memory`)

**用途**: 从历史会话中查找与当前查询相关的记忆片段

**特点**: 
- ✅ 仅在当前工作空间有历史记录时才触发（高性能）
- ✅ 自动筛选最相关的 Top-N 结果
- ✅ 显示历史会话的上下文和工具调用记录

**使用示例**:
```
用户：我之前在这个项目中是如何创建文件的？
Agent: （自动检测 workspace 历史）检测到您有过 3 次相关会话，是否查看？

或直接调用：
search_memory("创建文件", limit=3)
```

**参数**:
- `query`: 搜索关键词
- `workspace_path`: 工作空间路径（可选，默认当前）
- `limit`: 最大返回结果数（默认 5）

---

### 2. 代码搜索工具 (`search_code`)

**用途**: 在代码文件中搜索特定的代码片段或模式

**特点**:
- ✅ 支持正则表达式
- ✅ 可过滤文件类型（.py, .js, .ts 等）
- ✅ 显示匹配行及其上下文
- ✅ 限制最大结果数避免性能问题

**使用示例**:
```
# 搜索函数定义
search_code("def hello_world")

# 正则搜索所有类定义
search_code(r"^class\s+\w+", use_regex=True, file_extensions=['.py'])

# 在指定目录搜索
search_code("API_KEY", directory="src/", max_results=20)
```

**参数**:
- `pattern`: 搜索模式
- `directory`: 搜索目录（可选）
- `file_extensions`: 文件扩展名列表（如 `['.py', '.js']`）
- `use_regex`: 是否使用正则表达式
- `case_sensitive`: 是否区分大小写
- `max_results`: 最大返回结果数（默认 50）

---

### 3. 文件搜索工具 (`search_files`)

**用途**: 按文件名搜索文件（支持通配符）

**特点**:
- ✅ 支持通配符（`*` 和 `?`）
- ✅ 递归搜索子目录
- ✅ 显示文件大小和修改时间
- ✅ 可限制最大深度

**使用示例**:
```
# 搜索所有 Python 文件
search_files("*.py")

# 搜索配置文件
search_files("config.*")

# 精确搜索
search_files("README.md", recursive=False)
```

**参数**:
- `name_pattern`: 文件名模式
- `directory`: 搜索目录（可选）
- `recursive`: 是否递归子目录（默认 True）
- `max_depth`: 最大递归深度（可选）
- `max_results`: 最大返回结果数（默认 100）

---

### 4. 按内容查找文件 (`find_files_by_content`)

**用途**: 在文件中搜索包含特定内容的行

**特点**:
- ✅ 不区分大小写的模糊匹配
- ✅ 显示匹配行及其上下文
- ✅ 可结合文件名过滤

**使用示例**:
```
# 在所有文件中搜索
find_files_by_content("TODO")

# 只在 Python 文件中搜索
find_files_by_content("import os", file_pattern="*.py")

# 在指定目录搜索
find_files_by_content("database", directory="src/")
```

**参数**:
- `content_pattern`: 内容模式
- `file_pattern`: 文件名过滤（如 `"*.py"`）
- `directory`: 搜索目录（可选）
- `max_results`: 最大返回结果数（默认 50）

---

## 🔧 配置说明

在 `config/config.json` 中添加以下配置：

```json
{
  "memory": {
    "enabled": true,                    // 是否启用记忆存储
    "storage_dir": "data/.transcripts", // 存储目录
    "min_duration_seconds": 10,         // 最小保存时长（秒）
    "save_triggers": [                  // 保存触发条件
      "session_end",
      "task_completed"
    ],
    "retention_days": 90,               // 会话保留天数
    "auto_retrieve_enabled": true,      // 是否自动提示历史记忆
    "retrieve_check_interval": 300      // 历史检查间隔（秒）
  },
  "search": {
    "default_max_results": 50,          // 默认最大结果数
    "supported_extensions": [           // 支持的代码文件类型
      ".py", ".js", ".ts", ".java"
    ],
    "exclude_directories": [            // 排除的目录
      "node_modules",
      ".git",
      "__pycache__",
      "bin", "build", "dist"
    ],
    "max_search_depth": 10              // 最大搜索深度
  }
}
```

---

## 💡 最佳实践

### 记忆检索

✅ **推荐**:
- 在开始新任务前，先询问是否有相关历史经验
- 使用具体的关键词而非笼统的描述
- 限制结果数量（3-5 条）以获得最相关的信息

❌ **避免**:
- 频繁调用（系统会自动检测并提示）
- 在完全不同工作空间中搜索（不会找到结果）

### 代码搜索

✅ **推荐**:
- 使用明确的函数名或类名作为搜索词
- 对复杂模式使用正则表达式
- 指定文件类型以缩小搜索范围

❌ **避免**:
- 搜索过于通用的词汇（如 "test"、"data"）
- 不限制最大结果数（可能导致性能问题）

### 文件搜索

✅ **推荐**:
- 使用通配符进行模糊搜索（`*.py`）
- 在大型项目中限制搜索深度
- 结合内容搜索定位特定代码

❌ **避免**:
- 在无限制情况下搜索通用名称
- 在排除目录中搜索（浪费资源）

---

## 🎨 输出格式示例

### 记忆检索输出

```markdown
## 记忆搜索结果 (找到 3 条相关记录)

### 1. session_20260310_093021 (相关性：0.87)
**时间**: 2026-03-10 09:30:21  
**工作空间**: F:/ProjectCode/LearnTerminalAgent  
**片段**: 
> 👤 User: 如何实现上下文压缩？
> 🤖 Assistant: 使用 ContextCompactor 的 auto_compact 方法...

**工具调用**: 2 次  
**完成任务**: task_003

---
```

### 代码搜索输出

```markdown
## 代码搜索结果 (找到 12 处匹配)

### 1. src/learn_agent/services/context.py:220
```python
timestamp = int(time.time())
transcript_path = self.transcript_dir / f"transcript_{timestamp}.json"
```

### 2. src/learn_agent/tools/tools.py:172
```python
backup_id = backup_manager.create_backup(file_path, operation="edit")
```

... (还有 10 处匹配)
```

### 文件搜索输出

```markdown
## 文件搜索结果 (找到 6 个文件)

### 1. `main.py`
- 大小：2.5 KB

### 2. `test_main.py`
- 大小：1.8 KB

...
```

---

## 🧪 测试验证

运行以下测试验证功能正常：

```bash
# 测试记忆存储
python dev_tests/test_memory_storage.py

# 测试记忆检索
python dev_tests/test_memory_retrieval.py

# 测试代码和文件搜索
python dev_tests/test_code_file_search.py
```

所有测试应显示 ✅ 通过。

---

## ❓ 常见问题

### Q: 为什么我的搜索没有结果？

A: 可能的原因：
1. 当前工作空间没有历史记忆（记忆检索）
2. 搜索词过于具体或生僻
3. 文件类型过滤排除了目标文件
4. 搜索目录不正确

### Q: 记忆存储会影响性能吗？

A: 不会。记忆存储在后台异步进行，且：
- 短于 10 秒的会话自动跳过
- 使用缓存机制减少 IO
- 仅在会话结束时保存

### Q: 如何禁用自动记忆存储？

A: 在 `config/config.json` 中设置：
```json
{
  "memory": {
    "enabled": false
  }
}
```

### Q: 搜索工具支持哪些编程语言？

A: 默认支持：
- Python (.py)
- JavaScript (.js)
- TypeScript (.ts)
- Java (.java)
- Go (.go)
- Rust (.rs)
- C/C++ (.c, .cpp, .h, .hpp)

可在配置中添加更多语言。

---

## 📞 需要帮助？

查看详细文档：
- [`docs/dev/IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md) - 实施总结
- [`docs/dev/MEMORY_SYSTEM_IMPLEMENTATION.md`](../PROJECT_OVERVIEW.md) - 记忆系统设计

---

**祝您使用愉快！** 🎉
