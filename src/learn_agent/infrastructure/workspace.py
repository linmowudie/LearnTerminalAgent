"""
LearnTerminalAgent 工作空间沙箱管理模块

确保所有文件操作和命令执行都限制在指定的工作目录内
类似代码编辑器的"打开文件夹"功能
"""

import os
from pathlib import Path
from typing import Optional
from .logger import logger_workspace, log_context


class WorkspaceManager:
    """
    工作空间管理器（单例模式）
    
    提供沙箱隔离功能，确保所有操作都在工作目录内
    """
    
    _instance: Optional['WorkspaceManager'] = None
    _workspace_root: Optional[Path] = None
    
    def __new__(cls):
        """单例模式：确保全局只有一个工作空间实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self, workspace_path: Optional[str] = None, force: bool = False):
        """
        初始化工作空间
        
        Args:
            workspace_path: 工作空间路径（可选，默认当前目录）
            force: 是否强制重新初始化（即使已经初始化过）
        """
        # 如果已经初始化过且不是强制重新初始化，则直接返回
        if self._workspace_root is not None and not force:
            logger_workspace.debug(f"工作空间已初始化，跳过：{self._workspace_root}")
            return
        
        if workspace_path:
            self._workspace_root = Path(workspace_path).resolve()
        else:
            self._workspace_root = Path.cwd().resolve()
        
        # 确保目录存在
        if not self._workspace_root.exists():
            logger_workspace.error(f"工作空间不存在：{self._workspace_root}")
            raise ValueError(f"工作空间不存在：{self._workspace_root}")
        
        logger_workspace.info(f"工作空间已设置：{self._workspace_root}")
        print(f"[OK] 工作空间已设置：{self._workspace_root}")
    
    @property
    def root(self) -> Path:
        """获取工作空间根目录"""
        if self._workspace_root is None:
            self.initialize()
        return self._workspace_root
    
    def resolve_path(self, path: str) -> Path:
        """
        解析并验证路径（核心安全方法）
        
        Args:
            path: 相对或绝对路径
            
        Returns:
            解析后的绝对路径
            
        Raises:
            ValueError: 路径越界时抛出异常
        """
        logger_workspace.debug(f"解析路径：{path}")
        
        path_obj = Path(path)
        
        # 如果是相对路径，相对于工作空间根目录解析
        if not path_obj.is_absolute():
            abs_path = self.root / path_obj
            logger_workspace.debug(f"相对路径，解析为：{abs_path}")
        else:
            abs_path = path_obj.resolve()
            logger_workspace.debug(f"绝对路径，解析为：{abs_path}")
        
        # 检查是否在工作空间内
        try:
            abs_path.relative_to(self.root)
            logger_workspace.debug(f"路径验证通过")
            return abs_path
        except ValueError:
            logger_workspace.error(f"路径越界：{path} -> {abs_path}")
            raise ValueError(
                f"路径越界：{path}\n"
                f"工作空间：{self.root}\n"
                f"目标路径：{abs_path}"
            )
    
    def is_safe_path(self, path: str) -> bool:
        """
        检查路径是否安全（在工作空间内）
        
        Args:
            path: 要检查的路径
            
        Returns:
            True 表示安全，False 表示越界
        """
        try:
            self.resolve_path(path)
            return True
        except ValueError:
            return False
    
    def get_relative_path(self, path: str) -> str:
        """
        获取相对于工作空间的路径
        
        Args:
            path: 绝对路径
            
        Returns:
            相对路径字符串
        """
        abs_path = self.resolve_path(path)
        try:
            return str(abs_path.relative_to(self.root))
        except ValueError:
            return str(abs_path)
    
    def change_directory(self, path: str):
        """
        切换工作目录（仅在沙箱内）
        
        Args:
            path: 目标目录
        """
        target_path = self.resolve_path(path)
        os.chdir(target_path)
        print(f"✓ 工作目录已切换：{self.get_relative_path(target_path)}")
    
    @classmethod
    def reset(cls):
        """重置单例实例（用于测试）"""
        cls._instance = None
        cls._workspace_root = None


# 全局工作空间实例
_workspace: Optional[WorkspaceManager] = None


def get_workspace() -> WorkspaceManager:
    """
    获取全局工作空间管理器
    
    Returns:
        WorkspaceManager 实例
    """
    global _workspace
    if _workspace is None:
        _workspace = WorkspaceManager()
        _workspace.initialize()
    return _workspace
