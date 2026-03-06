#!/usr/bin/env python3
"""
测试流式输出和 HTML 格式化功能
"""

import sys
import os

# 添加 src 目录到 Python 路径
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

from learn_agent.main import _format_response_card


def test_format_card():
    """测试卡片格式化功能"""
    
    # 测试 1: 普通文本响应
    response1 = "我已经完成了你的任务。文件已成功创建并保存到指定目录。"
    print("\n" + "="*60)
    print("测试 1: 普通文本响应")
    print("="*60)
    print(_format_response_card(response1))
    
    # 测试 2: 包含代码的响应
    response2 = """以下是创建的 Python 文件：

```python
def hello():
    print("Hello, World!")

hello()
```

文件已保存为 test.py"""
    print("\n" + "="*60)
    print("测试 2: 包含代码的响应")
    print("="*60)
    print(_format_response_card(response2))
    
    # 测试 3: 包含成功标记的响应
    response3 = """✅ 任务完成

✓ 文件已创建
✓ 内容已写入
✓ 权限已设置

所有步骤都成功了！"""
    print("\n" + "="*60)
    print("测试 3: 包含成功标记的响应")
    print("="*60)
    print(_format_response_card(response3))
    
    # 测试 4: 多行混合内容
    response4 = """我帮你分析了项目结构：

项目包含以下主要目录：
- src/ - 源代码
- tests/ - 测试文件
- docs/ - 文档

⚠️ 注意：config 目录不存在

需要我创建它吗？"""
    print("\n" + "="*60)
    print("测试 4: 多行混合内容")
    print("="*60)
    print(_format_response_card(response4))


if __name__ == "__main__":
    test_format_card()
    print("\n\n✨ 所有测试完成！\n")
