"""
简单验证工作空间功能
"""
import sys
from pathlib import Path
import tempfile

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from learn_agent.workspace import WorkspaceManager, get_workspace
from learn_agent.tools import read_file, write_file

print("=" * 60)
print("工作空间沙箱功能验证")
print("=" * 60)

# 创建临时目录作为工作空间
temp_dir = tempfile.TemporaryDirectory()
workspace_path = Path(temp_dir.name)
print(f"\n1. 创建工作空间：{workspace_path}")

# 初始化工作空间
workspace = WorkspaceManager()
workspace.initialize(str(workspace_path))

# 创建测试文件
test_file = workspace_path / "test.txt"
test_file.write_text("Hello Workspace!")
print(f"2. 创建测试文件：{test_file}")

# 测试 1：读取工作空间内的文件
print("\n3. 测试：读取工作空间内的文件")
result = read_file.invoke({"path": str(test_file)})
print(f"   结果：{result}")
assert "Hello Workspace!" in result, "❌ 测试失败"
print("   ✅ 通过")

# 测试 2：尝试读取工作空间外的文件
print("\n4. 测试：尝试读取工作空间外的文件")
result = read_file.invoke({"path": "C:/Windows/System32/drivers/etc/hosts"})
print(f"   结果：{result}")
assert "路径越界" in result, "❌ 测试失败"
print("   ✅ 通过")

# 测试 3：写入工作空间内的文件
print("\n5. 测试：写入工作空间内的文件")
new_file = workspace_path / "new.txt"
result = write_file.invoke({
    "path": str(new_file),
    "content": "New file content"
})
print(f"   结果：{result}")
assert "Successfully wrote" in result, "❌ 测试失败"
assert new_file.exists(), "❌ 文件未创建"
print("   ✅ 通过")

# 清理
temp_dir.cleanup()

print("\n" + "=" * 60)
print("✅ 所有验证通过！")
print("=" * 60)
