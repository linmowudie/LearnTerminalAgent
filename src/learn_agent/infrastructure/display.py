"""
终端显示模块

提供统一的终端显示功能，包括加载动画、工具调用显示、流式输出等。
实现关注点分离，减少核心业务文件的代码复杂度。
"""

import threading
import time
import sys
from typing import Optional, Any

# 尝试导入 Rich，如果不可用则降级到 ANSI 模式
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from rich.text import Text
    from rich.box import DOUBLE, ROUNDED, HEAVY
    from rich.style import Style
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = Any  # type: ignore


# ANSI 颜色常量
STYLE_GRAY = "\033[90m"         # 灰色（用于思考过程、次要信息）
STYLE_BRIGHT_GRAY = "\033[37m"  # 亮灰色（备用）
STYLE_CYAN = "\033[36m"
STYLE_YELLOW = "\033[33m"
STYLE_RED = "\033[31m"
STYLE_GREEN = "\033[32m"
STYLE_RESET = "\033[0m"

# Windows 兼容性处理：检测控制台是否支持 UTF-8
# 如果不支持，使用 ASCII 替代字符
IS_WINDOWS = sys.platform.startswith('win')

# 尝试检测控制台编码
try:
    console_encoding = sys.stdout.encoding.lower()
    SUPPORTS_UTF8 = 'utf' in console_encoding
except:
    SUPPORTS_UTF8 = False

# 全局 Console 实例（单例模式）
_console: Optional[Console] = None


def get_console() -> Console:
    """获取全局 Console 实例"""
    global _console
    if _console is None:
        # Windows 兼容性处理
        _console = Console(
            force_terminal=True,
            force_interactive=True,
            legacy_windows=IS_WINDOWS and not SUPPORTS_UTF8
        )
    return _console

# 根据编码支持选择字符集
if SUPPORTS_UTF8:
    LOADING_CHARS = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    ROBOT_ICON = "🤖"
    WARNING_ICON = "⚠️"
else:
    LOADING_CHARS = ['|', '/', '-', '\\']
    ROBOT_ICON = "[Agent]"
    WARNING_ICON = "[!]"


def safe_print(text: str):
    """
    安全打印函数，处理编码不兼容的字符
    
    Args:
        text: 要打印的文本
    """
    try:
        print(text)
    except UnicodeEncodeError:
        # 如果打印失败，尝试用 ASCII 模式重新编码
        # 替换无法编码的字符
        if IS_WINDOWS:
            # Windows 下使用 replace 错误处理方式
            encoded = text.encode('gbk', errors='replace').decode('gbk', errors='ignore')
            print(encoded)
        else:
            # 其他系统直接忽略错误
            print(text.encode('ascii', errors='ignore').decode('ascii'))


class TerminalDisplay:
    """
    终端显示管理类
    
    负责所有终端输出相关的功能，包括：
    - 加载动画显示
    - 工具调用信息打印
    - 流式输出块打印
    - 分段标题打印
    - 错误/警告信息打印
    - Markdown 渲染和富文本格式化
    """
    
    def __init__(self, verbose: bool = True, use_rich: Optional[bool] = None):
        """
        初始化终端显示器
        
        Args:
            verbose: 是否启用详细输出模式，False 时所有输出方法都不产生实际输出
            use_rich: 是否使用 Rich 库，None 时自动检测
        """
        self.verbose = verbose
        self._loading_stop_event = threading.Event()
        self._loading_thread: Optional[threading.Thread] = None
        self._loading_prefix = ""
        
        # Rich 模式控制
        if use_rich is None:
            self.use_rich = RICH_AVAILABLE
        else:
            self.use_rich = use_rich and RICH_AVAILABLE
        
        if self.use_rich:
            self.console = get_console()
    
    def show_loading_animation(self, prefix: str = "🤖 Agent 思考中:", show_complete_message: bool = True, is_static: bool = False):
        """
        启动加载动画
        
        在后台线程中显示 Unicode Braille 字符旋转动画，直到调用 stop_loading_animation
        
        Args:
            prefix: 动画前缀文字
            show_complete_message: 停止时是否显示完成消息（默认显示，工具执行时设为 False）
            is_static: 是否使用静态加载指示器（不旋转，只显示一次，用于工具执行）
        """
        if not self.verbose:
            return
        
        # 如果前缀包含默认机器人图标，替换为兼容的图标
        if "🤖" in prefix and not SUPPORTS_UTF8:
            prefix = prefix.replace("🤖", ROBOT_ICON)
        
        self._loading_prefix = prefix
        self._loading_stop_event.clear()
        self._show_complete_message = show_complete_message
        self._is_static = is_static
        
        # 启动加载动画线程
        self._loading_thread = threading.Thread(
            target=self._show_loading_loop, 
            daemon=True
        )
        self._loading_thread.start()
    
    def _show_loading_loop(self):
        """加载动画循环（在后台线程运行）"""
        idx = 0
        
        # 静态模式：只显示一次，不循环
        if self._is_static:
            # 修改：使用灰色代替青色
            text = f"{STYLE_GRAY}{self._loading_prefix}{STYLE_RESET} {LOADING_CHARS[0]}"
            try:
                print(text, end="", flush=True)
            except UnicodeEncodeError:
                safe_text = text.encode('gbk', errors='replace').decode('gbk', errors='ignore')
                print(safe_text, end="", flush=True)
            # 等待停止信号
            while not self._loading_stop_event.is_set():
                time.sleep(0.1)
        else:
            # 动态模式：循环显示旋转动画
            while not self._loading_stop_event.is_set():
                # 修改：使用灰色代替青色
                text = f"\r{STYLE_GRAY}{self._loading_prefix}{STYLE_RESET} {LOADING_CHARS[idx % len(LOADING_CHARS)]}"
                try:
                    print(text, end="", flush=True)
                except UnicodeEncodeError:
                    # Windows GBK 编码兼容处理
                    safe_text = text.encode('gbk', errors='replace').decode('gbk', errors='ignore')
                    print(safe_text, end="", flush=True)
                idx += 1
                time.sleep(0.1)
        
        # 清除动画，根据标志决定是否显示完成消息
        if hasattr(self, '_show_complete_message') and self._show_complete_message:
            # 修改：完成消息也使用灰色
            text = f"\r{STYLE_GRAY}{self._loading_prefix}{STYLE_RESET} 思考完毕{STYLE_RESET}\n"
            try:
                print(text, end="", flush=True)
            except UnicodeEncodeError:
                safe_text = text.encode('gbk', errors='replace').decode('gbk', errors='ignore')
                print(safe_text, end="", flush=True)
        else:
            # 不显示完成消息，只换行
            print()
    
    def stop_loading_animation(self):
        """停止并清除加载动画"""
        if not self.verbose:
            return
        
        if self._loading_thread and self._loading_thread.is_alive():
            self._loading_stop_event.set()
            self._loading_thread.join(timeout=0.2)
            
            # 清除当前行动画残留字符
            # 先回到行首，然后清除整行
            try:
                print("\r\033[K", end="", flush=True)  # \r 回到行首，\033[K 清除整行
            except:
                pass
    
    def print_tool_call(self, tool_name: str, tool_args: dict):
        """
        打印工具调用信息
        
        Args:
            tool_name: 工具名称
            tool_args: 工具参数
        """
        if not self.verbose:
            return
        
        # write_file 工具特殊处理：不显示实际内容
        if tool_name == "write_file":
            path = tool_args.get('path', '未知路径')
            content_length = len(tool_args.get('content', ''))
            # 只显示路径和长度，不显示实际内容
            text = f"\033[33m[{tool_name}] 准备写入 {content_length} 字符到 {path}\033[0m"
        elif tool_name == "bash":
            cmd = tool_args.get('command', str(tool_args))
            text = f"\033[33m$ {cmd}\033[0m"
        else:
            # 其他工具正常显示
            text = f"\033[33m[{tool_name}] {tool_args}\033[0m"
        
        try:
            print(text)
        except UnicodeEncodeError:
            safe_text = text.encode('gbk', errors='replace').decode('gbk', errors='ignore')
            print(safe_text)
    
    def print_tool_result(self, result: str, max_preview: int = 200):
        """
        打印工具执行结果预览
        
        Args:
            result: 工具执行结果
            max_preview: 最大预览长度，超过此长度会截断并添加 ...
        """
        if not self.verbose:
            return
        
        if result:
            preview = result[:max_preview]
            if len(result) > max_preview:
                preview += "..."
            try:
                print(preview)
            except UnicodeEncodeError:
                safe_preview = preview.encode('gbk', errors='replace').decode('gbk', errors='ignore')
                print(safe_preview)
    
    def print_stream_chunk(self, chunk: str):
        """
        打印流式输出的文本块
        
        Args:
            chunk: 文本块
        """
        if not self.verbose:
            return
        
        if chunk:
            try:
                print(chunk, end="", flush=True)
            except UnicodeEncodeError:
                safe_chunk = chunk.encode('gbk', errors='replace').decode('gbk', errors='ignore')
                print(safe_chunk, end="", flush=True)
    
    def print_section_header(self, text: str):
        """
        打印分段标题
        
        Args:
            text: 标题文字
        """
        if not self.verbose:
            return
        
        try:
            print(f"\n{text}")
        except UnicodeEncodeError:
            safe_text = text.encode('gbk', errors='replace').decode('gbk', errors='ignore')
            print(f"\n{safe_text}")
    
    def print_error(self, message: str):
        """
        打印错误信息（红色）
        
        Args:
            message: 错误信息
        """
        if not self.verbose:
            return
        
        text = f"{STYLE_RED}{WARNING_ICON} {message}{STYLE_RESET}"
        try:
            print(text)
        except UnicodeEncodeError:
            safe_text = text.encode('gbk', errors='replace').decode('gbk', errors='ignore')
            print(safe_text)
    
    def print_warning(self, message: str):
        """
        打印警告信息（黄色）
        
        Args:
            message: 警告信息
        """
        if not self.verbose:
            return
        
        text = f"{STYLE_YELLOW}{WARNING_ICON} {message}{STYLE_RESET}"
        try:
            print(text)
        except UnicodeEncodeError:
            safe_text = text.encode('gbk', errors='replace').decode('gbk', errors='ignore')
            print(safe_text)
    
    def clear_line(self):
        """清除当前行"""
        if not self.verbose:
            return
        
        try:
            print("\r", end="", flush=True)
        except UnicodeEncodeError:
            pass
    
    def print_newline(self):
        """打印换行符"""
        if not self.verbose:
            return
        
        try:
            print()
        except UnicodeEncodeError:
            pass
    
    # ========== Rich 富文本输出方法 ==========
    
    def render_markdown(self, markdown_text: str):
        """
        渲染 Markdown 格式的文本
        
        Args:
            markdown_text: Markdown 格式的文本
        """
        if not self.verbose:
            return
        
        if self.use_rich:
            md = Markdown(markdown_text)
            self.console.print(md)
        else:
            # 降级到普通输出
            print(markdown_text)
    
    def print_response_card(self, content: str, style: str = "default"):
        """
        使用 Rich Panel 打印响应卡片
        
        Args:
            content: 要显示的内容
            style: 样式类型 (default, success, warning, error, code)
        """
        if not self.verbose:
            return
        
        if self.use_rich:
            # 定义样式映射
            style_config = {
                "default": {"border_style": "cyan", "title": None},
                "success": {"border_style": "green", "title": "✅ 成功"},
                "warning": {"border_style": "yellow", "title": "⚠️ 警告"},
                "error": {"border_style": "red", "title": "❌ 错误"},
                "code": {"border_style": "yellow", "title": "📝 代码"},
            }
            
            config = style_config.get(style, style_config["default"])
            
            # 检测是否包含代码块
            if "```" in content:
                # 渲染代码块
                panel_content = self._render_mixed_content(content)
            else:
                # 普通文本
                panel_content = Text(content)
            
            panel = Panel(
                panel_content,
                border_style=config["border_style"],
                title=config["title"],
                box=ROUNDED,
                padding=(1, 2),
            )
            
            self.console.print(panel)
        else:
            # 降级到 ANSI 卡片格式
            print(self._format_ansi_card(content))
    
    def _render_mixed_content(self, content: str):
        """
        渲染混合内容（文本 + 代码块）
        
        Args:
            content: 包含 Markdown 代码块的内容
            
        Returns:
            Rich Text 或 Composite 对象
        """
        from rich.console import Group
        
        elements = []
        lines = content.split('\n')
        current_block = []
        in_code_block = False
        code_lang = ""
        
        for line in lines:
            if line.strip().startswith('```'):
                if in_code_block:
                    # 结束代码块
                    if current_block:
                        code_content = '\n'.join(current_block)
                        syntax = Syntax(code_content, code_lang or "text", theme="monokai")
                        elements.append(syntax)
                        current_block = []
                    in_code_block = False
                else:
                    # 开始代码块
                    if current_block:
                        elements.append(Text('\n'.join(current_block)))
                        current_block = []
                    in_code_block = True
                    code_lang = line.strip()[3:].strip()
            else:
                current_block.append(line)
        
        # 处理剩余内容
        if current_block:
            if in_code_block:
                code_content = '\n'.join(current_block)
                syntax = Syntax(code_content, code_lang or "text", theme="monokai")
                elements.append(syntax)
            else:
                elements.append(Text('\n'.join(current_block)))
        
        return Group(*elements)
    
    def _format_ansi_card(self, content: str) -> str:
        """
        使用 ANSI 转义码格式化卡片（Rich 不可用时的降级方案）
        
        Args:
            content: 要格式化的内容
            
        Returns:
            格式化后的字符串
        """
        # ANSI 颜色代码
        GREEN = "\033[32m"
        CYAN = "\033[36m"
        YELLOW = "\033[33m"
        BOLD = "\033[1m"
        RESET = "\033[0m"
        
        # 固定边距空格数
        LEFT_MARGIN = "  "
        RIGHT_MARGIN = "  "
        
        # 分割内容为行
        lines = content.split('\n')
        
        # 构建卡片边框
        max_content_width = max(len(line) for line in lines)
        inner_width = max_content_width + 2
        border = LEFT_MARGIN + f"{CYAN}╔" + "═" * inner_width + f"╗{RIGHT_MARGIN}{RESET}"
        bottom_border = LEFT_MARGIN + f"{CYAN}╚" + "═" * inner_width + f"╝{RIGHT_MARGIN}{RESET}"
        
        # 构建卡片内容
        formatted_lines = [border]
        
        for line in lines:
            if line.strip().startswith(('```', 'import ', 'def ', 'class ', 'return ')):
                formatted_lines.append(LEFT_MARGIN + f"{CYAN}║ {YELLOW}{line.ljust(max_content_width)}{CYAN} ║{RIGHT_MARGIN}{RESET}")
            elif line.strip().startswith(('✅', '✓', '✔')):
                formatted_lines.append(LEFT_MARGIN + f"{CYAN}║ {GREEN}{BOLD}{line.ljust(max_content_width)}{CYAN} ║{RIGHT_MARGIN}{RESET}")
            elif line.strip().startswith(('⚠️', '❗', 'Error')):
                formatted_lines.append(LEFT_MARGIN + f"{CYAN}║ \033[31m{line.ljust(max_content_width)}{CYAN} ║{RIGHT_MARGIN}{RESET}")
            else:
                formatted_lines.append(LEFT_MARGIN + f"{CYAN}║ {GREEN}{line.ljust(max_content_width)}{CYAN} ║{RIGHT_MARGIN}{RESET}")
        
        formatted_lines.append(bottom_border)
        
        return '\n'.join(formatted_lines)
