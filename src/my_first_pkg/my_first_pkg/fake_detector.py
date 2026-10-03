import random

import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from rcl_interfaces.msg import (
    FloatingPointRange, IntegerRange, ParameterDescriptor
)

from vision_interfaces.msg import DetectionArray, Detection, BoundingBox

# Labels the fake detector can "see". The index is the class_id.
CLASS_NAMES = ['person', 'dog', 'car', 'bicycle']

# Smallest allowed box side, as a fraction of the image.
MIN_BOX_SIZE = 0.05


class FakeDetector(Node):

    def __init__(self):
        super().__init__('fake_detector')

        rate_descriptor = ParameterDescriptor(
            description='Publishing rate in Hz (0.1 to 50.0). Read at startup only.',
            floating_point_range=[FloatingPointRange(
                from_value=0.1, to_value=50.0, step=0.0
            )],
        )
        max_det_descriptor = ParameterDescriptor(
            description='Maximum detections per frame (0 to 20). Can be changed live.',
            integer_range=[IntegerRange(
                from_value=0, to_value=20, step=1
            )],
        )
        self.declare_parameter('publish_rate', 2.0, rate_descriptor)
        self.declare_parameter('max_detections', 5, max_det_descriptor)

        self.publisher_ = self.create_publisher(DetectionArray, 'detections', 10)

        rate = self.get_parameter('publish_rate').value
        self.timer_ = self.create_timer(
            timer_period_sec=1.0 / rate,
            callback=self.timer_callback,
        )

    def make_box(self):
        """Random BoundingBox, always valid:
        0 <= x_min < x_max <= 1 and 0 <= y_min < y_max <= 1,
        with each side at least MIN_BOX_SIZE."""
        x_min = random.uniform(0.0, 1.0 - MIN_BOX_SIZE)
        x_max = random.uniform(x_min + MIN_BOX_SIZE, 1.0)
        y_min = random.uniform(0.0, 1.0 - MIN_BOX_SIZE)
        y_max = random.uniform(y_min + MIN_BOX_SIZE, 1.0)
        return BoundingBox(x_min=x_min, y_min=y_min, x_max=x_max, y_max=y_max)

    def make_detection(self):
        """One random Detection."""
        class_id = random.randrange(len(CLASS_NAMES))
        return Detection(
            class_name=CLASS_NAMES[class_id],
            class_id=class_id,
            confidence=random.uniform(0.3, 1.0),
            box=self.make_box(),
        )

    def timer_callback(self):
        msg = DetectionArray()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'camera'

        max_det = self.get_parameter('max_detections').value
        count = random.randint(0, max_det)
        msg.detections = [self.make_detection() for _ in range(count)]

        self.publisher_.publish(msg)
        labels = [d.class_name for d in msg.detections]
        self.get_logger().info(f'Published {count} detections: {labels}')


def main(args=None):
    rclpy.init(args=args)
    node = FakeDetector()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
