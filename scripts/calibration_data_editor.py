#!/usr/bin/python3
import canopen, argparse, struct, time, sys, socket, traceback, datetime
from canopen.nmt import NmtError, NMT_STATES
from serial.tools import list_ports
from threading import Thread, Lock
from tabulate import tabulate

class CalibrationData:
    def __init__(self, id, ser_port):
        self.idx = 0x5501
        self.serial_port = ser_port
        self.system_id = id
        self.network = canopen.Network()
        if ser_port == 'can':
            self.network.connect(bustype="pcan", channel='PCAN_USBBUS1', bitrate=1000000)
        else:
            self.network.connect(bustype="exoserial", channel=self.serial_port, baudrate=115200)
        self.node = self.network.add_node(self.system_id)
        self.network.add_node(self.node)
        self.node.sdo.RESPONSE_TIMEOUT = 2


        self.calibration_cmds = {
            "0": {"name": "Quit", "func":quit, "help": "Quit Script"},
            "1": {"name": "Write Calibration Offset", "func": self.rw_calibration_data,"action":"w", "what":"offset", "help": "Write Calibration Offset"},
            "2": {"name": "Read Calibration Offset", "func": self.rw_calibration_data, "action":"r", "what":"offset", "help": "Read Calibration Offset"},
            "3": {"name": "Write Calibration Scaling Factor", "func": self.rw_calibration_data, "action":"w", "what":"sf","help": "Write Calibration Scaling Factor"},
            "4": {"name": "Read Calibration Scaling Factor", "func": self.rw_calibration_data, "action":"r", "what":"sf","help": "Read Calibration Scaling Factor"},
            "5": {"name": "Erase Calibration Data", "func": self.rw_calibration_data, "action":"e", "what":"all", "help": "Erase Current Calibration Data"}
        }


    def rw_calibration_data(self, action, what):
        if what == 'offset':
            self.subidx = 2 
            self.w_msg = "enter offset in PSI (ex: 0.123) or 'b' to go back: "
            self.r_msg = "offset in PSI: "
        elif what == 'sf':
            self.subidx = 1
            self.w_msg = "enter scaling factor (ex: 0.1922) or 'b' to go back: " 
            self.r_msg = "scaling factor: " 

        if action == 'r':
            ret = self.node.sdo.upload(self.idx, self.subidx)   
            ret = struct.unpack('<f', ret)[0]
            print(self.r_msg,ret, type(ret))
        if action == 'w':
            data = input(self.w_msg)
            if data != 'b':
                data = float(data)
                data = struct.pack('<f', data)
                self.node.sdo.download(self.idx, self.subidx, data)   
                print(data)
        if action == 'e':
            data = bytearray([0xff, 0xff, 0xff, 0xff])
            self.node.sdo.download(self.idx, 1, data)   
            self.node.sdo.download(self.idx, 2, data)   
            print(data)

    def help(self):
        """
        help, reads the predefined cmds and prints them in a table.
        """
        print("============= ExoTerra Error Handling Help Menu =============")
        for v in self.calibration_cmds:
            x = self.calibration_cmds.get(v)
            print(f"{v} - {x.get('name')} : [{x.get('help')}]")


    def console(self):
        """
        console, reads input from the user and matches it to the predefined cmds, if one is found its executed.
        """
        while True:
            try:
                self.help()
                inp = input(f"> ").lower().strip()
                if inp in self.calibration_cmds.keys():
                    cmd = self.calibration_cmds.get(inp)
                    func   = cmd.get("func")
                    action = cmd.get("action")
                    what   = cmd.get("what")
                    if func != None:
                        print(f"{func}")
                        try:
                            func(action, what)
                        except Exception as e:
                            print(e)
            except KeyboardInterrupt as e:
                sys.exit(0)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Read/Write Calibration Offset and Scaling Factor')
    parser.add_argument('--action', action='store', type=str, help='dump module error log or configure fault handling')
    parser.add_argument('serial_port', action='store', type=str, help='The Serial Port to use for RS485, or use can to select the pcan', default="/dev/ttyUSB0")
    parser.add_argument('system_id', action='store', type=str, help='The System Id for the connection usually 0x22.', default=0x22)

    args = parser.parse_args()

    print("============= Calibration Data Editor =============")
    valid = False
    id = 0x22
    ports = list_ports.comports()
    if args.serial_port == "can":
        valid = True
    else:
        for p in ports:
            if args.serial_port.lower() == p.name.lower() or \
                    args.serial_port.lower() == "/dev/" + p.name.lower():
                try:
                    id = int(args.system_id, 16)
                except ValueError as e:
                    print(f"Check system_id, {args.system_id} is not a  hex number.")
                valid = True
                break
    if not valid:
        print("Serial Port Not Found")
        print("Available Serial Ports:")
        for p in ports:
            print(p.name)
    err_handler = CalibrationData(id, args.serial_port)
    err_handler.console()
