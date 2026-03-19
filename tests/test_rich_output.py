"""
测试 Rich Markdown 渲染功能

展示如何使用 Rich 库渲染 AI 返回的 Markdown 格式内容
"""

from src.learn_agent.infrastructure.display import TerminalDisplay


def test_basic_markdown():
    """测试基础 Markdown 渲染"""
    print("\n" + "="*60)
    print("测试 1: 基础 Markdown 渲染")
    print("="*60)
    
    display = TerminalDisplay(verbose=True, use_rich=True)
    
    markdown_content = """
# 任务完成报告

我已经成功完成了你的任务。以下是详细说明：

## 执行步骤

1. **创建文件** - 在指定目录创建了 `test.py`
2. **写入内容** - 添加了 Python 代码
3. **验证结果** - 确认文件已保存

## 代码示例

```python
def hello_world():
    print("Hello, World!")
    return True

if __name__ == "__main__":
    hello_world()
```

## 注意事项

- ✅ 文件已成功创建
- ⚠️ 请记得设置执行权限
- ❌ 不要删除重要文件

> 提示：运行 `python test.py` 来测试代码
"""
    
    display.render_markdown(markdown_content)


def test_response_card():
    """测试响应卡片"""
    print("\n" + "="*60)
    print("测试 2: 响应卡片展示")
    print("="*60)
    
    display = TerminalDisplay(verbose=True, use_rich=True)
    
    # 测试不同样式的卡片
    test_cases = [
        ("default", "这是一个普通的响应卡片。\n包含多行文本内容。\n用于展示 AI 的常规回复。"),
        ("success", "✅ 任务已成功完成！\n\n所有文件都已保存到指定位置。\n你可以随时查看或修改这些文件。"),
        ("warning", "⚠️ 请注意以下事项：\n\n1. 某些操作可能需要额外权限\n2. 请定期备份重要数据\n3. 遇到问题请及时反馈"),
        ("error", "❌ 发生错误：\n\n无法访问目标文件。\n请检查文件路径是否正确。\n\n错误详情：FileNotFoundError"),
        ("code", "这是生成的代码：\n\n```python\nclass Calculator:\n    def add(self, a, b):\n        return a + b\n    \n    def multiply(self, a, b):\n        return a * b\n```"),
    ]
    
    for style, content in test_cases:
        print(f"\n样式：{style}\n")
        display.print_response_card(content, style=style)


def test_mixed_content():
    """测试混合内容（文本 + 代码）"""
    print("\n" + "="*60)
    print("测试 3: 混合内容渲染")
    print("="*60)
    
    display = TerminalDisplay(verbose=True, use_rich=True)
    
    mixed_content = """
我已经分析了你的代码项目。

## 项目结构

```
project/
├── src/
│   ├── main.py
│   └── utils.py
├── tests/
│   └── test_main.py
└── README.md
```

## 代码分析

### main.py

```python
import sys
from utils import helper

def main():
    # 主函数入口
    print("Starting application...")
    
    try:
        result = helper.process()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## 建议

1. ✅ 代码结构清晰
2. ⚠️ 建议添加类型注解
3. 💡 可以增加更多错误处理

需要我帮你优化代码吗？
"""
    
    display.print_response_card(mixed_content, style="default")


def test_ansi_fallback():
    """测试 ANSI 降级模式（Rich 不可用时）"""
    print("\n" + "="*60)
    print("测试 4: ANSI 降级模式")
    print("="*60)
    
    # 强制使用 ANSI 模式
    display = TerminalDisplay(verbose=True, use_rich=False)
    
    content = """这是一个测试卡片。
包含一些示例文本。
用于展示 ANSI 模式的降级效果。"""
    
    display.print_response_card(content, style="default")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Rich Markdown 渲染功能测试")
    print("="*60)
    
    # 运行所有测试
    test_basic_markdown()
    test_response_card()
    test_mixed_content()
    test_ansi_fallback()
    
    print("\n" + "="*60)
    print("所有测试完成！")
    print("="*60)
    print("\n提示：观察上面的输出，看看 Rich 渲染的效果如何。")
    print("- Markdown 标题应该有正确的层级和样式")
    print("- 代码块应该有语法高亮")
    print("- 卡片应该有圆角边框和适当的颜色")
    print("- 列表和引用应该正确格式化")
    print()
