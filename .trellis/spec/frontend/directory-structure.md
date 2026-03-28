# ROS 上位机 - 目录结构

> ROS1 工作空间的代码组织方式。

---

## Overview

上位机使用 ROS1 (catkin) 工作空间，包含 4 个功能包。开发语言为 Python（节点脚本）和 XML（launch 文件 / URDF）。

---

## Directory Layout

```
Lin_ws/
├── src/
│   ├── chassis_bringup/         # 底盘驱动包
│   │   ├── launch/
│   │   │   ├── bringup.launch           # 底盘启动（核心）
│   │   │   ├── calibrate_linear.launch  # 线性校准
│   │   │   └── calibrate_angular.launch # 角度校准
│   │   ├── scripts/
│   │   │   ├── calibrate_linear.py
│   │   │   ├── calibrate_angular.py
│   │   │   └── transform_utils.py
│   │   ├── src/                 # C++ 节点源码（chassis_drive_node）
│   │   ├── CMakeLists.txt
│   │   └── package.xml
│   │
│   ├── robot_navigation/        # SLAM + 导航包
│   │   ├── launch/
│   │   │   ├── navigation.launch        # 完整导航启动（核心入口）
│   │   │   ├── slam_laser.launch        # SLAM 建图
│   │   │   ├── move_base.launch         # 路径规划
│   │   │   ├── patrol.launch            # 多点巡航
│   │   │   ├── map_saver.launch         # 保存地图
│   │   │   └── include/                 # 子 launch（被其他 launch 引用）
│   │   │       ├── amcl.launch          # 自适应蒙特卡洛定位
│   │   │       ├── gmapping.launch
│   │   │       ├── hector.launch
│   │   │       ├── karto.launch
│   │   │       └── cartographer.launch
│   │   ├── param/                       # 导航参数 YAML
│   │   │   ├── params_nav_common/       # 导航通用参数
│   │   │   └── params_costmap_common/   # 代价地图参数
│   │   ├── config/
│   │   │   └── waypoints.yaml           # 巡航点配置
│   │   ├── map/                         # 保存的地图文件
│   │   ├── rviz/                        # RViz 配置
│   │   ├── scripts/
│   │   │   └── waypoint_patrol.py       # 巡航节点
│   │   ├── CMakeLists.txt
│   │   └── package.xml
│   │
│   ├── robot_description/       # 机器人模型包
│   │   ├── launch/
│   │   │   ├── robot_model_visual.launch  # TF + URDF 发布
│   │   │   ├── display.launch             # RViz 模型展示
│   │   │   └── gazebo.launch              # Gazebo 仿真
│   │   ├── urdf/
│   │   │   └── robot_description.urdf     # 机器人 URDF 模型
│   │   └── meshes/                        # 3D 模型文件 (.STL)
│   │
│   └── ydlidar_ros_driver/      # 激光雷达驱动（第三方，尽量不修改）
│       └── launch/
│           ├── X2.launch                  # 本项目使用的型号
│           └── *.launch                   # 其他型号配置
│
├── pts/                         # 虚拟串口目录
└── devel/                       # catkin 构建输出
```

---

## Package Organization

### 新功能放在哪个包？

| 功能类型 | 目标包 |
|----------|--------|
| 底盘通信、里程计 | `chassis_bringup` |
| 导航、SLAM、路径规划 | `robot_navigation` |
| TF、URDF、模型 | `robot_description` |
| 雷达驱动 | `ydlidar_ros_driver`（尽量不改） |

### 新包创建规则

一般不需要创建新包。如果确实需要：

```bash
cd Lin_ws/src
catkin_create_pkg new_pkg rospy std_msgs
```

---

## Naming Conventions

| 类型 | 规则 | 示例 |
|------|------|------|
| 功能包 | 小写下划线 | `robot_navigation` |
| Launch 文件 | 小写下划线.launch | `navigation.launch` |
| Python 脚本 | 小写下划线.py | `waypoint_patrol.py` |
| 节点名 | 小写下划线 | `chassis_drive`, `waypoint_patrol` |
| 话题名 | /小写下划线 | `/cmd_vel`, `/scan` |
| 参数文件 | 小写下划线.yaml | `waypoints.yaml` |
| Include launch | 放在 `launch/include/` | `amcl.launch` |

---

## Examples

### 良好组织示例：robot_navigation

- Launch 文件分层：`navigation.launch` 引用 `bringup.launch` + `amcl.launch` + `move_base.launch`
- 参数外置：导航参数用 YAML 文件，通过 `rosparam load` 加载
- 子 launch 放在 `include/` 目录，不直接暴露给用户
