from setuptools import find_packages, setup
import glob

package_name = 'my_first_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob.glob("launch/*.launch.py")),
        ('share/' + package_name + '/config', glob.glob("config/*.yaml")),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sulojan',
    maintainer_email='sulojanrajkumar@gmail.com',
    description='First PubSub Package',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            "my_pub_node = my_first_pkg.simple_publisher:main",
            "my_sub_node = my_first_pkg.simple_subscriber:main",
            "fake_detector = my_first_pkg.fake_detector:main"
        ],
    },
)
