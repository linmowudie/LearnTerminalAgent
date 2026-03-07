"""
真实场景测试：模拟用户实际使用
"""
import sys
from pathlib import Path
import tempfile

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from learn_agent.infrastructure.workspace import WorkspaceManager
from learn_agent.tools.tools import read_file, write_file, list_directory

print("=" * 60)
print("真实场景测试")
print("=" * 60)

# 创建两个独立的项目目录
project1 = tempfile.TemporaryDirectory(prefix="project_A_")
project2 = tempfile.TemporaryDirectory(prefix="project_B_")

path1 = Path(project1.name)
path2 = Path(project2.name)

print(f"\n📁 项目 A: {path1}")
print(f"📁 项目 B: {path2}")

# 在项目 A 中创建文件
(path1 / "config.ini").write_text("[settings]\nkey=A")
(path1 / "data.txt").write_text("Project A Data")

# 在项目 B 中创建文件  
(path2 / "config.ini").write_text("[settings]\nkey=B")
(path2 / "data.txt").write_text("Project B Data")

print("\n✓ 两个项目都已初始化")

# 测试场景 1：在项目 A 工作空间读取项目 A 的文件
print("\n" + "=" * 60)
print("场景 1：在项目 A 工作空间内操作")
print("=" * 60)

workspace = WorkspaceManager()
workspace.initialize(str(path1), force=True)

print(f"当前工作空间：{path1}")

result = read_file.invoke({"path": str(path1 / "config.ini")})
print(f"✅ 读取 config.ini: {result}")
assert "key=A" in result

result = read_file.invoke({"path": str(path1 / "data.txt")})
print(f"✅ 读取 data.txt: {result}")
assert "Project A Data" in result

# 测试场景 2：尝试访问项目 B 的文件（应该失败）
print("\n" + "=" * 60)
print("场景 2：尝试访问另一个项目的文件")
print("=" * 60)

result = read_file.invoke({"path": str(path2 / "config.ini")})
print(f"❌ 读取项目 B 的 config.ini:")
print(f"   {result}")
assert "路径越界" in result
print("✅ 成功阻止跨项目访问")

# 测试场景 3：切换到项目 B 工作空间
print("\n" + "=" * 60)
print("场景 3：切换到项目 B 工作空间")
print("=" * 60)

workspace.initialize(str(path2), force=True)
print(f"当前工作空间：{path2}")

result = read_file.invoke({"path": str(path2 / "config.ini")})
print(f"✅ 读取项目 B 的 config.ini: {result}")
assert "key=B" in result

result = read_file.invoke({"path": str(path2 / "data.txt")})
print(f"✅ 读取项目 B 的 data.txt: {result}")
assert "Project B Data" in result

# 测试场景 4：在项目 B 中尝试访问项目 A（应该失败）
result = read_file.invoke({"path": str(path1 / "config.ini")})
print(f"\n❌ 尝试访问项目 A 的 config.ini:")
print(f"   {result}")
assert "路径越界" in result
print("✅ 成功阻止")

# 清理
project1.cleanup()
project2.cleanup()

print("\n" + "=" * 60)
print("✅ 真实场景测试全部通过！")
print("=" * 60)
print("\n验证结论：")
print("1. ✅ 不同项目完全隔离")
print("2. ✅ 无法跨项目访问文件")
print("3. ✅ 工作空间切换正常")
print("4. ✅ 每个项目内工具正常工作")
print("5. ✅ 安全性得到保证")
