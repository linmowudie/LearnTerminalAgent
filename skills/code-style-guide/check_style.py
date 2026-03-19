#!/usr/bin/env python3
"""
Code Style Checker - 代码规范检查器

检查 Python 代码的格式、命名和最佳实践
"""

import argparse
import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class CodeStyleChecker:
    """代码风格检查器"""
    
    # 错误代码定义
    ERROR_CODES = {
        "E001": "缩进不正确（应该使用 4 个空格）",
        "E002": "行宽超过 88 字符",
        "E003": "缺少模块 docstring",
        "E004": "函数缺少 docstring",
        "E005": "类缺少 docstring",
        "E006": "导入语句未分组",
        "E007": "使用了 wildcard import (*)",
        "N001": "类名应该使用大驼峰命名 (PascalCase)",
        "N002": "函数名应该使用小写 + 下划线 (snake_case)",
        "N003": "变量名应该使用小写 + 下划线 (snake_case)",
        "N004": "常量名应该使用全大写 + 下划线",
        "N005": "私有成员应该以单下划线开头",
        "Q001": "函数参数过多 (> 5 个)",
        "Q002": "函数复杂度过高 (圈复杂度 > 10)",
        "Q003": "嵌套层级过深 (> 4 层)",
        "Q004": "函数长度过长 (> 50 行)",
        "Q005": "类长度过长 (> 500 行)",
    }
    
    def __init__(self):
        """初始化检查器"""
        self.errors: List[Dict] = []
        self.warnings: List[Dict] = []
    
    def check_file(self, file_path: Path) -> List[Dict]:
        """
        检查单个文件
        
        Args:
            file_path: Python 文件路径
            
        Returns:
            问题列表
        """
        self.errors = []
        self.warnings = []
        
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            
            # 基础格式检查
            self._check_line_format(lines, file_path)
            
            # AST 分析
            self._check_ast(content, file_path)
            
        except Exception as e:
            self.errors.append({
                "file": str(file_path),
                "line": 0,
                "column": 0,
                "code": "F001",
                "message": f"读取文件失败：{e}",
                "severity": "error",
            })
        
        return self.errors + self.warnings
    
    def _check_line_format(
        self, lines: List[str], file_path: Path
    ):
        """检查行格式"""
        for line_num, line in enumerate(lines, start=1):
            # 检查行宽
            if len(line) > 88:
                self.errors.append({
                    "file": str(file_path),
                    "line": line_num,
                    "column": 89,
                    "code": "E002",
                    "message": self.ERROR_CODES["E002"],
                    "severity": "warning",
                })
            
            # 检查缩进（简单的 Tab 检测）
            if "\t" in line and not line.strip().startswith("#"):
                stripped = line.lstrip()
                indent = line[: len(line) - len(stripped)]
                if "\t" in indent:
                    self.errors.append({
                        "file": str(file_path),
                        "line": line_num,
                        "column": 1,
                        "code": "E001",
                        "message": self.ERROR_CODES["E001"],
                        "severity": "error",
                    })
    
    def _check_ast(self, content: str, file_path: Path):
        """使用 AST 进行深度检查"""
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            self.errors.append({
                "file": str(file_path),
                "line": e.lineno or 0,
                "column": e.offset or 0,
                "code": "S001",
                "message": f"语法错误：{e.msg}",
                "severity": "error",
            })
            return
        
        # 检查模块 docstring
        if not ast.get_docstring(tree):
            self.warnings.append({
                "file": str(file_path),
                "line": 1,
                "column": 0,
                "code": "E003",
                "message": self.ERROR_CODES["E003"],
                "severity": "warning",
            })
        
        # 遍历 AST 节点
        for node in ast.walk(tree):
            # 检查类
            if isinstance(node, ast.ClassDef):
                self._check_class(node, file_path)
            
            # 检查函数
            elif isinstance(node, ast.FunctionDef) or isinstance(
                node, ast.AsyncFunctionDef
            ):
                self._check_function(node, file_path)
            
            # 检查导入
            elif isinstance(node, ast.Import):
                self._check_import(node, file_path)
            elif isinstance(node, ast.ImportFrom):
                self._check_import_from(node, file_path)
    
    def _check_class(self, node: ast.ClassDef, file_path: Path):
        """检查类定义"""
        # 检查类名命名
        class_name = node.name
        if not self._is_pascal_case(class_name):
            self.errors.append({
                "file": str(file_path),
                "line": node.lineno,
                "column": node.col_offset,
                "code": "N001",
                "message": f"{self.ERROR_CODES['N001']}: '{class_name}'",
                "severity": "warning",
            })
        
        # 检查类 docstring
        if not ast.get_docstring(node):
            self.warnings.append({
                "file": str(file_path),
                "line": node.lineno,
                "column": node.col_offset,
                "code": "E005",
                "message": self.ERROR_CODES["E005"],
                "severity": "warning",
            })
        
        # 检查类长度
        if node.end_lineno and node.end_lineno - node.lineno > 500:
            self.warnings.append({
                "file": str(file_path),
                "line": node.lineno,
                "column": node.col_offset,
                "code": "Q005",
                "message": self.ERROR_CODES["Q005"],
                "severity": "info",
            })
    
    def _check_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: Path,
    ):
        """检查函数定义"""
        func_name = node.name
        
        # 检查函数名命名
        if not self._is_snake_case(func_name):
            self.errors.append({
                "file": str(file_path),
                "line": node.lineno,
                "column": node.col_offset,
                "code": "N002",
                "message": f"{self.ERROR_CODES['N002']}: '{func_name}'",
                "severity": "warning",
            })
        
        # 检查函数 docstring
        if not ast.get_docstring(node):
            self.warnings.append({
                "file": str(file_path),
                "line": node.lineno,
                "column": node.col_offset,
                "code": "E004",
                "message": self.ERROR_CODES["E004"],
                "severity": "warning",
            })
        
        # 检查参数数量
        num_args = len(node.args.args)
        if num_args > 5:
            self.warnings.append({
                "file": str(file_path),
                "line": node.lineno,
                "column": node.col_offset,
                "code": "Q001",
                "message": f"{self.ERROR_CODES['Q001']} (当前：{num_args}个)",
                "severity": "info",
            })
        
        # 检查函数长度
        if node.end_lineno and node.end_lineno - node.lineno > 50:
            self.warnings.append({
                "file": str(file_path),
                "line": node.lineno,
                "column": node.col_offset,
                "code": "Q004",
                "message": self.ERROR_CODES["Q004"],
                "severity": "info",
            })
    
    def _check_import(
        self, node: ast.Import, file_path: Path
    ):
        """检查导入语句"""
        for alias in node.names:
            if alias.name == "*":
                self.errors.append({
                    "file": str(file_path),
                    "line": node.lineno,
                    "column": node.col_offset,
                    "code": "E007",
                    "message": self.ERROR_CODES["E007"],
                    "severity": "error",
                })
    
    def _check_import_from(
        self, node: ast.ImportFrom, file_path: Path
    ):
        """检查 from ... import 语句"""
        if node.names and any(alias.name == "*" for alias in node.names):
            self.errors.append({
                "file": str(file_path),
                "line": node.lineno,
                "column": node.col_offset,
                "code": "E007",
                "message": self.ERROR_CODES["E007"],
                "severity": "error",
            })
    
    def _is_pascal_case(self, name: str) -> bool:
        """检查是否为大驼峰命名"""
        if not name:
            return False
        return name[0].isupper() and "_" not in name
    
    def _is_snake_case(self, name: str) -> bool:
        """检查是否为小写 + 下划线命名"""
        if not name:
            return False
        return name.islower() or ("_" in name and name.replace("_", "").islower())
    
    def check_directory(
        self,
        dir_path: Path,
        recursive: bool = True,
        pattern: str = "*.py",
    ) -> Dict[Path, List[Dict]]:
        """
        检查目录中的所有 Python 文件
        
        Args:
            dir_path: 目录路径
            recursive: 是否递归子目录
            pattern: 文件匹配模式
            
        Returns:
            文件到问题列表的映射
        """
        results = {}
        
        if recursive:
            files = dir_path.rglob(pattern)
        else:
            files = dir_path.glob(pattern)
        
        for file_path in files:
            if file_path.is_file():
                issues = self.check_file(file_path)
                if issues:
                    results[file_path] = issues
        
        return results
    
    def generate_report(
        self, results: Dict[Path, List[Dict]], output_file: Path
    ):
        """
        生成检查报告
        
        Args:
            results: 检查结果
            output_file: 输出文件路径
        """
        total_errors = 0
        total_warnings = 0
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# 代码规范检查报告\n\n")
            f.write(f"总文件数：{len(results)}\n\n")
            
            for file_path, issues in sorted(results.items()):
                f.write(f"## {file_path}\n\n")
                
                file_errors = sum(
                    1 for i in issues if i["severity"] == "error"
                )
                file_warnings = sum(
                    1 for i in issues if i["severity"] == "warning"
                )
                
                f.write(f"- 错误：{file_errors}\n")
                f.write(f"- 警告：{file_warnings}\n\n")
                
                for issue in issues:
                    severity_icon = "❌" if issue["severity"] == "error" else "⚠️"
                    f.write(
                        f"{severity_icon} **第{issue['line']}行** "
                        f"[{issue['code']}] {issue['message']}\n"
                    )
                
                f.write("\n")
                total_errors += file_errors
                total_warnings += file_warnings
            
            f.write("---\n\n")
            f.write(f"**总计**: {total_errors} 个错误，{total_warnings} 个警告\n")
        
        print(f"报告已生成：{output_file}")


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="Code Style Checker - 代码规范检查器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s src/my_module.py
  %(prog)s src/ --recursive
  %(prog)s src/ --report style_report.md
  %(prog)s . -r --ignore E002,E003
        """,
    )
    
    parser.add_argument(
        "path",
        type=str,
        help="要检查的文件或目录",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="递归检查子目录",
    )
    parser.add_argument(
        "--report",
        type=str,
        default=None,
        help="生成报告文件路径",
    )
    parser.add_argument(
        "--ignore",
        type=str,
        default="",
        help="忽略的错误代码，逗号分隔",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="仅显示错误和警告总数",
    )
    
    args = parser.parse_args()
    
    target_path = Path(args.path)
    
    if not target_path.exists():
        print(f"❌ 路径不存在：{target_path}")
        sys.exit(1)
    
    checker = CodeStyleChecker()
    
    # 解析忽略的代码
    ignore_codes = set()
    if args.ignore:
        ignore_codes = set(code.strip() for code in args.ignore.split(","))
    
    # 执行检查
    if target_path.is_file():
        issues = checker.check_file(target_path)
        results = {target_path: issues} if issues else {}
    else:
        results = checker.check_directory(
            target_path, recursive=args.recursive
        )
    
    # 过滤忽略的代码
    filtered_results = {}
    for file_path, issues in results.items():
        filtered_issues = [
            i for i in issues if i["code"] not in ignore_codes
        ]
        if filtered_issues:
            filtered_results[file_path] = filtered_issues
    
    # 输出结果
    total_errors = sum(
        sum(1 for i in issues if i["severity"] == "error")
        for issues in filtered_results.values()
    )
    total_warnings = sum(
        sum(1 for i in issues if i["severity"] == "warning")
        for issues in filtered_results.values()
    )
    
    if args.quiet:
        print(f"\n检查完成")
        print(f"❌ 错误：{total_errors}")
        print(f"⚠️  警告：{total_warnings}")
    else:
        print(f"\n{'='*60}")
        print("代码规范检查结果")
        print(f"{'='*60}\n")
        
        for file_path, issues in sorted(filtered_results.items()):
            print(f"📄 {file_path}")
            print("-" * 60)
            
            for issue in sorted(issues, key=lambda x: x["line"]):
                icon = "❌" if issue["severity"] == "error" else "⚠️"
                print(
                    f"  {icon} 第{issue['line']:4d}行 [{issue['code']:5s}] "
                    f"{issue['message']}"
                )
            
            print()
        
        print(f"{'='*60}")
        print(f"总计：{total_errors} 个错误，{total_warnings} 个警告")
        print(f"{'='*60}")
    
    # 生成报告
    if args.report:
        report_path = Path(args.report)
        checker.generate_report(filtered_results, report_path)
    
    # 返回状态码
    if total_errors > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
