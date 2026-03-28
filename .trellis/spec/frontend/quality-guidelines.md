# ROS 上位机 - 质量规范

> ROS 代码质量标准和审查清单。

---

## Overview

上位机代码质量重点在于：**参数一致性**、**坐标系正确性**、**launch 文件可靠性**。

---

## Forbidden Patterns

### 1. 禁止硬编码路径

```xml
<!-- WRONG -->
<node pkg="map_server" args="/home/user/maps/map.yaml"/>

<!-- RIGHT: 使用 $(find) 和 arg -->
<arg name="map_file" default="$(find robot_navigation)/map/map.yaml"/>
<node pkg="map_server" args="$(arg map_file)"/>
```

### 2. 禁止未经验证修改校准参数

`odom_x_scale`、`odom_z_scale_*` 等校准参数必须通过实际标定（1m 直线 / 360° 旋转）后才能修改。

### 3. 禁止使用不匹配的 frame_id

所有涉及 frame_id 的配置必须与实际发布的 TF 一致。历史教训：
- costmap 中曾写 `laser`，但雷达实际发布 `laser_frame`（已修复，现在统一为 `laser_frame`）
- launch 中写 `odom`，实际使用 `odom_combined`

### 4. 禁止在 service 回调中长时间阻塞

使用线程异步执行耗时操作（参见 component-guidelines.md）。

---

## Required Patterns

### 1. Launch 文件参数化

所有可配置项必须用 `<arg>` 暴露，提供合理默认值：

```xml
<arg name="planner" default="teb" doc="opt: dwa, teb"/>
```

### 2. Python 节点类封装

所有 Python 节点使用类封装（参见 component-guidelines.md 模板）。

### 3. 依赖完整声明

`package.xml` 中声明所有运行时依赖：

```xml
<exec_depend>rospy</exec_depend>
<exec_depend>actionlib</exec_depend>
<exec_depend>move_base_msgs</exec_depend>
<exec_depend>std_srvs</exec_depend>
```

### 4. catkin_install_python 配置

`CMakeLists.txt` 中安装 Python 脚本：

```cmake
catkin_install_python(PROGRAMS
  scripts/waypoint_patrol.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
```

---

## Build & Test

```bash
# 编译
cd Lin_ws
catkin_make

# 运行（示例）
source devel/setup.bash
roslaunch robot_navigation navigation.launch
```

---

## Code Review Checklist

### Launch 文件
- [ ] 所有路径使用 `$(find pkg)` 而非硬编码
- [ ] `<arg>` 参数有合理默认值和 `doc` 描述
- [ ] include 的子 launch 正确传递了所有必要参数
- [ ] 条件启动（`<group if>`）逻辑正确

### 参数配置
- [ ] frame_id 与实际 TF 发布一致
- [ ] costmap 的 sensor_frame 与雷达 launch 中的 frame_id 一致
- [ ] 新增参数在 launch 文件中有默认值

### Python 节点
- [ ] 使用类封装，入口有 `try/except ROSInterruptException`
- [ ] 参数使用 `rospy.get_param('~xxx', default)` 有默认值
- [ ] 脚本文件有 `#!/usr/bin/env python3` shebang
- [ ] 脚本有执行权限 (`chmod +x`)
- [ ] `package.xml` 声明了所有依赖

### 导航参数修改
- [ ] 修改前查看 `ros-development.md` 踩坑记录
- [ ] 校准参数修改有实测数据支持
- [ ] 同时检查关联参数（如修改 costmap 大小时一并检查 inflation_radius）
