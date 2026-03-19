#!/usr/bin/env python3
"""
Git Workflow Helpers - Git 工作流助手

提供分支管理、提交规范、冲突解决等辅助功能
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional


class GitHelpers:
    """Git 辅助工具类"""
    
    # Conventional Commits 类型
    COMMIT_TYPES = {
        "feat": "新功能",
        "fix": "Bug 修复",
        "docs": "文档变更",
        "style": "代码格式",
        "refactor": "重构",
        "test": "测试相关",
        "chore": "构建/工具",
        "perf": "性能优化",
        "ci": "CI 配置",
        "build": "构建系统",
    }
    
    def __init__(self, repo_path: Optional[Path] = None):
        """
        初始化 Git 助手
        
        Args:
            repo_path: Git 仓库路径，默认为当前目录
        """
        self.repo_path = repo_path or Path.cwd()
        
        # 验证是否为 Git 仓库
        if not (self.repo_path / ".git").exists():
            raise RuntimeError(f"{self.repo_path} 不是 Git 仓库")
    
    def run_git(self, *args: str, check: bool = True) -> str:
        """
        运行 Git 命令
        
        Args:
            args: Git 命令参数
            check: 是否检查返回码
            
        Returns:
            命令输出
            
        Raises:
            subprocess.CalledProcessError: 当命令失败且 check=True
        """
        try:
            result = subprocess.run(
                ["git"] + list(args),
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=check,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"❌ Git 命令失败：{e}")
            print(f"错误输出：{e.stderr}")
            raise
    
    # ========== 分支管理 ==========
    
    def list_branches(self, verbose: bool = False) -> List[str]:
        """列出所有本地分支"""
        args = ["branch"]
        if verbose:
            args.append("-v")
        
        output = self.run_git(*args)
        branches = []
        
        for line in output.split("\n"):
            if line.strip():
                # 移除当前分支标记
                branch = line.lstrip("* ").split()[0]
                branches.append(branch)
        
        return branches
    
    def list_remote_branches(self) -> List[str]:
        """列出所有远程分支"""
        output = self.run_git("branch", "-r")
        branches = []
        
        for line in output.split("\n"):
            if line.strip() and "HEAD" not in line:
                branch = line.strip().split("/")[-1]
                branches.append(branch)
        
        return branches
    
    def create_branch(
        self,
        branch_type: str,
        branch_name: str,
        from_branch: str = "develop",
    ) -> str:
        """
        创建新分支
        
        Args:
            branch_type: 分支类型 (feature, bugfix, hotfix, release)
            branch_name: 分支名称
            from_branch: 基于的分支
            
        Returns:
            新分支名称
        """
        valid_types = ["feature", "bugfix", "hotfix", "release"]
        if branch_type not in valid_types:
            raise ValueError(
                f"无效的分层类型：{branch_type}。可选值：{valid_types}"
            )
        
        full_name = f"{branch_type}/{branch_name}"
        
        # 切换到基础分支并更新
        print(f"📥 切换到 {from_branch} 并更新...")
        self.run_git("checkout", from_branch)
        self.run_git("pull", "origin", from_branch)
        
        # 创建新分支
        print(f"🌿 创建分支：{full_name}")
        self.run_git("checkout", "-b", full_name)
        
        print(f"✅ 分支创建成功：{full_name}")
        return full_name
    
    def delete_branch(self, branch_name: str, force: bool = False) -> None:
        """删除本地分支"""
        args = ["branch"]
        
        if force:
            args.append("-D")
        else:
            args.append("-d")
        
        args.append(branch_name)
        
        try:
            self.run_git(*args)
            print(f"✅ 分支已删除：{branch_name}")
        except subprocess.CalledProcessError:
            print(f"❌ 删除分支失败：{branch_name}")
            raise
    
    def cleanup_merged_branches(self) -> List[str]:
        """清理已合并的分支"""
        # 获取已合并的分支列表
        output = self.run_git("branch", "--merged")
        
        deleted = []
        for line in output.split("\n"):
            branch = line.strip().lstrip("* ")
            
            # 跳过当前分支和主要分支
            if branch and branch not in ["main", "master", "develop"]:
                try:
                    self.delete_branch(branch)
                    deleted.append(branch)
                except Exception:
                    pass
        
        return deleted
    
    # ========== 提交管理 ==========
    
    def commit(
        self,
        commit_type: str,
        scope: Optional[str],
        description: str,
        body: Optional[str] = None,
        footer: Optional[str] = None,
    ) -> str:
        """
        创建符合 Conventional Commits 规范的提交
        
        Args:
            commit_type: 提交类型 (feat, fix, docs, etc.)
            scope: 影响范围（可选）
            description: 简短描述
            body: 详细描述（可选）
            footer: 页脚信息（可选）
            
        Returns:
            提交 hash
        """
        if commit_type not in self.COMMIT_TYPES:
            raise ValueError(
                f"无效的提交类型：{commit_type}。"
                f"可选值：{list(self.COMMIT_TYPES.keys())}"
            )
        
        # 构建提交信息
        header = f"{commit_type}"
        if scope:
            header += f"({scope})"
        header += f": {description}"
        
        message = header
        
        if body:
            message += f"\n\n{body}"
        
        if footer:
            message += f"\n\n{footer}"
        
        # 执行提交
        try:
            self.run_git("commit", "-m", message)
            
            # 获取提交 hash
            commit_hash = self.run_git("rev-parse", "--short", "HEAD")
            
            type_desc = self.COMMIT_TYPES.get(commit_type, commit_type)
            print(f"✅ 提交成功 [{type_desc}]: {commit_hash}")
            
            return commit_hash
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 提交失败")
            raise
    
    def interactive_commit(self) -> None:
        """交互式提交向导"""
        print("\n📝 Conventional Commits 提交向导\n")
        
        # 选择提交类型
        print("提交类型:")
        for i, (ctype, desc) in enumerate(self.COMMIT_TYPES.items(), 1):
            print(f"  {i}. {ctype} - {desc}")
        
        while True:
            try:
                type_idx = int(input("\n请选择类型 (数字): "))
                commit_type = list(self.COMMIT_TYPES.keys())[type_idx - 1]
                break
            except (ValueError, IndexError):
                print("❌ 无效输入，请重试")
        
        # 输入影响范围
        scope = input("影响范围 (可选，直接回车跳过): ").strip()
        if not scope:
            scope = None
        
        # 输入简短描述
        description = input("简短描述: ").strip()
        if not description:
            print("❌ 描述不能为空")
            return
        
        # 输入详细描述
        use_body = input("添加详细描述？(y/n): ").lower()
        body = None
        if use_body == "y":
            print("输入详细描述 (输入空行结束):")
            body_lines = []
            while True:
                line = input()
                if not line:
                    break
                body_lines.append(line)
            body = "\n".join(body_lines) if body_lines else None
        
        # 输入页脚
        use_footer = input("添加页脚 (如 Closes #123)? (y/n): ").lower()
        footer = None
        if use_footer == "y":
            footer = input("页脚内容: ").strip()
        
        # 确认提交信息
        print("\n📋 提交信息预览:")
        print("-" * 60)
        
        commit_header = f"{commit_type}"
        if scope:
            commit_header += f"({scope})"
        commit_header += f": {description}"
        
        print(commit_header)
        if body:
            print(f"\n{body}")
        if footer:
            print(f"\n{footer}")
        
        print("-" * 60)
        
        confirm = input("确认提交？(y/n): ").lower()
        if confirm == "y":
            self.commit(commit_type, scope, description, body, footer)
        else:
            print("❌ 提交已取消")
    
    # ========== 历史记录 ==========
    
    def show_log(
        self,
        author: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        max_count: int = 20,
        oneline: bool = True,
    ) -> str:
        """
        显示提交历史
        
        Args:
            author: 作者过滤
            since: 起始时间
            until: 结束时间
            max_count: 最大数量
            oneline: 单行格式
            
        Returns:
            日志内容
        """
        args = ["log"]
        
        if oneline:
            args.extend(["--oneline", "--graph"])
        
        if author:
            args.extend(["--author", author])
        
        if since:
            args.extend(["--since", since])
        
        if until:
            args.extend(["--until", until])
        
        args.extend(["-n", str(max_count)])
        
        return self.run_git(*args)
    
    def get_stats(
        self,
        branch: Optional[str] = None,
        since: Optional[str] = None,
    ) -> dict:
        """
        获取 Git 统计信息
        
        Args:
            branch: 分支名称
            since: 起始时间
            
        Returns:
            统计信息字典
        """
        stats = {
            "total_commits": 0,
            "authors": {},
            "files_changed": 0,
            "insertions": 0,
            "deletions": 0,
        }
        
        try:
            # 获取提交数
            args = ["rev-list", "--count", "HEAD"]
            if branch:
                args.append(branch)
            stats["total_commits"] = int(self.run_git(*args))
            
            # 获取作者统计
            output = self.run_git("shortlog", "-sn", "HEAD")
            for line in output.split("\n"):
                if line.strip():
                    parts = line.strip().split("\t")
                    if len(parts) == 2:
                        count = int(parts[0].strip())
                        name = parts[1].strip()
                        stats["authors"][name] = count
            
            # 获取代码变更统计
            args = ["diff", "--shortstat"]
            if branch:
                args.insert(1, branch)
            if since:
                args.extend(["--since", since])
            
            output = self.run_git(*args)
            
            # 解析统计信息
            if "insertion" in output:
                parts = output.split(",")
                for part in parts:
                    part = part.strip()
                    if "insertion" in part:
                        stats["insertions"] = int(part.split()[0])
                    elif "deletion" in part:
                        stats["deletions"] = int(part.split()[0])
                    elif "file" in part:
                        stats["files_changed"] = int(part.split()[0])
        
        except Exception as e:
            print(f"⚠️  获取统计信息失败：{e}")
        
        return stats
    
    # ========== 冲突解决 ==========
    
    def show_conflicts(self) -> List[dict]:
        """显示当前的合并冲突"""
        conflicts = []
        
        # 获取冲突文件列表
        output = self.run_git("diff", "--name-only", "--diff-filter=U")
        
        if not output:
            print("✅ 没有未解决的冲突")
            return conflicts
        
        conflict_files = output.split("\n")
        
        for file_path in conflict_files:
            if file_path.strip():
                conflicts.append({
                    "file": file_path.strip(),
                    "status": "conflicted",
                })
        
        return conflicts
    
    def mark_resolved(self, *files: str) -> None:
        """标记文件为已解决"""
        for file_path in files:
            self.run_git("add", file_path)
            print(f"✅ 已标记为已解决：{file_path}")


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="Git Workflow Helpers - Git 工作流助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s branch list
  %(prog)s branch create feature my-feature
  %(prog)s commit
  %(prog)s commit feat auth "add user login"
  %(prog)s log --author "John" --since "2024-01-01"
  %(prog)s stats
  %(prog)s conflicts show
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # branch 命令
    branch_parser = subparsers.add_parser("branch", help="分支管理")
    branch_subparsers = branch_parser.add_subparsers(dest="subcommand")
    
    # branch list
    branch_list_parser = branch_subparsers.add_parser("list", help="列出分支")
    branch_list_parser.add_argument(
        "-v", "--verbose", action="store_true", help="显示详细信息"
    )
    branch_list_parser.add_argument(
        "-r", "--remote", action="store_true", help="列出远程分支"
    )
    
    # branch create
    branch_create = branch_subparsers.add_parser("create", help="创建分支")
    branch_create.add_argument(
        "type",
        choices=["feature", "bugfix", "hotfix", "release"],
        help="分支类型",
    )
    branch_create.add_argument("name", help="分支名称")
    branch_create.add_argument(
        "--from",
        dest="from_branch",
        default="develop",
        help="基于的分支，默认 develop",
    )
    
    # branch delete
    branch_delete = branch_subparsers.add_parser("delete", help="删除分支")
    branch_delete.add_argument("branch", help="分支名称")
    branch_delete.add_argument(
        "-f", "--force", action="store_true", help="强制删除"
    )
    
    # branch cleanup
    branch_cleanup = branch_subparsers.add_parser(
        "cleanup", help="清理已合并分支"
    )
    
    # commit 命令
    commit_parser = subparsers.add_parser("commit", help="提交代码")
    commit_parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="交互式提交向导",
    )
    commit_parser.add_argument(
        "type",
        nargs="?",
        choices=list(GitHelpers.COMMIT_TYPES.keys()),
        help="提交类型",
    )
    commit_parser.add_argument("scope", nargs="?", help="影响范围")
    commit_parser.add_argument("description", nargs="?", help="简短描述")
    commit_parser.add_argument("-b", "--body", help="详细描述")
    commit_parser.add_argument("-f", "--footer", help="页脚信息")
    
    # log 命令
    log_parser = subparsers.add_parser("log", help="查看提交历史")
    log_parser.add_argument("--author", help="作者过滤")
    log_parser.add_argument("--since", help="起始时间")
    log_parser.add_argument("--until", help="结束时间")
    log_parser.add_argument(
        "-n", "--max-count", type=int, default=20, help="最大数量"
    )
    
    # stats 命令
    stats_parser = subparsers.add_parser("stats", help="统计信息")
    stats_parser.add_argument("--branch", help="分支名称")
    stats_parser.add_argument("--since", help="起始时间")
    
    # conflicts 命令
    conflicts_parser = subparsers.add_parser("conflicts", help="冲突管理")
    conflicts_subparsers = conflicts_parser.add_subparsers(
        dest="subcommand"
    )
    conflicts_show = conflicts_subparsers.add_parser("show", help="显示冲突")
    
    args = parser.parse_args()
    
    try:
        git = GitHelpers()
    except RuntimeError as e:
        print(f"❌ 错误：{e}")
        sys.exit(1)
    
    if args.command == "branch":
        if args.subcommand == "list":
            if args.remote:
                branches = git.list_remote_branches()
                print("远程分支:")
            else:
                branches = git.list_branches(verbose=args.verbose)
                print("本地分支:")
            
            for branch in branches:
                print(f"  {branch}")
        
        elif args.subcommand == "create":
            git.create_branch(args.type, args.name, args.from_branch)
        
        elif args.subcommand == "delete":
            git.delete_branch(args.branch, force=args.force)
        
        elif args.subcommand == "cleanup":
            deleted = git.cleanup_merged_branches()
            print(f"✅ 清理了 {len(deleted)} 个分支")
        
        else:
            branch_parser.print_help()
    
    elif args.command == "commit":
        if args.interactive:
            git.interactive_commit()
        elif args.type and args.description:
            git.commit(
                args.type,
                args.scope,
                args.description,
                body=args.body,
                footer=args.footer,
            )
        else:
            commit_parser.print_help()
    
    elif args.command == "log":
        output = git.show_log(
            author=args.author,
            since=args.since,
            until=args.until,
            max_count=args.max_count,
        )
        print(output)
    
    elif args.command == "stats":
        stats = git.get_stats(branch=args.branch, since=args.since)
        
        print("\n📊 Git 统计信息")
        print("=" * 60)
        print(f"总提交数：{stats['total_commits']}")
        print(f"文件变更：{stats['files_changed']}")
        print(f"新增行数：{stats['insertions']}")
        print(f"删除行数：{stats['deletions']}")
        print("\n作者贡献:")
        for author, count in sorted(
            stats["authors"].items(), key=lambda x: x[1], reverse=True
        )[:10]:
            print(f"  {author}: {count} 次提交")
        print("=" * 60)
    
    elif args.command == "conflicts":
        if args.subcommand == "show":
            conflicts = git.show_conflicts()
            if conflicts:
                print("🔴 未解决的冲突:")
                for conflict in conflicts:
                    print(f"  ❌ {conflict['file']}")
            else:
                print("✅ 没有未解决的冲突")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
