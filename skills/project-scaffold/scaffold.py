#!/usr/bin/env python3
"""
Project Scaffold - 项目脚手架生成器

快速创建标准化的项目目录结构
"""

import argparse
import os
from pathlib import Path
from typing import Dict, List, Optional


class ProjectScaffold:
    """项目脚手架生成器"""
    
    # Python 项目模板
    PYTHON_TEMPLATE = {
        "{name}": {
            "src": {
                "{package_name}": ["__init__.py", "main.py"],
            },
            "tests": ["__init__.py", "test_main.py"],
            "docs": [],
            "scripts": [],
            "config": [],
            ".gitignore": "",
            "README.md": "",
            "requirements.txt": "",
            "pyproject.toml": "",
        }
    }
    
    # React 项目模板
    REACT_TEMPLATE = {
        "{name}": {
            "public": ["index.html"],
            "src": {
                "components": [],
                "pages": [],
                "utils": [],
                "styles": [],
                "App.jsx": "",
                "index.js": "",
            },
            "package.json": "",
            "vite.config.js": "",
            "README.md": "",
        }
    }
    
    # Vue 项目模板
    VUE_TEMPLATE = {
        "{name}": {
            "public": ["index.html"],
            "src": {
                "components": [],
                "views": [],
                "router": [],
                "stores": [],
                "assets": [],
                "App.vue": "",
                "main.js": "",
            },
            "package.json": "",
            "vite.config.js": "",
            "README.md": "",
        }
    }
    
    # TypeScript 库模板
    TYPESCRIPT_TEMPLATE = {
        "{name}": {
            "src": ["index.ts"],
            "examples": [],
            "tests": [],
            "docs": [],
            "tsconfig.json": "",
            "package.json": "",
            ".gitignore": "",
            "README.md": "",
        }
    }
    
    # 简单项目模板
    SIMPLE_TEMPLATE = {
        "{name}": {
            "src": [],
            "tests": [],
            "README.md": "",
            ".gitignore": "",
        }
    }
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        初始化脚手架
        
        Args:
            base_dir: 基础目录，默认为当前目录
        """
        self.base_dir = base_dir or Path.cwd()
    
    def create_project(
        self,
        name: str,
        project_type: str = "python",
        force: bool = False,
        custom_dirs: Optional[List[str]] = None,
    ) -> Path:
        """
        创建项目
        
        Args:
            name: 项目名称
            project_type: 项目类型 (python, react, vue, typescript, simple)
            force: 是否覆盖已存在的目录
            custom_dirs: 自定义目录列表
            
        Returns:
            项目根目录路径
            
        Raises:
            FileExistsError: 当目录已存在且 force=False
        """
        package_name = name.replace("-", "_")
        project_dir = self.base_dir / name
        
        # 检查目录是否已存在
        if project_dir.exists():
            if not force:
                raise FileExistsError(
                    f"目录 '{project_dir}' 已存在。使用 --force 参数强制覆盖。"
                )
        
        # 选择模板
        template = self._get_template(project_type)
        
        # 如果有自定义目录，合并到模板
        if custom_dirs:
            template = self._merge_custom_dirs(template, name, custom_dirs)
        
        # 替换模板变量
        template = self._replace_template_vars(
            template, name=name, package_name=package_name
        )
        
        # 创建目录结构
        self._create_structure(template, project_dir)
        
        # 创建文件内容
        self._create_file_contents(project_dir, project_type, name)
        
        return project_dir
    
    def _get_template(self, project_type: str) -> Dict:
        """获取对应的项目模板"""
        templates = {
            "python": self.PYTHON_TEMPLATE,
            "react": self.REACT_TEMPLATE,
            "vue": self.VUE_TEMPLATE,
            "typescript": self.TYPESCRIPT_TEMPLATE,
            "simple": self.SIMPLE_TEMPLATE,
        }
        
        if project_type not in templates:
            available = ", ".join(templates.keys())
            raise ValueError(
                f"未知的项目类型 '{project_type}'。可用类型：{available}"
            )
        
        return templates[project_type]
    
    def _replace_template_vars(
        self,
        template: Dict,
        name: str,
        package_name: str,
    ) -> Dict:
        """替换模板中的变量"""
        import json
        
        template_str = json.dumps(template)
        template_str = template_str.replace("{name}", name)
        template_str = template_str.replace("{package_name}", package_name)
        
        return json.loads(template_str)
    
    def _merge_custom_dirs(
        self,
        template: Dict,
        project_name: str,
        custom_dirs: List[str],
    ) -> Dict:
        """合并自定义目录到模板"""
        # 简单的实现：添加额外的空目录
        project_key = list(template.keys())[0]
        structure = template[project_key]
        
        for dir_name in custom_dirs:
            if dir_name not in structure:
                structure[dir_name] = []
        
        return template
    
    def _create_structure(self, template: Dict, base_path: Path):
        """递归创建目录结构"""
        for name, content in template.items():
            current_path = base_path / name
            
            if isinstance(content, dict):
                # 是目录
                current_path.mkdir(parents=True, exist_ok=True)
                self._create_structure(content, current_path)
            elif isinstance(content, list):
                # 是目录，包含文件
                current_path.mkdir(parents=True, exist_ok=True)
                for file_name in content:
                    if isinstance(file_name, str):
                        file_path = current_path / file_name
                        file_path.touch(exist_ok=True)
    
    def _create_file_contents(
        self,
        project_dir: Path,
        project_type: str,
        project_name: str,
    ):
        """创建文件的初始内容"""
        
        # .gitignore 内容
        gitignore_content = self._get_gitignore_content(project_type)
        gitignore_file = project_dir / ".gitignore"
        if gitignore_file.exists():
            gitignore_file.write_text(gitignore_content, encoding="utf-8")
        
        # README.md 内容
        readme_content = self._get_readme_content(project_name, project_type)
        readme_file = project_dir / "README.md"
        if readme_file.exists():
            readme_file.write_text(readme_content, encoding="utf-8")
        
        # requirements.txt (Python 项目)
        if project_type == "python":
            req_file = project_dir / "requirements.txt"
            if req_file.exists():
                req_file.write_text("# 项目依赖\n", encoding="utf-8")
            
            # pyproject.toml
            pyproject_file = project_dir / "pyproject.toml"
            if pyproject_file.exists():
                pyproject_file.write_text(
                    self._get_pyproject_content(project_name),
                    encoding="utf-8",
                )
        
        # package.json (Node.js 项目)
        if project_type in ["react", "vue", "typescript"]:
            package_file = project_dir / "package.json"
            if package_file.exists():
                package_file.write_text(
                    self._get_package_json_content(project_name, project_type),
                    encoding="utf-8",
                )
    
    def _get_gitignore_content(self, project_type: str) -> str:
        """获取.gitignore 内容"""
        if project_type == "python":
            return """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Project specific
*.log
logs/
"""
        elif project_type in ["react", "vue", "typescript"]:
            return """# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
dist
dist-ssr
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# Environment
.env
.env.local
.env.production
"""
        else:
            return """# Common ignores
*~
*.swp
*.swo
.DS_Store
"""
    
    def _get_readme_content(self, project_name: str, project_type: str) -> str:
        """获取 README.md 内容"""
        return f"""# {project_name}

简短的项目描述。

## 安装

""" + (
            f"""```bash
pip install -e .
```"""
            if project_type == "python"
            else f"""```bash
npm install
```"""
        ) + f"""

## 使用方法

""" + (
            f"""```python
from {project_name.replace('-', '_')} import main
```"""
            if project_type == "python"
            else """```javascript
import App from './src/App'
```"""
        ) + """

## 开发

""" + (
            """```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\\Scripts\\activate
# Unix/MacOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest
```"""
            if project_type == "python"
            else """```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 构建
npm run build
```"""
        ) + """

## License

MIT
"""
    
    def _get_pyproject_content(self, project_name: str) -> str:
        """获取 pyproject.toml 内容"""
        package_name = project_name.replace("-", "_")
        return f"""[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{package_name}"
version = "0.1.0"
description = "A short description of the project."
readme = "README.md"
requires-python = ">=3.8"
license = {{text = "MIT"}}
authors = [
    {{name = "Your Name", email = "your.email@example.com"}}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
dependencies = [
    # 添加你的依赖
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "black>=22.0",
    "ruff>=0.1.0",
]

[project.scripts]
{package_name} = "{package_name}.main:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.black]
line-length = 88
target-version = ['py38']

[tool.ruff]
line-length = 88
select = ["E", "F", "I"]
"""
    
    def _get_package_json_content(
        self, project_name: str, project_type: str
    ) -> str:
        """获取 package.json 内容"""
        return f"""{{
  "name": "{project_name}",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {{
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "test": "vitest"
  }},
  "dependencies": {{
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }},
  "devDependencies": {{
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.2.2",
    "vite": "^5.0.8",
    "vitest": "^1.1.0"
  }}
}}
"""


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="Project Scaffold - 项目脚手架生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s create python my_project
  %(prog)s create react my_web_app
  %(prog)s create typescript my_lib --dirs "src,tests,docs"
  %(prog)s create simple test_project --force
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # create 命令
    create_parser = subparsers.add_parser("create", help="创建新项目")
    create_parser.add_argument(
        "type",
        choices=["python", "react", "vue", "typescript", "simple"],
        help="项目类型",
    )
    create_parser.add_argument("name", help="项目名称")
    create_parser.add_argument(
        "--dirs",
        type=str,
        default=None,
        help="自定义目录列表，逗号分隔，如：src,tests,docs",
    )
    create_parser.add_argument(
        "--force",
        action="store_true",
        help="强制覆盖已存在的目录",
    )
    create_parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="输出目录，默认为当前目录",
    )
    
    args = parser.parse_args()
    
    if args.command == "create":
        # 确定输出目录
        base_dir = Path(args.output) if args.output else Path.cwd()
        
        # 解析自定义目录
        custom_dirs = None
        if args.dirs:
            custom_dirs = [d.strip() for d in args.dirs.split(",")]
        
        try:
            scaffold = ProjectScaffold(base_dir=base_dir)
            project_dir = scaffold.create_project(
                name=args.name,
                project_type=args.type,
                force=args.force,
                custom_dirs=custom_dirs,
            )
            print(f"✅ 项目创建成功：{project_dir}")
            print(f"\n下一步:")
            print(f"  cd {args.name}")
            if args.type == "python":
                print(f"  python -m venv venv")
                print(f"  source venv/bin/activate  # Windows: venv\\Scripts\\activate")
                print(f"  pip install -r requirements.txt")
            else:
                print(f"  npm install")
        except FileExistsError as e:
            print(f"❌ 错误：{e}")
            exit(1)
        except Exception as e:
            print(f"❌ 创建项目时出错：{e}")
            exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
