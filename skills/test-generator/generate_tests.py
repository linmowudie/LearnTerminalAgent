#!/usr/bin/env python3
"""
Test Generator - 测试用例生成器

自动分析 Python 代码并生成 pytest 测试模板
"""

import argparse
import ast
import os
from pathlib import Path
from typing import Dict, List, Optional, Set


class TestGenerator:
    """测试用例生成器"""
    
    def __init__(self, template_dir: Optional[Path] = None):
        """
        初始化生成器
        
        Args:
            template_dir: 自定义模板目录
        """
        self.template_dir = template_dir
    
    def generate_for_file(
        self,
        source_file: Path,
        output_dir: Optional[Path] = None,
        with_mock: bool = False,
        prefix: str = "test_",
    ) -> Path:
        """
        为源文件生成测试
        
        Args:
            source_file: Python 源文件路径
            output_dir: 输出目录，默认为源文件同级 tests 目录
            with_mock: 是否包含 Mock
            prefix: 测试文件前缀
            
        Returns:
            生成的测试文件路径
        """
        # 读取源文件
        content = source_file.read_text(encoding="utf-8")
        
        # 解析 AST
        tree = ast.parse(content)
        
        # 分析代码结构
        analysis = self._analyze_ast(tree)
        
        # 确定输出路径
        if output_dir is None:
            output_dir = source_file.parent / "tests"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        test_filename = f"{prefix}{source_file.stem}.py"
        test_file = output_dir / test_filename
        
        # 生成测试代码
        test_code = self._generate_test_code(
            analysis,
            source_file.stem,
            with_mock=with_mock,
        )
        
        # 写入测试文件
        test_file.write_text(test_code, encoding="utf-8")
        
        return test_file
    
    def _analyze_ast(self, tree: ast.AST) -> dict:
        """
        分析 AST 提取函数和类信息
        
        Args:
            tree: AST 树
            
        Returns:
            分析结果字典
        """
        result = {
            "module_name": "",
            "functions": [],
            "classes": [],
            "imports": [],
        }
        
        for node in ast.walk(tree):
            # 收集函数
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_info = self._extract_function_info(node)
                result["functions"].append(func_info)
            
            # 收集类
            elif isinstance(node, ast.ClassDef):
                class_info = self._extract_class_info(node)
                result["classes"].append(class_info)
            
            # 收集导入
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    result["imports"].append(f"{module}.{alias.name}")
        
        return result
    
    def _extract_function_info(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> dict:
        """提取函数信息"""
        func_info = {
            "name": node.name,
            "is_async": isinstance(node, ast.AsyncFunctionDef),
            "args": [],
            "has_return": False,
            "raises_exceptions": False,
            "docstring": ast.get_docstring(node),
            "decorators": [],
            "line_no": node.lineno,
        }
        
        # 提取参数
        for arg in node.args.args:
            if arg.arg != "self":
                func_info["args"].append({
                    "name": arg.arg,
                    "type": self._get_annotation_type(arg.annotation),
                })
        
        # 检查返回值
        if node.returns:
            func_info["has_return"] = True
        
        # 检查是否抛出异常
        for child in ast.walk(node):
            if isinstance(child, ast.Raise):
                func_info["raises_exceptions"] = True
                break
        
        # 提取装饰器
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                func_info["decorators"].append(decorator.id)
            elif isinstance(decorator, ast.Attribute):
                func_info["decorators"].append(decorator.attr)
        
        return func_info
    
    def _extract_class_info(self, node: ast.ClassDef) -> dict:
        """提取类信息"""
        class_info = {
            "name": node.name,
            "bases": [],
            "methods": [],
            "docstring": ast.get_docstring(node),
            "line_no": node.lineno,
        }
        
        # 提取基类
        for base in node.bases:
            if isinstance(base, ast.Name):
                class_info["bases"].append(base.id)
        
        # 提取方法
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_info = self._extract_function_info(item)
                class_info["methods"].append(method_info)
        
        return class_info
    
    def _get_annotation_type(
        self, annotation: Optional[ast.expr]
    ) -> Optional[str]:
        """获取类型注解字符串"""
        if annotation is None:
            return None
        
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Subscript):
            if isinstance(annotation.value, ast.Name):
                return annotation.value.id
        
        return None
    
    def _generate_test_code(
        self,
        analysis: dict,
        module_name: str,
        with_mock: bool = False,
    ) -> str:
        """
        生成测试代码
        
        Args:
            analysis: 代码分析结果
            module_name: 模块名称
            with_mock: 是否包含 Mock
            
        Returns:
            测试代码字符串
        """
        lines = []
        
        # 文件头注释
        lines.append('"""')
        lines.append(f"{module_name} 模块的测试套件")
        lines.append("")
        lines.append("此文件由 test-generator 自动生成")
        lines.append("请根据实际业务逻辑完善测试用例")
        lines.append('"""')
        lines.append("")
        
        # 导入语句
        lines.append("import pytest")
        if with_mock:
            lines.append("from unittest.mock import Mock, MagicMock, patch")
        lines.append(f"from {module_name} import *")
        lines.append("")
        lines.append("")
        
        # 为函数生成测试
        for func in analysis["functions"]:
            # 跳过私有函数
            if func["name"].startswith("_"):
                continue
            
            lines.extend(
                self._generate_function_tests(func, module_name, with_mock)
            )
            lines.append("")
        
        # 为类生成测试
        for cls in analysis["classes"]:
            lines.extend(
                self._generate_class_tests(cls, module_name, with_mock)
            )
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_function_tests(
        self,
        func: dict,
        module_name: str,
        with_mock: bool = False,
    ) -> List[str]:
        """生成函数测试代码"""
        lines = []
        func_name = func["name"]
        
        # 测试类定义
        class_name = f"Test{func_name.replace('_', ' ').title().replace(' ', '')}"
        lines.append(f"class {class_name}:")
        lines.append(f'    """{func_name} 函数的测试类"""')
        lines.append("")
        
        # 1. 基本功能测试
        lines.append("    def test_basic_functionality(self):")
        lines.append(f'        """测试 {func_name} 的基本功能"""')
        lines.append("        # TODO: 设置测试数据")
        
        # 根据参数生成调用示例
        args = func["args"]
        if args:
            arg_names = [arg["name"] for arg in args]
            lines.append(f"        # result = {func_name}({', '.join(arg_names)})")
        else:
            lines.append(f"        # result = {func_name}()")
        
        lines.append("        # TODO: 添加断言")
        lines.append("        # assert result == expected_value")
        lines.append("")
        
        # 2. 参数化测试（如果有多个参数）
        if len(args) >= 1:
            lines.append("    @pytest.mark.parametrize(")
            lines.append('        "input_value,expected",')
            lines.append("        [")
            lines.append("            # TODO: 添加测试用例")
            lines.append('            # (input1, expected1),')
            lines.append('            # (input2, expected2),')
            lines.append("        ],")
            lines.append("    )")
            lines.append("    def test_parametrized_cases(self, input_value, expected):")
            lines.append("        """测试多个输入输出场景"""")
            lines.append("        # TODO: 实现参数化测试")
            lines.append("")
        
        # 3. 异常测试
        if func["raises_exceptions"]:
            lines.append("    def test_error_handling(self):")
            lines.append("        """测试异常处理"""")
            lines.append("        # TODO: 测试异常情况")
            lines.append('        # with pytest.raises(ExpectedError):')
            lines.append(f"        #     {func_name}(invalid_input)")
            lines.append("")
        
        # 4. 边界值测试
        lines.append("    def test_boundary_values(self):")
        lines.append("        """测试边界值"""")
        lines.append("        # TODO: 测试边界条件")
        lines.append("        # 例如：空值、零值、最大值、最小值等")
        lines.append("")
        
        return lines
    
    def _generate_class_tests(
        self,
        cls: dict,
        module_name: str,
        with_mock: bool = False,
    ) -> List[str]:
        """生成类测试代码"""
        lines = []
        class_name = cls["name"]
        
        # 测试类定义
        test_class_name = f"Test{class_name}"
        lines.append(f"class {test_class_name}:")
        lines.append(f'    """{class_name} 类的测试类"""')
        lines.append("")
        
        # 添加 fixture
        if with_mock and cls["bases"]:
            lines.append("    @pytest.fixture")
            lines.append("    def mock_dependencies(self):")
            lines.append("        """创建依赖的 Mock 对象"""")
            lines.append("        # TODO: 创建基类的 Mock")
            lines.append("        mock_obj = Mock()")
            lines.append("        yield mock_obj")
            lines.append("")
        
        lines.append("    @pytest.fixture")
        lines.append(f"    def {class_name.lower()}_instance(self):")
        lines.append(f"        """创建 {class_name} 实例"""")
        lines.append("        # TODO: 创建实例所需的参数")
        lines.append(f"        # instance = {class_name}()")
        lines.append("        # yield instance")
        lines.append("")
        
        # 为每个公共方法生成测试
        for method in cls["methods"]:
            if method["name"].startswith("_"):
                continue
            
            method_name = method["name"]
            lines.append(f"    def test_{method_name}(self):")
            lines.append(f'        """测试 {method_name} 方法"""')
            lines.append("        # TODO: 实现测试逻辑")
            lines.append("        # Arrange - 准备测试数据")
            lines.append("        # Act - 执行操作")
            lines.append("        # Assert - 验证结果")
            lines.append("")
        
        return lines
    
    def generate_for_directory(
        self,
        source_dir: Path,
        output_dir: Path,
        recursive: bool = True,
        skip_existing: bool = False,
    ) -> List[Path]:
        """
        为目录中所有 Python 文件生成测试
        
        Args:
            source_dir: 源代码目录
            output_dir: 输出目录
            recursive: 是否递归子目录
            skip_existing: 跳过已存在的测试文件
            
        Returns:
            生成的测试文件列表
        """
        generated_files = []
        
        if recursive:
            py_files = source_dir.rglob("*.py")
        else:
            py_files = source_dir.glob("*.py")
        
        for source_file in py_files:
            # 跳过测试文件本身
            if source_file.name.startswith("test_"):
                continue
            
            # 跳过 __init__.py
            if source_file.name == "__init__.py":
                continue
            
            # 计算相对路径
            try:
                rel_path = source_file.relative_to(source_dir)
            except ValueError:
                rel_path = Path(source_file.name)
            
            # 确定输出文件路径
            test_file = output_dir / rel_path
            test_file = test_file.with_name(f"test_{test_file.name}")
            
            # 检查是否已存在
            if skip_existing and test_file.exists():
                print(f"⏭️  跳过已存在：{test_file}")
                continue
            
            # 创建输出目录
            test_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 生成测试
            print(f"📝 生成测试：{source_file.name} -> {test_file.name}")
            generated_file = self.generate_for_file(
                source_file,
                output_dir=output_dir.parent,
            )
            generated_files.append(generated_file)
        
        return generated_files


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="Test Generator - 测试用例生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s src/my_module.py
  %(prog)s src/calculator.py -o tests/
  %(prog)s src/service.py --with-mock
  %(prog)s src/ -r -o tests/
  %(prog)s src/ --skip-existing
        """,
    )
    
    parser.add_argument(
        "source",
        type=str,
        help="源代码文件或目录",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="输出目录，默认为源文件同级的 tests 目录",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="递归处理子目录",
    )
    parser.add_argument(
        "--with-mock",
        action="store_true",
        help="生成包含 Mock 的测试代码",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="跳过已存在的测试文件",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="test_",
        help="测试文件前缀，默认 test_",
    )
    
    args = parser.parse_args()
    
    source_path = Path(args.source)
    
    if not source_path.exists():
        print(f"❌ 路径不存在：{source_path}")
        sys.exit(1)
    
    generator = TestGenerator()
    
    if source_path.is_file():
        # 处理单个文件
        output_dir = Path(args.output) if args.output else None
        
        print(f"📝 正在为 {source_path.name} 生成测试...")
        test_file = generator.generate_for_file(
            source_path,
            output_dir=output_dir,
            with_mock=args.with_mock,
            prefix=args.prefix,
        )
        print(f"✅ 测试文件已生成：{test_file}")
        print(f"\n下一步:")
        print(f"  1. 打开 {test_file}")
        print(f"  2. 完善 TODO 标记的测试用例")
        print(f"  3. 运行 pytest {test_file}")
    
    elif source_path.is_dir():
        # 处理目录
        output_dir = Path(args.output) if args.output else source_path / "tests"
        
        print(f"📝 正在为 {source_path} 生成测试...")
        generated_files = generator.generate_for_directory(
            source_path,
            output_dir=output_dir,
            recursive=args.recursive,
            skip_existing=args.skip_existing,
        )
        
        print(f"\n✅ 生成了 {len(generated_files)} 个测试文件:")
        for test_file in generated_files:
            print(f"  ✓ {test_file}")
        
        print(f"\n下一步:")
        print(f"  1. 完善生成的测试文件中的 TODO 项")
        print(f"  2. 运行 pytest {output_dir} 执行所有测试")
        print(f"  3. 查看测试覆盖率：pytest --cov={source_path}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    import sys
    main()
