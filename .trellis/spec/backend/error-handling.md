# ESP32 下位机 - 错误处理

> ESP-IDF 项目中的错误处理约定。

---

## Overview

ESP-IDF 使用 `esp_err_t` 返回值体系。本项目遵循 ESP-IDF 官方错误处理模式。

---

## Error Types

### esp_err_t 返回值

所有可能失败的函数必须返回 `esp_err_t`：

```c
esp_err_t mc_new(const mc_config_t *config, float max_rpm, mc_handle_t *ret_handle);
```

常用错误码：
| 错误码 | 含义 | 使用场景 |
|--------|------|----------|
| `ESP_OK` | 成功 | 正常返回 |
| `ESP_ERR_INVALID_ARG` | 参数无效 | NULL 指针、越界值 |
| `ESP_ERR_INVALID_STATE` | 状态无效 | 未初始化就调用、重复初始化 |
| `ESP_ERR_NO_MEM` | 内存不足 | malloc 失败 |
| `ESP_FAIL` | 通用失败 | FreeRTOS API 返回 false |

---

## Error Handling Patterns

### Pattern 1: ESP_RETURN_ON_ERROR（推荐）

用于函数内部调用其他 ESP-IDF API 时的错误传播：

```c
// 来自 controller.c
ESP_RETURN_ON_ERROR(bdc_motor_enable(handle->motor), TAG, "enable motor failed");
ESP_RETURN_ON_ERROR(bdc_motor_forward(handle->motor), TAG, "forward motor failed");
```

### Pattern 2: ESP_GOTO_ON_ERROR（需要清理资源时）

```c
// 来自 controller.c - mc_new()
ESP_GOTO_ON_ERROR(encoder_new(&config->encoder_config, &handle->encoder), err,
    TAG, "create encoder handle failed");
// ...
err:
    if (handle) free(handle);
    return ret;
```

### Pattern 3: ESP_ERROR_CHECK（仅用于初始化阶段）

初始化期间如果失败应立即终止：

```c
// 来自 main.c
ESP_ERROR_CHECK(mc_new(&config, 150, &ctx->left));
```

### Pattern 4: 状态前置检查宏

本项目定义了一组状态检查宏（见 `controller.c`）：

```c
#define RETURN_ON_FALSE(a, msg) ESP_RETURN_ON_FALSE(a, ESP_ERR_INVALID_STATE, TAG, msg)
#define RETURN_ON_UNCREATED(msg) RETURN_ON_FALSE(g_timer_handle != NULL, msg)
#define RETURN_ON_INACTIVE(msg) RETURN_ON_FALSE(!xTimerIsTimerActive(g_timer_handle), msg)
```

### Pattern 5: bool 返回值（硬件初始化链）

`hardware_init()` 使用简单的 bool 链式检查：

```c
// 来自 main.c
if (!wifi_init()) return false;
if (!oled_init()) return false;
if (!mpu6050_hardware_init(&ctx.mpu6050)) return false;
```

---

## Common Mistakes

1. **忘记检查返回值** - 所有返回 `esp_err_t` 的调用都必须检查
2. **在中断/定时器回调中使用 ESP_ERROR_CHECK** - 会导致 abort，应该用日志记录替代
3. **资源泄漏** - 使用 `goto err` 模式确保 malloc 后的资源在失败时被释放
4. **状态检查遗漏** - 调用 API 前先验证前置条件（如定时器是否已创建）

---

## Forbidden Patterns

```c
// WRONG: 忽略错误返回值
bdc_motor_enable(handle->motor);

// RIGHT: 总是检查或传播错误
ESP_RETURN_ON_ERROR(bdc_motor_enable(handle->motor), TAG, "enable motor failed");
```

```c
// WRONG: 在定时器回调中使用 ESP_ERROR_CHECK（会 abort）
static void timer_cb(TimerHandle_t xTimer) {
    ESP_ERROR_CHECK(some_function());  // 不要这样做
}

// RIGHT: 在回调中只记录错误
static void timer_cb(TimerHandle_t xTimer) {
    esp_err_t ret = some_function();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "function failed: %s", esp_err_to_name(ret));
    }
}
```
