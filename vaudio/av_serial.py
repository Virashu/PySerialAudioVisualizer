__all__ = ["Serial"]

import serial
import serial.tools.list_ports


class Serial:

    @staticmethod
    def select() -> str:
        """Select serial port by console and return its name

        Example: 'COM1', '/dev/ttyUSB0'"""
        avail_ports = serial.tools.list_ports.comports()

        if len(avail_ports) == 0:
            raise RuntimeError("No serial ports found")

        print("Select port:")

        for i, p in enumerate(avail_ports):
            print(f"[{i}] {p}")

        port_index = int(input())
        return avail_ports[port_index].name

    @staticmethod
    def list() -> None:
        """Print available ports' names to console"""
        avail_ports = serial.tools.list_ports.comports()

        if len(avail_ports) == 0:
            raise RuntimeError("No serial ports found")

        for i, p in enumerate(avail_ports):
            print(f"[{i}] {p}")

    def __init__(self, port: str):
        self._port = serial.Serial(port=port, baudrate=115200)

    def send(self, data: str) -> None:
        """Send str data to serial"""
        self._port.write(data.encode())
