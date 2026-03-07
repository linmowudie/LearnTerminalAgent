"""
测试在其他目录调用 main() 的情况
模拟用户在不同项目目录使用框架的场景
"""
import sys
import os
from pathlib import Path
import tempfile

print("=" * 60)
print("跨目录调用测试")
print("=" * 60)

# 场景 1：在项目根目录外调用
print("\n📁 场景 1：从父目录调用框架")
print("-" * 60)

# 创建临时项目目录
temp_project = tempfile.TemporaryDirectory(prefix="test_project_")
project_path = Path(temp_project.name)
print(f"创建测试项目：{project_path}")

# 在项目中创建一些文件
(project_path / "src").mkdir()
(project_path / "data").mkdir()
(project_path / "README.md").write_text("# Test Project")
(project_path / "src" / "main.py").write_text("print('Hello')")
(project_path / "data" / "config.txt").write_text("key=value")

print(f"✓ 项目结构已创建")
print(f"  - {project_path}/src/main.py")
print(f"  - {project_path}/data/config.txt")
print(f"  - {project_path}/README.md")

# 添加 src 到路径（模拟安装后的环境）
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# 导入 Agent（模拟在其他目录启动）
from learn_agent.workspace import WorkspaceManager
from learn_agent.tools import read_file, write_file, list_directory, bash

print("\n🔧 初始化工作空间为测试项目")
workspace = WorkspaceManager()
workspace.initialize(str(project_path))

# 测试 1：读取项目内的文件
print("\n✅ 测试 1：读取项目内的文件")
result = read_file.invoke({"path": str(project_path / "README.md")})
print(f"   结果：{result[:50]}...")
assert "# Test Project" in result
print("   ✅ 通过")

# 测试 2：列出项目目录
print("\n✅ 测试 2：列出项目目录")
result = list_directory.invoke({"path": str(project_path)})
print(f"   结果：包含 {result.count('📁') + result.count('📄')} 个项目")
assert "src" in result and "data" in result
print("   ✅ 通过")

# 测试 3：尝试读取项目外的文件（应该失败）
print("\n❌ 测试 3：尝试读取项目外的文件")
# 创建一个项目外的文件
outside_file = Path(tempfile.gettempdir()) / "outside.txt"
outside_file.write_text("This is outside workspace")

result = read_file.invoke({"path": str(outside_file)})
print(f"   结果：{result}")
assert "路径越界" in result
print("   ✅ 成功阻止")

# 测试 4：在项目内创建文件
print("\n✅ 测试 4：在项目内创建文件")
new_file = project_path / "new_file.txt"
result = write_file.invoke({
    "path": str(new_file),
    "content": "New content inside workspace"
})
print(f"   结果：{result}")
assert "Successfully wrote" in result
assert new_file.exists()
print("   ✅ 通过")

# 测试 5：运行命令（应该在工作空间根目录执行）
print("\n✅ 测试 5：运行 Python 命令")
test_script = project_path / "check_dir.py"
test_script.write_text("import os; print(os.getcwd())")
result = bash.invoke({"command": f"python {test_script}"})
print(f"   执行目录：{result.strip()}")
assert str(project_path) in result
print("   ✅ 通过")

# 清理
temp_project.cleanup()

print("\n" + "=" * 60)
print("✅ 所有跨目录测试通过！")
print("=" * 60)
print("\n结论：")
print("1. ✅ 可以在任意目录调用框架")
print("2. ✅ 工作空间限制正常工作")
print("3. ✅ 工具在项目范围内正常运行")
print("4. ✅ 成功阻止访问项目外文件")
print("5. ✅ 命令在工作空间根目录执行")
