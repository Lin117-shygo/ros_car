@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ROS小车项目 - 代码更新脚本 (Windows主机)
:: 用法: host_update.bat
:: 在开始开发前运行，检查并同步远程更新

cd /d "%~dp0.."

echo.
echo ========================================
echo   ROS小车项目 - 代码更新工具
echo ========================================
echo.

:: 1. 检查git仓库
if not exist ".git" (
    echo 错误: 当前目录不是git仓库！
    pause
    exit /b 1
)

:: 2. 检查本地状态
echo [1/3] 检查本地状态...
echo ----------------------------------------
git status --short Lin_ws/
echo ----------------------------------------

:: 检查是否有未提交的更改
for /f %%i in ('git status --porcelain Lin_ws/ 2^>nul') do (
    echo.
    echo 警告: 检测到本地修改！
    echo 建议先提交或暂存本地更改，否则可能产生冲突。
    echo.
    set /p confirm="是否继续更新? (y/n): "
    if /i not "!confirm!"=="y" (
        echo 已取消。
        pause
        exit /b 0
    )
    goto :fetch
)

:fetch
:: 3. 获取远程更新
echo.
echo [2/3] 从GitHub获取更新...
git fetch origin

:: 比较本地和远程
for /f %%a in ('git rev-parse HEAD') do set LOCAL=%%a
for /f %%a in ('git rev-parse origin/main') do set REMOTE=%%a

if "%LOCAL%"=="%REMOTE%" (
    echo.
    echo ========================================
    echo   已是最新版本，无需更新。
    echo ========================================
    echo.
    pause
    exit /b 0
)

:: 4. 显示更新内容
echo.
echo [3/3] 发现远程更新，变更内容:
echo ----------------------------------------
git log --oneline HEAD..origin/main
echo ----------------------------------------
echo.

:: 5. 执行更新
set /p confirm="是否拉取这些更新? (y/n): "
if /i not "%confirm%"=="y" (
    echo 已取消。
    pause
    exit /b 0
)

echo.
echo 正在更新...
git pull origin main

if %errorlevel% neq 0 (
    echo.
    echo 更新失败！可能存在冲突，请手动解决。
    pause
    exit /b 1
)

echo.
echo ========================================
echo   更新完成！
echo ========================================
echo.
pause
