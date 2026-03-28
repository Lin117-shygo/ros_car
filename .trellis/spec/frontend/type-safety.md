# ROS 上位机 - URDF 与 TF 规范

> 机器人模型和坐标变换的编写约定。

**注意**: 本文件原为 type-safety 模板，已适配为 URDF/TF 规范。

---

## Overview

URDF 定义了机器人的物理结构（link + joint），TF 描述了运行时的坐标变换。两者共同构成机器人的空间模型。

---

## URDF Structure

### 本项目的 URDF

位于 `robot_description/urdf/robot_description.urdf`，由 SolidWorks 导出：

```xml
<robot name="robot_description">
  <link name="base_link">
    <inertial>...</inertial>
    <visual>
      <geometry>
        <mesh filename="package://robot_description/meshes/base_link.STL"/>
      </geometry>
    </visual>
    <collision>...</collision>
  </link>
  <!-- 更多 link 和 joint... -->
</robot>
```

### URDF 修改规则

1. **不要手动编辑惯性参数** - `<inertial>` 数据来自 SolidWorks，手动修改容易出错
2. **可以修改 joint 关系** - 如需调整传感器安装位置
3. **mesh 文件路径** - 必须使用 `package://robot_description/meshes/` 格式
4. **base_footprint → base_link 关系** - 当前被注释掉，通过底盘驱动发布

---

## TF Publishing

### 静态 TF（URDF 定义）

由 `robot_state_publisher` 从 URDF 自动发布：
- `base_link → imu_link`
- `base_link → laser_frame`
- 其他 link 间的关系

### 动态 TF

| 发布者 | 变换 | 说明 |
|--------|------|------|
| `chassis_drive_node` | `odom → base_footprint` | 里程计 |
| `robot_pose_ekf` | `odom_combined → base_footprint` | 融合里程计 |
| `amcl` | `map → odom_combined` | 全局定位 |

---

## Adding a New Sensor

如果要添加新传感器（如摄像头）：

1. 在 URDF 中添加 link 和 joint：
```xml
<link name="camera_link">
  <visual>...</visual>
</link>
<joint name="camera_joint" type="fixed">
  <parent link="base_link"/>
  <child link="camera_link"/>
  <origin xyz="0.1 0 0.05" rpy="0 0 0"/>
</joint>
```

2. 确保传感器驱动发布的 `frame_id` 与 URDF 中的 link name 一致
3. 更新 costmap 配置中的 sensor 设置

---

## Common Mistakes

1. **frame_id 大小写/下划线不一致** - ROS 的 frame_id 是大小写敏感的
2. **忘记更新 URDF** - 添加新传感器后，URDF 中也需要对应的 link
3. **joint origin 方向错误** - SolidWorks 导出的坐标系可能与 ROS 约定不同（ROS: x 前，y 左，z 上）
4. **mesh 文件缺失** - STL 文件没有提交到 git
