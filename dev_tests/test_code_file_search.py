"""
Test Code Search and File Search Tools

测试代码搜索和文件搜索工具的功能
"""

import os
from pathlib import Path
import tempfile
import shutil

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from learn_agent.tools.code_search_tool import CodeSearcher, search_code
from learn_agent.tools.file_search_tool import FileSearcher, search_files, find_files_by_content


class TestCodeSearch:
    """测试 CodeSearcher 类"""
    
    def __init__(self):
        """初始化测试环境"""
        self.test_dir = Path(tempfile.mkdtemp())
        print(f"测试目录：{self.test_dir}")
        
        # 创建测试文件结构
        self._create_test_files()
        
        # 创建搜索引擎
        self.searcher = CodeSearcher(str(self.test_dir))
    
    def _create_test_files(self):
        """创建测试文件"""
        # Python 文件
        py_file1 = self.test_dir / "test_module.py"
        py_file1.write_text("""
def hello_world():
    print("Hello, World!")

class Calculator:
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b

# Main execution
if __name__ == "__main__":
    calc = Calculator()
    result = calc.add(5, 3)
    print(f"Result: {result}")
""", encoding='utf-8')
        
        # 另一个 Python 文件
        py_file2 = self.test_dir / "utils.py"
        py_file2.write_text("""
def format_string(text):
    return text.strip().lower()

def calculate_sum(numbers):
    return sum(numbers)
""", encoding='utf-8')
        
        # JavaScript 文件
        js_file = self.test_dir / "app.js"
        js_file.write_text("""
function greet(name) {
    console.log(`Hello, ${name}!`);
}

const add = (a, b) => a + b;

module.exports = { greet, add };
""", encoding='utf-8')
        
        # 子目录中的文件
        subdir = self.test_dir / "subdir"
        subdir.mkdir()
        py_file3 = subdir / "helper.py"
        py_file3.write_text("""
def helper_function(x, y):
    '''Helper function for testing'''
    return x * y
""", encoding='utf-8')
        
        print(f"已创建 {4} 个测试文件")
        print(f"  - test_module.py")
        print(f"  - utils.py")
        print(f"  - app.js")
        print(f"  - subdir/helper.py")
    
    def cleanup(self):
        """清理测试环境"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        print(f"\n已清理测试目录：{self.test_dir}")
    
    def test_search_function_definition(self):
        """测试搜索函数定义"""
        print("\n=== 测试 1: 搜索函数定义 ===")
        
        pattern = "def hello_world"
        results = self.searcher.search(pattern, extensions=['.py'])
        
        assert len(results) > 0, "应找到函数定义"
        assert any('hello_world' in r['match'] for r in results), "应包含 hello_world 函数"
        
        print(f"✓ 找到 {len(results)} 处匹配")
        for r in results[:2]:
            print(f"  - {r['file']}:{r['line']} - {r['match'][:50]}")
    
    def test_search_class_definition(self):
        """测试搜索类定义"""
        print("\n=== 测试 2: 搜索类定义 ===")
        
        pattern = "class Calculator"
        results = self.searcher.search(pattern, extensions=['.py'])
        
        assert len(results) > 0, "应找到类定义"
        assert any('Calculator' in r['match'] for r in results), "应包含 Calculator 类"
        
        print(f"✓ 找到 {len(results)} 处匹配")
        for r in results[:2]:
            print(f"  - {r['file']}:{r['line']} - {r['match'][:50]}")
    
    def test_search_with_context(self):
        """测试搜索带上下文的代码"""
        print("\n=== 测试 3: 搜索带上下文的代码 ===")
        
        pattern = "return a + b"
        results = self.searcher.search(pattern, extensions=['.py'], context_lines=2)
        
        assert len(results) > 0, "应找到匹配的代码"
        
        # 验证上下文包含足够的行
        first_result = results[0]
        context_lines = first_result['context'].split('\n')
        assert len(context_lines) > 1, "上下文应包含多行"
        
        print(f"✓ 找到 {len(results)} 处匹配")
        print(f"  示例上下文:")
        print(f"  {first_result['context'][:200]}")
    
    def test_regex_search(self):
        """测试正则表达式搜索"""
        print("\n=== 测试 4: 正则表达式搜索 ===")
        
        # 搜索所有 def 开头的行
        pattern = r"^\s*def\s+\w+"
        results = self.searcher.search(pattern, extensions=['.py'], use_regex=True)
        
        assert len(results) > 0, "应找到函数定义"
        
        print(f"✓ 正则搜索找到 {len(results)} 处匹配")
        for r in results[:3]:
            print(f"  - {r['file']}:{r['line']}")
    
    def test_file_type_filtering(self):
        """测试文件类型过滤"""
        print("\n=== 测试 5: 文件类型过滤 ===")
        
        pattern = "function"
        
        # 只搜索 Python 文件
        py_results = self.searcher.search(pattern, extensions=['.py'])
        
        # 只搜索 JavaScript 文件
        js_results = self.searcher.search(pattern, extensions=['.js'])
        
        # 验证结果分离
        for r in py_results:
            assert r['file'].endswith('.py'), "Python 搜索结果应为.py 文件"
        
        for r in js_results:
            assert r['file'].endswith('.js'), "JS 搜索结果应为.js 文件"
        
        print(f"✓ Python 文件：{len(py_results)} 处匹配")
        print(f"✓ JavaScript 文件：{len(js_results)} 处匹配")


class TestFileSearch:
    """测试 FileSearcher 类"""
    
    def __init__(self):
        """初始化测试环境"""
        self.test_dir = Path(tempfile.mkdtemp())
        print(f"\nFileSearch 测试目录：{self.test_dir}")
        
        # 创建测试文件结构
        self._create_test_structure()
        
        # 创建搜索引擎
        self.searcher = FileSearcher(str(self.test_dir))
    
    def _create_test_structure(self):
        """创建测试文件结构"""
        # 创建多个文件
        files = [
            "config.json",
            "README.md",
            "main.py",
            "test_main.py",
            "utils.py",
            ".gitignore",
            "subdir/nested_file.txt",
            "subdir/another.py",
            "src/app.py",
            "src/lib/helper.py",
        ]
        
        for file_path in files:
            full_path = self.test_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(f"# Content of {file_path}", encoding='utf-8')
        
        print(f"已创建 {len(files)} 个测试文件")
    
    def cleanup(self):
        """清理测试环境"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        print(f"已清理测试目录：{self.test_dir}")
    
    def test_search_by_exact_name(self):
        """测试精确文件名搜索"""
        print("\n=== 测试 6: 精确文件名搜索 ===")
        
        results = self.searcher.search_by_name("main.py")
        
        assert len(results) > 0, "应找到 main.py"
        assert any(r['path'] == 'main.py' for r in results), "应包含精确匹配"
        
        print(f"✓ 找到 {len(results)} 个匹配文件")
        for r in results[:3]:
            print(f"  - {r['path']}")
    
    def test_search_by_wildcard(self):
        """测试通配符搜索"""
        print("\n=== 测试 7: 通配符搜索 ===")
        
        # 搜索所有 .py 文件
        results = self.searcher.search_by_name("*.py")
        
        assert len(results) > 0, "应找到.py 文件"
        
        # 验证所有结果都是.py 文件
        for r in results:
            assert r['path'].endswith('.py'), f"应为.py 文件：{r['path']}"
        
        print(f"✓ 找到 {len(results)} 个.py 文件")
        for r in results[:5]:
            print(f"  - {r['path']}")
    
    def test_search_by_partial_name(self):
        """测试部分文件名搜索"""
        print("\n=== 测试 8: 部分文件名搜索 ===")
        
        # 搜索包含 test 的文件
        results = self.searcher.search_by_name("test")
        
        assert len(results) > 0, "应找到包含'test'的文件"
        
        # 验证所有结果都包含 test
        for r in results:
            assert 'test' in r['path'].lower(), f"路径应包含'test': {r['path']}"
        
        print(f"✓ 找到 {len(results)} 个包含'test'的文件")
        for r in results[:3]:
            print(f"  - {r['path']}")
    
    def test_search_by_content(self):
        """测试按内容搜索"""
        print("\n=== 测试 9: 按内容搜索 ===")
        
        # 搜索包含"Content"的行
        results = self.searcher.search_by_content("Content", file_pattern="*.py")
        
        assert len(results) > 0, "应找到包含'Content'的文件"
        
        print(f"✓ 找到 {len(results)} 处内容匹配")
        for r in results[:3]:
            print(f"  - {r['file']}:{r['line']} - {r['match'][:50]}")
    
    def test_recursive_search(self):
        """测试递归搜索"""
        print("\n=== 测试 10: 递归搜索 ===")
        
        # 递归搜索所有.py 文件
        results = self.searcher.search_by_name("*.py", recursive=True)
        
        # 应找到子目录中的文件
        has_subdir_file = any('subdir' in r['path'] or 'src' in r['path'] for r in results)
        assert has_subdir_file, "应找到子目录中的文件"
        
        print(f"✓ 递归搜索找到 {len(results)} 个.py 文件（包括子目录）")
    
    def test_max_depth_limit(self):
        """测试最大深度限制"""
        print("\n=== 测试 11: 最大深度限制 ===")
        
        # 限制深度为 1
        results_limited = self.searcher.search_by_name("*.py", max_depth=1)
        
        # 不限制深度
        results_unlimited = self.searcher.search_by_name("*.py", max_depth=10)
        
        # 有限的结果应该更少或相等
        assert len(results_limited) <= len(results_unlimited), "深度限制应减少结果数量"
        
        print(f"✓ 深度限制=1: {len(results_limited)} 个文件")
        print(f"✓ 深度限制=10: {len(results_unlimited)} 个文件")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Code Search & File Search 工具测试")
    print("=" * 60)
    
    try:
        # Code Search 测试
        print("\n【Code Search 测试】")
        code_tester = TestCodeSearch()
        code_tester.test_search_function_definition()
        code_tester.test_search_class_definition()
        code_tester.test_search_with_context()
        code_tester.test_regex_search()
        code_tester.test_file_type_filtering()
        code_tester.cleanup()
        
        # File Search 测试
        print("\n【File Search 测试】")
        file_tester = TestFileSearch()
        file_tester.test_search_by_exact_name()
        file_tester.test_search_by_wildcard()
        file_tester.test_search_by_partial_name()
        file_tester.test_search_by_content()
        file_tester.test_recursive_search()
        file_tester.test_max_depth_limit()
        file_tester.cleanup()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ 测试失败：{e}")
        raise


if __name__ == "__main__":
    run_all_tests()
    print("\n🎉 所有测试完成！")
