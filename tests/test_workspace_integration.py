"""
工作空间集成测试
测试工具函数是否正确集成了沙箱检查
"""

import pytest
import tempfile
from pathlib import Path
import sys

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from learn_agent.workspace import WorkspaceManager
from learn_agent.tools import read_file, write_file, list_directory, bash


class TestWorkspaceIntegration:
    """工具集成测试类"""
    
    def setup_method(self):
        """准备工作空间"""
        WorkspaceManager.reset()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace_path = Path(self.temp_dir.name)
        
        # 初始化工作空间
        workspace = WorkspaceManager()
        workspace.initialize(str(self.workspace_path))
        
        # 创建测试文件
        (self.workspace_path / "test.txt").write_text("hello world")
        (self.workspace_path / "subdir").mkdir()
        (self.workspace_path / "subdir" / "nested.txt").write_text("nested content")
    
    def teardown_method(self):
        """清理"""
        # 重置工作空间，避免文件锁定
        WorkspaceManager.reset()
        self.temp_dir.cleanup()
    
    def test_read_file_inside_workspace(self):
        """测试读取工作空间内的文件"""
        result = read_file.invoke({"path": str(self.workspace_path / "test.txt")})
        assert "hello world" in result
    
    def test_read_file_outside_workspace(self):
        """测试读取工作空间外的文件（应失败）"""
        result = read_file.invoke({"path": "/etc/passwd"})
        assert "Error:" in result
        assert "路径越界" in result
    
    def test_write_file_inside_workspace(self):
        """测试写入工作空间内的文件"""
        new_file = self.workspace_path / "new_file.txt"
        result = write_file.invoke({
            "path": str(new_file),
            "content": "new content"
        })
        assert "Successfully wrote" in result
        assert new_file.exists()
    
    def test_write_file_outside_workspace(self):
        """测试写入工作空间外的文件（应失败）"""
        result = write_file.invoke({
            "path": "/tmp/evil.txt",
            "content": "malicious content"
        })
        assert "Error:" in result
        assert "路径越界" in result
    
    def test_list_directory_inside_workspace(self):
        """测试列出工作空间内的目录"""
        result = list_directory.invoke({"path": str(self.workspace_path)})
        assert "Directory:" in result
        assert "test.txt" in result
    
    def test_list_directory_outside_workspace(self):
        """测试列出工作空间外的目录（应失败）"""
        result = list_directory.invoke({"path": "/etc"})
        assert "Error:" in result
        assert "路径越界" in result
    
    def test_bash_uses_workspace_root(self):
        """测试 bash 命令使用工作空间根目录"""
        # 创建一个测试脚本
        test_script = self.workspace_path / "test_pwd.py"
        test_script.write_text("import os; print(os.getcwd())")
        
        result = bash.invoke({"command": f"python {test_script}"})
        # 应该在工作空间根目录执行
        assert str(self.workspace_path) in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
