#!/usr/bin/env python3

import time

import rclpy
import serial
from rclpy.node import Node
from std_msgs.msg import String


class DistancePublisher(Node):
    def __init__(self):
        super().__init__('lcd_publisher')

        self.declare_parameter('topic', '/lcd/text')
        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baud', 9600)
        self.declare_parameter('publish_hz', 5.0)
        self.declare_parameter('heartbeat_hz', 1.0)
        self.declare_parameter('show_raw_hex', True)
        self.declare_parameter('frame_len', 4)

        self.topic = str(self.get_parameter('topic').value)
        self.port = str(self.get_parameter('port').value)
        self.baud = int(self.get_parameter('baud').value)
        self.publish_hz = float(self.get_parameter('publish_hz').value)
        self.heartbeat_hz = float(self.get_parameter('heartbeat_hz').value)
        self.show_raw_hex = bool(self.get_parameter('show_raw_hex').value)
        self.frame_len = int(self.get_parameter('frame_len').value)

        self.publisher = self.create_publisher(String, self.topic, 10)

        self.serial_port = None
        self.buffer = bytearray()
        self.last_publish_time = 0.0
        self.last_heartbeat_time = 0.0
        self.last_distance = None
        self.rx_bytes_total = 0

        self.open_uart()

        self.get_logger().info(f'Publishing on topic: {self.topic}')
        self.get_logger().info(
            f'UART: {self.port} @ {self.baud} 8N1 | frame_len={self.frame_len}'
        )

        self.timer = self.create_timer(0.01, self.loop)

    def open_uart(self):
        try:
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baud,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.05,
                rtscts=False,
                dsrdtr=False,
                xonxoff=False,
            )
        except serial.SerialException as error:
            self.serial_port = None
            self.get_logger().error(f'Could not open UART port {self.port}: {error}')

    @staticmethod
    def hexdump(data: bytes) -> str:
        return ' '.join(f'{byte:02X}' for byte in data)

    def publish_text(self, line_1: str, line_2: str):
        message = String()
        message.data = f'{line_1}\n{line_2}'
        self.publisher.publish(message)

    @staticmethod
    def checksum_ok_4b(frame: bytes) -> bool:
        header, data_high, data_low, checksum = frame
        expected_checksum = (header + data_high + data_low) & 0xFF
        return checksum == expected_checksum

    def parse_frames_4b(self):
        while True:
            try:
                header_index = self.buffer.index(0xFF)
            except ValueError:
                self.buffer.clear()
                return

            if header_index > 0:
                del self.buffer[:header_index]

            if len(self.buffer) < 4:
                return

            frame = bytes(self.buffer[:4])
            del self.buffer[:4]

            yield frame

    def send_heartbeat(self, current_time: float):
        heartbeat_interval = 1.0 / max(self.heartbeat_hz, 0.1)

        if current_time - self.last_heartbeat_time < heartbeat_interval:
            return

        self.last_heartbeat_time = current_time

        if self.last_distance is None:
            self.publish_text('Distance:', 'waiting...')
        else:
            self.publish_text('Last dist:', f'{self.last_distance} mm')

    def read_uart(self):
        if self.serial_port is None:
            return

        chunk = self.serial_port.read(128)

        if not chunk:
            return

        self.rx_bytes_total += len(chunk)
        self.buffer.extend(chunk)

        if self.show_raw_hex:
            self.get_logger().info(f'RX {len(chunk)}B: {self.hexdump(chunk)}')

    def process_frame(self, frame: bytes, current_time: float):
        if not self.checksum_ok_4b(frame):
            if self.show_raw_hex:
                self.get_logger().warning(f'Bad checksum frame: {self.hexdump(frame)}')
            return

        _, data_high, data_low, _ = frame
        distance_mm = data_high * 256 + data_low
        self.last_distance = distance_mm

        publish_interval = 1.0 / max(self.publish_hz, 0.1)

        if current_time - self.last_publish_time < publish_interval:
            return

        self.last_publish_time = current_time
        self.publish_text('Distance:', f'{distance_mm} mm')

        self.get_logger().info(
            f'Published distance: {distance_mm} mm | frame: {self.hexdump(frame)}'
        )

    def loop(self):
        current_time = time.time()

        self.send_heartbeat(current_time)
        self.read_uart()

        if self.frame_len != 4:
            return

        for frame in self.parse_frames_4b():
            self.process_frame(frame, current_time)

    def destroy_node(self):
        try:
            if self.serial_port is not None and self.serial_port.is_open:
                self.serial_port.close()
        except serial.SerialException:
            pass

        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    node = DistancePublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
