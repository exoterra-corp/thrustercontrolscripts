#!/usr/bin/python3
import canopen, argparse, struct, time, sys, socket, traceback, datetime
import serial
from serial.tools import list_ports
from threading import Thread, Lock
from os.path import exists
from src.mr_logger import MrLogger, LogType
from src.config_manager import ConfigManager
from src.hsi_defines import TCS, HSIDefines

"""
ExoTerra Resource Thruster Command Script.
description:
Allows Communications (Queries and Writes) with the Engine System Controller - Thruster Command Sections over Serial.

contact:
joshua.meyers@exoterracorp.com 
jeremy.mitchell@exoterracorp.com
"""

class ThrusterCommand:
    """
    ThrusterCommand,
    Contains function definitions for communicating with the ecp, and definitions on what indexes and sub-idxs to
    communicate with.
    """

    def __init__(self, ecp_id, ser_port, eds_file, listen_mode, debug, test_name):
        """
        __init__, sets up serial port and cmds definitions and launches the help menu.
        """
        self.th_command_index = "ThrusterCommand"
        self.trace_msg_index = "Trace"
        self.debug = debug
        self.test_name = test_name
        self.raw_q = None
        #setup classes
        self.conf_man = ConfigManager()
        self.mr_logger = MrLogger(self.conf_man, "logs", test_name)
        self.hsi_defs = HSIDefines()
        #passed in params
        self.version = "0.0.8"
        self.serial_port = ser_port
        self.eds_file = eds_file
        # main loop control
        self.running = True
        # thread control
        self.thread_run = False
        # status console print vars
        self.status_console_thread = None
        self.status_console_run = False
        self.status_console_lock = Lock()
        self.eds = {}
        self.system_id = ecp_id
        self.node = None
        self.nmt_state = None
        self.listen_thread = None
        self.write_mutex = Lock()
        self.nmt_state_str = ""
        self.listen_mode = listen_mode
        self.mode_status = 0
        self.state_status = 0
        self.thruster_status = 0
        self.thruster_status_parsed = 0
        self.bit_status = 0
        self.cond_status = 0
        self.thrust_point = 0
        self.bootup_msg = False

        #read default config variables
        self.udp_enable = self.conf_man.get("DEFAULT", "UDP_ENABLE", bool)
        self.status_console_print_delay = self.conf_man.get("DEFAULT", "STATUS_CONSOLE_PRINT_DELAY", int)
        self.mode_status_subindex = self.conf_man.get("DEFAULT", "MODE_STATUS_SUBINDEX")
        self.state_status_subindex = self.conf_man.get("DEFAULT", "STATE_STATUS_SUBINDEX")
        self.thruster_status_subindex = self.conf_man.get("DEFAULT", "THRUSTER_STATUS_SUBINDEX")
        self.condition_status_subindex = self.conf_man.get("DEFAULT", "CONDITION_STATUS_SUBINDEX")
        self.thrust_point_subindex = self.conf_man.get("DEFAULT", "THRUST_POINT_SUBINDEX")
        self.bit_status_subindex = self.conf_man.get("DEFAULT","BIT_STATUS_SUBINDEX")

        #read trace config variables
        self.trace_udp_ip = self.conf_man.get("TRACE", "TRACE_UDP_IP")
        self.trace_udp_port = self.conf_man.get("TRACE", "TRACE_UDP_PORT", int)
        self.trace_sleep_time = self.conf_man.get("TRACE", "TRACE_SLEEP_TIME", int)
        self.trace_msg_max_gather = self.conf_man.get("TRACE", "TRACE_MSG_MAX_GATHER", int)

        #read hsi config variables
        self.hsi_status_ip = self.conf_man.get("HSI", "HSI_STATUS_IP")
        self.hsi_block_udp_port = self.conf_man.get("HSI", "HSI_BLOCK_UDP_PORT", int)
        self.hsi_sleep_time = self.conf_man.get("HSI", "HSI_SLEEP_TIME", int)

        #read raw config variables
        self.raw_udp_ip = self.conf_man.get("RAW", "RAW_UDP_IP")
        self.raw_udp_port = self.conf_man.get("RAW", "RAW_UDP_PORT", int)

        self.hsi_cmds = {
            "0": {"name": "Exit", "func": self.exit, "help": "Exits the Program"},
            "1": {"name": "Help", "func": self.help, "help": "Displays the help Menu"},
            "2": {"name": "NMT STATE INIT", "func": self.change_nmt_state,
                  "args": {"nmt_state": "INIT"},
                  "help": "Changes NMT STATE to INIT."},
            "3": {"name": "NMT STATE PRE-OP", "func": self.change_nmt_state,
                  "args": {"nmt_state": "PREOPERATIONAL"},
                  "help": "Changes NMT STATE to PRE-OP."},
            "4": {"name": "NMT STATE OPERATIONAL", "func": self.change_nmt_state,
                  "args": {"nmt_state": "OPERATIONAL"},
                  "help": "Changes NMT STATE to OPERATIONAL."},
            "5": {"name": "Run Ready Mode", "func": self.get_write_value,
                  "args": {"index": self.th_command_index, "subindex": "Ready Mode", "type": "<I", "default": "0x1"},
                  "help": "Writes a UINT-32 to the Thruster Ready Mode."},
            "6": {"name": "Run Steady State", "func": self.get_write_value,
                  "args": {"index": self.th_command_index, "subindex": "Steady State", "type": "<I"},
                  "help": "Writes a UINT-32 to the Thruster Steady State."},
            "7": {"name": "Thruster Shutdown", "func": self.get_write_value,
                  "args": {"index": self.th_command_index, "subindex": "Shutdown", "type": "<B", "default": "0x1"},
                  "help": "Shutdown down the thruster."},
            "8": {"name": "Status", "func": self.get_status_index,
                  "args": {"index": self.th_command_index},
                  "help": "Prints Status of Ready Mode, Steady State, and ThrusterStatus continuously."},
            "9": {"name": "Write Set Thrust", "func": self.get_write_value,
                  "args": {"index": self.th_command_index, "subindex": "Thrust", "type": "<I"},
                  "help": "Writes a throttle set point to the System Controller."},
            "10": {"name": "Condition", "func": self.get_write_value,
                   "args": {"index": self.th_command_index, "subindex": "Condition", "type": "<I"},
                   "help": "Run the conditioning sequence."},
            "11": {"name": "Test", "func": self.get_write_value,
                   "args": {"index": self.th_command_index, "subindex": "BIT", "type": "<I"},
                   "help": "Run the BIT sequence."},
            "12": {"name": "Query Block HSI", "func": self.query_block_hsi,
                   "args": {"index": 0x3100, "subindex": 0x1, "type": "<I"},
                   "help": "Queries the HSI values using a block transfer"},
        }
        self.trace_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # trace port
        self.hsi_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # hsi port
        self.help(None)
        self.connect_to_ecp()

    def print_conditoning_stats(self, args):
        index = args.get("index")
        subindex = args.get("subindex")

        count = self.read(index, subindex, "<B", True)
        step = self.read(index, 0x1, "<I", True)
        step_status = self.read(index, 0x2, "<I", True)
        print(count)
        r = int(count/3)
        for v in range(0, r):
            seq_stat_cond = hex(self.read(index, 0x4 + v, "<I", True))
            elapsed_ms = self.read(index, 0x5 + v, "<I", True)
            monitor_err = hex(self.read(index, 0x6 + v, "<I", True))
            print(f"[{v}] seq_stat_cond-{seq_stat_cond}, elapsed_ms-{elapsed_ms}, monitor_err-{monitor_err}")

    def connect_to_ecp(self):
        """
        connect_to_ecp, sets up the serial interface with exoserial and adds the node to the network.
        """
        try:
            self.network = canopen.Network()
            if self.serial_port == "can":
                if self.debug:
                    self.mr_logger.log(LogType.SYS, "Selected can network type")
                self.network.connect(bustype='pcan', channel='PCAN_USBBUS1', bitrate=1000000)  # 1MHZ
            else:
                if self.debug:
                    self.mr_logger.log(LogType.SYS, "Selected serial network type")
                try:
                    self.network.connect(bustype="exoserial", channel=self.serial_port, baudrate=115200)
                except serial.SerialException as e:
                    print(f"{e}")
                    sys.exit(1)
            self.node = self.network.add_node(self.system_id, self.eds_file)
            self.network.add_node(self.node)
            self.raw_q = self.node.network.bus.get_int_q()
            self.mr_logger.set_raw_queue(self.raw_q)
            self.node.sdo.RESPONSE_TIMEOUT = 2
            self.node.emcy.add_callback(self.handle_emcy)
            self.network.subscribe(0x722, self.notify_bootup)

            # check to see if device is connected
            attemps = 0
            while self.nmt_state is None and attemps < 3:
                self.nmt_state = self.read(self.th_command_index, self.thruster_status_subindex, "<I")
                attemps += 1
            # check to see if msg was recieved
            if self.nmt_state is None:
                self.mr_logger.log(LogType.SYS, "System Controller Failed to Connect.  Waiting for bootup msg.")
                while not self.bootup_msg:
                    time.sleep(0.01)
                self.mr_logger.log(LogType.SYS, "System Controller Connected!")

            # read the state on bootup
            self.get_status(self.th_command_index)
            cur_state = ""
            if self.nmt_state is not None:
                self.notify_updated_state(self.nmt_state)
                if self.nmt_state == 0x2:  # preop state
                    cur_state = "Pre Operational"
                    self.start_threads()
                elif self.nmt_state >= 0x7 or self.nmt_state == 0x3:
                    cur_state = "Operational"
                    self.start_threads()
                elif self.nmt_state == 0x1:
                    cur_state = "Bootup - Init"
                self.nmt_state_str = cur_state
                self.mr_logger.log(LogType.SYS, "System Controller Connected!")

        except Exception as a:
            self.mr_logger.log(LogType.SYS, traceback.print_exc())

    def notify_bootup(self, can_id, data, timestamp):
        self.bootup_msg = True

    def get_var(self, index_str, subindex_str) -> {}:
        """
        get_var takes in a str index and subindex and returns an int index and subindex.
        """
        index = None
        subindex = None
        try:
            var = self.node.object_dictionary.get_variable(index_str, subindex_str)
            if var is None:
                self.mr_logger.log(LogType.SYS,
                                   f"Error Not found.  Check if {index_str} and {subindex_str} are in the eds file.")
            else:
                index = var.index
                subindex = var.subindex
        except KeyError as e:
            self.mr_logger.log(LogType.SYS, f"{traceback.print_exc()} {e}")
        return {"index": index, "subindex": subindex}

    def notify_updated_state(self, state):
        """
        notify_updated_state, when a new state is detected this function starts the scanning threads.
        """
        cur_state = "unknown"
        if state == 0x2:  # preop state
            cur_state = "Pre Operational"
            if not self.thread_run:
                self.start_threads()
        elif state >= 0x7 or state == 0x3:
            cur_state = "Operational"
            if not self.thread_run:
                self.start_threads()
        elif state == 0x1:
            cur_state = "Bootup - Init"
            self.thread_run = False
        if self.nmt_state != state:
            thruster_state_str = None
            try:
                thruster_state_str = TCS(int(self.thruster_status,16))
            except ValueError:
                None #ignore when it doesnt match
            self.mr_logger.log(LogType.SYS, f"NMT State: {cur_state} Thruster State: {thruster_state_str}")
            self.nmt_state_str = cur_state
            self.nmt_state_str = cur_state
            self.nmt_state = state

    def change_nmt_state(self, args):
        """
        change_nmt_state, is called by the NmtMaster callback when the state changes.
        """
        if self.debug:
            self.mr_logger.log(LogType.SYS, "Thread Stopped")
        state = args.get("nmt_state")
        if state == "OPERATIONAL":
            self.mr_logger.log(LogType.SYS, "Switching State Operational")
            self.node.nmt.send_command(0x1)
            self.start_threads()
        elif state == "PREOPERATIONAL":
            self.mr_logger.log(LogType.SYS, "Switching State Pre-Operational")
            self.node.nmt.send_command(0x80)
            self.start_threads()
        elif state == "INIT":
            self.mr_logger.log(LogType.SYS, "Switching State Init")
            self.node.nmt.send_command(0x81)
        elif state == "STOP":
            self.mr_logger.log(LogType.SYS, "Switching State Stop")
            self.thread_run = False
            self.node.nmt.send_command(0x2)

    def handle_emcy(self, error):
        """
        handle_emcy, on emcy msg this function prints the error to console and udp port
        """
        message = f"EMCYTimestamp: {error.timestamp}, EMCYCode: {error.code}," \
                  f" EMCYData: 0x{error.data.hex()}"


        self.send_udp_packet(message, self.trace_udp_ip, self.trace_udp_port)
        self.mr_logger.log(LogType.SYS, message)

    def read_cond_values(self, args):
        index = args.get("index")
        subindex = args.get("subindex")

        #get the count
        cnt = self.read(index,subindex,python_type="<B")
        for i in range(1, cnt):
            val = self.read(index, subindex+i, python_type="<I")
            print(hex(val))

    def get_status_index(self, args):
        """
        get_status_index, gets the status and checks to make sure that the threads are enabled if operational.
        """
        index = args.get("index")
        noprint = args.get("noprint")
        statuses = self.get_status(index, noprint)
        if statuses[2] >= '0x7':
            self.start_threads()

        self.status_console_lock.acquire()
        if not self.status_console_run:
            time.sleep(1)
            self.status_console_run = True
            self.status_console_thread = Thread(target=self.status_thread)
            self.status_console_thread.start()
            self.mr_logger.log(LogType.SYS, "status console print enabled!")
            self.mr_logger.log(LogType.SYS, "8 to disable status console print.")
        else:
            self.status_console_run = False
            self.mr_logger.log(LogType.SYS, "status console print disabled!")
        self.status_console_lock.release()

    def get_status(self, index, noprint=False):
        """
        get_status, this function provides more direct access to the status variables.
        """
        mode_status = self.read(index, self.mode_status_subindex, "<I")
        state_status = self.read(index, self.state_status_subindex, "<I")
        self.thruster_status_parsed = self.read(index, self.thruster_status_subindex, "<I")
        cond_status = self.read(index, self.condition_status_subindex, "<I")
        thrust_point = self.read(index, self.thrust_point_subindex, "<I")
        bit_status = self.read(index, self.bit_status_subindex, "<I")

        if mode_status == None:
            mode_status = 0
        if state_status == None:
            state_status = 0
        if self.thruster_status_parsed == None:
            self.thruster_status_parsed = 0
        if cond_status == None:
            cond_status = 0
        if thrust_point == None:
            thrust_point = 0
        if bit_status == None:
            bit_status = 0

        self.mode_status = hex(mode_status)
        self.state_status = hex(state_status)
        self.thruster_status = hex(self.thruster_status_parsed)
        self.cond_status = hex(cond_status)
        self.thrust_point = hex(thrust_point)
        self.bit_status = hex(bit_status)

        msg = f"Ready Mode: {self.mode_status}: Steady State: {self.state_status}: ThrusterStatus:{self.thruster_status} Condition Status:{self.cond_status} Thrust Point:{self.thrust_point}  Bit Status: {self.bit_status}"
        if noprint is True:
            msg = f"Ready Mode: {self.mode_status}: Steady State: {self.state_status}: ThrusterStatus:{self.thruster_status}:  Bit Status: {self.bit_status} "
            # self.send_udp_packet(msg, STATUS_UDP_IP, STATUS_UDP_PORT)
        else:
            self.mr_logger.log(LogType.SYS, msg)
        return (self.mode_status, self.state_status, self.thruster_status)

    def status_thread(self):
        """
        status_thread, continually reads the status and updates the variable.
        """
        while getattr(self, "status_console_run"):
            self.status_console_lock.acquire()
            status = self.get_status(self.th_command_index, False)
            self.status_console_lock.release()
            time.sleep(self.status_console_print_delay)

    def gather_status_and_trace(self):
        """
        gather_status_and_trace, gathers hsi and trace messages by calling functions and sends udp, runs in a thread.
        """
        if self.debug:
            self.mr_logger.log(LogType.SYS, "Starting Query Thread")
        while getattr(self, "thread_run"):
            if self.nmt_state != "Stopped":
                statuses = self.get_status(self.th_command_index, True)
                if statuses[2] is not None:
                    try:
                        self.notify_updated_state(int(statuses[2], 16))
                        self.get_trace_msg()
                        self.get_block_hsi()
                    except Exception as e:
                        self.mr_logger.log(LogType.SYS, f"{e}", )
            time.sleep(self.trace_sleep_time)

    def get_block_hsi(self):
        """
        get_block_hsi, gets hsi data and sends it out for parsing.
        """
        data = self.node.sdo.upload(0x3100, 0x1)
        #save it to the log file
        self.mr_logger.log(LogType.HSI, f"{data}")
        self.trace_sock.sendto(data, (self.hsi_status_ip, self.hsi_block_udp_port))

    def query_block_hsi(self, args):
        """
        query_block_hsi, reads and prints the hsi to the console
        """
        index = args.get("index")
        subindex = args.get("subindex")
        try:
            # loop through it once generate the string and then loop over it again to print it out
            parse_str = "<"
            for v in self.hsi_defs.block_hsi:
                parse_str += v.get("type").replace("<", "")
            data = self.node.sdo.upload(index, subindex)
            # if len(data) % 2 == 0:
            raw_vals = struct.unpack_from(parse_str, data)
            for i,value in enumerate(self.hsi_defs.block_hsi):
                name = value.get("name")
                hex_en = value.get("hex")
                parsed_val = raw_vals[i]
                if hex_en:
                    parsed_val = hex(parsed_val)
                self.mr_logger.log(LogType.SYS,f"{name} - {parsed_val}")
            else:
                self.mr_logger.log(LogType.SYS, f"Cant parse the bytearray because its not divisable by 2.  Len Data: {len(data)}")
        except canopen.sdo.exceptions.SdoCommunicationError as comms_err: \
                self.mr_logger.log(LogType.SYS,f"Query Failed: {comms_err}")
        except canopen.sdo.exceptions.SdoAbortedError as aborted_err: \
                self.mr_logger.log(LogType.SYS,f"Query Failed: {aborted_err}")
        except Exception as e:
            self.mr_logger.log(LogType.SYS,f"Query Failed: {e}")

    def start_threads(self):
        """
        start_threads, starts 2 gather threads for trace and hsi messages.
        """
        if not self.thread_run:
            if self.debug:
                self.mr_logger.log(LogType.SYS, f"Starting Trace / Status thread. Sending HSI to {self.hsi_status_ip}:{self.hsi_block_udp_port}.")
            self.thread_run = True
            self.listen_thread = Thread(target=self.gather_status_and_trace, daemon=True)
            self.listen_thread.start()

    def get_write_value(self, args):
        """
        get_write_value, looks for a default value and if one is found just writes it, otherwise its prompts the user
        for a hex value to write.
        """
        index = args.get("index")
        subindex = args.get("subindex")
        python_type = args.get("type")
        default = args.get("default")

        if type(index) is str and type(subindex) is str:
            var = self.get_var(index, subindex)
            index = var.get("index")
            subindex = var.get("subindex")

        valid = False
        if index != None and subindex != None and python_type != None:
            if default is not None:  # if we have a default value just write it and dont prompt user.
                self.write(index, subindex, default, python_type)
            else:
                while not valid:
                    self.mr_logger.log(LogType.SYS,
                                       "Enter hex value to send to ECP - or 'x' to return to previous menu.")
                    inp = input("write> 0x")
                    if inp.lower() == "back" or inp.lower() == "x":
                        return
                    if len(inp) > 0:
                        self.write(index, subindex, inp, python_type)
                        valid = True

    def write(self, index, subindex, val, python_type):
        """
        write, uses a index, subindex, and a type to ask for a hex value and then send this data over serial to the
        Engine System Controller.
        """
        try:
            self.write_mutex.acquire()
            if self.nmt_state != 0x4:  # check to see if stopped
                int_val = int(val, 16)
                val = struct.pack(python_type, int_val)
                self.node.sdo.download(index, subindex,
                                       bytearray(val))
                self.mr_logger.log(LogType.SYS, f"Wrote:{hex(index)}-{hex(subindex)}: 0x{val.hex()}")
        except struct.error as e:
            self.mr_logger.log(LogType.SYS, f"{e}")
        except canopen.sdo.exceptions.SdoCommunicationError as comms_err:
            self.mr_logger.log(LogType.SYS, f"Write Failed: {comms_err}")
        except canopen.sdo.exceptions.SdoAbortedError as aborted_err:
            self.mr_logger.log(LogType.SYS, f"Write Failed: {aborted_err}")
        except Exception as e:
            self.mr_logger.log(LogType.SYS, f"Write Failed: {e}")
        finally:
            self.write_mutex.release()

    def query(self, args):
        """
        query, uses a index, subindex to read the field from the Engine System Controller and print it in hex.
        """
        index = args.get("index")
        subindex = args.get("subindex")

        # get var from eds file
        in_val = self.read(index, subindex, "<I")
        self.mr_logger.log(LogType.SYS, f"Query:{hex(index)}-{hex(subindex)}: {hex(in_val)}")

    def read(self, index, subindex, python_type, show_failure=True):
        if type(index) is str and type(subindex) is str:
            var = self.get_var(index, subindex)
            index = var.get("index")
            subindex = var.get("subindex")
        inp = ""
        valid = False
        if index != None and subindex != None:
            try:
                self.write_mutex.acquire()
                if self.nmt_state != 0x4:  # check to see if stopped
                    val = self.node.sdo.upload(index, subindex)
                    in_val = val
                    if python_type != "noparse":
                        in_val = struct.unpack(python_type, val)[0]
                    return in_val
            except canopen.sdo.exceptions.SdoCommunicationError as comms_err:
                if show_failure:
                    self.mr_logger.log(LogType.SYS, f"Query Failed {hex(index)}:{hex(subindex)}: {comms_err}")
            except canopen.sdo.exceptions.SdoAbortedError as aborted_err:
                if show_failure:
                    self.mr_logger.log(LogType.SYS, f"Query Failed {hex(index)}:{hex(subindex)}: {aborted_err}")
            except Exception as e:
                if show_failure:
                    self.mr_logger.log(LogType.SYS, f"Query Failed {hex(index)}:{hex(subindex)}: {e}")
            finally:
                self.write_mutex.release()
        else:
            self.mr_logger.log(LogType.SYS, f"Error with args to write function, check index - {index} and subindex - {subindex}")
        return None

    def get_trace_msg(self):
        """
            get_trace_msg, gets a trace msg by first looking at the head and the tail to see if there is one to get.
            if the head and the tail are == then there are no messages just return.
        """
        try:
            for i in range(0, self.trace_msg_max_gather):
                # msg = self.read(self.trace_msg_index, TRACE_MSG_SUBINDEX, "noparse", False)
                msg = self.node.sdo.upload(0x5001, 0x6)
                if msg is not None:
                    self.mr_logger.log(LogType.TRACE, msg)
                    self.send_udp_packet(msg, self.trace_udp_ip, self.trace_udp_port)
        except Exception as e:
            # ran out of msgs to get
            None

    def send_udp_packet(self, msg, ip, port):
        """send_udp_packet, sends a packet locally and to a specified other network host as well."""
        now = datetime.datetime.now()
        time_string = now.strftime("%Y_%m_%d_%H_%M_%S.%f")
        msg = f"{time_string}:{msg}".strip()
        if ip != "127.0.0.1":
            self.trace_sock.sendto(bytes(msg, "ascii"), ("127.0.0.1", port))  # redirect local as well
        self.trace_sock.sendto(bytes(msg, "ascii"), (ip, port))

    def console(self):
        """
        console, reads input from the user and matches it to the predefined cmds, if one is found its executed.
        """
        while self.running:
            try:
                var_str = f"[rm:{self.mode_status}:ss:{self.state_status}:ts:{self.thruster_status}]".zfill(10)
                self.mr_logger.log(LogType.SYS, f"{var_str}>", end='', print_val=False)
                inp = input(f"{var_str}>").lower().strip()
                self.mr_logger.log(LogType.SYS, f"{inp}", end='', print_val=False)
                if inp in self.hsi_cmds.keys():
                    cmd = self.hsi_cmds.get(inp)
                    func = cmd.get("func")
                    args = cmd.get("args")
                    name = cmd.get("name")
                    if func != None:
                        self.mr_logger.log(LogType.SYS,f"{name}")
                        try:
                            func(args)
                        except Exception as e:
                            self.mr_logger.log(LogType.SYS,f"{e}")
            except KeyboardInterrupt as e:
                self.exit(None)

    def help(self, args):
        """
        help, reads the predefined cmds and prints them in a table.
        """
        self.mr_logger.log(LogType.SYS, "============= ExoTerra Thruster Command Help Menu =============")
        for v in self.hsi_cmds:
            x = self.hsi_cmds.get(v)
            self.mr_logger.log(LogType.SYS, f"{v} - {x.get('name')} : [{x.get('help')}]")

    def exit(self, args):
        """
        exit, exits the program.
        """
        self.mr_logger.close()
        self.thread_run = False
        self.running = False
        self.node.sdo.abort() #abort the last message
        self.network.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Controls and Queries the Thruster Command on the Engine System Control Processor.')
    parser.add_argument('serial_port', action='store', type=str,
                        help='The Serial Port to use for RS485, or use can to select the pcan',
                        default="/dev/ttyUSB0")
    parser.add_argument('system_id', action='store', type=str, help='The System Id for the connection usually 0x22.',
                        default=0x22)
    parser.add_argument('eds_file', action='store', type=str, help='The eds file used for communication.',
                        default="eds_file.eds")
    parser.add_argument('--listen', action='store', type=str, help='sends requests to udp port.')
    parser.add_argument('--debug', action='store_true', help='enable debug mode.')
    parser.add_argument('--hsi', action='store', help='Overrides localhost hsi target.', default="127.0.0.1")
    parser.add_argument('--testname', action='store',
                        help='Overwrites the default log file name and puts the log data in its own folder.')
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
    if args.debug:
        valid = True
    if not valid:
        print("Serial Port Not Found")
        print("Available Serial Ports:")
        for p in ports:
            print(p.name)
    # look for eds file
    elif not exists(args.eds_file):
        print(f"EDS file {args.eds_file} not found.")
    else:
        listen_mode = False
        debug = False
        if args.listen:
            listen_mode = True
        if args.debug:
            debug = True
        if args.hsi:
            HSI_UDP_IP = args.hsi
        if args.testname is None:
            args.testname = "unnamed_test_"
        thrus_cmd = ThrusterCommand(id, args.serial_port, args.eds_file, listen_mode, debug, args.testname)
        try:
            thrus_cmd.console()
        except Exception as e:
            print(traceback.print_exc())
