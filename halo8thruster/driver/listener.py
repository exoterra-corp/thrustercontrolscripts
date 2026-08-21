import socket, datetime, struct, threading, time
from halo8thruster.driver.telem_window import FlaskHSIWindow
from halo8thruster.driver.defines import HSIDefines


class Listener:
    """Listens and decodes trace, HSI, and raw exoserial messages over UDP."""

    def __init__(self, mode, udp_ip, udp_port):
        self.mode = mode
        self.udp_ip = udp_ip
        self.udp_port = int(udp_port)
        self.running = True
        self.hsi_defs = HSIDefines()
        self.send_count = 0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.udp_ip, self.udp_port))
        if self.mode == "gui":
            self.frame = FlaskHSIWindow()

    def run(self):
        t = threading.Thread(target=self.listen)
        t.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.on_exit()

    def on_exit(self):
        self.running = False
        self.sock.sendto(bytes("", "ascii"), (self.udp_ip, self.udp_port))

    def listen(self):
        try:
            while self.running:
                data, addr = self.sock.recvfrom(1024)
                now = datetime.datetime.now()
                time_string_disp = now.strftime("%M:%S.%f")
                if self.mode == "raw":
                    if data[0] == 0xA:
                        tx_bytes = data[1:]
                        if (tx_bytes[0] & 0xF8) == 0xa8:
                            cob_id = (tx_bytes[0] & 0x7) << 8 | (tx_bytes[1] & 0xFF)
                            data_length = tx_bytes[2] & 0xF
                            data = tx_bytes[3:11]
                            self.send_count += 1
                            print(f"S:{time_string_disp}:{tx_bytes.hex()}: id:{hex(cob_id)}: dl:{data_length}: d:{data.hex()}: cnt:{self.send_count}")
                    elif data[0] == 0xB:
                        rx_bytes = data[1:]
                        if (rx_bytes[0] & 0xF8) == 0xa8:
                            cob_id = (rx_bytes[0] & 0x7) << 8 | (rx_bytes[1] & 0xFF)
                            data_length = rx_bytes[2] & 0xF
                            data = rx_bytes[3:11]
                            if struct.unpack("<H", rx_bytes[4:6])[0] == 0x5001 and rx_bytes[6] == 0x3:
                                self.sock.sendto(data, (self.udp_ip, self.udp_port + 1))
                            print(f"R:{time_string_disp}:{rx_bytes.hex()}: id:{hex(cob_id)}: dl:{data_length}: d:{data.hex()}")
                elif self.mode in ("hsi", "trace"):
                    print(data.decode("ascii")[14:])
                elif self.mode == "gui":
                    try:
                        hsi_frame = self.hsi_defs.parse_hsi_packet(data)
                        for name, val in hsi_frame.items():
                            entry = self.hsi_defs.hsi[name]
                            self.frame.write_display(entry["row"], entry["col"], val)
                    except Exception as e:
                        print(f"Query Failed: {e}")
        except IndexError:
            pass
