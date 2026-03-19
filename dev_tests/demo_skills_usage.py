#!/usr/bin/env python3
"""
Skills 使用演示脚本

展示如何使用新创建的 5 个 skills
"""

import subprocess
import sys
from pathlib import Path


def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"[操作] {description}")
    print(f"[命令] {' '.join(cmd)}")
    print("-" * 70)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=False,
        )
        
        if result.returncode == 0:
            print(f"[成功] {description}")
            if result.stdout:
                print("\n输出:")
                print(result.stdout)
        else:
            print(f"[失败] {description}")
            if result.stderr:
                print(f"错误：{result.stderr}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"[异常] {e}")
        return False


def demo_project_scaffold():
    """演示项目脚手架生成器"""
    print_section("1. Project Scaffold - 项目脚手架生成器")
    
    # 创建测试目录
    test_dir = Path(__file__).parent / "temp_demo"
    test_dir.mkdir(exist_ok=True)
    
    # 创建 Python 项目
    cmd = [
        sys.executable,
        str(Path(__file__).parent.parent / "skills" / "project-scaffold" / "scaffold.py"),
        "create",
        "python",
        "demo_project",
        "--force",
    ]
    
    success = run_command(cmd, "创建 Python 项目脚手架")
    
    if success:
        project_dir = test_dir / "demo_project"
        if project_dir.exists():
            print(f"\n[查看] 项目结构已创建在：{project_dir}")
            print("\n项目包含的文件:")
            for item in project_dir.iterdir():
                print(f"  - {item.name}")


def demo_code_style_check():
    """演示代码规范检查器"""
    print_section("2. Code Style Guide - 代码规范检查器")
    
    # 检查脚手架脚本本身
    scaffold_file = Path(__file__).parent.parent / "skills" / "project-scaffold" / "scaffold.py"
    
    cmd = [
        sys.executable,
        str(Path(__file__).parent.parent / "skills" / "code-style-guide" / "check_style.py"),
        str(scaffold_file),
        "--quiet",
    ]
    
    run_command(cmd, "检查 scaffold.py 的代码规范")


def demo_git_workflow():
    """演示 Git 工作流助手"""
    print_section("3. Git Workflow - Git 工作流助手")
    
    # 列出分支
    cmd = [
        sys.executable,
        str(Path(__file__).parent.parent / "skills" / "git-workflow" / "git_helpers.py"),
        "branch",
        "list",
    ]
    
    run_command(cmd, "列出 Git 分支")


def demo_test_generator():
    """演示测试用例生成器"""
    print_section("4. Test Generator - 测试用例生成器")
    
    # 为脚手架工具的一个小函数生成测试
    scaffold_file = Path(__file__).parent.parent / "skills" / "project-scaffold" / "scaffold.py"
    
    cmd = [
        sys.executable,
        str(Path(__file__).parent.parent / "skills" / "test-generator" / "generate_tests.py"),
        str(scaffold_file),
        "--skip-existing",
    ]
    
    run_command(cmd, "为 scaffold.py 生成测试模板")


def demo_doc_generator():
    """演示文档生成助手"""
    print_section("5. Doc Generator - 文档生成助手")
    
    # 为 skills 目录生成 README
    skills_dir = Path(__file__).parent.parent / "skills" / "project-scaffold"
    
    cmd = [
        sys.executable,
        str(Path(__file__).parent.parent / "skills" / "doc-generator" / "generate_docs.py"),
        str(skills_dir),
        "--readme",
        "-o",
        str(skills_dir / "README_GENERATED.md"),
    ]
    
    run_command(cmd, "为 project-scaffold 生成 README")


def main():
    """主函数"""
    print("\n" + "🎯" * 35)
    print("LearnTerminalAgent Skills 使用演示")
    print("🎯" * 35)
    
    # 依次演示每个 skill
    demo_project_scaffold()
    demo_code_style_check()
    demo_git_workflow()
    demo_test_generator()
    demo_doc_generator()
    
    print_section("演示完成")
    print("所有 skills 的功能已展示完毕！")
    print("\n详细信息请查看:")
    print("  - dev_tests/SKILLS_SUMMARY.md - 完整总结")
    print("  - dev_tests/SKILLS_QUICK_REFERENCE.md - 快速参考")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[中断] 演示被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n[错误] 演示过程中发生异常：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
