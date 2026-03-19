#!/usr/bin/env python3
"""Skills 验证测试 - 简化版"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.learn_agent.tools.skills import get_skill_loader

print("=" * 60)
print("Skills 加载测试")
print("=" * 60)

loader = get_skill_loader()
skills = loader.list_skills()

print(f"\n成功加载 {len(skills)} 个技能:\n")

for skill_name in skills:
    info = loader.get_skill_info(skill_name)
    print(f"  [OK] {skill_name}")
    print(f"       描述：{info['description']}")
    print(f"       标签：{info['tags']}")
    print()

expected_skills = [
    "project-scaffold",
    "code-style-guide", 
    "git-workflow",
    "test-generator",
    "doc-generator",
]

missing = [s for s in expected_skills if s not in skills]

if missing:
    print(f"[FAIL] 缺失技能：{missing}")
    sys.exit(1)
else:
    print(f"[PASS] 所有 5 个预期技能都已加载!")
    
    # 测试获取内容
    print("\n测试技能内容获取:")
    for skill_name in expected_skills[:2]:
        content = loader.get_content(skill_name)
        if content and content.startswith("---"):
            print(f"  [OK] {skill_name}: 包含完整的 YAML frontmatter")
        else:
            print(f"  [WARN] {skill_name}: frontmatter 可能有问题")
    
    print("\n[PASS] Skills 创建成功!")
    sys.exit(0)
