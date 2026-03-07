# API Key 隐藏优化说明

## 📋 优化内容

### 修改前 ❌
```
[OK] API Key: sk-xxxxx1234...5678
```
显示前 10 位 + `...` + 最后 4 位，可能泄露过多信息

### 修改后 ✅
```
[OK] API Key: sk-0***************************8696
```
只显示前 4 位 + 中间 `*` + 最后 4 位，更安全

---

## 🔧 技术实现

### 新增方法

```python
def _mask_api_key(self, show_chars: int = 4) -> str:
    """
    隐藏 API Key，只显示前 N 位和最后 4 位
    
    Args:
        show_chars: 显示前几位（默认 4）
        
    Returns:
        掩码后的 API Key
    """
    if not self.api_key:
        return "(empty)"
    
    if len(self.api_key) <= show_chars + 4:
        # 太短，全部用 * 代替
        return "*" * len(self.api_key)
    
    # 显示前 show_chars 位 + 中间 * + 最后 4 位
    middle_len = len(self.api_key) - show_chars - 4
    return f"{self.api_key[:show_chars]}{'*' * middle_len}{self.api_key[-4:]}"
```

### 使用示例

```python
# print_info() 方法中
api_key_display = self._mask_api_key()
print(f"[OK] API Key: {api_key_display}")

# 输出：sk-0***************************8696
```

---

## 📊 效果对比

| API Key 长度 | 原显示方式 | 新显示方式 | 安全性提升 |
|------------|-----------|-----------|-----------|
| 32 字符 | `sk-xxxxx1234...5678` | `sk-0***************************8696` | ⭐⭐⭐⭐⭐ |
| 20 字符 | `sk-xxxxx1234...5678` | `sk-0***************5678` | ⭐⭐⭐⭐⭐ |
| < 8 字符 | `sk-xxxxx1234...5678` | `****************` | ⭐⭐⭐⭐⭐ |

---

## 🎯 配置参数

### 可调整参数

在 `_mask_api_key()` 方法中：
```python
def _mask_api_key(self, show_chars: int = 4) -> str:
```

**修改建议**:
- `show_chars=4` - 显示前 4 位（推荐）
- `show_chars=6` - 显示前 6 位（更宽松）
- `show_chars=2` - 显示前 2 位（更严格）

### 特殊处理

**API Key 过短时**:
```python
if len(self.api_key) <= show_chars + 4:
    return "*" * len(self.api_key)
```

例如：`abc123` → `******`

---

## 🔒 安全优势

### 为什么这样设计？

1. **防止泄露** - 不暴露完整的 API Key 前缀
2. **便于识别** - 保留前后缀，方便识别是哪个 Key
3. **视觉友好** - 使用 `*` 号填充，直观显示已隐藏

### 最佳实践

✅ **推荐**:
- 生产环境使用此掩码方式
- 日志中永远不要打印完整 API Key
- 配置文件设置合适的权限

❌ **避免**:
- 在终端打印完整 API Key
- 将 API Key 提交到版本控制
- 在公开场合分享 API Key

---

## 📝 相关文件

**修改文件**:
- [`src/learn_agent/config.py`](../src/learn_agent/config.py)

**影响范围**:
- `config.print_info()` - 配置信息打印
- 任何调用 `_mask_api_key()` 的地方

---

## 🧪 测试验证

### 测试用例

```python
from src.learn_agent.config import get_config

config = get_config()
config.print_info()

# 预期输出：
# [OK] API Key: sk-0***************************8696
```

### 实际输出

```bash
$ python -c "from src.learn_agent.config import get_config; config = get_config(); config.print_info()"

============================================================
LearnAgent 配置
============================================================
[OK] 模型：qwen3.5-flash
[OK] Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
[OK] API Key: sk-0***************************8696
[OK] Max Tokens: 8000
[OK] Timeout: 120s
============================================================
```

✅ **测试通过** - API Key 已成功隐藏

---

## 💡 扩展建议

### 未来可以改进的地方

1. **环境变量检测** - 自动检测是否在 CI/CD 环境
2. **配置化** - 允许通过配置调整显示位数
3. **审计日志** - 记录 API Key 的使用情况

### 其他敏感信息处理

建议同样处理：
- 数据库密码
- OAuth Token
- 私钥文件路径

---

**优化完成！** 🔒  
**版本**: v1.0  
**日期**: 2026-03-07
