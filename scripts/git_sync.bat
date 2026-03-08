@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ROS小车项目 - Git同步脚本 (Windows主机)
:: 用法: git_sync.bat [commit信息]
:: 示例: git_sync.bat "feat: 添加多点巡航功能"

cd /d "%~dp0.."

echo.
echo ========================================
echo   ROS小车项目 - Git同步工具
echo ========================================
echo.

:: 1. 显示当前状态
echo [1/4] 检查Git状态...
echo ----------------------------------------
git status --short
echo ----------------------------------------
echo.

:: 2. 显示变更详情
echo [2/4] 变更详情:
echo ----------------------------------------
git diff --stat
echo ----------------------------------------
echo.

:: 3. 询问是否继续
set /p confirm="确认要提交这些更改吗? (y/n): "
if /i not "%confirm%"=="y" (
    echo 已取消操作。
    pause
    exit /b 0
)

:: 4. 获取commit信息
if "%~1"=="" (
    set /p commit_msg="请输入commit信息: "
) else (
    set "commit_msg=%~1"
)

if "!commit_msg!"=="" (
    echo 错误: commit信息不能为空！
    pause
    exit /b 1
)

:: 5. 执行Git操作
echo.
echo [3/4] 添加并提交更改...
git add -A
git commit -m "!commit_msg!"

if %errorlevel% neq 0 (
    echo 提交失败！
    pause
    exit /b 1
)

:: 6. 推送到远程
echo.
echo [4/4] 推送到GitHub...
git push

if %errorlevel% neq 0 (
    echo 推送失败！请检查网络连接。
    pause
    exit /b 1
)

echo.
echo ========================================
echo   同步完成！
echo ========================================
echo.
pause
