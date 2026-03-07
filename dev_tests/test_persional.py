"""
测试在 PersionalProject 目录启动并运行工具
"""
import sys
from pathlib import Path
import tempfile

# 模拟 PersionalProject 目录
test_dir = Path("F:/ProjectCode/PersionalProject")
if not test_dir.exists():
    test_dir = Path(tempfile.mkdtemp(prefix="persional_test_"))
    print(f"创建测试目录：{test_dir}")

print(f"测试目录：{test_dir}")

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from learn_agent.infrastructure.workspace import WorkspaceManager
from learn_agent.tools.tools import list_directory, write_file, read_file

print("\n1. 初始化工作空间为测试目录")
workspace = WorkspaceManager()
workspace.initialize(str(test_dir), force=True)

print(f"\n2. 当前工作空间：{workspace.root}")

print("\n3. 测试列出目录内容...")
try:
    result = list_directory.invoke({"path": "."})
    print(f"✅ 成功！看到 {len(result)} 字符的输出")
    if len(result) > 200:
        print(f"   前 200 字符：{result[:200]}...")
    else:
        print(f"   内容：{result}")
except Exception as e:
    print(f"❌ 失败：{e}")
    import traceback
    traceback.print_exc()

print("\n4. 测试创建文件...")
try:
    result = write_file.invoke({
        "path": "hello.py",
        "content": "print('Hello from PersionalProject!')"
    })
    print(f"✅ 成功！{result}")
    
    # 验证文件是否存在
    hello_file = test_dir / "hello.py"
    if hello_file.exists():
        print(f"✅ 文件已创建：{hello_file}")
        content = hello_file.read_text()
        print(f"   内容：{content}")
    else:
        print(f"❌ 文件未创建成功")
        
except Exception as e:
    print(f"❌ 失败：{e}")
    import traceback
    traceback.print_exc()

print("\n5. 测试读取文件...")
try:
    result = read_file.invoke({"path": "hello.py"})
    print(f"✅ 成功！读取到：{result}")
except Exception as e:
    print(f"❌ 失败：{e}")
    import traceback
    traceback.print_exc()

print("\n6. 测试 bash 命令执行...")
try:
    from learn_agent.tools.tools import bash
    result = bash.invoke({"command": "dir" if sys.platform == 'win32' else "ls"})
    print(f"✅ bash 命令成功！输出长度：{len(result)} 字符")
    print(f"   前 100 字符：{result[:100]}...")
except Exception as e:
    print(f"❌ 失败：{e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("所有测试完成！")
print("=" * 60)
