#!/usr/bin/env python
"""
Agent 响应优化验证测试

测试目标：
1. 零空响应 - 禁止"思考完成"类回复
2. 即时工具调用 - 隐含操作请求时立即调用工具
3. 简洁回应 - 回应简洁直接，聚焦结果
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.learn_agent.agent import AgentLoop


def test_list_directory():
    """测试：查看目录"""
    print("\n" + "="*60)
    print("测试用例 1: 查看当前文件夹内容")
    print("="*60)
    
    agent = AgentLoop()
    response = agent.run("查看当前文件夹内容", verbose=False)
    
    # 检查是否调用了 list_directory 工具
    messages_str = str(agent.messages)
    if "list_directory" in messages_str:
        print("✅ PASS: 调用了 list_directory 工具")
    else:
        print("❌ FAIL: 未调用 list_directory 工具")
        return False
    
    # 检查是否为空响应
    if response.strip() in ["思考完成", "", " "]:
        print("❌ FAIL: 返回了空响应")
        return False
    else:
        print("✅ PASS: 非空响应")
    
    print(f"\n响应内容预览：{response[:100]}...")
    return True


def test_create_file():
    """测试：创建文件"""
    print("\n" + "="*60)
    print("测试用例 2: 创建一个 test.txt 文件，写入 hello")
    print("="*60)
    
    agent = AgentLoop()
    response = agent.run("创建一个 test.txt 文件，写入 hello", verbose=False)
    
    # 检查是否调用了 write_file 工具
    messages_str = str(agent.messages)
    if "write_file" in messages_str:
        print("✅ PASS: 调用了 write_file 工具")
    else:
        print("❌ FAIL: 未调用 write_file 工具")
        return False
    
    # 检查是否只说不做
    if "我会创建" in response or "我要创建" in response:
        print("❌ FAIL: 只说不做")
        return False
    else:
        print("✅ PASS: 直接行动")
    
    print(f"\n响应内容预览：{response[:100]}...")
    return True


def test_run_command():
    """测试：运行命令"""
    print("\n" + "="*60)
    print("测试用例 3: 运行 python --version")
    print("="*60)
    
    agent = AgentLoop()
    response = agent.run("运行 python --version", verbose=False)
    
    # 检查是否调用了 bash 工具
    messages_str = str(agent.messages)
    if "bash" in messages_str:
        print("✅ PASS: 调用了 bash 工具")
    else:
        print("❌ FAIL: 未调用 bash 工具")
        return False
    
    # 检查是否冗长解释
    forbidden_phrases = ["让我想想", "我来帮你运行", "我需要先"]
    if any(phrase in response for phrase in forbidden_phrases):
        print(f"❌ FAIL: 包含冗长解释：{[p for p in forbidden_phrases if p in response]}")
        return False
    else:
        print("✅ PASS: 简洁回应")
    
    print(f"\n响应内容预览：{response[:100]}...")
    return True


def test_read_file():
    """测试：读取文件"""
    print("\n" + "="*60)
    print("测试用例 4: 读取 README.md 的内容")
    print("="*60)
    
    agent = AgentLoop()
    response = agent.run("读取 README.md 的内容", verbose=False)
    
    # 检查是否调用了 read_file 工具
    messages_str = str(agent.messages)
    if "read_file" in messages_str:
        print("✅ PASS: 调用了 read_file 工具")
    else:
        print("❌ FAIL: 未调用 read_file 工具")
        return False
    
    print(f"\n响应内容预览：{response[:100]}...")
    return True


def test_no_empty_response():
    """测试：禁止空响应"""
    print("\n" + "="*60)
    print("测试用例 5: 简单问候（无工具调用场景）")
    print("="*60)
    
    agent = AgentLoop()
    response = agent.run("你好", verbose=False)
    
    # 检查是否为空响应
    if response.strip() in ["思考完成", "", " "]:
        print("❌ FAIL: 返回了空响应")
        return False
    else:
        print("✅ PASS: 非空响应")
    
    # 检查是否有实质性内容
    if len(response.strip()) < 10:
        print(f"❌ FAIL: 响应过于简短（{len(response)}字）")
        return False
    else:
        print("✅ PASS: 有实质性内容")
    
    print(f"\n响应内容：{response}")
    return True


def test_keyword_trigger():
    """测试：关键词触发机制"""
    print("\n" + "="*60)
    print("测试用例 6: 英文关键词触发（list files）")
    print("="*60)
    
    agent = AgentLoop()
    response = agent.run("list files in current directory", verbose=False)
    
    # 检查是否调用了 list_directory 工具
    messages_str = str(agent.messages)
    if "list_directory" in messages_str:
        print("✅ PASS: 英文关键词成功触发工具调用")
    else:
        print("❌ FAIL: 英文关键词未触发工具调用")
        return False
    
    print(f"\n响应内容预览：{response[:100]}...")
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🧪 Agent 响应优化验证测试")
    print("="*60)
    
    tests = [
        ("查看目录", test_list_directory),
        ("创建文件", test_create_file),
        ("运行命令", test_run_command),
        ("读取文件", test_read_file),
        ("禁止空响应", test_no_empty_response),
        ("关键词触发", test_keyword_trigger),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} 测试异常：{type(e).__name__}: {e}")
            results.append((name, False))
    
    # 统计结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n总计：{passed}/{total} 通过")
    print(f"通过率：{passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有测试通过！优化效果显著！")
        return True
    else:
        print(f"\n⚠️ {total - passed} 个测试失败，需要进一步改进")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
