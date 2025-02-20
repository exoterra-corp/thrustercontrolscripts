#!/usr/bin/python3
import socket, argparse, datetime, struct, os, sys, threading, time
try:
    import wx
except ModuleNotFoundError as e:
    print("wxpython is not installed, please install it before continuing.")
    sys.exit(1)
from queue import Queue
from src.HSIExcelWindow import HSIExcelWindow
from src.hsi_defines import HSIDefines

"""
ExoTerra Resource Listener Script.
description:
The listener.py script allows for viewing and capturing of raw serial messages, trace, and telemetry messages.
Thruster Command forwards msg traffic over UDP to the listener script on 3 ports, one for raw serial msgs, 
one for debug messages, and one for telemetry messages.  The UDP ports are 4000, 4002, 4001 respectively.

contact:
joshua.meyers@exoterracorp.com 
jeremy.mitchell@exoterracorp.com
"""

class Listener():
    """
    Listener, This class listens and logs trace, hsi and raw serial messages.
    """

    def __init__(self, mode, udp_ip, udp_port, logdir):
        self.mode = mode
        self.udp_ip = udp_ip
        self.udp_port = int(udp_port)
        self.logdir = f"./{logdir}/"
        self.running = True
        self.hsi_defs = HSIDefines()
        self.q = Queue()
        self.sock = socket.socket(socket.AF_INET,  # Internet
                                  socket.SOCK_DGRAM)  # UDP
        try:
            self.sock.bind((self.udp_ip, int(self.udp_port)))
        except os.error as e:
            print(f"{e}")
            sys.exit(1)
        t = threading.Thread(target=self.listen)
        if self.mode == "gui":
            print("gui enabled")
            app = wx.App(False)
            self.frame = HSIExcelWindow(None)
            self.frame.Bind(wx.EVT_CLOSE, self.on_exit)
            self.frame.Show()
            t.start()
            app.MainLoop()
        else:
            t.start()
            try:
                while True:
                    if not self.q.empty():
                        m = self.q.get()
                        self.log(m)
                    else:
                        time.sleep(0.1)
            except KeyboardInterrupt:
                self.running = False
                self.sock.sendto(bytes("", "ascii"), (self.udp_ip, self.udp_port))
                sys.exit(1)

    def on_exit(self, event=None):
        """
        on_exit, called on exit, cleans up thread and exits.
        """
        self.running = False
        self.sock.sendto(bytes("", "ascii"), (self.udp_ip, self.udp_port))
        # self.logf.close()
        sys.exit(1)

    def log(self, msg):
        """
        log, writes a msg to the log file.
        """
        None
        # self.logf.write(msg + "\n")
        # self.logf.flush()

    def listen(self):
        """
        listen, listens for data on a network port and depending on the mode decodes trace, hsi, or raw exoserial msgs.
        Should be run in a thread.
        """
        try:
            while self.running:
                data, addr = self.sock.recvfrom(1024)
                now = datetime.datetime.now()
                time_string = now.strftime("%Y_%m_%d_%H_%M_%S.%f")
                time_string_disp = now.strftime("%M:%S.%f")
                if self.mode == "raw":
                    if data[0] == 0xA:
                        # sent from the gui
                        tx_bytes = data[1:]  # remove the first byte
                        # rx_cnt = data[2]
                        header = (tx_bytes[0] & 0xF8)
                        if (header) == 0xa8:
                            # get the cob id
                            cob_id = (tx_bytes[0] & 0x7) << 8  # move the 3bits up to the top
                            cob_id |= (tx_bytes[1] & 0xFF)  # append the bottom 8 bits
                            remote_frame = (tx_bytes[2] & 0x80) >> 7
                            extended_id = (tx_bytes[2] & 0x40) >> 6
                            data_length = (tx_bytes[2] & 0xF)
                            data = tx_bytes[3:11]
                            msg = f" id:{hex(cob_id)}: dl:{data_length}: d:{data.hex()}"

                            self.log(f"[S:{time_string}]:{tx_bytes.hex()}:{msg}")
                            print(f"S:{time_string_disp}:{tx_bytes.hex()}:{msg}")

                    elif data[0] == 0xB:
                        # recv from sam
                        rx_bytes = data[1:]  # remove the first byte
                        # rx_cnt = hex(data[2])
                        header = (rx_bytes[0] & 0xF8)
                        if (header) == 0xa8:
                            # get the cob id
                            cob_id = (rx_bytes[0] & 0x7) << 8  # move the 3bits up to the top
                            cob_id |= (rx_bytes[1] & 0xFF)  # append the bottom 8 bits
                            data_length = (rx_bytes[2] & 0xF)
                            data = rx_bytes[3:11]

                            index = struct.unpack("<H", rx_bytes[4:6])[0]
                            subindex = rx_bytes[6]
                            if index == 0x5001 and subindex == 0x3:
                                self.sock.sendto(data, (self.udp_ip, self.udp_port + 1))
                            msg = f" id:{hex(cob_id)}: dl:{data_length}: d:{data.hex()}"
                            self.log(f"[R:{time_string}]:{rx_bytes.hex()}:{msg}")
                            print(f"R:{time_string_disp}:{rx_bytes.hex()}:{msg}")
                    else:
                        # garbage
                        None

                elif self.mode == "hsi" or self.mode == "trace":
                    str_msg = data.decode("ascii")
                    self.log(str_msg)
                    str_msg = str_msg[14:]
                    print(str_msg)

                elif self.mode == "gui":
                    #parse block hsi
                    try:
                        # loop through it once generate the string and then loop over it again to print it out
                        parse_str = "<"
                        for v in self.hsi_defs.block_hsi:
                            parse_str += v.get("type").replace("<", "")
                        raw_vals = struct.unpack_from(parse_str, data)
                        for i, value in enumerate(self.hsi_defs.block_hsi):
                            name = value.get("name")
                            hex_en = value.get("hex")
                            parsed_val = raw_vals[i]
                            if hex_en:
                                parsed_val = hex(parsed_val)
                            el = self.hsi_defs.hsi.get(name)
                            if el is not None:
                                r = el.get("row")
                                c = el.get("col")
                                if r is not None and c is not None:
                                    wx.CallAfter(self.frame.write_display, r, c, parsed_val)
                    except Exception as e:
                        print(f"Query Failed: {e}")
        except IndexError:
            None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Listens for exoserial data on the local network (udp).')
    parser.add_argument('-trace', action='store_true', help='Enables Trace Mode.')
    parser.add_argument('-hsi', action='store_true', help='Enables HSI Mode.')
    parser.add_argument('-gui', action='store_true', help='Enables Gui.')
    parser.add_argument('-socket', action='store', type=str, help='The Network host to bind to.',
                        default="127.0.0.1", required=False)
    parser.add_argument('-port', action='store', type=str, help='The port to listen on.',
                        default=4000, required=False)
    args = parser.parse_args()
    mode = "raw"
    logdir = "listener_exoserial"
    if args.trace:
        logdir = "listener_trace"
        args.port = 4002
        mode = "trace"
        print(f"Listening for trace msgs {args.socket}:{args.port}.")
        print("Enabled Trace Mode.")
    elif args.hsi:
        logdir = "listener_hsi"
        mode = "hsi"
        args.port = 4001
        print(f"Listening for hsi and trace msgs {args.socket}:{args.port}.")
        print("Enabled HSI Mode.")
    elif args.gui:
        logdir = "listener_hsi"
        args.port = 4001
        mode = "gui"
        print("Enabled HSI-GUI Mode.")
    else:
        mode = "raw"
        print("Enabled Raw Mode.")
        print(f"Listening for exoserial msgs on {args.socket}:{args.port}.")
    if args.socket and args.port:
        l = Listener(mode, args.socket, args.port, logdir)
