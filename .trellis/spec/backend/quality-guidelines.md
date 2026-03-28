# ESP32 下位机 - 质量规范

> ESP-IDF 代码质量标准和审查清单。

---

## Overview

下位机代码运行在资源受限的 ESP32-S3 上，质量要求侧重**实时性**、**内存安全**和**硬件正确性**。

---

## Forbidden Patterns

### 1. 禁止随意修改硬件参数

```c
// WRONG: 随意修改已校准的参数
#define PID_P   2.0     // 未经测试就改
#define MOTOR_WHEEL_SPACING  130.0  // 凭感觉改

// RIGHT: 修改前必须说明原因，并经过实测验证
// 硬件参数定义在 main.c 顶部，修改前请参考 ros-development.md
```

### 2. 禁止在中断/定时器回调中阻塞

```c
// WRONG: 在定时器回调中阻塞
static void pid_loop_tcb(TimerHandle_t xTimer) {
    vTaskDelay(pdMS_TO_TICKS(10));  // 绝对不要
    printf("debug\n");              // printf 也可能阻塞
}

// RIGHT: 回调中只做快速计算和赋值
```

### 3. 禁止修改 managed_components

`managed_components/` 下的代码由 ESP-IDF 组件管理器管理，任何修改都会在下次 `idf.py build` 时被覆盖。

### 4. 禁止在非初始化阶段使用 ESP_ERROR_CHECK

`ESP_ERROR_CHECK` 失败会 abort 整个系统。运行时错误应该用 `ESP_RETURN_ON_ERROR` 传播。

---

## Required Patterns

### 1. Doxygen 风格注释

所有公共函数必须有文档注释：

```c
/**
 * @brief 设置电机期望转速
 * @param handle 电机控制句柄
 * @param expect_rpm 期望转速（RPM），可为负数
 */
void mc_set_expect_rpm(mc_handle_t handle, float expect_rpm);
```

### 2. 资源创建/销毁配对

每个 `_new` 函数必须有对应的 `_del` 函数：
- `mc_new()` ↔ `mc_del()`
- `encoder_new()` ↔ `encoder_del()`

### 3. 状态机前置检查

状态敏感的 API 必须在函数开头检查前置条件：

```c
esp_err_t mc_timer_loop_start(void) {
    RETURN_ON_UNCREATED("please call mc_timer_loop_init first");
    RETURN_ON_INACTIVE("timer loop has been already started");
    // ...
}
```

### 4. GPIO 有效性验证

配置 GPIO 前检查引脚号有效性：

```c
if (dir1_gpio >= SOC_GPIO_PIN_COUNT) {
    return ESP_ERR_INVALID_ARG;
}
```

---

## Build & Flash

```bash
# 在 micu_ros_car/ 目录下
idf.py build          # 编译
idf.py flash          # 烧录
idf.py monitor        # 串口监控
idf.py flash monitor  # 烧录 + 监控
```

---

## Code Review Checklist

- [ ] 所有 `esp_err_t` 返回值都已检查
- [ ] 没有在高频回调中添加阻塞操作或日志输出
- [ ] 新增 GPIO 引脚不与现有引脚冲突
- [ ] 硬件参数修改有实测数据支持
- [ ] `malloc` 后有对应的 `free` 路径（包括错误路径）
- [ ] 新组件有 `CMakeLists.txt` 和 `include/` 目录
- [ ] Doxygen 注释覆盖所有公共 API
