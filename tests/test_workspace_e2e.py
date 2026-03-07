"""
工作空间端到端测试
模拟真实使用场景
"""

import pytest
import tempfile
import subprocess
import sys
from pathlib import Path


class TestWorkspaceEndToEnd:
    """端到端测试类"""
    
    def setup_method(self):
        """准备测试环境"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace_path = Path(self.temp_dir.name)
        
        # 创建测试项目结构
        (self.workspace_path / "src").mkdir()
        (self.workspace_path / "data").mkdir()
        (self.workspace_path / "src" / "main.py").write_text(
            "print('Hello from main.py')"
        )
        (self.workspace_path / "data" / "config.txt").write_text("key=value")
    
    def teardown_method(self):
        """清理环境"""
        self.temp_dir.cleanup()
    
    def test_agent_respects_workspace(self):
        """测试 Agent 尊重工作空间限制"""
        # 创建一个简单的测试脚本，模拟 Agent 行为
        test_script = self.workspace_path / "test_agent.py"
        test_script.write_text(f"""
import sys
sys.path.insert(0, r'{Path(__file__).parent.parent / 'src'}')

from learn_agent.infrastructure.workspace import WorkspaceManager
from learn_agent.tools.tools import read_file

# 初始化工作空间
workspace = WorkspaceManager()
workspace.initialize(r'{self.workspace_path}')

# 尝试读取工作空间内的文件
result1 = read_file.invoke({{"path": "data/config.txt"}})
print(f"Inside workspace: {{result1}}")

# 尝试读取工作空间外的文件
result2 = read_file.invoke({{"path": "/etc/passwd"}})
print(f"Outside workspace: {{result2}}")
""")
        
        # 运行测试脚本
        result = subprocess.run(
            [sys.executable, str(test_script)],
            capture_output=True,
            text=True,
            cwd=str(self.workspace_path)
        )
        
        # 验证输出
        assert "Inside workspace: key=value" in result.stdout
        assert "Error:" in result.stdout
        assert "路径越界" in result.stdout
    
    def test_cli_accepts_workspace_argument(self):
        """测试 CLI 接受工作空间参数"""
        # 这个测试需要在实际环境中运行
        # 这里只是示例
        result = subprocess.run(
            [
                sys.executable, "-m", "learn_agent.main",
                str(self.workspace_path)
            ],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # 应该显示工作空间设置信息
        assert "工作空间已设置" in result.stdout or "workspace" in result.stdout.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
