#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多目标点巡航节点
使用 actionlib 客户端控制 move_base 实现自主巡航
"""

import rospy
import yaml
import actionlib
import threading
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
        patrol_config = self.config.get('patrol', {})
        self.loop = patrol_config.get('loop', True)
        self.wait_duration = patrol_config.get('wait_duration', 2.0)
        self.clear_costmaps_each_goal = patrol_config.get('clear_costmaps_each_goal', True)
        self.clear_costmaps_delay = patrol_config.get('clear_costmaps_delay', 0.3)
        self.clear_costmaps_service_name = patrol_config.get(
            'clear_costmaps_service',
            '/move_base/clear_costmaps'
        )

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
        self._patrol_thread = None
        self.clear_costmaps_client = None

        if self.clear_costmaps_each_goal:
            try:
                rospy.wait_for_service(self.clear_costmaps_service_name, timeout=3.0)
                self.clear_costmaps_client = rospy.ServiceProxy(
                    self.clear_costmaps_service_name,
                    Empty
                )
            except rospy.ROSException:
                rospy.logwarn(
                    f"clear_costmaps service unavailable: {self.clear_costmaps_service_name}"
                )

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

    def _clear_costmaps(self, reason):
        """Clear move_base costmaps before sending the next goal."""
        if self.clear_costmaps_client is None:
            return

        try:
            self.clear_costmaps_client()
            rospy.loginfo(f"cleared costmaps: {reason}")
            if self.clear_costmaps_delay > 0.0:
                rospy.sleep(self.clear_costmaps_delay)
        except rospy.ServiceException as exc:
            rospy.logwarn(f"clear_costmaps failed: {exc}")

    def _handle_start(self, req):
        """处理启动巡航请求（异步启动，立即返回）"""
        # 检查旧线程是否还在运行，如果在则等待它结束
        if self._patrol_thread is not None and self._patrol_thread.is_alive():
            rospy.logwarn("等待上一次巡航线程结束...")
            self._patrol_thread.join(timeout=2.0)
            if self._patrol_thread.is_alive():
                rospy.logerr("旧巡航线程未能及时结束，请稍后重试")
                return EmptyResponse()

        if not self.is_running:
            self.is_running = True
            self.current_index = 0
            rospy.loginfo("开始巡航...")
            # 使用线程异步执行巡航，避免阻塞服务调用方
            self._patrol_thread = threading.Thread(target=self._run_patrol, daemon=True)
            self._patrol_thread.start()
        else:
            rospy.logwarn("巡航已在运行中")
        return EmptyResponse()

    def _handle_stop(self, req):
        """处理停止巡航请求"""
        if self.is_running:
            self.is_running = False
            self.client.cancel_all_goals()
            # 等待巡航线程结束，避免竞态
            if self._patrol_thread is not None and self._patrol_thread.is_alive():
                self._patrol_thread.join(timeout=3.0)
            rospy.loginfo("巡航已停止")
        return EmptyResponse()

    def _run_patrol(self):
        """执行巡航主循环"""
        try:
            while self.is_running and not rospy.is_shutdown():
                waypoint = self.waypoints[self.current_index]
                name = waypoint.get('name', f'点{self.current_index}')

                rospy.loginfo(f"前往目标点 [{self.current_index + 1}/{len(self.waypoints)}]: {name}")

                # 发送目标
                goal = self._create_goal(waypoint)
                if self.clear_costmaps_each_goal:
                    self._clear_costmaps(f"before_goal_{self.current_index}")

                self.client.send_goal(goal)

                # 等待结果
                self.client.wait_for_result()
                state = self.client.get_state()

                # 处理导航结果
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
                        break
        finally:
            # 无论何种原因退出，都确保状态正确重置
            self.is_running = False
            rospy.loginfo("巡航循环结束")

    def _handle_navigation_result(self, state, waypoint_name):
        """
        处理导航结果，决定是否继续巡航

        参数:
            state: GoalStatus 枚举值
            waypoint_name: 当前目标点名称
        返回:
            bool: True 继续巡航, False 停止
        """
        if state == GoalStatus.SUCCEEDED:  # 成功到达
            rospy.loginfo(f"成功到达目标点{waypoint_name}")
            rospy.sleep(self.wait_duration)
            return True
        elif state == GoalStatus.ABORTED: #导航失败（无法到达）
            rospy.loginfo(f"无法到达目标点{waypoint_name}")
            return False
        elif state == GoalStatus.PREEMPTED: #被抢占
            rospy.loginfo(f"目标点{waypoint_name}被抢占")
            return False
        else:
            rospy.loginfo(f"遭遇未知情况，无法到达目标点{waypoint_name}")
            return False
        

    def spin(self):
        """保持节点运行"""
        rospy.spin()


if __name__ == '__main__':
    try:
        patrol = WaypointPatrol()
        patrol.spin()
    except rospy.ROSInterruptException:
        pass
