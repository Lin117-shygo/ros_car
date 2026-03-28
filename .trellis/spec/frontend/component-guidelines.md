# ROS 上位机 - 节点编写规范

> ROS 节点（Python / C++）的编写约定。

**注意**: 本文件原为 component-guidelines 模板，已适配为 ROS 节点规范。

---

## Overview

本项目的 ROS 节点分为两类：
- **C++ 节点**: `chassis_drive_node`（底盘驱动，性能关键）
- **Python 节点**: `waypoint_patrol.py`（巡航逻辑，开发灵活）

新功能优先使用 Python，除非有实时性要求。

---

## Python Node Structure

### 标准模板

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块简要说明
"""

import rospy
from xxx_msgs.msg import XxxMsg


class NodeName:
    """节点功能描述"""

    def __init__(self):
        rospy.init_node('node_name', anonymous=False)

        # 加载参数
        self.param = rospy.get_param('~param_name', default_value)

        # 创建 pub/sub/service/action
        self.pub = rospy.Publisher('topic', MsgType, queue_size=10)
        self.sub = rospy.Subscriber('topic', MsgType, self.callback)

        rospy.loginfo("节点初始化完成")

    def callback(self, msg):
        """回调函数说明"""
        pass

    def spin(self):
        rospy.spin()


if __name__ == '__main__':
    try:
        node = NodeName()
        node.spin()
    except rospy.ROSInterruptException:
        pass
```

### 实际示例：waypoint_patrol.py

关键模式：
- 类封装所有状态和逻辑
- `__init__` 中完成所有初始化（参数、action client、service）
- 长时间运行的操作放在独立线程中（避免阻塞 service 调用方）
- `rospy.loginfo/logwarn/logerr` 记录中文日志

---

## Node Conventions

### 参数传递

通过 launch 文件传入，使用 `~` 前缀表示私有参数：

```python
config_file = rospy.get_param('~waypoints_file', '')
```

对应 launch 文件：
```xml
<node pkg="robot_navigation" type="waypoint_patrol.py" name="waypoint_patrol">
    <param name="waypoints_file" value="$(arg waypoints_file)"/>
</node>
```

### 日志规范

```python
rospy.loginfo(f"前往目标点 [{idx}/{total}]: {name}")   # 正常流程
rospy.logwarn("巡航已在运行中")                          # 警告
rospy.logerr("无法加载配置文件")                          # 错误
```

### 服务定义

服务用于控制节点行为（启动/停止）：

```python
rospy.Service('~start_patrol', Empty, self._handle_start)
rospy.Service('~stop_patrol', Empty, self._handle_stop)
```

---

## Common Mistakes

1. **Service 回调中阻塞** - `wait_for_result()` 会阻塞调用方，应使用线程异步执行
2. **忘记设置 `anonymous=False`** - 多次启动同一节点会产生随机后缀
3. **参数无默认值** - `rospy.get_param('~xxx')` 在参数缺失时会抛异常
4. **脚本没有执行权限** - Python 脚本需要 `chmod +x`
5. **package.xml 缺少依赖** - 使用的消息包必须在 `<exec_depend>` 中声明

---

## Forbidden Patterns

```python
# WRONG: 在 service 回调中长时间阻塞
def _handle_start(self, req):
    self._run_patrol()  # 这会阻塞直到巡航结束
    return EmptyResponse()

# RIGHT: 使用线程异步执行
def _handle_start(self, req):
    thread = threading.Thread(target=self._run_patrol, daemon=True)
    thread.start()
    return EmptyResponse()
```

```python
# WRONG: 硬编码话题名和坐标系
goal.target_pose.header.frame_id = "my_map"

# RIGHT: 使用标准名称或参数化
goal.target_pose.header.frame_id = "map"
```
