#include <algorithm>
#include <chrono>
#include <optional>

#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "vision_interfaces/msg/detection_array.hpp"

using namespace std::chrono_literals;
using DetectionArray = vision_interfaces::msg::DetectionArray;
using Twist = geometry_msgs::msg::Twist;

class PersonFollower : public rclcpp::Node
{
public:
  PersonFollower()
  : Node("person_follower")
  {
    // Params
    declare_parameter<std::string>("target_class", "person");
    declare_parameter<double>("k_angular");
    declare_parameter<double>("k_linear");
    declare_parameter<double>("target_box_height", 0.6);
    declare_parameter<double>("center_deadband", 0.05);
    declare_parameter<double>("max_linear", 0.5);
    declare_parameter<double>("max_angular", 1.0);
    declare_parameter<double>("watchdog_timeout", 10.0);

    // Publisher
    cmd_pub = create_publisher<Twist>("cmd_vel", 10);

    // Subscriber
    det_sub = create_subscription<DetectionArray>(
      "detections", 10,
      [this](DetectionArray::ConstSharedPtr msg) { on_detections(msg);}
    );

    // Timer
    watchdog_timer_ = create_timer(100ms, [this]() { watchdog_check(); });
  }

  void stop()
  {
    geometry_msgs::msg::Twist stop_msg;
    cmd_pub->publish(stop_msg);
  }

private:
  void on_detections(DetectionArray::ConstSharedPtr msg)
  {
    last_detection_time_ = now();

    const std::string cls_name = get_parameter("class_name").as_string();
    const double k_ang = get_parameter("k_angular").as_double();
    const double k_lin = get_parameter("k_linear").as_double();
    const double box_h = get_parameter("target_box_height").as_double();
    const double cent_db = get_parameter("center_deadband").as_double();
    const double max_lin = get_parameter("max_linear").as_double();
    const double max_ang = get_parameter("max_angular").as_double();

    // Best box
    const vision_interfaces::msg::Detection * best =nullptr;
    for (const auto &det: msg->detections) {
      if (det.class_name == cls_name) {
        if (best == nullptr || det.confidence >= best->confidence) {
          best = &det;
        }
      }
    // TODO: e_x from the box center, deadband, h from the box,
    //       angular and linear commands, std::clamp both to the limits
    //
    // HINT (control law):
    //  - Box coords are normalized 0..1: center x = (x_min + x_max) / 2.
    //  - Sign check: in ROS, +angular.z turns LEFT (counter-clockwise).
    //    A person on the left has center x < 0.5, so 0.5 - cx > 0 gives
    //    a left turn with w = k_ang * e_x. Keep it consistent.
    //  - Deadband: if std::abs(e_x) < cent_db, set e_x to 0.0
    //    (std::abs for doubles comes from <cmath>).
    //  - h = y_max - y_min. A bigger box means the person is closer, so
    //    v = k_lin * (box_h - h) slows down as you approach and goes
    //    negative if you're too close.
    //  - std::clamp(v, lo, hi) needs all three args to be the SAME type.
    //    The box fields are float32 (float), the params are double, so do
    //    the math in double (e.g. static_cast<double>(...)) before clamping.
    //  - Decide the lower bound for v: -max_linear (allow backing up) or
    //    0.0 (never reverse). Angular is symmetric: [-max_angular, max_angular].
    best->box.x_min
    best->box.x_max
    best->box.y_min
    best->box.y_max
    const double cx = (static_cast<double>(best->box.x_min) + best->box.x_max) / 2.0;
    double e_x = 0.5 - cx;
    
    

    // TODO: build a Twist, set linear.x and angular.z, publish it
    //
    // HINT (publish): default-construct a Twist (all fields are zero),
    //  set only cmd.linear.x and cmd.angular.z, then cmd_pub->publish(cmd).
    //  Use the same publisher name as the member you declare at the bottom
    //  (the TODO there says cmd_pub_, the constructor uses cmd_pub).
    //
    // TODO: throttled log, e.g.
    //       RCLCPP_INFO_THROTTLE(get_logger(), *get_clock(), 1000,
    //                            "e_x=%.2f h=%.2f v=%.2f w=%.2f", ...);
  }

  void watchdog_check()
  {
    // TODO: if !last_detection_time_ (no detections yet), return
    // TODO: double age = (now() - *last_detection_time_).seconds();
    // TODO: if age > watchdog_timeout: stop() and a throttled RCLCPP_WARN
  }

  // TODO: member variables:
  //   rclcpp::Publisher<Twist>::SharedPtr cmd_pub_;
  //   rclcpp::Subscription<DetectionArray>::SharedPtr det_sub_;
  //   rclcpp::TimerBase::SharedPtr watchdog_timer_;
  //   std::optional<rclcpp::Time> last_detection_time_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  // TODO: create the node with std::make_shared<PersonFollower>()
  // TODO: rclcpp::spin(node);
  // TODO: best-effort stop before shutting down (see Concept 5):
  //       if rclcpp::ok() is still true, call node->stop()
  // TODO: rclcpp::shutdown();
  return 0;
}