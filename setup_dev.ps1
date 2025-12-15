$ErrorActionPreference = "Stop"
function Write-Info($m){Write-Host "[INFO] $m" -ForegroundColor Cyan}
function Write-Ok($m){Write-Host "[OK]  $m" -ForegroundColor Green}
function Write-Warn($m){Write-Host "[WARN] $m" -ForegroundColor Yellow}
function Write-Err($m){Write-Host "[ERR] $m" -ForegroundColor Red}

Write-Info "设置当前用户执行策略为 RemoteSigned（仅当前用户）"
try { Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force; Write-Ok "执行策略已设置" } catch { Write-Warn "设置执行策略失败: $($_.Exception.Message)" }

Write-Info "输出版本信息"
$checks = @(
  @{ name="Node";   cmd="node -v" },
  @{ name="npm";    cmd="npm -v" },
  @{ name="Python"; cmd="python --version" },
  @{ name="pip";    cmd="pip --version" },
  @{ name="Java";   cmd="java -version" },
  @{ name="Git";    cmd="git --version" },
  @{ name="VSCode"; cmd="code --version" }
)
foreach ($c in $checks) {
  Write-Host "---- $($c.name) ----" -ForegroundColor White
  try { iex $c.cmd } catch { Write-Warn "未能执行 $($c.cmd): $($_.Exception.Message)" }
}

Write-Info "尝试启动 Docker Desktop"
$dockerExe = "$Env:ProgramFiles\Docker\Docker\Docker Desktop.exe"
if (-not (Test-Path $dockerExe)) {
  Write-Err "未找到 Docker Desktop，请先安装（管理员）：winget install --id Docker.DockerDesktop -e --accept-source-agreements --accept-package-agreements"
  exit 1
}
Start-Process -FilePath $dockerExe | Out-Null

Write-Info "等待 Docker 引擎就绪（最多 120 秒）"
$ready = $false
for ($i=0; $i -lt 120; $i++) {
  try { docker info --format '{{.ServerVersion}}' | Out-Null; $ready = $true; break } catch { Start-Sleep -Seconds 1 }
}
if (-not $ready) { Write-Err "Docker 未在 120 秒内就绪，请查看 Docker Desktop 或重启后重试"; exit 1 }
Write-Ok "Docker 引擎已就绪"

Write-Info "运行 docker hello-world"
try { docker run --rm hello-world; Write-Ok "hello-world 运行成功" } catch { Write-Err "hello-world 运行失败: $($_.Exception.Message)"; exit 1 }
