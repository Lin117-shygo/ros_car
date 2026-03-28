# ESP32 下位机 - 通讯协议规范

> 上下位机之间的数据帧格式和通讯约定。

**注意**: 本文件原为 database-guidelines 模板，已适配为通讯协议规范。

---

## Overview

ESP32 与上位机 ROS 之间通过 WiFi 进行网络通信：

| 通道 | 协议 | 端口 | 用途 |
|------|------|------|------|
| 握手配置 | TCP | 8080 | 建立连接、交换配置 |
| 底盘数据 | UDP | 8082 | 速度指令 ↔ 里程计/IMU |
| 激光雷达 | UDP | 8083 | 雷达数据转发 |

---

## Data Frame Format

### ROS → ESP32（速度指令帧）

定义在 `components/protocal/proto_data/include/proto_data.h`：

```c
typedef struct {
    uint8_t head;           // 0x7B '{'
    uint8_t reserve;
    vec3_t velocity;        // X/Y/Z 速度 (mm/s)
    vec3_t acce;            // 加速度
    vec3_t gyro;            // 陀螺仪
    int16_t power;          // 电压 (mV)
    uint8_t checksum;       // XOR 校验
    uint8_t tail;           // 0x7D '}'
} ros_send_data_frame_t;    // 24 字节
```

### 校验算法

XOR 校验，从 head 到 checksum 前一个字节：

```c
// 来自 proto_data.c
uint8_t checksum = 0;
for (const uint8_t *p = frame_start; p < checksum_field; ++p) {
    checksum ^= *p;
}
```

### 帧标识

| 常量 | 值 | 说明 |
|------|-----|------|
| `ROS_HEAD` | `0x7B` | ROS 数据帧头 |
| `ROS_TAIL` | `0x7D` | ROS 数据帧尾 |

---

## Unit Conventions

上下位机之间的单位约定：

| 物理量 | 帧内单位 | ROS 单位 | 转换 |
|--------|---------|----------|------|
| 线速度 | mm/s | m/s | ÷1000 |
| 角速度 | mrad/s | rad/s | ÷1000 |
| 电压 | mV | V | ÷1000 |

转换在 `wireless_conn.c` 中完成。

---

## Differential Drive Kinematics

速度指令到左右轮 RPM 的解算也在 `wireless_conn.c` 中：

```
left_rpm  = (linear_x - angular_z * wheel_spacing / 2) / wheel_perimeter * 60
right_rpm = (linear_x + angular_z * wheel_spacing / 2) / wheel_perimeter * 60
```

**注意**: 右轮与左轮安装方向相反，代码中需要取反。

---

## Common Mistakes

1. **单位混淆** - ROS 用 m/s，ESP32 帧用 mm/s，忘记转换会导致速度异常
2. **字段错用** - 曾经出现 gyro 字段误用了 acce 数据（见 ros-development.md 踩坑记录）
3. **校验计算范围错误** - 必须从 head 开始到 checksum 字段之前
4. **结构体对齐** - 数据帧结构体使用 `__attribute__((packed))` 确保无填充
