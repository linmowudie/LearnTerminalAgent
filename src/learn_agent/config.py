"""
LearnTerminalAgent 配置管理模块

集中管理所有配置项，支持多环境变量来源和 JSON 配置文件
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List
from dotenv import load_dotenv
from .logger import logger_config


@dataclass
class AgentConfig:
    """Agent 配置类"""
    
    # API 配置
    api_key: str = ""
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    model_name: str = "qwen3.5-flash"
    
    # 运行配置
    max_tokens: int = 8000
    timeout: int = 120
    max_iterations: int = 50
    
    # 安全配置
    dangerous_patterns: List[str] = None
    
    # 上下文压缩配置
    context_threshold: int = 50000
    keep_recent: int = 3
    auto_compact_enabled: bool = True
    
    # 任务管理配置
    max_todos: int = 20
    
    # 后台任务配置
    bg_timeout: int = 300
    
    # 团队配置
    team_poll_interval: int = 5
    team_idle_timeout: int = 60
    
    # Worktree 配置
    worktree_enabled: bool = True
    worktree_base_ref: str = "HEAD"
    
    def __post_init__(self):
        """初始化后处理"""
        if self.dangerous_patterns is None:
            self.dangerous_patterns = [
                "rm -rf /", "sudo", "shutdown", 
                "reboot", "> /dev/", "mkfs", "dd if="
            ]
    
    @classmethod
    def from_env(cls) -> "AgentConfig":
        """从环境变量加载配置"""
        
        # 尝试加载 .env 文件
        load_dotenv(override=True)
        
        # 支持多种 API Key 环境变量名
        api_key = (
            os.getenv("QWEN_API_KEY") or
            os.getenv("ANTHROPIC_API_KEY") or
            os.getenv("OPENAI_API_KEY")
        )
        
        if not api_key:
            raise ValueError(
                "未找到 API Key！请设置以下环境变量之一:\n"
                "  - QWEN_API_KEY\n"
                "  - ANTHROPIC_API_KEY\n"
                "  - OPENAI_API_KEY"
            )
        
        # 加载其他配置
        base_url = os.getenv(
            "ANTHROPIC_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        model_name = os.getenv(
            "MODEL_ID",
            "qwen3.5-flash"
        )
        
        return cls(
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
        )
    
    @classmethod
    def from_json(cls, config_path: Optional[str] = None) -> "AgentConfig":
        """
        从 JSON 文件加载配置
        
        Args:
            config_path: 配置文件路径（可选，默认在以下位置查找）
                        1. 命令行指定的路径
                        2. ./config/config.json (项目根目录)
                        3. src/learn_agent/config.json (开发目录)
                        
        Returns:
            AgentConfig 实例
        """
        if config_path is None:
            # 尝试多个可能的路径
            possible_paths = [
                Path(__file__).parent.parent.parent / "config" / "config.json",  # ./config/config.json
                Path(__file__).parent / "config.json",  # src/learn_agent/config.json
            ]
            
            for path in possible_paths:
                if path.exists():
                    config_path = path
                    logger_config.info(f"找到配置文件：{config_path}")
                    break
            
            if config_path is None or not Path(config_path).exists():
                logger_config.debug(f"所有可能的配置文件都不存在")
                print(f"Warning: Config file not found in common locations.")
                print("Falling back to environment variables.")
                return cls.from_env()
        
        logger_config.info(f"从 JSON 加载配置：{config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 合并 JSON 配置和环境变量
            api_key = (
                os.getenv("QWEN_API_KEY") or
                os.getenv("ANTHROPIC_API_KEY") or
                os.getenv("OPENAI_API_KEY") or
                data.get("agent", {}).get("api_key", "")
            )
            
            if not api_key:
                raise ValueError(
                    "未找到 API Key！请在 config.json 或环境变量中设置"
                )
            
            config = cls(
                api_key=api_key,
                base_url=data.get("agent", {}).get("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
                model_name=data.get("agent", {}).get("model_name", "qwen3.5-flash"),
                max_tokens=data.get("agent", {}).get("max_tokens", 8000),
                timeout=data.get("agent", {}).get("timeout", 120),
                max_iterations=data.get("agent", {}).get("max_iterations", 50),
                dangerous_patterns=data.get("security", {}).get("dangerous_patterns", [
                    "rm -rf /", "sudo", "shutdown", "reboot", "> /dev/", "mkfs", "dd if="
                ]),
                context_threshold=data.get("context", {}).get("threshold", 50000),
                keep_recent=data.get("context", {}).get("keep_recent", 3),
                auto_compact_enabled=data.get("context", {}).get("auto_compact_enabled", True),
                max_todos=data.get("tasks", {}).get("max_items", 20),
                bg_timeout=data.get("background", {}).get("timeout", 300),
                team_poll_interval=data.get("team", {}).get("poll_interval", 5),
                team_idle_timeout=data.get("team", {}).get("idle_timeout", 60),
                worktree_enabled=data.get("worktree", {}).get("enabled", True),
                worktree_base_ref=data.get("worktree", {}).get("base_ref", "HEAD"),
            )
            
            logger_config.info(f"配置加载成功：{config_path}")
            print(f"[OK] Loaded config from: {config_path}")
            return config
            
        except Exception as e:
            logger_config.error(f"加载配置失败：{e}")
            print(f"Error loading config: {e}")
            print("Falling back to environment variables.")
            return cls.from_env()
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "agent": {
                "api_key": self.api_key,
                "base_url": self.base_url,
                "model_name": self.model_name,
                "max_tokens": self.max_tokens,
                "timeout": self.timeout,
                "max_iterations": self.max_iterations,
            },
            "security": {
                "dangerous_patterns": self.dangerous_patterns,
            },
            "context": {
                "threshold": self.context_threshold,
                "keep_recent": self.keep_recent,
                "auto_compact_enabled": self.auto_compact_enabled,
            },
            "tasks": {
                "max_items": self.max_todos,
            },
            "background": {
                "timeout": self.bg_timeout,
            },
            "team": {
                "poll_interval": self.team_poll_interval,
                "idle_timeout": self.team_idle_timeout,
            },
            "worktree": {
                "enabled": self.worktree_enabled,
                "base_ref": self.worktree_base_ref,
            },
        }
    
    def save_to_json(self, config_path: Optional[str] = None):
        """
        保存配置到 JSON 文件
        
        Args:
            config_path: 配置文件路径（可选）
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config.json"
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Saved config to: {config_path}")
    
    def validate(self) -> bool:
        """验证配置有效性"""
        if not self.api_key or len(self.api_key) < 10:
            raise ValueError("API Key 格式不正确")
        
        if not self.base_url.startswith("http"):
            raise ValueError("Base URL 格式不正确")
        
        return True
    
    def print_info(self):
        """打印配置信息"""
        print("\n" + "=" * 60)
        print("LearnAgent 配置")
        print("=" * 60)
        print(f"[OK] 模型：{self.model_name}")
        print(f"[OK] Base URL: {self.base_url}")
        print(f"[OK] API Key: {self.api_key[:10]}...{self.api_key[-4:]}")
        print(f"[OK] Max Tokens: {self.max_tokens}")
        print(f"[OK] Timeout: {self.timeout}s")
        print("=" * 60 + "\n")


# 全局配置实例（延迟加载）
_config: Optional[AgentConfig] = None


def get_config(from_json: bool = True) -> AgentConfig:
    """
    获取全局配置实例
    
    Args:
        from_json: 是否从 JSON 文件加载（默认 True）
        
    Returns:
        AgentConfig 实例
    """
    global _config
    if _config is None:
        if from_json:
            _config = AgentConfig.from_json()
        else:
            _config = AgentConfig.from_env()
        _config.validate()
    return _config


def reload_config(from_json: bool = True) -> AgentConfig:
    """
    重新加载配置
    
    Args:
        from_json: 是否从 JSON 文件加载（默认 True）
        
    Returns:
        AgentConfig 实例
    """
    global _config
    if from_json:
        _config = AgentConfig.from_json()
    else:
        _config = AgentConfig.from_env()
    _config.validate()
    return _config
