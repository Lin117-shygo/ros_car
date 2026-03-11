#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多目标点巡航节点
使用 actionlib 客户端控制 move_base 实现自主巡航
"""

import rospy
import yaml
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import Quaternion
from actionlib_msgs.msg import GoalStatus
from std_srvs.srv import Empty, EmptyResponse
import tf.transformations
import math


class WaypointPatrol:
    """多目标点巡航控制器"""

    def __init__(self):
        rospy.init_node('waypoint_patrol', anonymous=False)

        # 加载配置
        config_file = rospy.get_param('~waypoints_file', '')
        if not config_file:
            rospy.logerr("未指定巡航点配置文件！请设置 ~waypoints_file 参数")
            rospy.signal_shutdown("配置缺失")
            return

        self.config = self._load_config(config_file)
        if not self.config:
            return

        self.waypoints = self.config.get('waypoints', [])
        self.loop = self.config.get('patrol', {}).get('loop', True)
        self.wait_duration = self.config.get('patrol', {}).get('wait_duration', 2.0)

        if not self.waypoints:
            rospy.logerr("配置文件中没有定义巡航点！")
            rospy.signal_shutdown("无巡航点")
            return

        rospy.loginfo(f"已加载 {len(self.waypoints)} 个巡航点, 循环模式: {self.loop}")

        # 创建 move_base action 客户端
        self.client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        rospy.loginfo("等待 move_base action server...")
        self.client.wait_for_server()
        rospy.loginfo("move_base 连接成功！")

        # 状态变量
        self.current_index = 0
        self.is_running = False
        self.is_paused = False

        # 服务：启动/停止巡航
        rospy.Service('~start_patrol', Empty, self._handle_start)
        rospy.Service('~stop_patrol', Empty, self._handle_stop)

        rospy.loginfo("巡航节点就绪。调用 /waypoint_patrol/start_patrol 开始巡航")

    def _load_config(self, config_file):
        """加载 YAML 配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            rospy.logerr(f"无法加载配置文件 {config_file}: {e}")
            rospy.signal_shutdown("配置加载失败")
            return None

    def _yaw_to_quaternion(self, yaw):
        """将偏航角转换为四元数"""
        q = tf.transformations.quaternion_from_euler(0, 0, yaw)
        return Quaternion(x=q[0], y=q[1], z=q[2], w=q[3])

    def _create_goal(self, waypoint):
        """根据巡航点创建导航目标"""
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position.x = waypoint['x']
        goal.target_pose.pose.position.y = waypoint['y']
        goal.target_pose.pose.orientation = self._yaw_to_quaternion(waypoint.get('yaw', 0.0))
        return goal

    def _handle_start(self, req):
        """处理启动巡航请求"""
        if not self.is_running:
            self.is_running = True
            self.current_index = 0
            rospy.loginfo("开始巡航...")
            self._run_patrol()
        else:
            rospy.logwarn("巡航已在运行中")
        return EmptyResponse()

    def _handle_stop(self, req):
        """处理停止巡航请求"""
        if self.is_running:
            self.is_running = False
            self.client.cancel_all_goals()
            rospy.loginfo("巡航已停止")
        return EmptyResponse()

    def _run_patrol(self):
        """执行巡航主循环"""
        while self.is_running and not rospy.is_shutdown():
            waypoint = self.waypoints[self.current_index]
            name = waypoint.get('name', f'点{self.current_index}')

            rospy.loginfo(f"前往目标点 [{self.current_index + 1}/{len(self.waypoints)}]: {name}")

            # 发送目标
            goal = self._create_goal(waypoint)
            self.client.send_goal(goal)

            # 等待结果
            self.client.wait_for_result()
            state = self.client.get_state()

            # TODO(human): 实现导航结果处理逻辑
            # 根据 state 判断是否成功，并决定下一步动作
            # state == GoalStatus.SUCCEEDED 表示成功到达
            # 其他状态表示失败（如 ABORTED, PREEMPTED 等）
            should_continue = self._handle_navigation_result(state, name)
            if not should_continue:
                break

            # 更新索引
            self.current_index += 1
            if self.current_index >= len(self.waypoints):
                if self.loop:
                    self.current_index = 0
                    rospy.loginfo("完成一轮巡航，开始下一轮...")
                else:
                    rospy.loginfo("巡航完成！")
                    self.is_running = False
                    break

        rospy.loginfo("巡航循环结束")

    def _handle_navigation_result(self, state, waypoint_name):
        """
        TODO(human): 处理导航结果，决定是否继续巡航

        参数:
            state: GoalStatus 枚举值，表示导航结果
                   - GoalStatus.SUCCEEDED (3): 成功到达
                   - GoalStatus.ABORTED (4): 导航失败（无法到达）
                   - GoalStatus.PREEMPTED (2): 被抢占/取消
            waypoint_name: 当前目标点名称

        返回:
            bool: True 表示继续巡航, False 表示停止

        提示:
            - 成功时：打印日志，等待 self.wait_duration 秒，返回 True
            - 失败时：你可以选择跳过该点继续、或者停止巡航
        """
        pass  # 请在此实现你的逻辑

    def spin(self):
        """保持节点运行"""
        rospy.spin()


if __name__ == '__main__':
    try:
        patrol = WaypointPatrol()
        patrol.spin()
    except rospy.ROSInterruptException:
        pass
