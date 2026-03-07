"""
导入测试 - 验证所有模块的导入路径正确

用于在重构过程中确保导入关系不被破坏
"""

import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
src_dir = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_dir))


def test_package_import():
    """测试包级导入"""
    import learn_agent
    assert hasattr(learn_agent, 'AgentLoop')
    assert hasattr(learn_agent, 'AgentConfig')
    assert hasattr(learn_agent, 'get_config')
    print("[PASS] 包级导入成功")


def test_core_imports():
    """测试核心模块导入"""
    from learn_agent.core.agent import AgentLoop
    from learn_agent.core.config import AgentConfig, get_config
    from learn_agent.core.main import main
    
    assert AgentLoop is not None
    assert AgentConfig is not None
    assert get_config is not None
    assert main is not None
    print("[PASS] 核心模块导入成功")


def test_infrastructure_imports():
    """测试基础设施模块导入"""
    from learn_agent.infrastructure.logger import logger_workspace, logger_agent, logger_tools, logger_config
    from learn_agent.infrastructure.workspace import WorkspaceManager, get_workspace
    from learn_agent.infrastructure.project_config import ProjectConfig, get_project_config
    
    assert logger_workspace is not None
    assert WorkspaceManager is not None
    assert ProjectConfig is not None
    print("[PASS] 基础设施模块导入成功")


def test_tools_imports():
    """测试工具模块导入"""
    from learn_agent.tools.tools import bash, read_file, write_file, list_directory, edit_file
    from learn_agent.tools.todo import get_todo_tools, TodoManager
    from learn_agent.tools.task_system import get_task_tools, TaskManager
    from learn_agent.tools.skills import get_skill_tools, SkillLoader
    
    assert bash is not None
    assert read_file is not None
    assert get_todo_tools is not None
    assert get_task_tools is not None
    print("[PASS] 工具模块导入成功")


def test_agents_imports():
    """测试代理模块导入"""
    from learn_agent.agents.subagent import SubAgent, spawn_subagent
    from learn_agent.agents.teams import TeammateManager, MessageBus, get_teammate_manager, get_bus
    from learn_agent.agents.autonomous_agents import get_autonomous_tools, claim_task  # 修正导入
    
    assert SubAgent is not None
    assert spawn_subagent is not None
    assert TeammateManager is not None
    assert MessageBus is not None
    print("[PASS] 代理模块导入成功")


def test_services_imports():
    """测试服务模块导入"""
    from learn_agent.services.context import ContextCompactor, get_compactor, estimate_tokens
    from learn_agent.services.background import BackgroundManager, get_bg_manager
    
    assert ContextCompactor is not None
    assert get_compactor is not None
    assert BackgroundManager is not None
    print("[PASS] 服务模块导入成功")


def test_protocols_imports():
    """测试协议模块导入"""
    from learn_agent.protocols.team_protocols import get_protocol_tools, handle_plan_review  # 修正导入
    from learn_agent.protocols.worktree_isolation import WorktreeManager, get_worktree_manager  # 修正导入
    
    assert get_protocol_tools is not None
    assert WorktreeManager is not None
    print("[PASS] 协议模块导入成功")


def test_backward_compatibility():
    """测试向后兼容性 - 原有导入路径仍然有效"""
    # 这些是从 learn_agent.__init__.py 导出的
    from learn_agent import (
        AgentLoop,
        AgentConfig,
        get_config,
        get_all_tools,
        TodoManager,
        get_todo_manager,
        SubAgent,
        spawn_subagent,
        SkillLoader,
        get_skill_loader,
        ContextCompactor,
        get_compactor,
        estimate_tokens,
        TaskManager,
        get_task_manager,
        BackgroundManager,
        get_bg_manager,
        TeammateManager,
        MessageBus,
        get_teammate_manager,
        get_bus,
    )
    
    assert AgentLoop is not None
    assert get_config is not None
    assert get_all_tools is not None
    print("[PASS] 向后兼容性测试成功")


if __name__ == '__main__':
    """运行所有导入测试"""
    print("=" * 60)
    print("开始导入测试")
    print("=" * 60)
    
    tests = [
        ("包级导入", test_package_import),
        ("核心模块", test_core_imports),
        ("基础设施", test_infrastructure_imports),
        ("工具模块", test_tools_imports),
        ("代理模块", test_agents_imports),
        ("服务模块", test_services_imports),
        ("协议模块", test_protocols_imports),
        ("向后兼容", test_backward_compatibility),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            print(f"\n测试：{name}")
            test_func()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {name} 失败：{e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果：{passed} 通过，{failed} 失败")
    print("=" * 60)
    
    if failed > 0:
        sys.exit(1)
