import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, TextSubstitution


def generate_launch_description():
    
    # Paths loading
    pkg_share = get_package_share_directory('vision_sim')
    config_path = os.path.join(pkg_share, "config/bridge.yaml")

    # World is chosen at launch time, e.g. world:=detection_world.sdf
    world_arg = DeclareLaunchArgument(
        "world",
        default_value="camera_world.sdf",
        description="World file name inside the package's worlds/ directory",
    )
    world_path = PathJoinSubstitution([pkg_share, "worlds", LaunchConfiguration("world")])

    # Set Environment variables for GPU usage
    render_offload = SetEnvironmentVariable("__NV_PRIME_RENDER_OFFLOAD", "1")
    vendor_library = SetEnvironmentVariable("__GLX_VENDOR_LIBRARY_NAME", "nvidia")
    
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            "gz_args": [TextSubstitution(text="-r "), world_path]
        }.items(),
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
        world_arg, render_offload, vendor_library, gazebo, bridge
    ])