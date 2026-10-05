import time

import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from rclpy.qos import qos_profile_sensor_data
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from vision_interfaces.msg import DetectionArray, Detection, BoundingBox


class ColorDetector(Node):
    def __init__(self):
        super().__init__('color_detector')
        self.declare_parameter('hsv_lower', [0, 100, 100])
        self.declare_parameter('hsv_upper', [10, 255, 255])
        self.declare_parameter('min_area', 300)
        self.declare_parameter('class_name', 'green_object')

        self.bridge = CvBridge()
        
        # Subscribers and Publishers
        self.subscription = self.create_subscription(
            msg_type=Image, topic='camera/image_raw',
            callback=self.image_callback,
            qos_profile=qos_profile_sensor_data
        )
        self.detection_publisher = self.create_publisher(
            msg_type=DetectionArray, topic='detections',
            qos_profile=5
        )
        self.image_publisher = self.create_publisher(
            msg_type=Image, topic='camera/image_annotated',
            qos_profile=5
        )

    def image_callback(self, msg):
        start = time.perf_counter()
        
        bgr_arr = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        H, W = bgr_arr.shape[:2]
        hsv_arr = cv2.cvtColor(bgr_arr, cv2.COLOR_BGR2HSV)
        
        # HSV mask
        hsv_lower = self.get_parameter('hsv_lower').get_parameter_value().integer_array_value
        hsv_upper = self.get_parameter('hsv_upper').get_parameter_value().integer_array_value
        hsv_mask = cv2.inRange(hsv_arr, np.array(hsv_lower, dtype=np.uint8), np.array(hsv_upper, dtype=np.uint8))
        
        # Extract contours
        contours, _ = cv2.findContours(hsv_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections = DetectionArray()
        detections.header = msg.header

        class_name = self.get_parameter('class_name').get_parameter_value().string_value
        min_area = self.get_parameter('min_area').get_parameter_value().integer_value
        
        # Detect objects using HSV masks
        for contour in contours:
            if cv2.contourArea(contour) >= min_area:
                x, y, w, h = cv2.boundingRect(contour)
                x_min, y_min = x/W, y/H
                x_max, y_max = (x+w)/W, (y+h)/H
                bbox = BoundingBox(
                    x_min=x_min, 
                    y_min=y_min, 
                    x_max=x_max, 
                    y_max=y_max
                )
                det_array = Detection(
                    class_name=class_name,
                    class_id=0, 
                    confidence=1.0, 
                    box=bbox
                )
                detections.detections.append(det_array)
                cv2.rectangle(bgr_arr, (x, y), (x+w, y+h), (0,0,255))
        
        # Publish detections
        self.detection_publisher.publish(detections)
        img_msg = self.bridge.cv2_to_imgmsg(bgr_arr, encoding='bgr8')
        self.image_publisher.publish(img_msg)

        elapsed_ms = (time.perf_counter() - start) * 1000.0
        self.get_logger().info(
            message=f'Detected {len(detections.detections)} in {elapsed_ms:.1f} ms...',
            throttle_duration_sec=1.0
        )

def main(args=None):
    rclpy.init(args=args)
    node = ColorDetector()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        print("Shutdown externally...")
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()
