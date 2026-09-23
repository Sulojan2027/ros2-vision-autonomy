import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_msgs.msg import String

class SimplePublisher(Node):
    def __init__(self):
        super().__init__("my_publisher")
        self.publisher_ = self.create_publisher(
            String,"greetings",10
        )
        self.timer_=self.create_timer(
            timer_period_sec=0.5,
            callback=self.timer_callback
        )
        self.counter = 0
        
    def timer_callback(self):
        msg = String()
        msg.data = f"Hey buddy! {self.counter}"
        self.publisher_.publish(msg)
        self.get_logger().info(f"Publishing {msg.data}....!")
        self.counter += 1
        
def main(args=None):
    rclpy.init(args=args)
    publisher_node = SimplePublisher()
    try:  
        rclpy.spin(publisher_node)
    except (KeyboardInterrupt, ExternalShutdownException):
        publisher_node.get_logger().info("Shutdown externally...")
    finally:
        publisher_node.destroy_node()
        rclpy.try_shutdown()

if __name__ == "__main__":
    main()
        