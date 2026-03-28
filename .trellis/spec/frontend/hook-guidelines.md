# ROS 上位机 - Launch 文件规范

> Launch 文件的编写和组织约定。

**注意**: 本文件原为 hook-guidelines 模板，已适配为 ROS launch 文件规范。

---

## Overview

Launch 文件是 ROS 系统的入口点，负责启动节点、加载参数、建立话题连接。本项目的 launch 文件分为用户入口和内部模块两层。

---

## Launch File Hierarchy

```
用户入口（直接 roslaunch 使用）:
  navigation.launch    → 完整导航（底盘+雷达+定位+路径规划+RViz）
  slam_laser.launch    → SLAM 建图
  patrol.launch        → 多点巡航（包含 navigation.launch）
  bringup.launch       → 仅底盘驱动

内部模块（被其他 launch include）:
  include/amcl.launch
  include/gmapping.launch
  move_base.launch
  robot_model_visual.launch
```

---

## Launch File Patterns

### Pattern 1: 参数化启动

使用 `<arg>` 定义可配置参数，提供合理默认值：

```xml
<!-- 来自 navigation.launch -->
<arg name="map_file" default="$(find robot_navigation)/map/map.yaml"/>
<arg name="planner" default="teb" doc="opt: dwa, teb"/>
<arg name="open_rviz" default="true"/>
```

### Pattern 2: 层级 include

顶层 launch 引用底层模块，传递参数：

```xml
<!-- navigation.launch 引用 bringup -->
<include file="$(find chassis_bringup)/launch/bringup.launch"/>

<!-- navigation.launch 引用 move_base，传递参数 -->
<include file="$(find robot_navigation)/launch/move_base.launch">
    <arg name="planner" value="$(arg planner)"/>
</include>
```

### Pattern 3: 条件启动

使用 `<group if>` 或 `eval` 做条件分支：

```xml
<!-- 根据 planner 参数选择不同配置 -->
<group if="$(eval planner == 'teb')">
    <!-- TEB 配置 -->
</group>

<!-- 可选启动 RViz -->
<group if="$(arg open_rviz)">
    <node pkg="rviz" type="rviz" name="rviz" .../>
</group>
```

### Pattern 4: 参数文件加载

导航参数通过 YAML 文件加载到 parameter server：

```xml
<rosparam file="$(find robot_navigation)/param/params_nav_common/move_base_params.yaml"
          command="load" ns="move_base"/>
```

---

## Naming Conventions

| 类型 | 规则 | 示例 |
|------|------|------|
| 入口 launch | 功能描述.launch | `navigation.launch`, `patrol.launch` |
| 子模块 launch | 放在 `include/` 目录 | `include/amcl.launch` |
| 参数文件 | 按功能分目录 | `param/params_nav_common/`, `param/params_costmap_common/` |
| arg 名 | 小写下划线 | `map_file`, `open_rviz`, `use_dijkstra` |

---

## Common Mistakes

1. **路径硬编码** - 使用 `$(find pkg)` 代替绝对路径
2. **忘记传递 arg** - include 子 launch 时忘记传递必要参数
3. **sensor_frame 必须一致** - costmap 配置中的 `sensor_frame` 必须与雷达驱动发布的 frame_id 一致（本项目已统一为 `laser_frame`，曾经因不一致导致导航异常）
4. **namespace 冲突** - `rosparam load` 的 `ns` 参数要正确

---

## Important Config Files

### 导航参数目录

```
param/
├── params_nav_common/
│   ├── move_base_params.yaml          # move_base 基础参数
│   ├── base_global_planner_param.yaml # 全局规划器
│   ├── dwa_local_planner_params.yaml  # DWA 局部规划器
│   └── teb_local_planner_params.yaml  # TEB 局部规划器
└── params_costmap_common/
    ├── costmap_common_params.yaml     # 代价地图通用参数
    ├── local_costmap_params.yaml      # 局部代价地图
    └── global_costmap_params.yaml     # 全局代价地图
```

修改这些参数文件时务必参考 `ros-development.md` 中的踩坑记录。
