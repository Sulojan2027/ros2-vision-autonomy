import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    config_path = os.path.join(get_package_share_directory('my_first_pkg'),
                               "config/params.yaml"
                )

    publisher = Node(
        package="my_first_pkg",
        executable="my_pub_node",
        name="simple_publisher",
        output="screen",
        parameters=[config_path]
    )

    subscriber = Node(
        package="my_first_pkg",
        name="simple_subscriber",
        executable="my_sub_node",
        output="screen"
    )
    
    publisher_2 = Node(
        package="my_first_pkg",
        executable="my_pub_node",
        name="simple_publisher_2",
        output="screen",
        parameters=[config_path]
    )

    return LaunchDescription([
        publisher, subscriber, publisher_2
    ])