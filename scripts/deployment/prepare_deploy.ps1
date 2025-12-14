# Zeabur Deployment Preparation Script
# UTF-8 encoding required

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Zeabur Deployment Preparation Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Git status
Write-Host "1. Checking Git status..." -ForegroundColor Yellow
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "   [WARN] Uncommitted changes found:" -ForegroundColor Yellow
    git status --short | ForEach-Object { Write-Host "      $_" -ForegroundColor Gray }
    Write-Host ""
    $commit = Read-Host "   Commit changes now? (y/n)"
    if ($commit -eq "y" -or $commit -eq "Y") {
        $message = Read-Host "   Enter commit message (default: Prepare for Zeabur deployment)"
        if (-not $message) { $message = "Prepare for Zeabur deployment" }
        git add .
        git commit -m $message
        Write-Host "   [OK] Changes committed" -ForegroundColor Green
    }
} else {
    Write-Host "   [OK] Working directory is clean" -ForegroundColor Green
}
Write-Host ""

# Check required files
Write-Host "2. Checking required files..." -ForegroundColor Yellow
$requiredFiles = @("Procfile", "requirements.txt", "zeabur.json", "src/main.py")
$allExist = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "   [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "   [ERROR] $file not found" -ForegroundColor Red
        $allExist = $false
    }
}
Write-Host ""

# Check environment configuration
Write-Host "3. Checking environment configuration..." -ForegroundColor Yellow
try {
    $env:PYTHONIOENCODING = "utf-8"
    $result = python -c "from src.core.config import settings; print('OK')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   [OK] Configuration loaded successfully" -ForegroundColor Green
        
        $tokenCheck = python -c "from src.core.config import settings; print('1' if settings.facebook_access_token else '0')" 2>&1
        $appIdCheck = python -c "from src.core.config import settings; print('1' if settings.facebook_app_id else '0')" 2>&1
        $openaiCheck = python -c "from src.core.config import settings; print('1' if settings.openai_api_key else '0')" 2>&1
        
        $tokenStatus = if ($tokenCheck -eq '1') { '[OK] Configured' } else { '[WARN] Not configured' }
        $tokenColor = if ($tokenCheck -eq '1') { 'Green' } else { 'Yellow' }
        Write-Host "   Facebook Token: $tokenStatus" -ForegroundColor $tokenColor
        
        $appIdStatus = if ($appIdCheck -eq '1') { '[OK] Configured' } else { '[WARN] Not configured' }
        $appIdColor = if ($appIdCheck -eq '1') { 'Green' } else { 'Yellow' }
        Write-Host "   Facebook App ID: $appIdStatus" -ForegroundColor $appIdColor
        
        $openaiStatus = if ($openaiCheck -eq '1') { '[OK] Configured' } else { '[WARN] Not configured' }
        $openaiColor = if ($openaiCheck -eq '1') { 'Green' } else { 'Yellow' }
        Write-Host "   OpenAI Key: $openaiStatus" -ForegroundColor $openaiColor
    } else {
        Write-Host "   [WARN] Configuration check failed, but can be configured via Zeabur env vars" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   [WARN] Cannot check configuration" -ForegroundColor Yellow
}
Write-Host ""

# Check page token configuration
Write-Host "4. Checking page token configuration..." -ForegroundColor Yellow
try {
    $pageStatus = python scripts\tools\manage_pages.py status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   [OK] Page token management is working" -ForegroundColor Green
        $pageMatch = $pageStatus | Select-String "已配置 (\d+) 个页面"
        if ($pageMatch) {
            $pageCount = $pageMatch.Matches[0].Groups[1].Value
            Write-Host "   Currently configured: $pageCount pages" -ForegroundColor Cyan
        }
    } else {
        Write-Host "   [WARN] Cannot check page tokens, but can sync after deployment" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   [WARN] Cannot check page tokens" -ForegroundColor Yellow
}
Write-Host ""

# Generate deployment checklist
Write-Host "5. Generating deployment checklist..." -ForegroundColor Yellow
$checklist = @"
# Zeabur Deployment Checklist

## Pre-deployment
- [ ] Code pushed to GitHub
- [ ] All environment variable values prepared

## Zeabur Operations
- [ ] Create new project
- [ ] Connect GitHub repository
- [ ] Add PostgreSQL database
- [ ] Configure all environment variables
- [ ] Wait for deployment to complete

## Post-deployment
- [ ] Run database migration: `alembic upgrade head`
- [ ] Sync page tokens: `python scripts/tools/manage_pages.py sync`
- [ ] Update Facebook Webhook URL
- [ ] Verify health check

## Environment Variables
Configure these in Zeabur:

FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_user_token (with pages_show_list permission)
FACEBOOK_VERIFY_TOKEN=your_verify_token
OPENAI_API_KEY=sk-your_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
SECRET_KEY=generate_a_32_char_key
DEBUG=false
CORS_ORIGINS=https://your-app-name.zeabur.app (set after deployment)

"@

$checklist | Out-File -FilePath "DEPLOY_CHECKLIST.txt" -Encoding UTF8
Write-Host "   [OK] Generated DEPLOY_CHECKLIST.txt" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Preparation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Check DEPLOY_CHECKLIST.txt for detailed checklist" -ForegroundColor White
Write-Host "2. Visit https://zeabur.com to start deployment" -ForegroundColor White
Write-Host "3. Refer to docs/production/QUICK_DEPLOY.md for quick guide" -ForegroundColor White
Write-Host ""

