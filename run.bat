@echo off
REM LearnTerminalAgent 快速启动批处理脚本
REM 
REM 使用方法:
REM   run.bat [工作空间路径]
REM
REM 示例:
REM   run.bat                    - 在当前目录启动
REM   run.bat F:\Project\MyApp   - 指定工作空间

python "%~dp0run_agent.py" %*
