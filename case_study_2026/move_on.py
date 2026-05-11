import rclpy                           # ROS 2 Pythonクライアントライブラリをインポート
from rclpy.node import Node          # ノードクラスをインポート
from geometry_msgs.msg import Twist  # Twistメッセージをインポート
from nav_msgs.msg import Odometry 
import math

# グローバル変数
start_x = None
start_y = None
current_distance = 0.0


def odom_callback(msg):
    global start_x, start_y, current_distance
    # オドメトリデータをログに出力
    rclpy.logging.get_logger('sub_odom').info(f'Odom data: {msg}')  


    # ROS 2の初期化
    #rclpy.init(args=args)
    # 'minimal_publisher'という名前のノードを作成
    #node = Node('minimal_publisher')
    # 'topic'という名前のトピックにTwist型メッセージをパブリッシュするパブリッシャを作成
    #publisher = node.create_publisher(Twist,'/sobit_light/manual_control/cmd_vel', 10)
        
    # 現在位置取得
    x = msg.pose.pose.position.x
    y = msg.pose.pose.position.y
    # 初回のみ開始位置を保存
    if start_x is None:
        start_x = x
        start_y = y

    # 開始位置からの移動距離を計算
    current_distance = math.sqrt((x - start_x) ** 2 + (y - start_y) ** 2)

    # オドメトリデータをログ出力
    rclpy.logging.get_logger('sub_odom').info(
        f'Distance: {current_distance:.2f} m'
    )


# メイン関数
def main(args=None):
    global current_distance

    # ROS 2初期化
    rclpy.init(args=args)

    # ノード作成
    node = Node('minimal_publisher')

    # パブリッシャ作成
    publisher = node.create_publisher(
        Twist,
        '/sobit_light/manual_control/cmd_vel',
        10
    )

    # オドメトリ購読
    subscription = node.create_subscription(
        Odometry,
        '/sobit_light/wheel_controller/odom',   # 必要に応じてトピック名変更
        odom_callback,
        10
    )

    # タイマーコールバック
    def timer_callback():

        # 1m未満なら前進
        if current_distance < 1.0:

            msg = Twist()

            # 線形速度設定
            msg.linear.x = 0.5
            msg.linear.y = 0.0
            msg.linear.z = 0.0

            # 角速度設定
            msg.angular.x = 0.0
            msg.angular.y = 0.0
            msg.angular.z = 0.0

            # パブリッシュ
            publisher.publish(msg)

            node.get_logger().info(
                f'{current_distance:.2f}m進行中'
            )

            # 2秒経過後は停止して終了
        else:
            msg = Twist()  # 速度0で停止
            publisher.publish(msg)

            node.get_logger().info('1m到達したら: 停止します')

            # ノード終了
            node.destroy_node()
            rclpy.shutdown()

        # 0.5秒ごとに実行
    timer_period = 0.5
    node.create_timer(timer_period, timer_callback)

    try:
        rclpy.spin(node)       # ノードをスピンしてコールバック関数を実行し続ける
    except KeyboardInterrupt:  # キーボード割り込み（Ctrl+C）をキャッチ
        pass                   # 何もしない
    finally:
        node.destroy_node()    # ノードを破棄
        rclpy.shutdown()       # ROS 2をシャットダウン
        print("finished")      # プログラム終了時にメッセージを表示

# スクリプトが直接実行された場合
if __name__ == '__main__':   
    main()                     # メイン関数を実行
