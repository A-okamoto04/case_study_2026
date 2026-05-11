import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from nav_msgs.msg import Odometry
# File: hello_subscriber.py
class HelloSubscriber(Node):
    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
             Odometry,  # Topic先の型
             '/sobit_light/odometry/odometry', # 取得したい情報のTopic先の名前
             self.listener_callback, # ための関数名
             10) # 情報の取得に追いつかない場合，最後の10個のデータを残す
    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg)
def main(args=None):
    rclpy.init(args=args)
    hello_subscriber_node = HelloSubscriber()
    rclpy.spin(hello_subscriber_node)

    hello_subscriber_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
