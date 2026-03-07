"""
LearnTerminalAgent 项目配置管理

管理项目根目录、数据目录和配置
"""

import json
import os
from pathlib import Path
from typing import Optional


class ProjectConfig:
    """项目配置类"""
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        初始化项目配置
        
        Args:
            project_root: 项目根目录（可选，自动检测）
        """
        if project_root is None:
            project_root = self._find_project_root()
        
        self.project_root = project_root.resolve()
        self.config_dir = self.project_root / "config"
        self.data_dir = self.project_root / "data"
        self.config_file = self.config_dir / "config.json"
        
        # 确保必要目录存在
        self._ensure_dirs()
    
    def _find_project_root(self) -> Path:
        """查找项目根目录"""
        # 策略 1: 当前目录有 config/config.json
        if (Path.cwd() / "config" / "config.json").exists():
            return Path.cwd()
        
        # 策略 2: 父目录查找
        current = Path.cwd()
        for parent in [current] + list(current.parents):
            if (parent / "config" / "config.json").exists():
                return parent
            
            # 也检查是否在 learn_agent 包内（用于安装后的情况）
            if (parent / "learn_agent" / "__init__.py").exists():
                # 向上一级找到项目根目录
                potential_root = parent.parent
                if (potential_root / "config" / "config.json").exists():
                    return potential_root
        
        # 策略 3: 回退到当前目录
        return current
    
    def _ensure_dirs(self):
        """确保所有必要目录存在"""
        dirs = [
            self.config_dir,
            self.data_dir,
            self.data_dir / ".tasks",
            self.data_dir / ".team",
            self.data_dir / ".inbox",
            self.data_dir / ".transcripts",
            self.data_dir / ".worktrees",
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    def get_data_path(self, name: str) -> Path:
        """获取数据目录下的路径"""
        return self.data_dir / name
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "project_root": str(self.project_root),
            "config_dir": str(self.config_dir),
            "data_dir": str(self.data_dir),
        }
    
    def print_info(self):
        """打印项目信息"""
        print("\n" + "="*60)
        print("LearnAgent 项目配置")
        print("="*60)
        print(f"项目根目录：{self.project_root}")
        print(f"配置目录：{self.config_dir}")
        print(f"数据目录：{self.data_dir}")
        print("="*60 + "\n")


# 全局项目实例
_project: Optional[ProjectConfig] = None


def get_project_config() -> ProjectConfig:
    """获取全局项目配置"""
    global _project
    if _project is None:
        _project = ProjectConfig()
    return _project


def reset_project():
    """重置项目配置"""
    global _project
    _project = None
