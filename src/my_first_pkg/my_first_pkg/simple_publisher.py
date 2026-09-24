import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from rcl_interfaces.msg import SetParametersResult, FloatingPointRange, ParameterDescriptor
from std_msgs.msg import String

class SimplePublisher(Node):
    def __init__(self):
        super().__init__("my_publisher")
        pubrate_range = FloatingPointRange(
            from_value=0.1,
            to_value=50.0,
            step=0.0
        )
        param_descriptor = ParameterDescriptor(
            description="Message Publishing rate restricted between 0.1 and 50.0",
            floating_point_range=[pubrate_range]
        )
        self.declare_parameter("message_prefix", "Hey buddy!")
        self.declare_parameter(
            "publish_rate", 2.0, param_descriptor
        )
        
        self.publisher_ = self.create_publisher(
            String,"greetings",10
        )
        self.timer_=self.create_timer(
            timer_period_sec=1/self.get_parameter("publish_rate").value,
            callback=self.timer_callback
        )
        self.counter = 0

        self.add_post_set_parameters_callback(self.apply_params)
    
    def apply_params(self, params):
        for p in params:
            if p.name == "publish_rate":
                self.destroy_timer(self.timer_)
                self.timer_ = self.create_timer(
                    timer_period_sec= 1 / p.value,
                    callback=self.timer_callback
                )
                self.get_logger().info(f"Publish rate changed to {p.value} Hz")

    def timer_callback(self):
        msg_prefix = self.get_parameter("message_prefix").value
        msg = String()
        msg.data = f"{msg_prefix} {self.counter}"
        self.publisher_.publish(msg)
        self.get_logger().info(f"Publishing {msg.data}....!")
        self.counter += 1
        
def main(args=None):
    rclpy.init(args=args)
    publisher_node = SimplePublisher()
    try:  
        rclpy.spin(publisher_node)
    except (KeyboardInterrupt, ExternalShutdownException):
        print("Shutdown externally...")
    finally:
        publisher_node.destroy_node()
        rclpy.try_shutdown()

if __name__ == "__main__":
    main()
        