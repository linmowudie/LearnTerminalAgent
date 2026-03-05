"""
LearnAgent Team Protocols 模块 - s10

实现团队协议功能：
- Shutdown Protocol: 优雅关闭队友
- Plan Approval Protocol: 计划审批流程
"""

import json
import threading
import time
import uuid
from pathlib import Path
from typing import Dict, Optional
from langchain_core.tools import tool

from .teams import MessageBus, TeammateManager, get_bus, get_teammate_manager


# 请求追踪器
_shutdown_requests: Dict[str, dict] = {}
_plan_requests: Dict[str, dict] = {}
_tracker_lock = threading.Lock()


def handle_shutdown_request(teammate: str) -> str:
    """
    向队友发送关闭请求
    
    Args:
        teammate: 队友名称
        
    Returns:
        请求 ID 和状态
    """
    req_id = str(uuid.uuid4())[:8]
    with _tracker_lock:
        _shutdown_requests[req_id] = {
            "target": teammate,
            "status": "pending"
        }
    
    bus = get_bus()
    bus.send(
        "lead", teammate, "Please shut down gracefully.",
        "shutdown_request", {"request_id": req_id}
    )
    return f"Shutdown request {req_id} sent to '{teammate}' (status: pending)"


def handle_plan_review(request_id: str, approve: bool, feedback: str = "") -> str:
    """
    审批队友的计划
    
    Args:
        request_id: 请求 ID
        approve: 是否批准
        feedback: 反馈意见
        
    Returns:
        审批结果
    """
    with _tracker_lock:
        req = _plan_requests.get(request_id)
    
    if not req:
        return f"Error: Unknown plan request_id '{request_id}'"
    
    with _tracker_lock:
        req["status"] = "approved" if approve else "rejected"
    
    bus = get_bus()
    bus.send(
        "lead", req["from"], feedback, "plan_approval_response",
        {"request_id": request_id, "approve": approve, "feedback": feedback}
    )
    return f"Plan {'approved' if approve else 'rejected'} for '{req['from']}'"


def check_shutdown_status(request_id: str) -> str:
    """检查关闭请求状态"""
    with _tracker_lock:
        return json.dumps(_shutdown_requests.get(request_id, {"error": "not found"}))


@tool
def shutdown_request(teammate: str) -> str:
    """
    请求队友优雅关闭
    
    Args:
        teammate: 队友名称
        
    Returns:
        请求 ID 和状态
    """
    return handle_shutdown_request(teammate)


@tool
def shutdown_response(request_id: str) -> str:
    """
    检查关闭请求状态
    
    Args:
        request_id: 请求 ID
        
    Returns:
        请求状态
    """
    return check_shutdown_status(request_id)


@tool
def plan_approval(request_id: str, approve: bool, feedback: str = "") -> str:
    """
    批准或拒绝队友的计划
    
    Args:
        request_id: 请求 ID
        approve: 是否批准
        feedback: 反馈意见
        
    Returns:
        审批结果
    """
    return handle_plan_review(request_id, approve, feedback)


def reset_protocols():
    """重置协议状态"""
    global _shutdown_requests, _plan_requests
    with _tracker_lock:
        _shutdown_requests.clear()
        _plan_requests.clear()


def get_protocol_tools():
    """获取所有协议相关工具"""
    return [
        shutdown_request,
        shutdown_response,
        plan_approval,
    ]
