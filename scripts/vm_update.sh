#!/bin/bash

# ROS小车项目 - 代码更新脚本 (Ubuntu虚拟机)
# 只更新 Lin_ws 目录和 start_conn.py 文件
#
# 安装说明:
# 1. 将此脚本复制到虚拟机的项目目录
# 2. chmod +x vm_update.sh
# 3. 可选: 创建桌面快捷方式

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo -e "${BLUE}========================================"
echo "  ROS小车项目 - 代码更新工具"
echo -e "========================================${NC}"
echo ""

# 1. 检查git仓库
if [ ! -d ".git" ]; then
    echo -e "${RED}错误: 当前目录不是git仓库！${NC}"
    echo "当前目录: $(pwd)"
    exit 1
fi

# 2. 显示当前状态
echo -e "${YELLOW}[1/3] 检查本地状态...${NC}"
LOCAL_CHANGES=$(git status --porcelain Lin_ws/ start_conn.py 2>/dev/null)
if [ -n "$LOCAL_CHANGES" ]; then
    echo -e "${YELLOW}警告: 检测到本地修改，将被覆盖:${NC}"
    echo "$LOCAL_CHANGES"
    echo ""
    read -p "是否继续? (y/n): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "已取消。"
        exit 0
    fi
fi

# 3. 获取远程更新
echo ""
echo -e "${YELLOW}[2/3] 从GitHub获取更新...${NC}"
git fetch origin

# 检查是否有更新
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/master 2>/dev/null || git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
    echo -e "${GREEN}已是最新版本，无需更新。${NC}"
    echo ""
    exit 0
fi

# 4. 只更新指定文件
echo ""
echo -e "${YELLOW}[3/3] 更新文件...${NC}"

# 使用sparse checkout只更新需要的文件
git checkout origin/master -- Lin_ws/ start_conn.py 2>/dev/null || \
git checkout origin/main -- Lin_ws/ start_conn.py

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================"
    echo "  更新完成！"
    echo -e "========================================${NC}"
    echo ""
    echo "已更新文件:"
    echo "  - Lin_ws/ (ROS工作空间)"
    echo "  - start_conn.py (连接脚本)"
    echo ""

    # 提示重新编译
    echo -e "${YELLOW}提示: 如果有C++代码变更，请执行:${NC}"
    echo "  cd Lin_ws && catkin_make"
    echo ""
else
    echo -e "${RED}更新失败！${NC}"
    exit 1
fi
