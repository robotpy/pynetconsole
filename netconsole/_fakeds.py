import socket
import time
import threading


class FakeDS:
    """
    Connects to the robot and convinces it that a DS is connected to it

    Derived from the FakeDSConnector code in GradleRIO, MIT License, Jaci R
    """

    def start(self, address):

        self.running = True

        self.tcp_socket = socket.create_connection((address, 1740), timeout=3.0)
        self.tcp_socket.settimeout(5)

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_to = (address, 1110)

        self.udp_thread = threading.Thread(target=self._run_udp, daemon=True)
        self.udp_thread.start()

        self.tcp_thread = threading.Thread(target=self._run_tcp, daemon=True)
        self.tcp_thread.start()

    def stop(self):
        self.running = False
        self.udp_thread.join(1)
        self.tcp_thread.join(1)

    def _run_udp(self):
        seq = 0
        while self.running:
            seq += 1
            msg = bytes([seq & 0xFF, (seq >> 8) & 0xFF, 0x01, 0, 0, 0])
            self.udp_socket.sendto(msg, self.udp_to)
            time.sleep(0.020)

        self.udp_socket.close()

    def _run_tcp(self):
        while self.running:
            self.tcp_socket.recv(1)

        self.tcp_socket.close()
