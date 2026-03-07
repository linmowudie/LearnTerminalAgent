"""
工作空间管理器单元测试
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from learn_agent.workspace import WorkspaceManager, get_workspace


class TestWorkspaceManager:
    """工作空间管理器测试类"""
    
    def setup_method(self):
        """每个测试前的准备工作"""
        WorkspaceManager.reset()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace_path = Path(self.temp_dir.name)
        
        # 创建测试目录结构
        (self.workspace_path / "subdir").mkdir()
        (self.workspace_path / "test.txt").write_text("test content")
        (self.workspace_path / "subdir" / "nested.txt").write_text("nested content")
    
    def teardown_method(self):
        """每个测试后的清理工作"""
        self.temp_dir.cleanup()
        WorkspaceManager.reset()
    
    def test_initialize_default(self):
        """测试默认初始化（当前目录）"""
        manager = WorkspaceManager()
        manager.initialize()
        assert manager.root == Path.cwd().resolve()
    
    def test_initialize_custom_path(self):
        """测试自定义路径初始化"""
        manager = WorkspaceManager()
        manager.initialize(str(self.workspace_path))
        assert manager.root == self.workspace_path.resolve()
    
    def test_initialize_nonexistent_path(self):
        """测试不存在的路径"""
        manager = WorkspaceManager()
        with pytest.raises(ValueError, match="工作空间不存在"):
            manager.initialize("/nonexistent/path")
    
    def test_resolve_path_relative(self):
        """测试相对路径解析"""
        manager = WorkspaceManager()
        manager.initialize(str(self.workspace_path))
        
        # 切换到工作空间目录再测试相对路径
        original_cwd = os.getcwd()
        try:
            os.chdir(str(self.workspace_path))
            resolved = manager.resolve_path("test.txt")
            assert resolved == self.workspace_path / "test.txt"
        finally:
            os.chdir(original_cwd)
    
    def test_resolve_path_absolute(self):
        """测试绝对路径解析"""
        manager = WorkspaceManager()
        manager.initialize(str(self.workspace_path))
        
        abs_path = str(self.workspace_path / "test.txt")
        resolved = manager.resolve_path(abs_path)
        assert resolved == self.workspace_path / "test.txt"
    
    def test_resolve_path_escapes_workspace(self):
        """测试路径越界检测"""
        manager = WorkspaceManager()
        manager.initialize(str(self.workspace_path))
        
        with pytest.raises(ValueError, match="路径越界"):
            manager.resolve_path("/etc/passwd")
    
    def test_is_safe_path_valid(self):
        """测试安全路径检测（有效路径）"""
        manager = WorkspaceManager()
        manager.initialize(str(self.workspace_path))
        
        # 使用绝对路径测试
        assert manager.is_safe_path(str(self.workspace_path / "test.txt")) is True
        assert manager.is_safe_path(str(self.workspace_path / "subdir" / "nested.txt")) is True
    
    def test_is_safe_path_invalid(self):
        """测试安全路径检测（无效路径）"""
        manager = WorkspaceManager()
        manager.initialize(str(self.workspace_path))
        
        assert manager.is_safe_path("/etc/passwd") is False
        assert manager.is_safe_path("../other.txt") is False
    
    def test_get_relative_path(self):
        """测试获取相对路径"""
        manager = WorkspaceManager()
        manager.initialize(str(self.workspace_path))
        
        abs_path = self.workspace_path / "subdir" / "nested.txt"
        rel_path = manager.get_relative_path(str(abs_path))
        # Windows 使用反斜杠，需要统一处理
        assert rel_path.replace('\\', '/') == "subdir/nested.txt"
    
    def test_change_directory(self):
        """测试切换工作目录"""
        manager = WorkspaceManager()
        manager.initialize(str(self.workspace_path))
        
        original_cwd = os.getcwd()
        try:
            # 使用绝对路径切换
            manager.change_directory(str(self.workspace_path / "subdir"))
            assert os.getcwd() == str(self.workspace_path / "subdir")
        finally:
            os.chdir(original_cwd)
    
    def test_singleton_pattern(self):
        """测试单例模式"""
        manager1 = WorkspaceManager()
        manager1.initialize(str(self.workspace_path))
        
        manager2 = WorkspaceManager()
        # 不应该再次初始化
        assert manager2.root == manager1.root


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
