# ROS 小车项目 - AI 助手指南

## 项目规范

开始任何工作前，请先阅读：
- `.trellis/spec/ros-development.md` - 开发规范和项目架构

## 项目结构

```
ros_car/
├── Lin_ws/              # 上位机 ROS 工作空间
│   ├── chassis_bringup/ # 底盘驱动
│   ├── robot_navigation/# SLAM + 导航
│   └── ydlidar_ros_driver/
└── micu_ros_car/        # 下位机 ESP32 代码
```

## Git 工作流（必须遵守）

每次修改代码后：
1. **执行 `git add`** 添加修改的文件
2. **报告变更** - 告诉我改了哪些文件、做了什么改动
3. **等待我确认** - 不要自动 commit

当我确认功能实现后：
1. 我会告诉你版本名/commit message
2. 执行 `git commit -m "我指定的信息"`
3. 执行 `git push`

**禁止**：未经我确认就 commit 或 push

---

## 当前开发任务

- [ ] 多目标点巡航功能

## 开发笔记

遇到问题时，请更新 `.trellis/spec/ros-development.md` 的"开发笔记"部分。