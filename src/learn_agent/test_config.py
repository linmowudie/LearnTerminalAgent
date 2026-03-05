#!/usr/bin/env python3
"""
LearnTerminalAgent 配置测试脚本

测试 JSON 配置文件是否正确加载
"""

import sys
from pathlib import Path

# 添加 LearnAgent 到路径
sys.path.insert(0, str(Path(__file__).parent))

from config import AgentConfig, get_config


def test_from_json():
    """测试从 JSON 加载配置"""
    print("\n" + "="*60)
    print("测试 1: 从 JSON 文件加载配置")
    print("="*60)
    
    try:
        config = AgentConfig.from_json()
        print(f"✓ 成功加载配置")
        config.print_info()
        return True
    except Exception as e:
        print(f"✗ 加载失败：{e}")
        return False


def test_from_env():
    """测试从环境变量加载配置"""
    print("\n" + "="*60)
    print("测试 2: 从环境变量加载配置")
    print("="*60)
    
    try:
        config = AgentConfig.from_env()
        print(f"✓ 成功从环境变量加载")
        config.print_info()
        return True
    except Exception as e:
        print(f"✗ 加载失败：{e}")
        return False


def test_get_config():
    """测试获取全局配置"""
    print("\n" + "="*60)
    print("测试 3: 获取全局配置（默认从 JSON）")
    print("="*60)
    
    try:
        config = get_config(from_json=True)
        print(f"✓ 成功获取全局配置")
        print(f"模型：{config.model_name}")
        print(f"Max Tokens: {config.max_tokens}")
        print(f"Timeout: {config.timeout}s")
        return True
    except Exception as e:
        print(f"✗ 获取失败：{e}")
        return False


def test_config_attributes():
    """测试所有配置属性"""
    print("\n" + "="*60)
    print("测试 4: 检查所有配置属性")
    print("="*60)
    
    try:
        config = AgentConfig.from_json()
        
        # 检查所有属性是否存在
        attrs = [
            'api_key', 'base_url', 'model_name',
            'max_tokens', 'timeout', 'max_iterations',
            'dangerous_patterns',
            'context_threshold', 'keep_recent', 'auto_compact_enabled',
            'max_todos', 'bg_timeout',
            'team_poll_interval', 'team_idle_timeout',
            'worktree_enabled', 'worktree_base_ref'
        ]
        
        all_ok = True
        for attr in attrs:
            if hasattr(config, attr):
                value = getattr(config, attr)
                if isinstance(value, list):
                    print(f"✓ {attr}: [{len(value)} items]")
                else:
                    print(f"✓ {attr}: {value}")
            else:
                print(f"✗ 缺少属性：{attr}")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print(f"✗ 测试失败：{e}")
        return False


def test_to_dict():
    """测试转换为字典"""
    print("\n" + "="*60)
    print("测试 5: 转换为字典")
    print("="*60)
    
    try:
        config = AgentConfig.from_json()
        data = config.to_dict()
        
        print(f"✓ 成功转换为字典")
        print(f"键数量：{len(data)}")
        print(f"顶层键：{list(data.keys())}")
        
        return True
    except Exception as e:
        print(f"✗ 转换失败：{e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("LearnAgent 配置测试")
    print("="*60)
    
    tests = [
        ("JSON 加载", test_from_json),
        ("环境变量", test_from_env),
        ("全局配置", test_get_config),
        ("配置属性", test_config_attributes),
        ("字典转换", test_to_dict),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n测试 {name} 时发生错误：{e}")
            results.append((name, False))
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {name}")
    
    print("\n" + "-"*60)
    print(f"总计：{passed}/{total} 个测试通过")
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
