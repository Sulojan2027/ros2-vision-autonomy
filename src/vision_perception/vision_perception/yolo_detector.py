import time

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from rclpy.qos import qos_profile_sensor_data
from rcl_interfaces.msg import (
    FloatingPointRange, IntegerRange, ParameterDescriptor
)
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from ultralytics import YOLO
from vision_interfaces.msg import DetectionArray, Detection, BoundingBox

# Resolution of the simulated camera, used for the warm-up image.
CAMERA_HEIGHT = 480
CAMERA_WIDTH = 640


class YoloDetector(Node):
    def __init__(self):
        super().__init__('yolo_detector')

        self.declare_parameter(
            'model_path',
            '/mnt/space/Projects/ros2_vision_ws/models/yolo26n.pt',
            ParameterDescriptor(
                description='Absolute path to the model .pt file. Startup only.',
                read_only=True,
            ),
        )
        self.declare_parameter(
            'confidence_threshold', 0.5,
            ParameterDescriptor(
                description='Minimum detection confidence (0.01 to 1.0). Live.',
                floating_point_range=[FloatingPointRange(
                    from_value=0.01, to_value=1.0, step=0.0
                )],
            ),
        )
        self.declare_parameter(
            'device', '0',
            ParameterDescriptor(
                description="Inference device: '0' for the first GPU, or 'cpu'. "
                            'Startup only.',
                read_only=True,
            ),
        )
        self.declare_parameter(
            'image_size', 640,
            ParameterDescriptor(
                description='Inference resolution in pixels, a multiple of 32. '
                            'Startup only.',
                integer_range=[IntegerRange(
                    from_value=320, to_value=1280, step=32
                )],
                read_only=True,
            ),
        )

        self.device = self.get_parameter('device').value
        self.image_size = self.get_parameter('image_size').value

        # Load the model
        model_path = self.get_parameter('model_path').value
        self.model = YOLO(model_path)
        self.get_logger().info(f'Loaded model {model_path} on device {self.device}')

        # Warm-up inference
        warmup_start = time.perf_counter()
        self.model(
            np.zeros((CAMERA_HEIGHT, CAMERA_WIDTH, 3), dtype=np.uint8),
            imgsz=self.image_size,
            device=self.device,
            verbose=False,
        )
        warmup_ms = (time.perf_counter() - warmup_start) * 1000.0
        self.get_logger().info(f'Warm-up inference took {warmup_ms:.1f} ms')
        
        
        self.bridge = CvBridge()
        self.detection_publisher = self.create_publisher(
            DetectionArray, 'detections', 5
        )
        self.image_publisher = self.create_publisher(
            Image, 'camera/image_annotated', 5
        )
        self.cam_sub = self.create_subscription(
            Image, 'camera/image_raw', self.image_callback,
            qos_profile_sensor_data,
        )

    def image_callback(self, msg):
        start = time.perf_counter()

        bgr = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        
        conf_threshold = self.get_parameter('confidence_threshold').value

        result = self.model(
            bgr,
            conf=conf_threshold,
            imgsz=self.image_size,
            device=self.device,
            verbose=False,
        )[0]

        out = DetectionArray()
        out.header = msg.header

        # Move results from GPU tensors to CPU arrays.
        xyxyn = result.boxes.xyxyn.cpu().numpy()
        confs = result.boxes.conf.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy()

        for box, confidence, cls in zip(xyxyn, confs, classes):
            class_id = int(cls)
            out.detections.append(Detection(
                class_name=result.names[class_id],
                class_id=class_id,
                confidence=float(confidence),
                box=BoundingBox(
                    x_min=float(box[0]),
                    y_min=float(box[1]),
                    x_max=float(box[2]),
                    y_max=float(box[3]),
                ),
            ))

        # Publish
        self.detection_publisher.publish(out)

        annotated = self.bridge.cv2_to_imgmsg(result.plot(), encoding='bgr8')
        annotated.header = msg.header
        self.image_publisher.publish(annotated)

        elapsed_ms = (time.perf_counter() - start) * 1000.0
        labels = [d.class_name for d in out.detections]
        self.get_logger().info(
            f'{len(labels)} detections {labels} in {elapsed_ms:.1f} ms',
            throttle_duration_sec=1.0,
        )

def main(args=None):
    rclpy.init(args=args)
    node = YoloDetector()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
