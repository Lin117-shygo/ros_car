#!/bin/bash

# ROS小车项目 - 代码提交脚本 (Ubuntu虚拟机)
# 用法: ./vm_commit.sh [commit信息]
# 示例: ./vm_commit.sh "fix: 调整导航参数"
#
# 安装说明:
# 1. chmod +x vm_commit.sh
# 2. 确保已配置 GitHub SSH key

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo ""
echo -e "${BLUE}========================================"
echo "  ROS小车项目 - 代码提交工具"
echo -e "========================================${NC}"
echo ""

# 1. 检查git仓库
if [ ! -d ".git" ]; then
    echo -e "${RED}错误: 当前目录不是git仓库！${NC}"
    exit 1
fi

# 2. 显示当前状态 (只关注 Lin_ws)
echo -e "${YELLOW}[1/4] 检查Git状态 (Lin_ws/)...${NC}"
echo "----------------------------------------"
git status --short Lin_ws/
echo "----------------------------------------"
echo ""

# 检查是否有变更
CHANGES=$(git status --porcelain Lin_ws/ 2>/dev/null)
if [ -z "$CHANGES" ]; then
    echo -e "${GREEN}Lin_ws/ 没有需要提交的更改。${NC}"
    exit 0
fi

# 3. 显示变更详情
echo -e "${YELLOW}[2/4] 变更详情:${NC}"
echo "----------------------------------------"
git diff --stat Lin_ws/
echo "----------------------------------------"
echo ""

# 4. 确认提交
read -p "确认要提交这些更改吗? (y/n): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "已取消。"
    exit 0
fi

# 5. 获取commit信息
if [ -n "$1" ]; then
    COMMIT_MSG="$1"
else
    echo ""
    read -p "请输入commit信息: " COMMIT_MSG
fi

if [ -z "$COMMIT_MSG" ]; then
    echo -e "${RED}错误: commit信息不能为空！${NC}"
    exit 1
fi

# 6. 执行提交 (只添加 Lin_ws 目录)
echo ""
echo -e "${YELLOW}[3/4] 添加并提交更改...${NC}"
git add Lin_ws/
git commit -m "$COMMIT_MSG"

if [ $? -ne 0 ]; then
    echo -e "${RED}提交失败！${NC}"
    exit 1
fi

# 7. 推送到远程
echo ""
echo -e "${YELLOW}[4/4] 推送到GitHub...${NC}"
git push origin main

if [ $? -ne 0 ]; then
    echo -e "${RED}推送失败！请检查网络连接。${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================"
echo "  提交并推送完成！"
echo -e "========================================${NC}"
echo ""
echo -e "${YELLOW}提示: 主机端开发前请先运行 host_update.bat 同步更新${NC}"
echo ""
