"""
文件备份管理器 - "后悔药"功能

提供文件操作前的自动备份、压缩存储和恢复功能
"""

import os
import shutil
import zipfile
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from ..infrastructure.logger import logger_tools


# 备份目录配置
BACKUP_DIR_NAME = ".backups"
BACKUP_METADATA_FILE = "backup_metadata.json"


class BackupManager:
    """
    文件备份管理器
    
    功能：
    - 自动备份被编辑/删除的文件
    - 压缩存储节省空间
    - 支持恢复到任意备份点
    - 元数据记录操作历史
    """
    
    def __init__(self, workspace_root: str):
        """
        初始化备份管理器
        
        Args:
            workspace_root: 工作空间根路径
        """
        self.workspace_root = Path(workspace_root)
        self.backup_dir = self.workspace_root / BACKUP_DIR_NAME
        self.metadata_file = self.backup_dir / BACKUP_METADATA_FILE
        
        # 确保备份目录存在
        self.backup_dir.mkdir(exist_ok=True)
        
        # 加载或创建元数据
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """加载备份元数据"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger_tools.warning(f"Failed to load backup metadata: {e}")
                return {"backups": []}
        else:
            return {"backups": []}
    
    def _save_metadata(self):
        """保存备份元数据"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger_tools.error(f"Failed to save backup metadata: {e}")
    
    def create_backup(self, file_path: str, operation: str = "edit") -> Optional[str]:
        """
        创建文件备份
        
        Args:
            file_path: 文件路径（相对于工作空间）
            operation: 操作类型 ("edit" 或 "delete")
            
        Returns:
            备份 ID，如果失败则返回 None
        """
        try:
            abs_path = self.workspace_root / file_path
            
            # 检查文件是否存在
            if not abs_path.exists():
                logger_tools.warning(f"Cannot backup non-existent file: {file_path}")
                return None
            
            # 生成备份 ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_id = f"{timestamp}_{Path(file_path).name}"
            
            # 创建备份子目录
            backup_subdir = self.backup_dir / backup_id
            backup_subdir.mkdir(exist_ok=True)
            
            # 复制文件到备份目录
            backup_file = backup_subdir / Path(file_path).name
            shutil.copy2(abs_path, backup_file)
            
            # 压缩备份
            zip_path = self._create_zip(backup_subdir, backup_id)
            
            # 清理临时目录
            shutil.rmtree(backup_subdir)
            
            # 记录元数据
            backup_record = {
                "id": backup_id,
                "original_path": file_path,
                "operation": operation,
                "timestamp": timestamp,
                "backup_file": str(zip_path.relative_to(self.workspace_root)),
                "file_size": abs_path.stat().st_size,
            }
            
            self.metadata["backups"].append(backup_record)
            self._save_metadata()
            
            logger_tools.info(f"Created backup: {backup_id} for {file_path}")
            return backup_id
            
        except Exception as e:
            logger_tools.error(f"Failed to create backup: {e}")
            return None
    
    def _create_zip(self, source_dir: Path, backup_id: str) -> Path:
        """
        创建压缩文件
        
        Args:
            source_dir: 源目录
            backup_id: 备份 ID
            
        Returns:
            ZIP 文件路径
        """
        zip_path = self.backup_dir / f"{backup_id}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in source_dir.rglob('*'):
                if file.is_file():
                    arcname = file.relative_to(source_dir)
                    zipf.write(file, arcname)
        
        return zip_path
    
    def restore_backup(self, backup_id: str) -> str:
        """
        恢复备份
        
        Args:
            backup_id: 备份 ID
            
        Returns:
            恢复结果消息
        """
        try:
            # 查找备份记录
            backup_record = None
            for record in self.metadata["backups"]:
                if record["id"] == backup_id:
                    backup_record = record
                    break
            
            if not backup_record:
                return f"Error: Backup '{backup_id}' not found"
            
            # 检查备份文件是否存在
            zip_path = self.workspace_root / backup_record["backup_file"]
            if not zip_path.exists():
                return f"Error: Backup file not found: {zip_path}"
            
            # 解压备份
            extract_dir = self.backup_dir / f"_restore_{backup_id}"
            extract_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(extract_dir)
            
            # 恢复文件
            original_path = self.workspace_root / backup_record["original_path"]
            backup_file = extract_dir / Path(backup_record["original_path"]).name
            
            if backup_file.exists():
                # 创建父目录
                original_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 复制恢复的文件
                shutil.copy2(backup_file, original_path)
                
                # 清理临时目录
                shutil.rmtree(extract_dir)
                
                logger_tools.info(f"Restored backup: {backup_id} to {backup_record['original_path']}")
                return f"Successfully restored {backup_record['original_path']} from backup {backup_id}"
            else:
                shutil.rmtree(extract_dir)
                return f"Error: Backup file content not found"
                
        except Exception as e:
            logger_tools.error(f"Failed to restore backup: {e}")
            return f"Error: {type(e).__name__}: {str(e)}"
    
    def list_backups(self, limit: int = 10) -> str:
        """
        列出最近的备份
        
        Args:
            limit: 最大显示数量
            
        Returns:
            备份列表文本
        """
        if not self.metadata["backups"]:
            return "No backups available"
        
        # 按时间倒序排序
        sorted_backups = sorted(
            self.metadata["backups"],
            key=lambda x: x["timestamp"],
            reverse=True
        )[:limit]
        
        lines = [f"Recent backups (showing {len(sorted_backups)} of {len(self.metadata['backups'])}):", ""]
        
        for backup in sorted_backups:
            dt = datetime.strptime(backup["timestamp"], "%Y%m%d_%H%M%S")
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            
            lines.append(
                f"ID: {backup['id']}\n"
                f"  File: {backup['original_path']}\n"
                f"  Operation: {backup['operation']}\n"
                f"  Time: {formatted_time}\n"
                f"  Size: {backup['file_size']} bytes\n"
            )
        
        return '\n'.join(lines)
    
    def delete_backup(self, backup_id: str) -> str:
        """
        删除备份
        
        Args:
            backup_id: 备份 ID
            
        Returns:
            删除结果消息
        """
        try:
            # 查找备份记录
            backup_record = None
            record_index = None
            for i, record in enumerate(self.metadata["backups"]):
                if record["id"] == backup_id:
                    backup_record = record
                    record_index = i
                    break
            
            if not backup_record:
                return f"Error: Backup '{backup_id}' not found"
            
            # 删除 ZIP 文件
            zip_path = self.workspace_root / backup_record["backup_file"]
            if zip_path.exists():
                zip_path.unlink()
            
            # 从元数据中移除
            self.metadata["backups"].pop(record_index)
            self._save_metadata()
            
            logger_tools.info(f"Deleted backup: {backup_id}")
            return f"Successfully deleted backup {backup_id}"
            
        except Exception as e:
            logger_tools.error(f"Failed to delete backup: {e}")
            return f"Error: {type(e).__name__}: {str(e)}"
    
    def cleanup_old_backups(self, days: int = 30) -> str:
        """
        清理旧备份
        
        Args:
            days: 保留天数
            
        Returns:
            清理结果消息
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            removed_count = 0
            
            backups_to_remove = []
            for record in self.metadata["backups"]:
                backup_time = datetime.strptime(record["timestamp"], "%Y%m%d_%H%M%S")
                if backup_time < cutoff_date:
                    backups_to_remove.append(record["id"])
            
            for backup_id in backups_to_remove:
                self.delete_backup(backup_id)
                removed_count += 1
            
            return f"Cleaned up {removed_count} old backups older than {days} days"
            
        except Exception as e:
            logger_tools.error(f"Failed to cleanup old backups: {e}")
            return f"Error: {type(e).__name__}: {str(e)}"


# 单例模式
_backup_manager: Optional[BackupManager] = None


def get_backup_manager(workspace_root: Optional[str] = None) -> BackupManager:
    """
    获取备份管理器实例
    
    Args:
        workspace_root: 工作空间路径（可选，首次调用时使用）
        
    Returns:
        BackupManager 实例
    """
    global _backup_manager
    
    if _backup_manager is None:
        if workspace_root is None:
            from .workspace import get_workspace
            workspace = get_workspace()
            workspace_root = str(workspace.root) if workspace.root else "."
        
        _backup_manager = BackupManager(workspace_root)
    
    return _backup_manager


def reset_backup_manager():
    """重置备份管理器（用于测试）"""
    global _backup_manager
    _backup_manager = None
