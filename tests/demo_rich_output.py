"""
快速演示：Rich Markdown 输出优化

展示 AI 返回的 Markdown 内容如何被美化为富文本格式
"""

from src.learn_agent.infrastructure.display import TerminalDisplay


def demo_ai_response():
    """演示典型的 AI 响应格式化"""
    
    print("\n" + "="*70)
    print("场景 1: AI 完成任务后的报告")
    print("="*70 + "\n")
    
    display = TerminalDisplay(verbose=True, use_rich=True)
    
    ai_response = """
# ✅ 任务完成报告

我已经成功完成了你的请求。以下是详细说明：

## 执行的操作

1. **创建文件** - 在 `./data` 目录下创建了 `output.txt`
2. **写入内容** - 添加了测试数据
3. **验证结果** - 确认文件已正确保存

## 生成的代码

```python
import os
from pathlib import Path

def create_output_file(content: str, filename: str = "output.txt"):
    \"\"\"创建输出文件\"\"\"
    output_dir = Path("./data")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / filename
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return output_file

if __name__ == "__main__":
    result = create_output_file("Hello, World!")
    print(f"文件已创建：{result}")
```

## 注意事项

- ✅ 文件编码为 UTF-8
- ⚠️ 请确保有写入权限
- 💡 可以修改 `filename` 参数自定义文件名

## 下一步建议

你可以：
1. 查看生成的文件内容
2. 修改代码添加更多功能
3. 运行测试验证正确性

需要我帮你做其他调整吗？
"""
    
    display.print_response_card(ai_response, style="default")


def demo_code_generation():
    """演示代码生成场景"""
    
    print("\n" + "="*70)
    print("场景 2: AI 生成代码示例")
    print("="*70 + "\n")
    
    display = TerminalDisplay(verbose=True, use_rich=True)
    
    code_response = """
这是你要的代码实现：

```python
class DataAnalyzer:
    \"\"\"数据分析器\"\"\"
    
    def __init__(self, data: list):
        self.data = data
    
    def calculate_average(self) -> float:
        \"\"\"计算平均值\"\"\"
        if not self.data:
            return 0.0
        return sum(self.data) / len(self.data)
    
    def find_max(self):
        \"\"\"找出最大值\"\"\"
        return max(self.data) if self.data else None
    
    def filter_by_threshold(self, threshold: float) -> list:
        \"\"\"过滤超过阈值的数据\"\"\"
        return [x for x in self.data if x > threshold]


# 使用示例
if __name__ == "__main__":
    analyzer = DataAnalyzer([10, 25, 18, 35, 42])
    print(f"平均值：{analyzer.calculate_average()}")
    print(f"最大值：{analyzer.find_max()}")
    print(f"超过 20 的数据：{analyzer.filter_by_threshold(20)}")
```

使用方法：
1. 将代码保存为 `analyzer.py`
2. 运行 `python analyzer.py` 查看结果
3. 根据需要修改阈值参数
"""
    
    display.print_response_card(code_response, style="code")


def demo_error_handling():
    """演示错误提示场景"""
    
    print("\n" + "="*70)
    print("场景 3: AI 报告错误")
    print("="*70 + "\n")
    
    display = TerminalDisplay(verbose=True, use_rich=True)
    
    error_response = """
❌ 遇到问题：无法创建文件

## 错误详情

```
FileNotFoundError: [Errno 2] No such file or directory: '/nonexistent/path/file.txt'
```

## 可能原因

1. **目录不存在** - 目标路径 `/nonexistent/path/` 不存在
2. **权限不足** - 当前用户没有写入权限
3. **路径错误** - 指定的路径无效

## 解决方案

### 方案 1：创建目录

```bash
# Linux/Mac
mkdir -p /nonexistent/path

# Windows PowerShell
New-Item -ItemType Directory -Force -Path C:\nonexistent\path
```

### 方案 2：使用有效路径

```python
# 使用当前目录
from pathlib import Path
current_dir = Path.cwd()
print(f"当前目录：{current_dir}")

# 或使用用户主目录
home_dir = Path.home()
print(f"主目录：{home_dir}")
```

## 需要帮助吗？

我可以帮你：
- ✅ 检查目录是否存在
- ✅ 列出可用目录
- ✅ 使用其他路径重新尝试

请告诉我你想怎么做？
"""
    
    display.print_response_card(error_response, style="error")


def demo_success_notification():
    """演示成功通知场景"""
    
    print("\n" + "="*70)
    print("场景 4: AI 报告成功")
    print("="*70 + "\n")
    
    display = TerminalDisplay(verbose=True, use_rich=True)
    
    success_response = """
✅ 所有操作已成功完成！

## 执行结果

- ✅ 创建了 3 个文件
- ✅ 安装了 2 个依赖包
- ✅ 配置了环境变量

## 文件列表

```
project/
├── main.py          # 主程序入口
├── config.py        # 配置文件
├── utils.py         # 工具函数
└── README.md        # 项目说明
```

## 安装的依赖

- `requests==2.31.0` - HTTP 客户端库
- `pyyaml==6.0.1` - YAML 解析器

## 下一步

你现在可以：

1. **运行程序**
   ```bash
   python main.py
   ```

2. **查看文档**
   ```bash
   cat README.md
   ```

3. **开始开发**
   编辑 `main.py` 添加你的业务逻辑

🎉 项目已准备就绪！
"""
    
    display.print_response_card(success_response, style="success")


def demo_mixed_language():
    """演示中英文混合场景"""
    
    print("\n" + "="*70)
    print("场景 5: 中英文混合内容")
    print("="*70 + "\n")
    
    display = TerminalDisplay(verbose=True, use_rich=True)
    
    mixed_response = """
# Project Analysis / 项目分析

I've analyzed your codebase. 我已经分析了你的代码库。

## Key Findings / 主要发现

### Architecture / 架构
- ✅ MVC Pattern - MVC 模式
- ✅ RESTful API - RESTful 接口
- ⚠️ Missing Tests - 缺少测试

### Code Quality / 代码质量

```python
# Good example / 良好示例
def process_data(items: list) -> dict:
    \"\"\"Process data items\"\"\"
    result = {
        'total': len(items),
        'processed': [item.upper() for item in items]
    }
    return result

# Needs improvement / 需要改进
def proc(d):
    r = []
    for i in d:
        r.append(i.upper())
    return r
```

## Recommendations / 建议

1. **Add Type Hints** - 添加类型注解
2. **Write Docstrings** - 编写文档字符串
3. **Add Unit Tests** - 添加单元测试

需要我帮你改进代码吗？ / Need help improving the code?
"""
    
    display.print_response_card(mixed_response, style="default")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("✨ Rich Markdown 输出优化演示 ✨")
    print("="*70)
    print("以下展示 5 个典型场景中 AI 响应的富文本格式化效果")
    print("="*70)
    
    # 运行所有演示
    demo_ai_response()
    demo_code_generation()
    demo_error_handling()
    demo_success_notification()
    demo_mixed_language()
    
    print("\n" + "="*70)
    print("演示完成！")
    print("="*70)
    print("\n观察要点：")
    print("  📦 圆角边框卡片使内容突出")
    print("  🎨 不同样式对应不同场景（成功/错误/代码）")
    print("  🖥️ 代码块语法高亮易读")
    print("  📝 Markdown 元素正确渲染")
    print("  🌐 中英文混排显示正常")
    print("\n这就是 LearnTerminalAgent 现在的输出效果！")
    print()
