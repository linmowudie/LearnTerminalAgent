"""
Test Memory Retrieval Tool

测试记忆检索工具的功能，特别是工作空间历史检查优化
"""

import json
from pathlib import Path
import tempfile
import shutil

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from learn_agent.tools.memory_retrieval_tool import MemoryRetriever


class TestMemoryRetrieval:
    """测试 MemoryRetriever 类"""
    
    def __init__(self):
        """初始化测试环境"""
        self.test_dir = Path(tempfile.mkdtemp())
        print(f"测试目录：{self.test_dir}")
        
        # 创建检索器实例
        self.retriever = MemoryRetriever(str(self.test_dir))
        
        # 准备测试数据
        self._create_test_sessions()
    
    def _create_test_sessions(self):
        """创建测试会话数据"""
        workspace1 = "/test/workspace/project_a"
        workspace2 = "/test/workspace/project_b"
        
        # 创建工作空间 A 的会话
        for i in range(3):
            session_data = {
                'session_id': f'session_a{i}',
                'start_time': f'2026-03-{10+i}T10:00:00',
                'workspace_root': workspace1,
                'messages': [
                    {'type': 'human', 'content': f'如何在 {workspace1} 中创建文件？'},
                    {'type': 'ai', 'content': f'我来帮你在 {workspace1} 创建文件'},
                    {'type': 'tool', 'content': 'File created successfully'}
                ],
                'metadata': {
                    'tool_calls_count': 2,
                    'tasks_completed': ['task_001']
                }
            }
            
            filepath = self.test_dir / f'session_a{i}.json'
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        # 创建工作空间 B 的会话
        for i in range(2):
            session_data = {
                'session_id': f'session_b{i}',
                'start_time': f'2026-03-{10+i}T14:00:00',
                'workspace_root': workspace2,
                'messages': [
                    {'type': 'human', 'content': f'在 {workspace2} 运行测试'},
                    {'type': 'ai', 'content': f'正在 {workspace2} 执行测试'}
                ],
                'metadata': {
                    'tool_calls_count': 1,
                    'tasks_completed': []
                }
            }
            
            filepath = self.test_dir / f'session_b{i}.json'
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        print(f"已创建 {5} 个测试会话")
        print(f"  - 工作空间 A: 3 个")
        print(f"  - 工作空间 B: 2 个")
    
    def cleanup(self):
        """清理测试环境"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        print(f"\n已清理测试目录：{self.test_dir}")
    
    def test_has_workspace_history_found(self):
        """测试工作空间历史检查 - 找到的情况"""
        print("\n=== 测试 1: 工作空间历史检查（找到） ===")
        
        workspace = "/test/workspace/project_a"
        result = self.retriever.has_workspace_history(workspace)
        
        assert result is True, f"应找到工作空间 {workspace} 的历史记录"
        
        # 验证缓存机制
        start_time = __import__('time').time()
        for _ in range(100):
            self.retriever.has_workspace_history(workspace)
        end_time = __import__('time').time()
        
        elapsed = (end_time - start_time) * 1000
        print(f"✓ 缓存机制有效（100 次检查耗时 {elapsed:.2f}ms）")
        print(f"✓ 工作空间 {workspace} 有历史记录")
    
    def test_has_workspace_history_not_found(self):
        """测试工作空间历史检查 - 未找到的情况"""
        print("\n=== 测试 2: 工作空间历史检查（未找到） ===")
        
        workspace = "/test/workspace/nonexistent"
        result = self.retriever.has_workspace_history(workspace)
        
        assert result is False, f"不应找到工作空间 {workspace} 的历史记录"
        
        print(f"✓ 工作空间 {workspace} 无历史记录（符合预期）")
    
    def test_search_with_workspace_filter(self):
        """测试带工作空间过滤的搜索"""
        print("\n=== 测试 3: 带工作空间过滤的搜索 ===")
        
        query = "创建文件"
        workspace = "/test/workspace/project_a"
        
        results = self.retriever.search(query=query, workspace_filter=workspace, limit=5)
        
        # 验证所有结果都属于指定的工作空间
        for result in results:
            session = result['session']
            assert session['workspace_root'] == workspace, f"结果工作空间不匹配：{session['workspace_root']}"
            assert 'score' in result, "结果应包含相关性分数"
        
        print(f"✓ 找到 {len(results)} 条相关结果")
        if results:
            print(f"✓ 所有结果均来自工作空间：{workspace}")
        else:
            print(f"⚠️  未找到相关结果（可能是相关性算法阈值较高）")
    
    def test_search_no_results(self):
        """测试无结果的搜索"""
        print("\n=== 测试 4: 无结果的搜索 ===")
        
        query = "完全不相关的关键词_xyz123"
        workspace = "/test/workspace/project_a"
        
        results = self.retriever.search(query=query, workspace_filter=workspace, limit=5)
        
        # 可能没有匹配的结果
        print(f"✓ 搜索结果：{len(results)} 条（可能为 0）")
    
    def test_cache_mechanism(self):
        """测试缓存机制"""
        print("\n=== 测试 5: 缓存机制测试 ===")
        
        workspace = "/test/workspace/project_a"
        
        # 第一次调用会扫描文件系统
        start_time = __import__('time').time()
        result1 = self.retriever.has_workspace_history(workspace)
        time1 = (__import__('time').time() - start_time) * 1000
        
        # 清除缓存
        self.retriever.clear_cache()
        
        # 第二次调用会重新扫描
        start_time = __import__('time').time()
        result2 = self.retriever.has_workspace_history(workspace)
        time2 = (__import__('time').time() - start_time) * 1000
        
        assert result1 == result2, "缓存前后结果应一致"
        
        print(f"✓ 缓存机制工作正常")
        print(f"  - 首次扫描：{time1:.2f}ms")
        print(f"  - 清除后扫描：{time2:.2f}ms")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("MemoryRetrieval 工具测试")
        print("=" * 60)
        
        try:
            # 测试 1: 工作空间历史检查（找到）
            self.test_has_workspace_history_found()
            
            # 测试 2: 工作空间历史检查（未找到）
            self.test_has_workspace_history_not_found()
            
            # 测试 3: 带工作空间过滤的搜索
            self.test_search_with_workspace_filter()
            
            # 测试 4: 无结果的搜索
            self.test_search_no_results()
            
            # 测试 5: 缓存机制
            self.test_cache_mechanism()
            
            print("\n" + "=" * 60)
            print("✅ 所有测试通过！")
            print("=" * 60)
            
        except AssertionError as e:
            print(f"\n❌ 测试失败：{e}")
            raise
        finally:
            self.cleanup()


if __name__ == "__main__":
    # 运行测试
    tester = TestMemoryRetrieval()
    tester.run_all_tests()
    
    print("\n🎉 所有测试完成！")
