#!/usr/bin/env python3
import rclpy
import time
from rclpy.node import Node
from rclpy.duration import Duration
from rclpy.action import ActionClient

from sobits_interfaces.action import MoveToPose, MoveJoint#メッセージの形式


class GraspSequence(Node):
    def __init__(self):
        super().__init__("sobit_light_grasp_sequence")#デフォルト設定

        # namespace は launch に合わせる（今は sobit_light）
        ns = "/sobit_light"
        self.pose_client = ActionClient(self, MoveToPose, f"{ns}/move_to_pose")#場所の指定、通信の指定、ros2勉強会、self.は概念、class概念を
        self.joint_client = ActionClient(self, MoveJoint, f"{ns}/move_joint")

        # まずはあなたが成功させたスケールに合わせる、
        self.HAND_OPEN = 0.015#速度の指定
        self.HAND_CLOSE = -0.015

    def send_pose(self, pose_name: str, sec: int = 5):#定義のまとまり
        goal = MoveToPose.Goal()#メッセージ型
        goal.pose_name = pose_name
        goal.time_allowance = Duration(seconds=sec).to_msg()

        self.get_logger().info(f"Waiting for move_to_pose... ({pose_name})")#途中経過のログを出す
        self.pose_client.wait_for_server()

        self.get_logger().info(f"Send move_to_pose: {pose_name}")
        future = self.pose_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()

        if not goal_handle.accepted:
            raise RuntimeError(f"move_to_pose rejected: {pose_name}")

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        result = result_future.result().result

        if not result.success:
            raise RuntimeError(f"move_to_pose failed: {pose_name} msg={result.message}")

    def send_hand(self, target_rad: float, sec: int = 3):
        goal = MoveJoint.Goal()
        goal.target_joint_names = ["hand_joint"]
        goal.target_joint_rad = [float(target_rad)]
        goal.time_allowance = Duration(seconds=sec).to_msg()

        self.get_logger().info("Waiting for move_joint... (hand_joint)")
        self.joint_client.wait_for_server()

        self.get_logger().info(f"Send move_joint: hand_joint -> {target_rad}")
        future = self.joint_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()

        if not goal_handle.accepted:
            raise RuntimeError("move_joint rejected (hand_joint)")

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        result = result_future.result().result

        if not result.success:
            raise RuntimeError(f"move_joint failed: msg={result.message}")

    def run(self):#動かしたい部分
        # まず退避姿勢へ（到達後、手を「閉じ」に固定）
        self.send_pose("initial_moving_pose", sec=5)
        self.send_hand(self.HAND_OPEN, sec=3)

        #　追加したコード
        time.sleep(5.0)

        # 把持姿勢へ（到達後、手を「開き」に固定）
        self.send_pose("initial_pose", sec=5)
        time.sleep(0.3)
        self.send_hand(self.HAND_CLOSE, sec=3)

        # （ここで物体前に置く・アプローチ等を別途やるなら挿入）

        #　追加したコード
        time.sleep(5.0)
        # 再び退避姿勢へ（到達後、手を「閉じ」に固定）
        self.send_pose("initial_moving_pose", sec=5)
        time.sleep(0.3)
        self.send_hand(self.HAND_CLOSE, sec=3)

#ここまでclass

def main():
    rclpy.init()
    node = GraspSequence()#実行
    try:
        node.run()#できたらここ
    except Exception as e:
        node.get_logger().error(f"Sequence failed: {e}")#できなかったらここ
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()