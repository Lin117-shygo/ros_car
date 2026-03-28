# ROS 上位机开发规范

> Ubuntu + ROS1 上位机开发的最佳实践。

**注意**: 本项目将 frontend 映射为 **ROS 上位机**开发。另见 [ros-development.md](../ros-development.md) 获取项目全局概览。

---

## Overview

上位机代码位于 `Lin_ws/`，基于 ROS1 (catkin) 开发，负责：
- SLAM 建图与定位（AMCL / gmapping / hector / cartographer）
- 自主导航（move_base + TEB/DWA 局部规划器）
- 多点巡航（waypoint_patrol.py）
- 机器人模型可视化（URDF + RViz）

**这是主要开发目录**，大部分新功能都在这里开发。

---

## Guidelines Index

| Guide | Description | Status |
|-------|-------------|--------|
| [Directory Structure](./directory-structure.md) | ROS 工作空间和包的目录组织 | Filled |
| [Node Guidelines](./component-guidelines.md) | ROS 节点编写规范（Python / C++） | Filled |
| [Launch File Guidelines](./hook-guidelines.md) | Launch 文件编写、层级和参数化规范 | Filled |
| [Parameters & TF](./state-management.md) | Parameter Server 和坐标系管理规范 | Filled |
| [URDF & TF](./type-safety.md) | 机器人模型和坐标变换规范 | Filled |
| [Quality Guidelines](./quality-guidelines.md) | 代码质量标准、禁止模式、审查清单 | Filled |

---

## Pre-Development Checklist

在开发 ROS 功能前，必须阅读：

1. **[ros-development.md](../ros-development.md)** - 项目架构、话题、踩坑记录
2. **[Directory Structure](./directory-structure.md)** - 确认代码放在正确的包中
3. **[Parameters & TF](./state-management.md)** - 坐标系关系（涉及 TF 时必读）
4. **[Launch File Guidelines](./hook-guidelines.md)** - 编写 launch 文件时必读
5. **[Node Guidelines](./component-guidelines.md)** - 编写新节点时必读

---

## Quick Reference

### 常用命令

```bash
# 编译
cd Lin_ws && catkin_make

# 运行导航
source devel/setup.bash
roslaunch robot_navigation navigation.launch

# SLAM 建图
roslaunch robot_navigation slam_laser.launch

# 多点巡航
roslaunch robot_navigation patrol.launch

# 保存地图
roslaunch robot_navigation map_saver.launch
```

### 核心话题

| 话题 | 类型 | 说明 |
|------|------|------|
| `/cmd_vel` | Twist | 速度指令 |
| `/odom` | Odometry | 里程计 |
| `/scan` | LaserScan | 激光雷达 |
| `/imu/data` | Imu | IMU 数据 |
