import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument, GroupAction, IncludeLaunchDescription, SetEnvironmentVariable,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, TextSubstitution


def generate_launch_description():
    
    # Paths loading
    pkg_share = get_package_share_directory('vision_sim')
    config_path = os.path.join(pkg_share, "config/bridge.yaml")

    world_arg = DeclareLaunchArgument(
        "world",
        default_value="camera_world.sdf",
        description="World file name inside the package's worlds/ directory",
    )
    world_path = PathJoinSubstitution([pkg_share, "worlds", LaunchConfiguration("world")])

    # Set Environment variables for GPU usage
    render_offload = SetEnvironmentVariable("__NV_PRIME_RENDER_OFFLOAD", "1")
    vendor_library = SetEnvironmentVariable("__GLX_VENDOR_LIBRARY_NAME", "nvidia")
    
    gz_sim_launch = os.path.join(
        get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py'
    )

    gz_server = GroupAction([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_sim_launch),
            launch_arguments={
                "gz_args": [TextSubstitution(text="-s -r "), world_path],
                "on_exit_shutdown": "true",
            }.items(),
        )
    ])

    gz_gui = TimerAction(
        period=12.0,
        actions=[GroupAction([
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(gz_sim_launch),
                launch_arguments={
                    "gz_args": "-g",
                    "on_exit_shutdown": "true",
                }.items(),
            )
        ])],
    )

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="gz_bridge",
        output="screen",
        parameters=[{
            'config_file': config_path,
            'use_sim_time': True
        }
            ],
    )

    return LaunchDescription([
        world_arg, render_offload, vendor_library, gz_server, gz_gui, bridge
    ])