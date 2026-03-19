"""
测试"后悔药"功能 - 文件备份和恢复
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.learn_agent.tools.backup import BackupManager
from pathlib import Path
import tempfile
import shutil


def test_backup_manager():
    """测试备份管理器基本功能"""
    
    print("\n" + "="*60)
    print("测试：后悔药功能（文件备份与恢复）")
    print("="*60 + "\n")
    
    # 创建临时工作目录
    temp_dir = Path(tempfile.mkdtemp(prefix="backup_test_"))
    print(f"测试目录：{temp_dir}\n")
    
    try:
        # 初始化备份管理器
        backup_manager = BackupManager(str(temp_dir))
        print("✅ 备份管理器初始化成功\n")
        
        # 创建测试文件
        test_file = temp_dir / "test.txt"
        test_file.write_text("这是原始内容\n第二行\n第三行", encoding='utf-8')
        print(f"✅ 创建测试文件：{test_file.name}")
        print(f"   原始内容:\n{test_file.read_text(encoding='utf-8')}\n")
        
        # 测试 1: 创建备份
        print("-" * 60)
        print("测试 1: 创建备份")
        print("-" * 60)
        backup_id = backup_manager.create_backup("test.txt", operation="edit")
        print(f"备份 ID: {backup_id}")
        print(f"备份文件：{temp_dir / '.backups' / f'{backup_id}.zip'}\n")
        
        # 修改文件
        test_file.write_text("这是修改后的内容\n第二行保持不变\n新增第四行", encoding='utf-8')
        print(f"修改后内容:\n{test_file.read_text(encoding='utf-8')}\n")
        
        # 测试 2: 列出备份
        print("-" * 60)
        print("测试 2: 列出备份")
        print("-" * 60)
        backup_list = backup_manager.list_backups()
        print(backup_list + "\n")
        
        # 测试 3: 恢复备份
        print("-" * 60)
        print("测试 3: 恢复备份")
        print("-" * 60)
        restore_result = backup_manager.restore_backup(backup_id)
        print(f"恢复结果：{restore_result}\n")
        
        print(f"恢复后内容:\n{test_file.read_text(encoding='utf-8')}\n")
        
        # 测试 4: 删除备份
        print("-" * 60)
        print("测试 4: 删除备份")
        print("-" * 60)
        delete_result = backup_manager.delete_backup(backup_id)
        print(f"删除结果：{delete_result}\n")
        
        # 验证备份已删除
        backup_list_after = backup_manager.list_backups()
        print(f"删除后备份列表:\n{backup_list_after}\n")
        
        print("="*60)
        print("✅ 所有测试完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试失败：{type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理临时目录
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            print(f"\n清理临时目录：{temp_dir}")


def test_edit_file_with_backup():
    """测试 edit_file 工具的备份功能"""
    
    print("\n" + "="*60)
    print("测试：edit_file 工具自动备份")
    print("="*60 + "\n")
    
    # 创建临时工作目录
    temp_dir = Path(tempfile.mkdtemp(prefix="edit_test_"))
    print(f"测试目录：{temp_dir}\n")
    
    try:
        from src.learn_agent.tools.tools import edit_file
        from src.learn_agent.infrastructure.workspace import get_workspace
        
        # 初始化工作空间
        workspace = get_workspace()
        workspace.initialize(str(temp_dir))
        
        # 创建测试文件
        test_file = temp_dir / "example.py"
        original_code = '''def hello():
    print("Hello, World!")
    
if __name__ == "__main__":
    hello()
'''
        test_file.write_text(original_code, encoding='utf-8')
        print(f"创建测试文件：{test_file.name}")
        print(f"原始内容:\n{original_code}\n")
        
        # 调用 edit_file（应该自动创建备份）
        print("-" * 60)
        print("调用 edit_file（自动备份）")
        print("-" * 60)
        
        # 获取工具的底层函数
        edit_func = edit_file.func if hasattr(edit_file, 'func') else edit_file
        result = edit_func(
            str(test_file.relative_to(temp_dir)),
            'print("Hello, World!")',
            'print("Hello, Backup!")'
        )
        print(f"编辑结果:\n{result}\n")
        
        print(f"修改后内容:\n{test_file.read_text(encoding='utf-8')}\n")
        
        # 检查备份是否创建
        from src.learn_agent.tools.backup import get_backup_manager
        backup_manager = get_backup_manager(str(temp_dir))
        backup_list = backup_manager.list_backups()
        print(f"创建的备份:\n{backup_list}\n")
        
        print("="*60)
        print("✅ edit_file 备份测试完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试失败：{type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理临时目录
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            print(f"\n清理临时目录：{temp_dir}")


if __name__ == "__main__":
    # 运行测试
    test_backup_manager()
    print("\n\n")
    test_edit_file_with_backup()
