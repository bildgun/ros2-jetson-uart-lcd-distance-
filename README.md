English | [Polski](README_PL.md)

# ROS2 Jetson UART Distance Sensor with I2C LCD Display

This project demonstrates a simple embedded sensor system built using ROS2 on NVIDIA Jetson Orin Nano.

The system reads distance data from a UART-based sensor, publishes it to a ROS2 topic, and displays it on a 16x2 LCD connected via I2C.

## Use case

This project simulates a basic onboard sensor module for UAV systems.

## Features

- ROS2 Humble (Python nodes)
- UART communication with a distance sensor
- 4-byte frame parsing: FF DH DL CS
- Checksum validation
- Topic-based communication using /lcd/text
- LCD display via I2C (16x2)
- Heartbeat mode when sensor data is unavailable

## Hardware

- NVIDIA Jetson Orin Nano
- UART distance sensor
- USB–UART converter (e.g. TTL-232R)
- 16x2 LCD with I2C interface
- Ubuntu 22.04
- ROS2 Humble

## System architecture

```
[UART Sensor] -> [lcd_publisher] -> /lcd/text -> [lcd_subscriber] -> [I2C LCD]
```

## ROS2 Nodes

### lcd_publisher

Reads raw data from UART, parses frames and publishes formatted distance.

Frame format:
```FF DH DL CS```

Distance calculation:
```distance_mm = DH * 256 + DL```

Checksum:
```CS == (FF + DH + DL) & 0xFF```

Example output:
Distance:
122 mm

### lcd_subscriber

Subscribes to /lcd/text and displays received text on a 16x2 LCD via I2C.

## Installation

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/YOUR_USERNAME/ros2-jetson-uart-lcd-distance.git
cd ~/ros2_ws

pip install -r src/ros2-jetson-uart-lcd-distance/requirements.txt

colcon build
source install/setup.bash
```
## Run

```bash
ros2 run py_pubsub lcd_publisher
ros2 run py_pubsub lcd_subscriber
```
Run with custom UART port:
```bash
ros2 run py_pubsub lcd_publisher --ros-args -p port:=/dev/ttyUSB0
```

Run with custom I2C address:
```bash
ros2 run py_pubsub lcd_subscriber --ros-args -p i2c_address:=39
```

## Repository structure
```
ros2-jetson-uart-lcd-distance/
├── README.md
├── README_PL.md
├── requirements.txt
├── images/
│   ├── setup_connected.jpg
│   └── setup_disconnected.jpg
└── src/
    └── py_pubsub/
        ├── package.xml
        ├── setup.py
        ├── setup.cfg
        ├── resource/
        │   └── py_pubsub
        └── py_pubsub/
            ├── __init__.py
            ├── lcd_publisher.py
            └── lcd_subscriber.py
```

## Demo

<table align="center">
  <tr>
    <td align="center">
      <img src="images/setup_connected.jpg" height="250"/><br>
      <sub>Sensor connected and system operating normally</sub>
    </td>
    <td align="center">
      <img src="images/setup_disconnected.jpg" height="250"/><br>
      <sub>Sensor disconnected (heartbeat mode)</sub>
    </td>
  </tr>
</table>

## Author

Bohdan Susulovskyi  
WAT, Avionics
