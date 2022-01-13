#!/usr/bin/python3
import canopen, argparse, struct, time, sys, socket, traceback, datetime, wx
from canopen.nmt import NmtError, NMT_STATES
from serial.tools import list_ports
from threading import Thread, Lock

class ErrorHandling:
    """
    Interacts with error handling firmware
    """
    def __init__(self, id, ser_port, eds_file):
        self.running = True
        self.serial_port = ser_port
        self.system_id = id
        self.network = canopen.Network()
        self.network.connect(bustype="exoserial", channel=self.serial_port, baudrate=115200)
        self.node = self.network.add_node(self.system_id, eds_file)
        self.network.add_node(self.node)
        self.node.sdo.RESPONSE_TIMEOUT = 2
        self.eds_file = eds_file 
        for obj in self.node.object_dictionary.values():
            print('0x%X: %s' % (obj.index, obj.name))
            if isinstance(obj, canopen.objectdictionary.Record):
                for subobj in obj.values():
                    print('  %d: %s' % (subobj.subindex, subobj.name))

        self.err_detail_cmds = {
                "0": {"name": "Dump Error Log", "func":self.error_log_dump, "help": "Dump a submodules error log", "args":"submodule"},
                "1": {"name": "Change Fault Handler", "func": self.self.fault_handler_change, "help": "Change a fault reaction for a fault type", "args":{}},
            "2": {"name": "NMT STATE INIT", "func": self.change_nmt_state,
                  "args": {"nmt_state": "INIT"},
                  "help": "Changes NMT STATE to INIT."},
            "3": {"name": "NMT STATE PRE-OP", "func": self.change_nmt_state,
                  "args": {"nmt_state": "PREOPERATIONAL"},
                  "help": "Changes NMT STATE to PRE-OP."}
        }

    def error_log_dump(self, submodule): 
        val = self.node.sdo.upload(index, subindex)

    def fault_handler_change(self, error_type, error_code, new_fault_handler):
        val = self.node.sdo.download(index, subindex, bytes(error_type, error_code, new_fault_handler))

    def fault_handler_config_dump(self):
        val = self.node.sdo.upload(index, subindex)

    def fault_reaction_status_dump(self):
        val = self.node.sdo.upload(index, subindex)

    def console(self):
        """
        console, reads input from the user and matches it to the predefined cmds, if one is found its executed.
        """
        while self.running:
            try:
                var_str = f"[rm:{self.mode_status}:ss:{self.state_status}:ts:{self.thruster_status}]".zfill(10)
                inp = input(f"{var_str}> ").lower().strip()
                if inp in self.hsi_cmds.keys():
                    cmd = self.hsi_cmds.get(inp)
                    func = cmd.get("func")
                    args = cmd.get("args")
                    name = cmd.get("name")
                    if func != None:
                        print(f"{name}")
                        try:
                            func(args)
                        except Exception as e:
                            print(e)
            except KeyboardInterrupt as e:
                sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Dumps Module Specific Error Logs, and Configures Fault Handlers')
    parser.add_argument('--action', action='store', type=str, help='dump module error log or configure fault handling')
    parser.add_argument('system_id', action='store', type=str, help='The System Id for the connection usually 0x22.',
                        default=0x22)
    parser.add_argument('serial_port', action='store', type=str, help='The Serial Port to use for RS485, or use can to select the pcan',
                        default="/dev/ttyUSB0")
    parser.add_argument('--debug', action='store_true', help='enable debug mode.')
    parser.add_argument('--hsi', action='store', help='Overrides localhost hsi target.', default="127.0.0.1")
    parser.add_argument('eds_file', action='store', type=str, help='The eds file used for communication.',
                        default="eds_file.eds")
    args = parser.parse_args()

    print("============= ExoTerra Thruster Command & Control =============")
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
    err_handler = ErrorHandling(id, args.serial_port, args.eds_file)
    err_handler.console()
