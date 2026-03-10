# ROS 小车开发规范

## 项目概述

这是一个 ROS1 自主导航小车项目，采用上下位机分离架构。

### 架构
- **上位机** (Lin_ws/): Ubuntu + ROS1，负责 SLAM、导航、可视化
- **下位机** (micu_ros_car/): ESP32-S3 + ESP-IDF，负责电机控制、IMU、通讯

### 通讯方式
- TCP:8080 - 握手配置
- UDP:8082 - 底盘数据（电机指令 ↔ 里程计/IMU）
- UDP:8083 - 激光雷达数据转发

---

## 硬件参数（禁止随意修改）

```c
// 机械参数 - 来自实际测量
#define MOTOR_WHEEL_SPACING     128.6   // 轮距 mm
#define PLUSE_PER_ROUND         1040    // 编码器脉冲数
#define MOTOR_WHEEL_CIRCLE      150.8   // 轮周长 mm（直径48mm）

// PID 参数 - 已调优
#define PID_P   1.15
#define PID_I   1.1
#define PID_D   0.01
```

---

## ROS 话题与坐标系

### TF 树结构
```
/map
  └─ /odom_combined (融合里程计，首选)
       └─ /base_footprint
            ├─ /base_link
            ├─ /imu_link
            └─ /laser
```

### 核心话题
| 话题 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `/cmd_vel` | geometry_msgs/Twist | 输入 | 速度指令 |
| `/odom` | nav_msgs/Odometry | 输出 | 里程计 |
| `/scan` | sensor_msgs/LaserScan | 输出 | 激光雷达 |
| `/imu/data` | sensor_msgs/Imu | 输出 | IMU 数据 |

---

## 数据帧格式（上下位机通讯）

### ROS → ESP32（速度指令）
```c
typedef struct {
    uint8_t head;           // 0x7B
    uint8_t reserve;
    vec3_t velocity;        // X/Y/Z 速度 (mm/s)
    vec3_t acce;            // 加速度
    vec3_t gyro;            // 陀螺仪
    int16_t power;          // 电压 (mV)
    uint8_t checksum;       // XOR 校验
    uint8_t tail;           // 0x7D
} ros_send_data_frame_t;    // 24 字节
```

---

## 编码规范

### ESP32 代码 (C)
- 使用 ESP-IDF 风格
- 组件放在 `components/` 目录
- 每个组件有独立的 `CMakeLists.txt`

### ROS 代码 (C++)
- 遵循 ROS C++ 风格指南
- 节点命名: `xxx_node`
- 话题命名: `/小写下划线`

---

## 开发笔记（踩坑记录）

> 这个部分在开发过程中逐渐填充，记录遇到的问题和解决方案。
> 格式：`[日期] 问题 → 解决方案`

<!-- 示例：
[2024-03-07] 修改电机方向后小车转圈 → 需要同时改 motor.c 的 PWM 极性
[2024-03-08] RViz 显示 TF 错误 → 新增传感器后忘记更新 URDF
-->

[2026-03-09] navigation.launch 导航不准且频繁碰壁 -> 先排查底盘里程计与导航参数，不要只归因于宿舍杂物。已确认问题包括：1) bringup.launch 中 odom_x_scale=2.06、odom_z_scale_positive/negative=2.1，属于异常大的里程计修正量；2) local_costmap 使用 map 作为 global_frame，局部规划容易受 AMCL 跳变影响；3) 局部代价地图窗口仅 0.8m x 0.8m，且 inflation_radius=0.15、TEB min_obstacle_dist=0.1，安全裕量偏小；4) 雷达驱动发布 laser_frame，但 costmap_common_params.yaml 中 sensor_frame 写成 laser；5) ESP32 wireless_conn.c 发送 ROS 数据帧时 gyro 字段误用了 curr_acce。建议排查顺序：先做直线 1m 和原地 360° 标定，再修正 TF/传感器帧与 local_costmap 配置，最后再细调 AMCL/TEB。



---

## 常见问题

### Q: 里程计漂移怎么办？
A: 检查 `odom_x_scale` 和 `odom_z_scale_*` 校准参数

### Q: 通讯断开怎么排查？
A: 1) 检查 WiFi 连接 2) 确认 start_conn.py 正常运行 3) 检查 UDP 端口
