"""
LearnTerminalAgent Skill Loading 模块 - s05

实现技能加载功能，支持按需加载知识
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from langchain_core.tools import tool

from .config import get_config
from .project_config import get_project_config

# 使用 ProjectConfig 管理路径
PROJECT = get_project_config()
skills_dir = PROJECT.project_root / "skills"


class SkillLoader:
    """
    技能加载器
    
    两层技能注入机制：
    - Layer 1: 技能名称和简短描述（放在系统提示中）
    - Layer 2: 完整技能内容（按需加载到 tool_result）
    """
    
    def __init__(self, skills_dir: Optional[Path] = None):
        """
        初始化技能加载器
        
        Args:
            skills_dir: 技能目录路径
        """
        if skills_dir is None:
            skills_dir = PROJECT.project_root / "skills"
        
        self.skills_dir = skills_dir
        self.skills: Dict[str, Dict] = {}
        
        # 加载所有技能
        self._load_all()
    
    def _load_all(self):
        """加载所有技能文件"""
        if not self.skills_dir.exists():
            return
        
        # 查找所有 SKILL.md 文件
        for skill_file in sorted(self.skills_dir.rglob("SKILL.md")):
            try:
                text = skill_file.read_text(encoding='utf-8')
                meta, body = self._parse_frontmatter(text)
                
                # 获取技能名称
                name = meta.get("name", skill_file.parent.name)
                
                # 存储技能信息
                self.skills[name] = {
                    "meta": meta,
                    "body": body,
                    "path": str(skill_file),
                    "dir": str(skill_file.parent),
                }
            except Exception as e:
                print(f"Warning: Failed to load skill from {skill_file}: {e}")
    
    def _parse_frontmatter(self, text: str) -> tuple:
        """
        解析 YAML frontmatter
        
        格式：
        ---
        name: skill-name
        description: Skill description
        ---
        Skill body content...
        """
        match = re.match(r"^---\n(.*?)\n---\n(.*)", text, re.DOTALL)
        
        if not match:
            # 没有 frontmatter，返回全部内容
            return {}, text.strip()
        
        # 解析 frontmatter
        meta = {}
        for line in match.group(1).strip().splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                meta[key.strip()] = val.strip()
        
        return meta, match.group(2).strip()
    
    def get_descriptions(self) -> str:
        """
        Layer 1: 获取所有技能的简短描述
        
        Returns:
            技能描述字符串
        """
        if not self.skills:
            return "(no skills available)"
        
        lines = []
        for name, skill in self.skills.items():
            desc = skill["meta"].get("description", "No description")
            tags = skill["meta"].get("tags", "")
            
            line = f"  - {name}: {desc}"
            if tags:
                line += f" [{tags}]"
            
            lines.append(line)
        
        return "\n".join(lines)
    
    def get_content(self, name: str) -> Optional[str]:
        """
        Layer 2: 获取技能完整内容
        
        Args:
            name: 技能名称
            
        Returns:
            技能完整内容
        """
        skill = self.skills.get(name)
        
        if not skill:
            return None
        
        # 返回完整的技能内容（包括 frontmatter）
        skill_file = Path(skill["path"])
        return skill_file.read_text(encoding='utf-8')
    
    def list_skills(self) -> List[str]:
        """
        列出所有可用技能
        
        Returns:
            技能名称列表
        """
        return list(self.skills.keys())
    
    def get_skill_info(self, name: str) -> Optional[Dict]:
        """
        获取技能详细信息
        
        Args:
            name: 技能名称
            
        Returns:
            技能信息字典
        """
        skill = self.skills.get(name)
        if not skill:
            return None
        
        return {
            "name": name,
            "description": skill["meta"].get("description", ""),
            "tags": skill["meta"].get("tags", ""),
            "path": skill["path"],
            "has_body": bool(skill["body"]),
        }


# 全局技能加载器实例
_skill_loader: Optional[SkillLoader] = None


def get_skill_loader() -> SkillLoader:
    """获取全局技能加载器"""
    global _skill_loader
    if _skill_loader is None:
        _skill_loader = SkillLoader()
    return _skill_loader


@tool
def load_skill(name: str) -> str:
    """
    加载技能内容（Layer 2）
    
    Args:
        name: 技能名称
        
    Returns:
        技能完整内容
    """
    loader = get_skill_loader()
    content = loader.get_content(name)
    
    if content:
        return f"<skill name=\"{name}\">\n{content}\n</skill>"
    else:
        return f"Error: Skill '{name}' not found"


@tool
def list_skills() -> str:
    """
    列出所有可用技能
    
    Returns:
        技能列表和描述
    """
    loader = get_skill_loader()
    descriptions = loader.get_descriptions()
    
    return f"Available skills:\n{descriptions}"


@tool
def get_skill_info(name: str) -> str:
    """
    获取技能信息
    
    Args:
        name: 技能名称
        
    Returns:
        技能信息
    """
    loader = get_skill_loader()
    info = loader.get_skill_info(name)
    
    if info:
        lines = [
            f"Name: {info['name']}",
            f"Description: {info['description']}",
        ]
        if info['tags']:
            lines.append(f"Tags: {info['tags']}")
        lines.append(f"Path: {info['path']}")
        return "\n".join(lines)
    else:
        return f"Error: Skill '{name}' not found"


@tool
def reload_skills() -> str:
    """
    重新加载技能
    
    Returns:
        加载结果
    """
    global _skill_loader
    _skill_loader = SkillLoader()
    
    skills = _skill_loader.list_skills()
    return f"Reloaded {len(skills)} skills: {', '.join(skills) if skills else 'none'}"


def get_skill_tools():
    """获取所有技能相关工具"""
    return [
        load_skill,
        list_skills,
        get_skill_info,
        reload_skills,
    ]
