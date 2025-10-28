# 🤖 Robotics - ROS2 Integration for Autonomous Systems

![ROS2](https://img.shields.io/badge/ROS2-Humble-blue?style=for-the-badge)
![SLAM](https://img.shields.io/badge/SLAM-Nav2-success?style=for-the-badge)

## Overview

Complete ROS2 Humble setup with Navigation2, SLAM, and computer vision for autonomous robotics applications.

### Features

✨ **ROS2 Humble Hawksbill** - Latest LTS release
🗺️ **SLAM** - Real-time mapping with SLAM Toolbox
🦭 **Nav2** - Autonomous navigation stack
🎯 **Object Detection** - Integrated YOLOv8
⚡ **GPU Accelerated** - CUDA-enabled perception

## Quick Deploy

```bash
git checkout use-case/robotics
docker-compose up -d

# Launch ROS2
docker exec -it jetson-ros2 bash
ros2 launch nav2_bringup navigation_launch.py
```

## Stack Components

- **ROS2 Humble**: Core framework
- **Nav2**: Navigation and planning
- **SLAM Toolbox**: Mapping
- **RViz2**: Visualization
- **MoveIt2**: Manipulation planning
- **sensor_msgs**: Lidar, Camera support

[🏠 Main](../../) | [📖 Setup](../../SETUP.md)