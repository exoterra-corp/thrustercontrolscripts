
def send_udp_packet(self, msg, ip, port):
    """send_udp_packet, sends a packet locally and to a specified other network host as well."""
    now = datetime.datetime.now()
    time_string = now.strftime("%Y_%m_%d_%H_%M_%S.%f")
    msg = f"{time_string}:{msg}".strip()
    if ip != "127.0.0.1":
        self.trace_sock.sendto(bytes(msg, "ascii"), ("127.0.0.1", port))  # redirect local as well
    self.trace_sock.sendto(bytes(msg, "ascii"), (ip, port))
