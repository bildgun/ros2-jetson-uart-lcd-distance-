🇬🇧 English | [🇵🇱 Polski](README_PL.md)

# ROS2 Jetson UART Distance Sensor with I2C LCD Display

This project demonstrates a simple embedded sensor system built using ROS2 on NVIDIA Jetson Orin Nano.

It reads distance data from a UART sensor, publishes it to a ROS2 topic, and displays it on a 16x2 LCD via I2C.

---

##  Use case

This project simulates a basic onboard sensor module for UAV systems.

---

##  Features

- ROS2 Humble (Python nodes)
- UART communication (distance sensor)
- 4-byte frame parsing: `FF DH DL CS`
- Checksum validation
- Topic-based communication (`/lcd/text`)
- LCD display via I2C
- Heartbeat mode (when sensor is disconnected)

---

##  Hardware

- NVIDIA Jetson Orin Nano
- UART distance sensor
- USB–UART converter (TTL-232R)
- 16x2 LCD (I2C)
- Ubuntu 22.04
- ROS2 Humble

---

##  System architecture

```text
[UART Sensor]
      |
      v
[lcd_publisher]
      |
      v
ROS2 topic: /lcd/text
      |
      v
[lcd_subscriber]
      |
      v
[I2C LCD]
```
