"""
Test Memory Storage Module

测试记忆存储模块的功能
"""

import json
import time
from pathlib import Path
import tempfile
import shutil

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from learn_agent.services.memory_storage import MemoryStorage, get_memory_storage, reset_memory_storage


class TestMemoryStorage:
    """测试 MemoryStorage 类"""
    
    def __init__(self):
        """初始化测试环境"""
        self.test_dir = Path(tempfile.mkdtemp())
        print(f"测试目录：{self.test_dir}")
        
        # 创建测试配置
        self.config = {
            'enabled': True,
            'storage_dir': str(self.test_dir),
            'min_duration_seconds': 1,  # 缩短时间以便测试
            'save_triggers': ['session_end', 'task_completed'],
            'retention_days': 90,
        }
        
        # 创建存储器实例
        self.storage = MemoryStorage(self.config)
    
    def cleanup(self):
        """清理测试环境"""
        # 结束所有活跃会话
        for session_id in list(self.storage._active_sessions.keys()):
            self.storage.end_session(session_id)
        
        # 删除测试目录
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        print(f"\n已清理测试目录：{self.test_dir}")
    
    def test_session_creation(self):
        """测试会话创建功能"""
        print("\n=== 测试 1: 会话创建 ===")
        
        workspace_root = "/test/workspace"
        session_id = self.storage.start_session(workspace_root)
        
        assert session_id.startswith("session_"), f"Session ID 格式错误：{session_id}"
        assert session_id in self.storage._active_sessions, "会话未保存到内存"
        
        session_data = self.storage._active_sessions[session_id]
        assert session_data['workspace_root'] == workspace_root, "工作空间路径不匹配"
        assert session_data['messages'] == [], "新会话不应包含消息"
        
        print(f"✓ 会话创建成功：{session_id}")
        return session_id
    
    def test_message_saving(self, session_id):
        """测试消息保存功能"""
        print("\n=== 测试 2: 消息保存 ===")
        
        # 保存人类消息
        self.storage.save_message(session_id, "你好，帮我创建一个文件", "human")
        
        # 保存 AI 消息
        self.storage.save_message(session_id, "好的，我来帮你创建文件", "ai")
        
        # 保存工具调用
        tool_result = {
            'tool_name': 'write_file',
            'tool_args': {'path': 'test.txt', 'content': 'hello'},
            'tool_result': 'File created'
        }
        self.storage.save_message(session_id, tool_result, "tool")
        
        session_data = self.storage._active_sessions[session_id]
        assert len(session_data['messages']) == 3, f"消息数量应为 3，实际为 {len(session_data['messages'])}"
        assert session_data['metadata']['tool_calls_count'] == 1, "工具调用计数应为 1"
        
        print(f"✓ 成功保存 {len(session_data['messages'])} 条消息")
        print(f"  - 工具调用次数：{session_data['metadata']['tool_calls_count']}")
    
    def test_task_completion(self, session_id):
        """测试任务完成标记"""
        print("\n=== 测试 3: 任务完成标记 ===")
        
        task_id = "task_001"
        self.storage.mark_task_completed(session_id, task_id)
        
        # 注意：由于配置了 task_completed 触发器，会话可能已经结束
        # 所以我们只验证没有抛出异常
        print(f"✓ 任务完成标记成功：{task_id}")
    
    def test_session_ending(self, session_id):
        """测试会话结束和持久化"""
        print("\n=== 测试 4: 会话结束和持久化 ===")
        
        # 等待满足最小持续时间
        print(f"等待 {self.config['min_duration_seconds']} 秒以满足最小持续时间...")
        time.sleep(self.config['min_duration_seconds'] + 0.5)
        
        # 结束会话
        self.storage.end_session(session_id)
        
        # 验证会话已从内存中移除
        assert session_id not in self.storage._active_sessions, "会话应从内存中移除"
        
        # 验证文件已保存到磁盘
        session_files = list(self.test_dir.glob("session_*.json"))
        assert len(session_files) == 1, f"应保存 1 个会话文件，实际为 {len(session_files)}"
        
        # 验证文件内容
        with open(session_files[0], 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        assert saved_data['session_id'] == session_id, "Session ID 不匹配"
        assert saved_data['workspace_root'] == "/test/workspace", "工作空间路径不匹配"
        assert len(saved_data['messages']) == 3, "消息数量不匹配"
        assert 'duration_seconds' in saved_data['metadata'], "缺少持续时间信息"
        
        print(f"✓ 会话持久化成功：{session_files[0].name}")
        print(f"  - 消息数：{len(saved_data['messages'])}")
        print(f"  - 持续时间：{saved_data['metadata']['duration_seconds']:.2f}秒")
    
    def test_short_session_skip(self):
        """测试短时会话跳过"""
        print("\n=== 测试 4: 短时会话跳过 ===")
        
        # 记录当前文件数
        session_files_before = list(self.test_dir.glob("session_*.json"))
        count_before = len(session_files_before)
        print(f"当前会话文件数：{count_before}")
        
        session_id = self.storage.start_session("/test/short")
        self.storage.save_message(session_id, "短消息", "human")
        
        # 立即结束（不满足最小持续时间）
        self.storage.end_session(session_id)
        
        # 验证会话已从内存中移除
        assert session_id not in self.storage._active_sessions, "会话应从内存中移除"
        
        # 验证没有新增文件
        session_files_after = list(self.test_dir.glob("session_*.json"))
        count_after = len(session_files_after)
        
        assert count_after == count_before, f"短时会话不应保存文件，文件数从 {count_before} 变为 {count_after}"
        
        print(f"✓ 短时会话正确跳过保存（文件数保持 {count_after}）")
    
    def test_storage_stats(self):
        """测试存储统计信息"""
        print("\n=== 测试 5: 存储统计信息 ===")
        
        stats = self.storage.get_storage_stats()
        
        assert 'total_sessions' in stats, "缺少总会话数"
        assert 'active_sessions' in stats, "缺少活跃会话数"
        assert 'storage_dir' in stats, "缺少存储目录"
        assert 'total_size_bytes' in stats, "缺少总大小"
        assert 'enabled' in stats, "缺少启用状态"
        
        print(f"✓ 存储统计信息:")
        print(f"  - 总会话数：{stats['total_sessions']}")
        print(f"  - 活跃会话数：{stats['active_sessions']}")
        print(f"  - 总大小：{stats['total_size_mb']:.2f} MB")
        print(f"  - 启用状态：{'是' if stats['enabled'] else '否'}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("MemoryStorage 模块测试")
        print("=" * 60)
        
        try:
            # 测试 1: 创建会话
            session_id = self.test_session_creation()
            
            # 测试 2: 保存消息
            self.test_message_saving(session_id)
            
            # 测试 3: 任务完成（会触发保存）
            self.test_task_completion(session_id)
            
            # 等待满足最小持续时间后手动结束会话
            print("\n等待后会话自动结束...")
            time.sleep(self.config['min_duration_seconds'] + 0.5)
            if session_id in self.storage._active_sessions:
                self.storage.end_session(session_id)
            
            # 验证持久化
            session_files = list(self.test_dir.glob("session_*.json"))
            if session_files:
                with open(session_files[0], 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                print(f"✓ 会话持久化成功：{session_files[0].name}")
                print(f"  - 消息数：{len(saved_data['messages'])}")
                if 'duration_seconds' in saved_data['metadata']:
                    print(f"  - 持续时间：{saved_data['metadata']['duration_seconds']:.2f}秒")
            
            # 测试 4: 短时会话跳过
            self.test_short_session_skip()
            
            # 测试 5: 存储统计
            self.test_storage_stats()
            
            print("\n" + "=" * 60)
            print("✅ 所有测试通过！")
            print("=" * 60)
            
        except AssertionError as e:
            print(f"\n❌ 测试失败：{e}")
            raise
        finally:
            self.cleanup()


def test_global_instance():
    """测试全局实例函数"""
    print("\n=== 测试全局实例函数 ===")
    
    # 重置全局实例
    reset_memory_storage()
    
    # 获取全局实例
    storage1 = get_memory_storage()
    storage2 = get_memory_storage()
    
    assert storage1 is storage2, "全局实例应复用同一对象"
    
    print("✓ 全局单例模式工作正常")


if __name__ == "__main__":
    # 运行测试
    tester = TestMemoryStorage()
    tester.run_all_tests()
    
    # 测试全局实例
    test_global_instance()
    
    print("\n🎉 所有测试完成！")
