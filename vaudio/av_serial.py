import serial
import serial.tools.list_ports

__all__ = ["Serial"]


class Serial:
    @staticmethod
    def select() -> str:
        avail_ports = serial.tools.list_ports.comports()

        if len(avail_ports) == 0:
            raise Exception("No serial ports found")

        print("Select port:")

        for i, p in enumerate(avail_ports):
            print(f"[{i}] {p}")

        port_num = int(input())
        port = avail_ports[port_num].name
        return port

    @staticmethod
    def list() -> None:
        avail_ports = serial.tools.list_ports.comports()

        if len(avail_ports) == 0:
            raise RuntimeError("No serial ports found")

        for i, p in enumerate(avail_ports):
            print(f"[{i}] {p}")

    def __init__(self, port: str):
        self._port = serial.Serial(port=port, baudrate=115200)

    def send(self, data: str) -> None:
        self._port.write(data.encode())
