import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.executors import ExternalShutdownException

class SimpleSubscriber(Node):
    def __init__(self):
        super().__init__("my_subscriber")
        self.subscriber_ = self.create_subscription(
            String, "greetings", self.listener_callback, 10
        )
        self.counter = 1
        
    def listener_callback(self, msg):
        self.get_logger().info(f"I am hearing {msg.data}...")
        self.get_logger().info(f"Recieved {self.counter} times...")
        self.counter += 1
        
def main(args=None):
    rclpy.init(args=args)
    subscriber_node = SimpleSubscriber()
    try:
        rclpy.spin(subscriber_node)
    except (KeyboardInterrupt, ExternalShutdownException):
        subscriber_node.get_logger().info("Shutdown externally...")
    finally:
        subscriber_node.destroy_node()
        rclpy.try_shutdown()
        
if __name__ == "__main__":
    main()