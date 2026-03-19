#!/usr/bin/env python3
"""
Documentation Generator - 文档生成助手

自动生成 API 文档、README 和代码注释
"""

import argparse
import ast
import os
from pathlib import Path
from typing import Dict, List, Optional


class DocGenerator:
    """文档生成器"""
    
    def __init__(self):
        """初始化生成器"""
        self.project_info = {
            "name": "",
            "version": "",
            "description": "",
            "author": "",
        }
    
    def generate_readme(
        self,
        source_dir: Path,
        output_file: Path,
        with_examples: bool = True,
    ) -> Path:
        """
        生成 README.md
        
        Args:
            source_dir: 源代码目录
            output_file: 输出文件路径
            with_examples: 是否包含示例
            
        Returns:
            生成的 README 文件路径
        """
        # 分析项目结构
        project_analysis = self._analyze_project(source_dir)
        
        # 生成 README 内容
        readme_content = self._generate_readme_content(
            project_analysis,
            with_examples=with_examples,
        )
        
        # 写入文件
        output_file.write_text(readme_content, encoding="utf-8")
        
        return output_file
    
    def _analyze_project(self, source_dir: Path) -> dict:
        """分析项目结构"""
        analysis = {
            "name": source_dir.name,
            "modules": [],
            "classes": [],
            "functions": [],
            "has_tests": False,
            "has_docs": False,
        }
        
        # 检查是否有测试目录
        if (source_dir.parent / "tests").exists():
            analysis["has_tests"] = True
        
        # 检查是否有文档目录
        if (source_dir.parent / "docs").exists():
            analysis["has_docs"] = True
        
        # 遍历 Python 文件
        for py_file in source_dir.glob("*.py"):
            if py_file.name.startswith("test_") or py_file.name == "__init__.py":
                continue
            
            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content)
                
                module_info = {
                    "name": py_file.stem,
                    "file": str(py_file),
                    "docstring": ast.get_docstring(tree),
                    "classes": [],
                    "functions": [],
                }
                
                # 提取类和函数
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_info = {
                            "name": node.name,
                            "docstring": ast.get_docstring(node),
                            "methods": [],
                        }
                        
                        # 提取方法
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                method_info = {
                                    "name": item.name,
                                    "docstring": ast.get_docstring(item),
                                    "args": self._get_function_args(item),
                                }
                                class_info["methods"].append(method_info)
                        
                        module_info["classes"].append(class_info)
                    
                    elif isinstance(node, ast.FunctionDef):
                        func_info = {
                            "name": node.name,
                            "docstring": ast.get_docstring(node),
                            "args": self._get_function_args(node),
                        }
                        module_info["functions"].append(func_info)
                
                analysis["modules"].append(module_info)
                
            except Exception as e:
                print(f"⚠️  分析 {py_file} 失败：{e}")
        
        return analysis
    
    def _get_function_args(
        self, node: ast.FunctionDef
    ) -> List[dict]:
        """获取函数参数信息"""
        args = []
        
        for arg in node.args.args:
            arg_info = {
                "name": arg.arg,
                "type": None,
                "default": None,
            }
            
            # 获取类型注解
            if arg.annotation:
                arg_info["type"] = ast.unparse(arg.annotation)
            
            args.append(arg_info)
        
        # 获取默认值
        defaults_count = len(node.args.defaults)
        args_count = len(args)
        
        for i, default in enumerate(node.args.defaults):
            arg_index = args_count - defaults_count + i
            if arg_index >= 0 and arg_index < len(args):
                args[arg_index]["default"] = ast.unparse(default)
        
        return args
    
    def _generate_readme_content(
        self, analysis: dict, with_examples: bool = True
    ) -> str:
        """生成 README 内容"""
        lines = []
        
        # 标题
        lines.append(f"# {analysis['name']}")
        lines.append("")
        lines.append("简短的项目描述。")
        lines.append("")
        
        # 徽章（可选）
        lines.append("[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()")
        lines.append("[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)]()")
        lines.append("")
        
        # 目录
        lines.append("## 📑 目录")
        lines.append("")
        lines.append("- [安装](#-安装)")
        lines.append("- [快速开始](#-快速开始)")
        lines.append("- [API 文档](#-api-文档)")
        lines.append("- [开发](#-开发)")
        lines.append("- [测试](#-测试)")
        lines.append("- [贡献](#-贡献)")
        lines.append("- [许可证](#-许可证)")
        lines.append("")
        
        # 安装
        lines.append("## 📦 安装")
        lines.append("")
        lines.append("```bash")
        lines.append("pip install -e .")
        lines.append("```")
        lines.append("")
        
        # 快速开始
        lines.append("## 🚀 快速开始")
        lines.append("")
        lines.append("```python")
        lines.append("# 导入模块")
        
        # 添加第一个模块的示例
        if analysis["modules"]:
            first_module = analysis["modules"][0]
            lines.append(f"from {analysis['name']} import {first_module['name']}")
            lines.append("")
            lines.append("# 使用示例")
            if first_module["functions"]:
                first_func = first_module["functions"][0]
                args = ", ".join([arg["name"] for arg in first_func["args"]])
                lines.append(f"result = {first_func['name']}({args})")
            elif first_module["classes"]:
                first_class = first_module["classes"][0]
                lines.append(f"obj = {first_class['name']}()")
        
        lines.append("```")
        lines.append("")
        
        # API 文档
        lines.append("## 📖 API 文档")
        lines.append("")
        
        for module in analysis["modules"]:
            lines.append(f"### `{module['name']}`")
            lines.append("")
            
            if module["docstring"]:
                lines.append(module["docstring"])
                lines.append("")
            
            # 类文档
            for cls in module["classes"]:
                lines.append(f"#### `{cls['name']}`")
                lines.append("")
                
                if cls["docstring"]:
                    lines.append(cls["docstring"])
                    lines.append("")
                
                # 方法列表
                if cls["methods"]:
                    lines.append("**方法**:")
                    lines.append("")
                    for method in cls["methods"]:
                        if not method["name"].startswith("_"):
                            args_str = ", ".join([a["name"] for a in method["args"]])
                            lines.append(f"- `{method['name']}({args_str})` - {method['docstring'] or ''}")
                    lines.append("")
            
            # 函数文档
            if module["functions"]:
                lines.append("**函数**:")
                lines.append("")
                for func in module["functions"]:
                    if not func["name"].startswith("_"):
                        args_str = ", ".join([a["name"] for a in func["args"]])
                        lines.append(f"- `{func['name']}({args_str})` - {func['docstring'] or ''}")
                lines.append("")
        
        # 开发
        lines.append("## 💻 开发")
        lines.append("")
        lines.append("```bash")
        lines.append("# 克隆仓库")
        lines.append("git clone <repository-url>")
        lines.append(f"cd {analysis['name']}")
        lines.append("")
        lines.append("# 创建虚拟环境")
        lines.append("python -m venv venv")
        lines.append("")
        lines.append("# 激活虚拟环境")
        lines.append("# Windows:")
        lines.append("venv\\Scripts\\activate")
        lines.append("# Unix/MacOS:")
        lines.append("source venv/bin/activate")
        lines.append("")
        lines.append("# 安装开发依赖")
        lines.append("pip install -r requirements-dev.txt")
        lines.append("```")
        lines.append("")
        
        # 测试
        lines.append("## 🧪 测试")
        lines.append("")
        if analysis["has_tests"]:
            lines.append("```bash")
            lines.append("pytest tests/")
            lines.append("```")
        else:
            lines.append("测试待添加。")
        lines.append("")
        
        # 贡献
        lines.append("## 🤝 贡献")
        lines.append("")
        lines.append("欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。")
        lines.append("")
        
        # 许可证
        lines.append("## 📄 许可证")
        lines.append("")
        lines.append("本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。")
        lines.append("")
        
        return "\n".join(lines)
    
    def generate_api_docs(
        self,
        source_dir: Path,
        output_dir: Path,
        format: str = "markdown",
    ) -> Path:
        """
        生成 API 文档
        
        Args:
            source_dir: 源代码目录
            output_dir: 输出目录
            format: 输出格式 (markdown, rst)
            
        Returns:
            输出目录路径
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 分析项目
        project_analysis = self._analyze_project(source_dir)
        
        # 生成索引文件
        index_file = output_dir / "index.md"
        index_content = self._generate_api_index(project_analysis)
        index_file.write_text(index_content, encoding="utf-8")
        
        # 为每个模块生成文档
        for module in project_analysis["modules"]:
            module_file = output_dir / f"{module['name']}.md"
            module_content = self._generate_module_docs(module, format=format)
            module_file.write_text(module_content, encoding="utf-8")
        
        return output_dir
    
    def _generate_api_index(self, analysis: dict) -> str:
        """生成 API 索引"""
        lines = []
        
        lines.append("# API 参考文档")
        lines.append("")
        lines.append(f"项目名称：{analysis['name']}")
        lines.append("")
        lines.append("## 模块列表")
        lines.append("")
        
        for module in analysis["modules"]:
            lines.append(f"- [{module['name']}]({module['name']}.md) - {module['docstring'] or '无描述'}")
        
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_module_docs(
        self, module: dict, format: str = "markdown"
    ) -> str:
        """生成模块文档"""
        if format == "markdown":
            return self._generate_module_markdown(module)
        elif format == "rst":
            return self._generate_module_rst(module)
        else:
            raise ValueError(f"不支持的格式：{format}")
    
    def _generate_module_markdown(self, module: dict) -> str:
        """生成 Markdown 格式模块文档"""
        lines = []
        
        lines.append(f"# {module['name']}")
        lines.append("")
        
        if module["docstring"]:
            lines.append(module["docstring"])
            lines.append("")
        
        # 类文档
        if module["classes"]:
            lines.append("## 类")
            lines.append("")
            
            for cls in module["classes"]:
                lines.append(f"### {cls['name']}")
                lines.append("")
                
                if cls["docstring"]:
                    lines.append(cls["docstring"])
                    lines.append("")
                
                # 方法详情
                if cls["methods"]:
                    lines.append("#### 方法")
                    lines.append("")
                    
                    for method in cls["methods"]:
                        if method["name"].startswith("_"):
                            continue
                        
                        args_signature = self._format_args_signature(method["args"])
                        lines.append(f"##### `{method['name']}{args_signature}`")
                        lines.append("")
                        
                        if method["docstring"]:
                            lines.append(method["docstring"])
                            lines.append("")
                        
                        # 参数说明
                        if method["args"]:
                            lines.append("**参数**:")
                            lines.append("")
                            for arg in method["args"]:
                                type_str = f" ({arg['type']})" if arg["type"] else ""
                                default_str = f" (默认：{arg['default']})" if arg["default"] else ""
                                lines.append(f"- `{arg['name']}`{type_str}{default_str}")
                            lines.append("")
        
        # 函数文档
        if module["functions"]:
            lines.append("## 函数")
            lines.append("")
            
            for func in module["functions"]:
                if func["name"].startswith("_"):
                    continue
                
                args_signature = self._format_args_signature(func["args"])
                lines.append(f"### `{func['name']}{args_signature}`")
                lines.append("")
                
                if func["docstring"]:
                    lines.append(func["docstring"])
                    lines.append("")
                
                # 参数说明
                if func["args"]:
                    lines.append("**参数**:")
                    lines.append("")
                    for arg in func["args"]:
                        type_str = f" ({arg['type']})" if arg["type"] else ""
                        default_str = f" (默认：{arg['default']})" if arg["default"] else ""
                        lines.append(f"- `{arg['name']}`{type_str}{default_str}")
                    lines.append("")
        
        return "\n".join(lines)
    
    def _format_args_signature(self, args: List[dict]) -> str:
        """格式化参数签名"""
        parts = []
        
        for arg in args:
            part = arg["name"]
            if arg["type"]:
                part += f": {arg['type']}"
            if arg["default"]:
                part += f"={arg['default']}"
            parts.append(part)
        
        return f"({', '.join(parts)})"
    
    def _generate_module_rst(self, module: dict) -> str:
        """生成 reStructuredText 格式模块文档"""
        lines = []
        
        lines.append(module["name"])
        lines.append("=" * len(module["name"]))
        lines.append("")
        
        if module["docstring"]:
            lines.append(module["docstring"])
            lines.append("")
        
        # 类文档
        if module["classes"]:
            lines.append("Classes")
            lines.append("-" * 7)
            lines.append("")
            
            for cls in module["classes"]:
                lines.append(f".. autoclass:: {cls['name']}")
                lines.append("   :members:")
                lines.append("")
        
        # 函数文档
        if module["functions"]:
            lines.append("Functions")
            lines.append("-" * 9)
            lines.append("")
            
            for func in module["functions"]:
                lines.append(f".. autofunction:: {func['name']}")
                lines.append("")
        
        return "\n".join(lines)
    
    def add_docstrings_to_file(
        self,
        source_file: Path,
        output_file: Optional[Path] = None,
        inplace: bool = False,
    ) -> Path:
        """
        为文件添加 docstring
        
        Args:
            source_file: 源文件路径
            output_file: 输出文件路径
            inplace: 是否原地修改
            
        Returns:
            输出文件路径
        """
        if inplace:
            output_file = source_file
        elif output_file is None:
            output_file = source_file.parent / f"{source_file.stem}_documented.py"
        
        # 读取并解析源文件
        content = source_file.read_text(encoding="utf-8")
        tree = ast.parse(content)
        
        # 添加 docstring（简化实现，实际需要更复杂的 AST 操作）
        print(f"⚠️  注意：此功能需要更复杂的 AST 操作来保持代码格式")
        print(f"建议使用专门的工具如 interrogate 或 pydocstyle")
        
        # 简单实现：仅生成建议
        suggestions = self._generate_docstring_suggestions(tree)
        
        suggestion_file = source_file.parent / f"{source_file.stem}_docstring_suggestions.md"
        suggestion_file.write_text(suggestions, encoding="utf-8")
        
        print(f"✅ 已生成 docstring 建议：{suggestion_file}")
        
        return suggestion_file
    
    def _generate_docstring_suggestions(self, tree: ast.AST) -> str:
        """生成 docstring 建议"""
        lines = []
        lines.append("# Docstring 建议")
        lines.append("")
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    node_type = "函数" if isinstance(node, ast.FunctionDef) else "类"
                    lines.append(f"## {node_type}: `{node.name}`")
                    lines.append("")
                    lines.append(f"位置：第 {node.lineno} 行")
                    lines.append("")
                    lines.append("建议添加 docstring:")
                    lines.append("")
                    
                    if isinstance(node, ast.FunctionDef):
                        lines.append(f'"""')
                        lines.append(f"TODO: 添加 {node.name} 函数的描述")
                        lines.append("")
                        if node.args.args:
                            lines.append("Args:")
                            for arg in node.args.args:
                                if arg.arg != "self":
                                    lines.append(f"    {arg.arg}: TODO: 参数描述")
                        lines.append("")
                        if node.returns:
                            lines.append("Returns:")
                            lines.append(f"    TODO: 返回值描述")
                        lines.append('"""')
                    else:
                        lines.append(f'"""')
                        lines.append(f"TODO: 添加 {node.name} 类的描述")
                        lines.append("")
                        lines.append("Attributes:")
                        lines.append("    TODO: 类属性描述")
                        lines.append('"""')
                    
                    lines.append("")
        
        return "\n".join(lines)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="Documentation Generator - 文档生成助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s src/ -o docs/
  %(prog)s --readme -o README.md
  %(prog)s src/ --api --format markdown
  %(prog)s src/module.py --add-docstrings --inplace
        """,
    )
    
    parser.add_argument(
        "source",
        nargs="?",
        type=str,
        help="源代码目录或文件",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="输出文件或目录",
    )
    parser.add_argument(
        "--readme",
        action="store_true",
        help="生成 README.md",
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="生成 API 文档",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "rst"],
        default="markdown",
        help="文档格式，默认 markdown",
    )
    parser.add_argument(
        "--add-docstrings",
        action="store_true",
        help="为代码添加 docstring 建议",
    )
    parser.add_argument(
        "--inplace",
        action="store_true",
        help="原地修改文件（与 --add-docstrings 一起使用）",
    )
    parser.add_argument(
        "--with-examples",
        action="store_true",
        help="包含使用示例",
    )
    
    args = parser.parse_args()
    
    generator = DocGenerator()
    
    if args.readme:
        # 生成 README
        if not args.source:
            print("❌ 生成 README 需要指定源代码目录")
            sys.exit(1)
        
        source_path = Path(args.source)
        output_path = Path(args.output) if args.output else Path("README.md")
        
        print(f"📝 正在生成 README...")
        readme_file = generator.generate_readme(
            source_path,
            output_path,
            with_examples=args.with_examples,
        )
        print(f"✅ README 已生成：{readme_file}")
    
    elif args.api:
        # 生成 API 文档
        if not args.source:
            print("❌ 生成 API 文档需要指定源代码目录")
            sys.exit(1)
        
        source_path = Path(args.source)
        output_path = Path(args.output) if args.output else Path("docs/api")
        
        print(f"📝 正在生成 API 文档...")
        api_dir = generator.generate_api_docs(
            source_path,
            output_path,
            format=args.format,
        )
        print(f"✅ API 文档已生成：{api_dir}")
    
    elif args.add_docstrings:
        # 添加 docstring 建议
        if not args.source:
            print("❌ 需要指定源代码文件或目录")
            sys.exit(1)
        
        source_path = Path(args.source)
        
        if source_path.is_file():
            print(f"📝 正在生成 docstring 建议...")
            output_file = generator.add_docstrings_to_file(
                source_path,
                inplace=args.inplace,
            )
            print(f"✅ Docstring 建议已生成：{output_file}")
        else:
            print("⚠️  批量处理目录尚未完全实现，请指定单个文件")
    
    else:
        # 默认行为：生成完整文档
        if not args.source:
            parser.print_help()
            sys.exit(1)
        
        source_path = Path(args.source)
        output_path = Path(args.output) if args.output else Path("docs")
        
        print(f"📝 正在生成完整文档...")
        
        # 生成 README
        readme_file = generator.generate_readme(source_path, output_path / "README.md")
        print(f"✓ README: {readme_file}")
        
        # 生成 API 文档
        api_dir = generator.generate_api_docs(source_path, output_path / "api")
        print(f"✓ API 文档：{api_dir}")
        
        print(f"\n✅ 文档生成完成！")


if __name__ == "__main__":
    import sys
    main()
