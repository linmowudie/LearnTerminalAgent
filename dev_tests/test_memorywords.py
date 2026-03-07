"""
测试在 MemoryWords 目录启动的情况
"""
import sys
from pathlib import Path
import tempfile

# 模拟在 MemoryWords 目录
memory_words_dir = Path("F:/ProjectCode/MemoryWords")
if not memory_words_dir.exists():
    memory_words_dir = Path(tempfile.mkdtemp())

print(f"测试目录：{memory_words_dir}")

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from learn_agent.workspace import WorkspaceManager
from learn_agent.tools import list_directory, write_file, read_file

print("\n1. 初始化工作空间为 MemoryWords")
workspace = WorkspaceManager()
workspace.initialize(str(memory_words_dir))

print(f"\n2. 当前工作空间：{workspace.root}")

print("\n3. 测试列出目录内容...")
try:
    result = list_directory.invoke({"path": "."})
    print(f"✅ 成功！看到 {len(result)} 字符的输出")
    print(f"   前 100 字符：{result[:100]}...")
except Exception as e:
    print(f"❌ 失败：{e}")

print("\n4. 测试创建文件...")
try:
    result = write_file.invoke({
        "path": "hello.py",
        "content": "print('Hello from MemoryWords!')"
    })
    print(f"✅ 成功！{result}")
    
    # 验证文件是否存在
    hello_file = memory_words_dir / "hello.py"
    if hello_file.exists():
        print(f"✅ 文件已创建：{hello_file}")
        print(f"   内容：{hello_file.read_text()}")
    else:
        print(f"❌ 文件未创建成功")
        
except Exception as e:
    print(f"❌ 失败：{e}")

print("\n5. 测试读取文件...")
try:
    result = read_file.invoke({"path": "hello.py"})
    print(f"✅ 成功！读取到：{result}")
except Exception as e:
    print(f"❌ 失败：{e}")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
