# LearnTerminalAgent PowerShell 启动脚本
# 
# 使用方法:
#   .\agent.ps1 [工作空间路径]
#
# 示例:
#   .\agent.ps1                    - 在当前目录启动
#   .\agent.ps1 F:\Project\MyApp  - 指定工作空间

param (
    [Parameter(Position= 0)]
    [string[]]$WorkspaceArgs
)

# 获取脚本所在目录
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 检查并激活虚拟环境
$venvPath = Join-Path $scriptDir ".venv"
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (Test-Path $activateScript) {
    # 静默激活虚拟环境
    & $activateScript -ErrorAction SilentlyContinue
    Write-Host "[INFO] Virtual environment activated: $venvPath" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Virtual environment not found at $venvPath" -ForegroundColor Yellow
    Write-Host "[INFO] Continuing with system Python..." -ForegroundColor Cyan
}

# 执行 Python 脚本
python (Join-Path $scriptDir "run_agent.py") @WorkspaceArgs
