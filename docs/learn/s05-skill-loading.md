# s05 - Skill Loading: 技能加载机制

LearnTerminalAgent 支持通过外部技能文件扩展 Agent 能力，实现按需加载知识和最佳实践。

## 📖 原理介绍

### 核心思想

**两层技能注入机制**:
- **Layer 1**: 技能名称和描述 → 放在系统提示中（轻量）
- **Layer 2**: 完整技能内容 → 按需加载到 tool_result（详细）

### 为什么需要技能系统？

1. **避免上下文污染**: 不是所有知识都需要在每次对话中加载
2. **按需学习**: 根据任务需要加载特定技能
3. **知识复用**: 可以积累和分享技能库
4. **持续更新**: 独立更新技能文件而不影响代码

### 技能文件格式

```markdown
---
name: skill-name
description: 简短的技能描述
tags: tag1,tag2,tag3
---

# 技能完整内容

这里是详细的教程、示例、最佳实践...

## 章节 1
内容...

## 章节 2
内容...
```

## 💻 实现方法

### SkillLoader 类

完整实现位于 [`src/learn_agent/skills.py`](../src/learn_agent/skills.py)

```python
class SkillLoader:
    """
    技能加载器
    
    两层技能注入机制：
    - Layer 1: 技能名称和简短描述（放在系统提示中）
    - Layer 2: 完整技能内容（按需加载到 tool_result）
    """
    
    def __init__(self, skills_dir: Optional[Path] = None):
        if skills_dir is None:
            skills_dir = PROJECT.project_root / "skills"
        
        self.skills_dir = skills_dir
        self.skills: Dict[str, Dict] = {}
        
        # 加载所有技能
        self._load_all()
```

### 技能加载流程

```python
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
```

### YAML Frontmatter 解析

```python
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
```

### Layer 1: 获取技能描述

```python
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
```

**输出示例**:
```
Available skills:
  - pdf-processing: Process and analyze PDF files [document,analysis]
  - code-review: Best practices for code review [quality,best-practices]
  - testing: Unit testing strategies and patterns [testing,quality]
```

### Layer 2: 获取完整内容

```python
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
```

### 工具定义

四个 LangChain 工具：

```python
@tool
def load_skill(name: str) -> str:
    """加载技能内容（Layer 2）"""
    loader = get_skill_loader()
    content = loader.get_content(name)
    
    if content:
        return f"<skill name=\"{name}\">\n{content}\n</skill>"
    else:
        return f"Error: Skill '{name}' not found"

@tool
def list_skills() -> str:
    """列出所有可用技能"""
    loader = get_skill_loader()
    descriptions = loader.get_descriptions()
    return f"Available skills:\n{descriptions}"

@tool
def get_skill_info(name: str) -> str:
    """获取技能信息"""
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
    """重新加载技能"""
    global _skill_loader
    _skill_loader = SkillLoader()
    
    skills = _skill_loader.list_skills()
    return f"Reloaded {len(skills)} skills: {', '.join(skills) if skills else 'none'}"
```

### Agent 集成

```python
class AgentLoop:
    # ========== s05: Skill Loading 功能 ==========
    
    def list_skills(self) -> str:
        """列出所有可用技能"""
        loader = get_skill_loader()
        return loader.get_descriptions()
    
    def load_skill(self, name: str) -> str:
        """加载指定技能"""
        loader = get_skill_loader()
        content = loader.get_content(name)
        if content:
            return f"<skill name=\"{name}\">\n{content}\n</skill>"
        else:
            return f"Error: Skill '{name}' not found"
    
    def reload_skills(self) -> str:
        """重新加载技能"""
        return reload_skills.invoke({})
```

### 全局实例

```python
# 全局技能加载器实例
_skill_loader: Optional[SkillLoader] = None

def get_skill_loader() -> SkillLoader:
    """获取全局技能加载器"""
    global _skill_loader
    if _skill_loader is None:
        _skill_loader = SkillLoader()
    return _skill_loader
```

## 🎯 使用示例

### 查看可用技能

```python
agent.run("我有哪些可用技能？")
# 或
skills = agent.list_skills()
print(skills)
```

输出：
```
Available skills:
  - pdf-processing: Process and analyze PDF files [document,analysis]
  - code-review: Best practices for code review [quality,best-practices]
  - testing: Unit testing strategies and patterns [testing,quality]
```

### 加载技能

```python
agent.run("加载 code-review 技能")
```

实际调用：
```python
skill_content = agent.load_skill("code-review")
print(skill_content)
```

输出：
```xml
<skill name="code-review">
---
name: code-review
description: Best practices for code review
tags: quality,best-practices
---

# Code Review Best Practices

## 1. Readability
- Clear variable names
- Consistent formatting
- Comments for complex logic

## 2. Error Handling
- Check all edge cases
- Proper exception handling
- Logging for debugging

... (更多内容)
</skill>
```

### 自然语言工作流

```
用户：我需要审查这段代码

Agent:
1. list_skills() 
   → Available skills: code-review, testing, ...

2. load_skill("code-review")
   → <skill name="code-review">...完整内容...</skill>

3. 使用技能中的最佳实践进行代码审查
```

### 创建自定义技能

在 `skills/my-skill/SKILL.md` 创建：

```markdown
---
name: my-custom-skill
description: My custom knowledge
tags: custom,special
---

# My Custom Skill

This is my special knowledge that I want the agent to use.

## Key Points
1. Point 1
2. Point 2
3. Point 3

## Examples
Example 1...
Example 2...
```

然后重新加载：

```python
agent.reload_skills()
```

## 📁 技能目录结构

```
skills/
├── pdf-processing/
│   └── SKILL.md
├── code-review/
│   └── SKILL.md
├── testing/
│   └── SKILL.md
└── my-custom-skill/
    └── SKILL.md
```

每个技能一个目录，目录名即技能名称（如果 frontmatter 中没有指定 name）。

## ⚙️ 配置选项

### 技能目录位置

由 `project_config.py` 管理：

```python
skills_dir = PROJECT.project_root / "skills"
```

### 技能数量

无硬性限制，但过多技能会影响：
- 启动时的加载时间
- list_skills 输出的长度

建议保持 10-20 个核心技能。

## 🐛 错误处理

### 常见错误

1. **技能不存在**
   ```
   Error: Skill 'nonexistent' not found
   ```
   **解决**: 检查技能名称拼写

2. **加载失败**
   ```
   Warning: Failed to load skill from ...
   ```
   **解决**: 检查文件格式和编码

3. **frontmatter 格式错误**
   ```
   技能元数据解析失败
   ```
   **解决**: 确保 YAML frontmatter 格式正确

## 📊 性能考虑

### 优势

✅ **按需加载**: 不占用主上下文  
✅ **灵活扩展**: 可以随时添加新技能  
✅ **知识沉淀**: 积累团队最佳实践  
✅ **减少 token**: 只在需要时加载完整内容  

### 劣势

⚠️ **额外步骤**: 需要先 list 再 load  
⚠️ **文件依赖**: 依赖外部文件存在性  
⚠️ **更新延迟**: 需要 reload 才能看到更改  

### 最佳实践

1. **精简描述**: Layer 1 的描述要简洁明确
2. **结构化内容**: Layer 2 的内容要有清晰的结构
3. **标签分类**: 使用 tags 便于搜索和组织
4. **示例驱动**: 包含实际例子便于理解
5. **定期更新**: 保持技能与最新实践同步

## 🔗 相关模块

- [s06 - Context Compaction](s06-context-compaction.md) - 上下文管理
- [s02 - Tool Use](s02-tool-use.md) - 工具使用
- [Guides/Skill Development](../guides/skill-development.md) - 技能开发指南

---

**下一步**: 了解 [上下文压缩策略](s06-context-compaction.md) →
