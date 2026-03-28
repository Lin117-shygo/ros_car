# ESP32 下位机开发规范

> ESP32-S3 + ESP-IDF 嵌入式开发的最佳实践。

**注意**: 本项目将 backend 映射为 **ESP32 下位机**开发。另见 [ros-development.md](../ros-development.md) 获取项目全局概览。

---

## Overview

下位机代码位于 `micu_ros_car/`，基于 ESP-IDF 框架开发，负责：
- 双轮差速电机控制（PID 闭环）
- MPU6050 六轴传感器数据采集
- WiFi 网络通信 + ROS 数据交换
- YDLidar 激光雷达数据转发
- OLED 显示

**一般情况下下位机代码基本不修改**，主要开发在 ROS 上位机端。

---

## Guidelines Index

| Guide | Description | Status |
|-------|-------------|--------|
| [Directory Structure](./directory-structure.md) | ESP-IDF 组件化目录结构和命名规范 | Filled |
| [Communication Protocol](./database-guidelines.md) | 上下位机通讯协议、数据帧格式、单位约定 | Filled |
| [Error Handling](./error-handling.md) | ESP-IDF esp_err_t 错误处理模式 | Filled |
| [Quality Guidelines](./quality-guidelines.md) | 代码质量标准、禁止模式、审查清单 | Filled |
| [Logging Guidelines](./logging-guidelines.md) | ESP_LOG 日志系统使用规范 | Filled |

---

## Pre-Development Checklist

在修改 ESP32 代码前，必须阅读：

1. **[ros-development.md](../ros-development.md)** - 硬件参数、通讯协议概览
2. **[Directory Structure](./directory-structure.md)** - 了解组件组织方式
3. **[Error Handling](./error-handling.md)** - ESP-IDF 错误处理约定
4. **[Communication Protocol](./database-guidelines.md)** - 数据帧格式（修改通讯相关代码时必读）

---

## Key Constraints

- **硬件参数禁止随意修改** - PID、轮距、编码器脉冲等参数经过实测校准
- **managed_components/ 禁止修改** - 由 ESP-IDF 组件管理器管理
- **修改后需实际烧录测试** - 嵌入式代码无法仅靠 lint 验证
