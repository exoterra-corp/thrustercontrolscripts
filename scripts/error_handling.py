#!/usr/bin/python3
import canopen, argparse, struct, time, sys, socket, traceback, datetime, wx
from canopen.nmt import NmtError, NMT_STATES
from serial.tools import list_ports
from threading import Thread, Lock
from tabulate import tabulate

class ErrorHandling:
    """
    Interacts with error handling firmware
    """
    def __init__(self, id, ser_port, eds_file):
        self.running = True
        self.serial_port = ser_port
        self.system_id = id
        self.network = canopen.Network()
        if ser_port == 'can':
            self.network.connect(bustype="pcan", channel='PCAN_USBBUS1', bitrate=1000000)
        else:
            self.network.connect(bustype="exoserial", channel=self.serial_port, baudrate=115200)
        self.node = self.network.add_node(self.system_id, eds_file)
        self.network.add_node(self.node)
        self.node.sdo.RESPONSE_TIMEOUT = 2
        self.eds_file = eds_file 


        self.err_detail_cmds = {
            "0": {"name": "Quit", "func":quit, "help": "Quit Script"},
            "1": {"name": "Dump Error Log", "func":self.error_log_dump, "help": "Dump a submodules error log", "args":"submodule"},
            "2": {"name": "Change Fault Handler", "func": self.fault_handler_change, "help": "Change a fault reaction for a fault type"},
            "3": {"name": "Dump Fault Handler Configs", "func": self.fault_handler_config_dump, "help": "Dumps fault handler configured for each error code"},
            "4": {"name": "Dump Fault Status", "func": self.fault_reaction_status_dump, "help": "Dump fault reaction status variable"}
        }

        self.submodules = {
                "0" : {"name":"Serial", "index": self.node.object_dictionary['ErrorDetail'].index, "subindex": self.node.object_dictionary['ErrorDetail']['SerialSubmodule'].subindex},
                "1" : {"name":"Client Control", "index": self.node.object_dictionary['ErrorDetail'].index, "subindex": self.node.object_dictionary['ErrorDetail']['ClientControlSubmodule'].subindex},
                "2" : {"name":"Anode Control", "index": self.node.object_dictionary['ErrorDetail'].index, "subindex": self.node.object_dictionary['ErrorDetail']['AnodeControl'].subindex},
                "3" : {"name":"Magnet Control", "index": self.node.object_dictionary['ErrorDetail'].index, "subindex": self.node.object_dictionary['ErrorDetail']['MagnetControl'].subindex},
                "4" : {"name":"Memory Scrubber", "index": self.node.object_dictionary['ErrorDetail'].index, "subindex": self.node.object_dictionary['ErrorDetail']['MemoryScrubberSubmodule'].subindex},
                "5" : {"name":"APP", "index": self.node.object_dictionary['ErrorDetail'].index, "subindex": self.node.object_dictionary['ErrorDetail']['AppSubmodule'].subindex},
                
        }

    def pretty_text(self, data, heading, formatting):
        if len(data)%2 == 0:
            parsed_vals = []
            if formatting == "<I":
                bites = 4
            elif formatting == "<c":
                bites = 1
            elif formatting == "<h":
                bites = 2
            vals = [data[i:i + bites] for i in range(0, len(data), bites)]
            for i,v in enumerate(vals):
                h = struct.unpack(formatting, v)[0]
                name =''
                if formatting == "<c":
                    h = int.from_bytes(h, "little")
                val = (f"{hex(int(str(i).zfill(2)))}: 0x{hex(h)[2:].zfill(bites*2)}")
                parsed_vals.append([name,val])
            print(tabulate(parsed_vals, [heading]))


    def error_log_dump(self): 
        inp = ""
        while inp != 'b':
            print("Enter submodule to dump error log or 'b' to go back:")
            for it in self.submodules.keys():
                print(it, self.submodules[it]["name"])

            inp = input(">> ")
            if inp in self.submodules.keys():
                print(self.submodules[inp]["name"])
                index = self.submodules[inp]["index"]
                subindex = self.submodules[inp]["subindex"]
                data = self.node.sdo.upload(index, subindex)
                self.pretty_text(data, "ERROR", "<I")


    def fault_handler_change(self):
        inp = ""
        while inp != 'b':
            print("Enter 'c' to read/write Error Code fault handler error codes, 'd' to dump current fault configurations or 'b' to go back:")
            inp = input(">>" )
            print(inp)
            if(inp != 'b'):
                if(inp == 'd'):
                    self.fault_handler_config_dump()
                elif(inp == 'c'):
                    print("Enter 'w fs fh' to write new fault config or 'r fs' to read fault config:")
                    inp = input(">>>" )                   
                    index_fault_code_select = self.node.object_dictionary['FaultReactionType'].index
                    subindex_fault_code_select = self.node.object_dictionary['FaultReactionType']['FaultCodeSelect'].subindex
                    index_fault_reaction_type = self.node.object_dictionary['FaultReactionType'].index
                    subindex_fault_reaction_type = self.node.object_dictionary['FaultReactionType']['FaultReactionType'].subindex
                    inp = inp.split(' ')
                    cmd = inp[0]
                    if(cmd == 'w'):
                        fault_select = bytearray([int(inp[1])])
                        fault_reaction_type = bytearray([int(inp[2])])
                        val = self.node.sdo.download(index_fault_code_select, subindex_fault_code_select, fault_select)
                        val = self.node.sdo.download(index_fault_reaction_type, subindex_fault_reaction_type, fault_reaction_type)
                    elif(cmd == 'r'):
                        fault_select = bytearray([int(inp[1])])
                        val = self.node.sdo.download(index_fault_code_select, subindex_fault_code_select, fault_select)
                        code = self.node.sdo.upload(index_fault_code_select, subindex_fault_code_select)
                        fh   = self.node.sdo.upload(index_fault_reaction_type, subindex_fault_reaction_type)
                        print("fault code = ", code, ", handler = ", fh)                         

    def fault_reaction_status_dump(self):
        print("Enter 'd' to dump fault configs, or 'w x (x = 1,2,3,4,5)' to dump fault status words.")
        inp = input(">")
        inp = inp.split(' ')
        if(inp[0] == 'd'):
            print("Dumping Fault Configurations...")
            index = self.node.object_dictionary['FaultStatus'].index,
            subindex = self.node.object_dictionary['FaultStatus']['FaultStatus'].subindex,
            val = self.node.sdo.upload(index[0], subindex[0])
            self.pretty_text(val, "Fault Status", "<I")

        elif(inp[0] == 'w'):
            index = self.node.object_dictionary['FaultStatus'].index,
            subindex = self.node.object_dictionary['FaultStatus'][int(inp[1]) + 1].subindex,
            print(index, subindex)
            val = self.node.sdo.upload(index[0], subindex[0])
            print("status word ", inp[1], "= ", val) 

    def fault_handler_config_dump(self):
        print("Dumping Fault Status...")
        index = self.node.object_dictionary['FaultStatus'].index,
        subindex = self.node.object_dictionary['FaultStatus']['FaultStatus'].subindex,
        val = self.node.sdo.upload(index[0], subindex[0])
        self.pretty_text(val, "FAULT_CONFIG", "<c") 

    def help(self):
        """
        help, reads the predefined cmds and prints them in a table.
        """
        print("============= ExoTerra Error Handling Help Menu =============")
        for v in self.err_detail_cmds:
            x = self.err_detail_cmds.get(v)
            print(f"{v} - {x.get('name')} : [{x.get('help')}]")

    def console(self):
        """
        console, reads input from the user and matches it to the predefined cmds, if one is found its executed.
        """
        while self.running:
            try:
                self.help()
                inp = input(f"> ").lower().strip()
                if inp in self.err_detail_cmds.keys():
                    cmd = self.err_detail_cmds.get(inp)
                    func = cmd.get("func")
                    name = cmd.get("name")
                    if func != None:
                        print(f"{name}")
                        try:
                            func()
                        except Exception as e:
                            print(e)
            except KeyboardInterrupt as e:
                sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Dumps Module Specific Error Logs, and Configures Fault Handlers')
    parser.add_argument('--action', action='store', type=str, help='dump module error log or configure fault handling')
    parser.add_argument('serial_port', action='store', type=str, help='The Serial Port to use for RS485, or use can to select the pcan', default="/dev/ttyUSB0")
    parser.add_argument('system_id', action='store', type=str, help='The System Id for the connection usually 0x22.', default=0x22)
    parser.add_argument('--debug', action='store_true', help='enable debug mode.')
    parser.add_argument('eds_file', action='store', type=str, help='The eds file used for communication.',
                        default="eds_file.eds")
    args = parser.parse_args()

    print("============= ExoTerra Error Handling =============")
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
