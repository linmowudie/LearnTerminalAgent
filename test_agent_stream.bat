@echo off
REM 测试 Agent 流式输出和工具调用功能

echo ========================================
echo 测试 LearnTerminalAgent 流式输出
echo ========================================
echo.

REM 设置环境变量（如果还没有设置）
if "%QWEN_API_KEY%"=="" (
    echo ⚠️  警告：QWEN_API_KEY 未设置
    echo 请先设置环境变量或创建 .env 文件
    echo.
    exit /b 1
)

echo ✅ API Key 已配置
echo.
echo 运行简单测试...
echo.

REM 使用 Python 直接测试
python -c "import sys; sys.path.insert(0, 'src'); from learn_agent.agent import AgentLoop; agent = AgentLoop(); print('✅ Agent 初始化成功')"

if %errorlevel% neq 0 (
    echo ❌ Agent 初始化失败
    exit /b 1
)

echo.
echo ========================================
echo 手动测试步骤:
echo ========================================
echo 1. 运行：python src\learn_agent\run.py
echo 2. 输入：创建一个 test.txt 文件，内容为"Hello World"
echo 3. 观察：
echo    - 是否有"🤖 Agent 思考中:"提示
echo    - 是否显示流式输出内容
echo    - 工具调用是否正确执行
echo    - 最终结果是否用卡片格式化显示
echo.
echo ========================================
