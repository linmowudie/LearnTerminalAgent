#!/usr/bin/env python3
"""
Skills 功能验证脚本

测试所有新创建的 skills 是否能正常加载和工作
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.learn_agent.tools.skills import get_skill_loader


def test_skill_loading():
    """测试技能加载"""
    print("=" * 60)
    print("测试 1: 技能加载")
    print("=" * 60)
    
    loader = get_skill_loader()
    skills = loader.list_skills()
    
    print(f"\n✅ 成功加载 {len(skills)} 个技能:")
    for skill_name in skills:
        print(f"  ✓ {skill_name}")
    
    # 验证是否包含我们创建的 5 个技能
    expected_skills = [
        "project-scaffold",
        "code-style-guide",
        "git-workflow",
        "test-generator",
        "doc-generator",
    ]
    
    missing_skills = []
    for expected in expected_skills:
        if expected not in skills:
            missing_skills.append(expected)
    
    if missing_skills:
        print(f"\n[FAIL] 缺失的技能：{missing_skills}")
        return False
    else:
        print(f"\n[PASS] 所有预期技能都已加载")
        return True


def test_skill_descriptions():
    """测试技能描述"""
    print("\n" + "=" * 60)
    print("测试 2: 技能描述")
    print("=" * 60)
    
    loader = get_skill_loader()
    descriptions = loader.get_descriptions()
    
    print("\n可用技能列表:")
    print(descriptions)
    
    # 验证描述中包含关键信息
    expected_keywords = {
        "project-scaffold": ["脚手架", "项目"],
        "code-style-guide": ["代码规范", "格式化"],
        "git-workflow": ["Git", "工作流"],
        "test-generator": ["测试", "pytest"],
        "doc-generator": ["文档", "生成"],
    }
    
    all_found = True
    for skill_name, keywords in expected_keywords.items():
        skill_desc = ""
        for line in descriptions.split("\n"):
            if skill_name in line:
                skill_desc = line.lower()
                break
        
        found_keywords = []
        for keyword in keywords:
            if keyword.lower() in skill_desc:
                found_keywords.append(keyword)
        
        if found_keywords:
            print(f"  ✓ {skill_name}: 找到关键词 {found_keywords}")
        else:
            print(f"  ⚠️  {skill_name}: 未找到预期关键词")
            all_found = False
    
    return all_found


def test_skill_content():
    """测试获取技能完整内容"""
    print("\n" + "=" * 60)
    print("测试 3: 技能内容完整性")
    print("=" * 60)
    
    loader = get_skill_loader()
    
    for skill_name in ["project-scaffold", "code-style-guide", "git-workflow"]:
        content = loader.get_content(skill_name)
        
        if content:
            lines = content.split("\n")
            print(f"  ✓ {skill_name}: {len(lines)} 行")
            
            # 验证包含 frontmatter
            if content.startswith("---"):
                print(f"    ✓ 包含 YAML frontmatter")
            else:
                print(f"    ⚠️  缺少 YAML frontmatter")
        else:
            print(f"  ❌ {skill_name}: 无法获取内容")
    
    return True


def test_script_files():
    """测试配套脚本文件存在性"""
    print("\n" + "=" * 60)
    print("测试 4: 配套脚本文件")
    print("=" * 60)
    
    # 使用绝对路径
    base_dir = Path(__file__).resolve().parent.parent / "skills"
    
    scripts = {
        "project-scaffold": "scaffold.py",
        "code-style-guide": "check_style.py",
        "git-workflow": "git_helpers.py",
        "test-generator": "generate_tests.py",
        "doc-generator": "generate_docs.py",
    }
    
    all_exist = True
    for skill_name, script_name in scripts.items():
        script_path = base_dir / skill_name / script_name
        
        if script_path.exists():
            print(f"  ✓ {skill_name}/{script_name} 存在")
        else:
            print(f"  ❌ {skill_name}/{script_name} 不存在")
            all_exist = False
    
    return all_exist


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("LearnTerminalAgent Skills 功能验证")
    print("=" * 60)
    
    results = []
    
    # 运行所有测试
    results.append(("技能加载", test_skill_loading()))
    results.append(("技能描述", test_skill_descriptions()))
    results.append(("技能内容", test_skill_content()))
    results.append(("脚本文件", test_script_files()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print(f"\n总计：{passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！Skills 创建成功！")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试未通过，请检查")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
