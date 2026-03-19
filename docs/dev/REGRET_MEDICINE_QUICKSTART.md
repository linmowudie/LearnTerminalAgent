# "后悔药"功能快速入门

## 🎯 功能简介

在执行**编辑**或**删除**操作时，自动保存文件副本到压缩备份中，支持随时恢复。

---

## 🚀 核心功能

### 1. 自动备份

```python
# 编辑文件 - 自动创建备份
edit_file("src/main.py", "old_code", "new_code")
# ✅ 返回包含 Backup ID

# 删除文件 - 自动创建备份  
delete_file("temp.txt")
# ✅ 返回包含 Backup ID

# 强制删除（不备份）
delete_file("temp.txt", force=True)
```

### 2. 查看备份

```python
list_backups(limit=10)
```

**输出示例**：
```
Recent backups (showing 2 of 15):

ID: 20260309_210000_temp.txt
  File: temp.txt
  Operation: delete
  Time: 2026-03-09 21:00:00
  Size: 1024 bytes

ID: 20260309_205712_main.py
  File: src/main.py
  Operation: edit
  Time: 2026-03-09 20:57:12
  Size: 2048 bytes
```

### 3. 恢复备份

```python
restore_backup("20260309_205712_main.py")
# ✅ 文件恢复到编辑/删除前的状态
```

### 4. 清理备份

```python
# 删除指定备份
delete_backup("20260309_205712_main.py")

# 批量清理旧备份
cleanup_old_backups(days=30)
```

---

## 📁 存储位置

```
workspace/
├── .backups/              # 备份目录（隐藏）
│   ├── *.zip             # 压缩备份文件
│   └── backup_metadata.json  # 元数据索引
└── your_files/           # 你的文件
```

---

## 💡 典型场景

### 场景 1: 代码重构

```
1. AI 帮你重构代码 → edit_file()
2. 发现改错了
3. 使用 restore_backup() 恢复
```

### 场景 2: 误删文件

```
1. AI 删除了文件 → delete_file()
2. 发现是重要文件
3. list_backups() 查找
4. restore_backup() 恢复
```

### 场景 3: 配置试验

```
1. 修改配置文件前 → 自动备份
2. 测试新配置
3. 不合适 → 一键恢复
```

---

## ⚡ 快速命令

| 需求 | 命令 |
|------|------|
| 查看最近备份 | `list_backups()` |
| 恢复文件 | `restore_backup("backup_id")` |
| 删除备份 | `delete_backup("backup_id")` |
| 清理 30 天前备份 | `cleanup_old_backups(days=30)` |

---

## 🔍 注意事项

### ✅ 优点
- 自动备份，无需手动操作
- ZIP 压缩节省空间
- 支持恢复到任意时间点

### ⚠️ 限制
- 默认保留所有备份（需定期清理）
- 仅在工作空间内有效
- 大文件备份占用空间

### 💡 最佳实践
1. 定期清理旧备份（建议每周）
2. 重要操作记录备份 ID
3. 与 Git 配合使用效果更佳

---

## 📖 详细文档

- [完整使用指南](docs/dev/REGRET_MEDICINE_BACKUP_SYSTEM.md)
- [技术实现总结](docs/dev/REGRET_MEDICINE_SUMMARY.md)

---

**版本**: v1.0  
**更新**: 2026-03-09
