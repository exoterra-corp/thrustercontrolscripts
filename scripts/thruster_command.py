#!/usr/bin/python3
import canopen, argparse, struct, time, sys, socket, traceback, datetime, wx
from canopen.nmt import NmtError, NMT_STATES
from os.path import exists
from serial.tools import list_ports
from threading import Thread, Lock

"""
ExoTerra Resource Thruster Command Script.
description:
Allows Communications (Queries and Writes) with the Engine System Controller - Thruster Command Sections over Serial.

contact:
joshua.meyers@exoterracorp.com 
jeremy.mitchell@exoterracorp.com
"""

# TUNEABLES
STATUS_UDP_IP = "127.0.0.1"
HSI_UDP_IP = "127.0.0.1"
STATUS_UDP_PORT = 4002
UDP_HSI_PORT = 4001
TRACE_SLEEP_TIME = 0
HSI_SLEEP_TIME = 0
TRACE_MSG_GATHER_CNT = 10
STATUS_CONSOLE_PRINT_DELAY = 1

MODE_STATUS_SUBINDEX = "ReadyMode"
STATE_STATUS_SUBINDEX = "SteadyState"
THRUSTER_STATUS_SUBINDEX = "Status"
CONDITION_STATUS_SUBINDEX = "Condition"
THRUST_POINT_SUBINDEX = "Thrust"
TRACE_MSG_SUBINDEX = "TraceMessageTail"
BIT_STATUS_SUBINDEX = "BIT"

class ThrusterCommand:
    """
    ThrusterCommand,
    Contains function definitions for communicating with the ecp, and definitions on what indexes and sub-idxs to
    communicate with.
    """

    def __init__(self, ecp_id, ser_port, eds_file, listen_mode, debug):
        """
        __init__, sets up serial port and cmds definitions and launches the help menu.
        """
        self.keeper_index = "KeeperDiag"
        self.anode_index = "AnodeDiag"
        self.mag_outer_index = "MagnetOuterDiag"
        self.mag_inner_index = "MagnetInnerDiag"
        self.valves_index = "ValveDiag"
        self.hk_index = "HKDiag"
        self.th_command_index = "ThrusterCommand"
        self.trace_msg_index = "Trace"

        self.debug = debug
        self.version = "0.0.6"
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

        self.hsi = {
            "k_vsepic": {"index": self.keeper_index, "subindex": "ADC0", "row": 1, "col": 0x0},
            "k_vin": {"index": self.keeper_index, "subindex": "ADC1", "row": 1, "col": 0x1},
            "k_iout": {"index": self.keeper_index, "subindex": "ADC2", "row": 1, "col": 0x2},
            "k_dacout": {"index": self.keeper_index, "subindex": "ADC3", "row": 1, "col": 0x3},
            "k_lasterr": {"index": self.keeper_index, "subindex": "ADC4", "row": 1, "col": 0x4},
            "k_cur_oft": {"index": self.keeper_index, "subindex": "ADC5", "row": 1, "col": 0x5},
            "k_msg_cnt": {"index": self.keeper_index, "subindex": "ADC6", "row": 1, "col": 0x6},
            "k_can_err": {"index": self.keeper_index, "subindex": "ADC7", "row": 1, "col": 0x7},

            "a_vx": {"index": self.anode_index, "subindex": "ADC0", "row": 4, "col": 0x0},
            "a_vy": {"index": self.anode_index, "subindex": "ADC1", "row": 4, "col": 0x1},
            "a_vout": {"index": self.anode_index, "subindex": "ADC2", "row": 4, "col": 0x2},
            "a_iout": {"index": self.anode_index, "subindex": "ADC3", "row": 4, "col": 0x3},
            "a_dac": {"index": self.anode_index, "subindex": "ADC4", "row": 4, "col": 0x4},
            "a_last_err": {"index": self.anode_index, "subindex": "ADC5", "row": 4, "col": 0x5},
            "a_cur_oft": {"index": self.anode_index, "subindex": "ADC6", "row": 4, "col": 0x6},
            "a_hs_temp": {"index": self.anode_index, "subindex": "ADC7", "row": 4, "col": 0x7},
            "a_msg_cnt": {"index": self.anode_index, "subindex": "ADC8", "row": 4, "col": 0x8},
            "a_can_err": {"index": self.anode_index, "subindex": "ADC9", "row": 4, "col": 0x9},

            "mo_vout": {"index": self.mag_inner_index, "subindex": "ADC0", "row": 7, "col": 0},
            "mo_iout": {"index": self.mag_inner_index, "subindex": "ADC1", "row": 7, "col": 1},
            "mo_dac_out": {"index": self.mag_inner_index, "subindex": "ADC2", "row": 7, "col": 2},
            "mo_last_err": {"index": self.mag_inner_index, "subindex": "ADC3", "row": 7, "col": 3},
            "mo_msg_cnt": {"index": self.mag_inner_index, "subindex": "ADC4", "row": 7, "col": 4},
            "mo_can_err": {"index": self.mag_inner_index, "subindex": "ADC5", "row": 7, "col": 5},

            "mi_vout": {"index": self.mag_outer_index, "subindex": "ADC0", "row": 10, "col": 0},
            "mi_iout": {"index": self.mag_outer_index, "subindex": "ADC1", "row": 10, "col": 1},
            "mi_dac_out": {"index": self.mag_outer_index, "subindex": "ADC2", "row": 10, "col": 2},
            "mi_last_err": {"index": self.mag_outer_index, "subindex": "ADC3", "row": 10, "col": 3},
            "mi_msg_cnt": {"index": self.mag_outer_index, "subindex": "ADC4", "row": 10, "col": 4},
            "mi_can_err": {"index": self.mag_outer_index, "subindex": "ADC5", "row": 10, "col": 5},

            "vo_anode_v": {"index": self.valves_index, "subindex": "ADC0", "row": 13, "col": 0x0},
            "vo_cath_hf_v": {"index": self.valves_index, "subindex": "ADC1", "row": 13, "col": 0x1},
            "vo_cath_lf_v": {"index": self.valves_index, "subindex": "ADC2", "row": 13, "col": 0x2},
            "vo_temp": {"index": self.valves_index, "subindex": "ADC3", "row": 13, "col": 0x3},
            "vo_tank_pressure": {"index": self.valves_index, "subindex": "ADC4", "row": 13, "col": 0x4},
            "vo_cathode_pressure": {"index": self.valves_index, "subindex": "ADC5", "row": 13, "col": 0x5},
            "vo_anode_pressure": {"index": self.valves_index, "subindex": "ADC6", "row": 13, "col": 0x6},
            "vo_reg_pressure": {"index": self.valves_index, "subindex": "ADC7", "row": 13, "col": 0x7},
            "vo_msg_cnt": {"index": self.valves_index, "subindex": "ADC8", "row": 13, "col": 0x8},
            "vo_can_err": {"index": self.valves_index, "subindex": "ADC9", "row": 13, "col": 0x9},

            "hk_current_28v": {"index": self.hk_index, "subindex": "ADC0", "row": 16, "col": 0x0},
            "hk_sense_14v": {"index": self.hk_index, "subindex": "ADC1", "row": 16, "col": 0x1},
            "hk_current_14v": {"index": self.hk_index, "subindex": "ADC2", "row": 16, "col": 0x2},
            "hk_sense_7a": {"index": self.hk_index, "subindex": "ADC3", "row": 16, "col": 0x3},
            "hk_current_7a": {"index": self.hk_index, "subindex": "ADC4", "row": 16, "col": 0x4},
        }

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
        self.bit_status = 0
        self.cond_status = 0
        self.thrust_point = 0

        self.bootup_msg = False
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
                  "args": {"index": self.th_command_index, "subindex": "ReadyMode", "type": "<I", "default": "0x1"},
                  "help": "Writes a UINT-32 to the Thruster Ready Mode."},
            "6": {"name": "Run Steady State", "func": self.get_write_value,
                  "args": {"index": self.th_command_index, "subindex": "SteadyState", "type": "<I"},
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
        }
        self.trace_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # trace port
        self.hsi_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # hsi port
        self.help(None)
        self.connect_to_ecp()

    def connect_to_ecp(self):
        """
        connect_to_ecp, sets up the serial interface with exoserial and adds the node to the network.
        """
        try:
            self.network = canopen.Network()
            if self.serial_port == "can":
                if self.debug:
                    print("Selected can network type")
                self.network.connect(bustype='pcan', channel='PCAN_USBBUS1', bitrate=1000000)  # 1MHZ
            else:
                if self.debug:
                    print("Selected serial network type")
                self.network.connect(bustype="exoserial", channel=self.serial_port, baudrate=115200)
            self.node = self.network.add_node(self.system_id, self.eds_file)
            self.network.add_node(self.node)
            self.node.sdo.RESPONSE_TIMEOUT = 2
            self.node.emcy.add_callback(self.handle_emcy)
            self.network.subscribe(0x722, self.notify_bootup)
            # check to see if device is connected
            self.nmt_state = self.read(self.th_command_index, THRUSTER_STATUS_SUBINDEX, "<I")  # nmt_state
            #check to see if msg was recieved
            if self.nmt_state is None:
                print("System Controller Failed to Connect.  Waiting for bootup msg.")
                while not self.bootup_msg:
                    time.sleep(0.01)
                print("System Controller Connected!")
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
                print("System Controller Connected!")

        except Exception as a:
            print(traceback.print_exc())

    def notify_bootup(self, can_id, data, timestamp):
        self.bootup_msg = True

    def load_eds_file(self):
        """
        load_eds_file, gathers all of the eds objects
        """
        for obj in self.node.object_dictionary.values():
            print('0x%X: %s' % (obj.index, obj.name))
            if isinstance(obj, canopen.objectdictionary.Record):
                for subobj in obj.values():
                    print('  %d: %s' % (subobj.subindex, subobj.name))

    def get_var(self, index_str, subindex_str) -> {}:
        """
        get_var takes in a str index and subindex and returns an int index and subindex.
        """
        index = None
        subindex = None
        try:
            var = self.node.object_dictionary.get_variable(index_str, subindex_str)
            if var is None:
                print(f"Error Not found.  Check if {index_str} and {subindex_str} are in the eds file.")
            else:
                index = var.index
                subindex = var.subindex
        except KeyError as e:
            print(e)
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
            print(f"Updated State: {cur_state}")
            self.nmt_state_str = cur_state
            self.nmt_state = state

    def change_nmt_state(self, args):
        """
        change_nmt_state, is called by the NmtMaster callback when the state changes.
        """
        if self.debug:
            print("Thread Stopped")
        state = args.get("nmt_state")
        if state == "OPERATIONAL":
            print("Switching State Operational")
            self.node.nmt.send_command(0x1)
            self.start_threads()
        elif state == "PREOPERATIONAL":
            print("Switching State Pre-Operational")
            self.node.nmt.send_command(0x80)
            self.start_threads()
        elif state == "INIT":
            print("Switching State Init")
            self.node.nmt.send_command(0x81)
        elif state == "STOP":
            print("Switching State Stop")
            self.thread_run = False
            self.node.nmt.send_command(0x2)

    def handle_emcy(self, error):
        """
        handle_emcy, on emcy msg this function prints the error to console and udp port
        """
        message = f"EMCYTimestamp: {error.timestamp}, EMCYCode: {error.code}," \
                  f" EMCYData: {error.data}"
        self.send_udp_packet(message, STATUS_UDP_IP, STATUS_UDP_PORT)
        print(message)

    def get_status_index(self, args):
        """
        get_status_index, gets the status and checks to make sure that the threads are enabled if operational.
        """
        index = args.get("index")
        noprint = args.get("noprint")
        statuses = self.get_status(index, noprint)
        if statuses[2] >= '0x7':
            self.start_threads()

        print(f"8 to enable / disable console status print")
        self.status_console_lock.acquire()
        if not self.status_console_run:
            time.sleep(1)
            self.status_console_run = True
            self.status_console_thread = Thread(target=self.status_thread)
            self.status_console_thread.start()
        else:
            self.status_console_run = False
        self.status_console_lock.release()

    def get_status(self, index, noprint=False):
        """
        get_status, this function provides more direct access to the status variables.
        """
        mode_status = self.read(index, MODE_STATUS_SUBINDEX, "<I")
        state_status = self.read(index, STATE_STATUS_SUBINDEX, "<I")
        thruster_status = self.read(index, THRUSTER_STATUS_SUBINDEX, "<I")
        cond_status = self.read(index, CONDITION_STATUS_SUBINDEX, "<I")
        thrust_point = self.read(index, THRUST_POINT_SUBINDEX, "<I")
        bit_status = self.read(index, BIT_STATUS_SUBINDEX, "<I")

        if mode_status == None:
            mode_status = 0
        if state_status == None:
            state_status = 0
        if thruster_status == None:
            thruster_status = 0
        if cond_status == None:
            cond_status = 0
        if thrust_point == None:
            thrust_point = 0
        if bit_status == None:
            bit_status = 0

        self.mode_status = hex(mode_status)
        self.state_status = hex(state_status)
        self.thruster_status = hex(thruster_status)
        self.cond_status = hex(cond_status)
        self.thrust_point = hex(thrust_point)
        self.bit_status = hex(bit_status)

        msg = f"Ready Mode: {self.mode_status}: Steady State: {self.state_status}: ThrusterStatus:{self.thruster_status} Condition Status:{self.cond_status} Thrust Point:{self.thrust_point}  Bit Status: {self.bit_status}"
        if noprint is True:
            msg = f"Ready Mode: {self.mode_status}: Steady State: {self.state_status}: ThrusterStatus:{self.thruster_status}:  Bit Status: {self.bit_status} "
            # self.send_udp_packet(msg, STATUS_UDP_IP, STATUS_UDP_PORT)
        else:
            print(msg)

        return (self.mode_status, self.state_status, self.thruster_status)

    def status_thread(self):
        """
        status_thread, continually reads the status and updates the variable.
        """
        while getattr(self, "status_console_run"):
            self.status_console_lock.acquire()
            status = self.get_status(self.th_command_index, False)
            self.status_console_lock.release()
            time.sleep(STATUS_CONSOLE_PRINT_DELAY)

    def gather_status_and_trace(self):
        """
        gather_status_and_trace, gathers hsi and trace messages by calling functions and sends udp, runs in a thread.
        """
        if self.debug:
            print("Starting Query Thread")
        while getattr(self, "thread_run"):
            if self.nmt_state != "Stopped":
                statuses = self.get_status(self.th_command_index, True)
                if statuses[2] is not None:
                    self.notify_updated_state(int(statuses[2], 16))
                    self.get_trace_msg()
                    self.gather_hsi_msgs()
            time.sleep(TRACE_SLEEP_TIME)

    def gather_hsi_msgs(self):
        """
        gather_hsi_msgs, this gathers hsi messages and sends it over udp, runs in thread.
        """
        for a in self.hsi.items():
            #if in pre-op ignore other hsi messages
            item_name = a[0]
            if self.state_status == '0x0' and "hk" not in item_name:
                continue
            item_name = a[0]
            index = a[1].get("index")
            subindex = a[1].get("subindex")
            val = self.read(index, subindex, "<H")
            var = self.get_var(index, subindex)
            if val is not None:
                msg = f"{item_name.ljust(10, ' ')}:index:{hex(var.get('index'))}:subindex:{hex(var.get('subindex'))}:val:{val}"
                self.send_udp_packet(msg, HSI_UDP_IP, UDP_HSI_PORT)
        time.sleep(HSI_SLEEP_TIME)

    def start_threads(self):
        """
        start_threads, starts 2 gather threads for trace and hsi messages.
        """
        if not self.thread_run:
            if self.debug:
                print(f"Starting Trace / Status thread. Sending HSI to {HSI_UDP_IP}:{UDP_HSI_PORT}.")
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
                    print("Enter hex value to send to ECP - or 'x' to return to previous menu.")
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
                print({f"Wrote:{hex(index)}-{hex(subindex)}: 0x{val.hex()}"})
        except struct.error as e:
            print(e)
        except canopen.sdo.exceptions.SdoCommunicationError as comms_err:
            print(f"Write Failed: {comms_err}")
        except canopen.sdo.exceptions.SdoAbortedError as aborted_err:
            print(f"Write Failed: {aborted_err}")
        except Exception as e:
            print(f"Write Failed: {e}")
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
        print({f"Query:{hex(index)}-{hex(subindex)}: {hex(in_val)}"})

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
                    print(f"Query Failed {hex(index)}:{hex(subindex)}: {comms_err}")
            except canopen.sdo.exceptions.SdoAbortedError as aborted_err:
                if show_failure:
                    print(f"Query Failed {hex(index)}:{hex(subindex)}: {aborted_err}")
            except Exception as e:
                if show_failure:
                    print(f"Query Failed {hex(index)}:{hex(subindex)}: {e}")
            finally:
                self.write_mutex.release()
        else:
            print("Error with args to write function, check index and subindex")
        return None

    def get_trace_msg(self):
        """
            get_trace_msg, gets a trace msg by first looking at the head and the tail to see if there is one to get.
            if the head and the tail are == then there are no messages just return.
        """
        try:
            for i in range(0, TRACE_MSG_GATHER_CNT):
                msg = self.read(self.trace_msg_index, TRACE_MSG_SUBINDEX, "noparse", False)
                if msg is not None:
                    self.send_udp_packet(msg, STATUS_UDP_IP, STATUS_UDP_PORT)
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

    def help(self, args):
        """
        help, reads the predefined cmds and prints them in a table.
        """
        print("============= ExoTerra Thruster Command Help Menu =============")
        for v in self.hsi_cmds:
            x = self.hsi_cmds.get(v)
            print(f"{v} - {x.get('name')} : [{x.get('help')}]")

    def exit(self, args):
        """
        exit, exits the program.
        """
        self.thread_run = False
        self.running = False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Controls and Queries the Thruster Command on the Engine System Control Processor.')
    parser.add_argument('--listen', action='store', type=str, help='sends requests to udp port.')
    parser.add_argument('serial_port', action='store', type=str,
                        help='The Serial Port to use for RS485, or use can to select the pcan',
                        default="/dev/ttyUSB0")
    parser.add_argument('system_id', action='store', type=str, help='The System Id for the connection usually 0x22.',
                        default=0x22)
    parser.add_argument('eds_file', action='store', type=str, help='The eds file used for communication.',
                        default="eds_file.eds")
    parser.add_argument('--debug', action='store_true', help='enable debug mode.')
    parser.add_argument('--hsi', action='store', help='Overrides localhost hsi target.', default="127.0.0.1")
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
        thrus_cmd = ThrusterCommand(id, args.serial_port, args.eds_file, listen_mode, debug)
        try:
            thrus_cmd.console()
        except Exception as e:
            print(traceback.print_tb())
