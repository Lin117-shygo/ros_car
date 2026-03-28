# ESP32 下位机 - 目录结构

> ESP32-S3 + ESP-IDF 项目的代码组织方式。

---

## Overview

下位机使用 ESP-IDF 框架，采用**组件化架构**。每个功能模块是一个独立的 ESP-IDF component。

---

## Directory Layout

```
micu_ros_car/
├── main/
│   └── main.c                  # 入口函数 app_main()，负责初始化和任务创建
├── components/                  # 自定义组件（核心业务代码）
│   ├── motor/                   # 电机控制（PID + 编码器 + 驱动器）
│   │   ├── src/
│   │   │   ├── controller.c     # PID 闭环控制核心
│   │   │   └── encoder.c        # 编码器测速
│   │   └── include/
│   │       ├── controller.h
│   │       └── encoder.h
│   ├── app_mpu6050/             # MPU6050 传感器应用层
│   ├── oled/                    # OLED 显示驱动
│   ├── protocal/                # 通讯协议（注意：目录名拼写为 protocal）
│   │   ├── proto_data/          # 数据帧定义和校验
│   │   ├── ring_buffer/         # 环形缓冲区
│   │   └── UART/                # UART 串口驱动
│   ├── wireless_conn/           # WiFi 网络通信 + ROS 数据交换
│   ├── wifi/                    # WiFi 连接管理
│   └── lib/                     # 底层库
│       ├── esp32_i2c_rw/        # I2C 读写封装
│       ├── imu_ahrs/            # IMU 姿态融合算法
│       ├── mcu_dmp/             # MPU6050 DMP 驱动
│       ├── rotary_encoder/      # 旋转编码器 PCNT 驱动
│       └── WP_Math/             # 数学工具库
├── managed_components/          # ESP-IDF 组件管理器下载的第三方组件（不要修改）
│   ├── espressif__bdc_motor/    # 有刷直流电机驱动
│   ├── espressif__mpu6050/      # MPU6050 驱动
│   └── espressif__pid_ctrl/     # PID 控制器
├── sdkconfig                    # ESP-IDF 配置文件
└── CMakeLists.txt               # 顶层构建文件
```

---

## Module Organization

### 新组件创建规则

1. 在 `components/` 下创建目录
2. 必须包含 `CMakeLists.txt`、`include/` 和源文件
3. 头文件放在 `include/` 中，通过 CMakeLists.txt 的 `INCLUDE_DIRS` 暴露

```
components/new_module/
├── CMakeLists.txt
├── include/
│   └── new_module.h
└── new_module.c        # 或 src/new_module.c
```

### 层次划分

| 层次 | 目录 | 说明 |
|------|------|------|
| 应用层 | `main/` | 初始化流程、任务创建 |
| 功能组件 | `components/motor/`, `wireless_conn/` 等 | 业务逻辑 |
| 底层库 | `components/lib/` | 硬件驱动封装、算法库 |
| 第三方 | `managed_components/` | ESP-IDF 组件管理器管理，**禁止手动修改** |

---

## Naming Conventions

| 类型 | 规则 | 示例 |
|------|------|------|
| 组件目录 | 小写下划线 | `wireless_conn/`, `app_mpu6050/` |
| 源文件 | 小写下划线 | `controller.c`, `proto_data.c` |
| 头文件 | 小写下划线 | `controller.h`, `proto_data.h` |
| 日志 TAG | 双引号字符串 | `#define TAG "motor_ctrl"` |
| 函数名 | 模块前缀_功能 | `mc_new()`, `mc_set_expect_rpm()` |
| 全局变量 | `g_` 前缀 | `g_timer_handle`, `g_socks[]` |
| 宏定义 | 全大写下划线 | `MOTOR_WHEEL_SPACING`, `PID_P` |

---

## Examples

### 良好组织示例：motor 组件

`micu_ros_car/components/motor/` - 功能内聚，接口清晰：
- `controller.c` 提供 `mc_new/mc_del/mc_set_expect_rpm` 等 API
- `encoder.c` 提供 `encoder_get_rpm` 等 API
- 头文件在 `include/` 中定义公共接口，内部实现用 `static` 隐藏

### 反模式

- 不要在 `main.c` 中写业务逻辑，只做初始化和任务启动
- 不要修改 `managed_components/` 下的代码
