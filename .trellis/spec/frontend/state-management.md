# ROS 上位机 - 参数管理与坐标系

> ROS Parameter Server 和 TF 坐标系的使用约定。

**注意**: 本文件原为 state-management 模板，已适配为 ROS 参数/坐标系规范。

---

## Overview

ROS 中的"状态管理"对应两个核心机制：
- **Parameter Server** - 配置参数（类似全局状态）
- **TF 树** - 坐标系关系（空间状态）

---

## Parameter Server

### 参数层次

| 层次 | 来源 | 示例 |
|------|------|------|
| 全局参数 | launch 文件 `<param>` | `usart_port_name`, `serial_baud_rate` |
| 命名空间参数 | `rosparam load` + `ns` | `move_base/base_local_planner` |
| 私有参数 | 节点内 `~param` | `~waypoints_file` |

### 参数文件规范

YAML 文件存放在各包的 `param/` 或 `config/` 目录：

```yaml
# 巡航参数示例 - config/waypoints.yaml
patrol:
  loop: true
  wait_duration: 2.0

waypoints:
  - name: "起点"
    x: 0.0
    y: 0.0
    yaw: 0.0
```

### 里程计校准参数（重要）

位于 `chassis_bringup/launch/bringup.launch`，需要实测校准：

```xml
<param name="odom_x_scale"           value="2.18"/>   <!-- 线性校准 -->
<param name="odom_z_scale_positive"  value="1.93"/>   <!-- 角度校准（正向）-->
<param name="odom_z_scale_negative"  value="1.93"/>   <!-- 角度校准（负向）-->
```

**警告**: 这些值异常大（正常应接近 1.0），说明底盘里程计原始精度不高。修改前必须做 1m 直线和 360° 原地旋转标定。

---

## TF Tree

### 本项目的 TF 结构

```
/map                          ← AMCL 发布
  └─ /odom_combined           ← robot_pose_ekf 融合里程计
       └─ /base_footprint     ← 底盘驱动发布
            ├─ /base_link     ← URDF 定义
            ├─ /imu_link      ← URDF 定义
            └─ /laser_frame   ← 雷达驱动发布（注意不是 laser）
```

### Frame ID 对照表

| 组件 | 发布的 frame_id | 说明 |
|------|-----------------|------|
| 雷达驱动 | `laser_frame` | YDLidar X2 默认，URDF/costmap/驱动已统一 |
| 底盘驱动 | `base_footprint` | robot_frame_id 参数 |
| EKF 滤波器 | `odom_combined` | output_frame 参数 |
| AMCL | `map` | 全局定位 |

### 关键一致性检查

**必须保证以下 frame_id 一致：**

1. 雷达 launch 中 `frame_id` = costmap 参数中 `sensor_frame`
2. 底盘 launch 中 `robot_frame_id` = EKF 中 `base_footprint_frame`
3. EKF 中 `output_frame` = AMCL 中 `odom_frame_id`

---

## Common Mistakes

1. **sensor_frame 已统一** - URDF link、雷达驱动、costmap 配置现在都使用 `laser_frame`（历史上曾经 costmap 写成 `laser` 导致问题，已修复）
2. **odom frame 混用** - `odom` vs `odom_combined`，本项目使用 `odom_combined`（经过 EKF 融合）
3. **local_costmap 的 global_frame** - 设为 `map` 会受 AMCL 跳变影响，建议用 `odom_combined`
4. **AMCL 初始位姿** - 启动导航后必须在 RViz 中设置正确的初始位姿（踩坑记录 2026-03-10）
