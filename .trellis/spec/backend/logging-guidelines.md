# ESP32 下位机 - 日志规范

> ESP-IDF 日志系统的使用约定。

---

## Overview

使用 ESP-IDF 内置的 `esp_log.h` 日志系统。每个源文件定义一个 `TAG` 宏标识模块。

---

## Log Levels

| 级别 | 宏 | 使用场景 | 示例 |
|------|-----|---------|------|
| Error | `ESP_LOGE` | 不可恢复错误、初始化失败 | 电机创建失败、内存不足 |
| Warning | `ESP_LOGW` | 可恢复异常、性能警告 | 通讯超时重试、参数越界被裁剪 |
| Info | `ESP_LOGI` | 关键状态变化、初始化成功 | 电机系统启动、WiFi 连接成功 |
| Debug | `ESP_LOGD` | 调试信息，正常运行不需要 | PID 计算细节、方向切换 |
| Verbose | `ESP_LOGV` | 大量数据输出 | 每帧数据内容 |

---

## TAG 定义规则

每个 `.c` 文件顶部定义一个 TAG：

```c
#define TAG "motor_ctrl"    // controller.c
#define TAG "ros_conn"      // wireless_conn.c
#define TAG "main"          // main.c
```

TAG 命名规则：
- 简短、有辨识度
- 全小写，下划线分隔
- 与组件/模块名对应

---

## What to Log

### 必须记录
- 硬件初始化结果（成功/失败）
- 网络连接状态变化
- FreeRTOS 任务创建
- 错误和异常情况

### 建议记录（Info 级别）
- 电机驱动类型选择（TB6612 vs DRV8833）
- PID 参数配置值
- GPIO 引脚分配

### 示例（来自 main.c）

```c
ESP_LOGI("main", "Initializing motors with TB6612 driver");
ESP_LOGI("main", "Motor control system started with %s driver", MOTOR_DRIVER_TYPE);
```

---

## What NOT to Log

- **不要在高频回调中打印** - PID 控制循环（100ms）中的 `ESP_LOGI` 会严重影响实时性
- **不要打印大块二进制数据** - 激光雷达原始数据、通讯帧原始字节
- **注释掉的调试日志保留但不启用**

```c
// 来自 controller.c - PID 回调中的调试日志被注释
//ESP_LOGI(TAG, "<rpm>:%.2f,%.2f\n", handle->expect_rpm, current_rpm);
```

---

## Common Mistakes

1. **在 PID 循环中加 ESP_LOGI** - 100ms 周期内频繁打印会阻塞控制
2. **忘记定义 TAG** - 编译报错或使用错误的 TAG
3. **日志级别不当** - 正常流程用了 `ESP_LOGE`，导致排查困难
