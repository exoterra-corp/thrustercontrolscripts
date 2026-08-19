#!/usr/bin/python3
import canopen, argparse, struct, time, sys, socket, traceback, datetime, operator
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
jmitchell@exoterra.com
"""

class ThrusterCommand:
    """
    ThrusterCommand,
    Contains function definitions for communicating with the ecp, and definitions on what indexes and sub-idxs to
    communicate with.
    """

    def __init__(self, ecp_id, ser_port, eds_file, listen_mode, debug, test_name, telem_en, half_duplex):
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
        self.version = "0.0.9"
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
        self.thread_lock = Lock()
        self.telem_en = telem_en
        self.half_duplex = half_duplex

        #read default config variables
        self.udp_enable = True
        self.status_console_print_delay = 1
        self.mode_status_subindex = "ReadyMode"
        self.state_status_subindex = "SteadyState"
        self.thruster_status_subindex = "Status"
        self.condition_status_subindex = "Condition"
        self.thrust_point_subindex = "Thrust"
        self.bit_status_subindex = "BIT"

        #read trace config variables
        self.trace_udp_ip = "127.0.0.1"
        self.trace_udp_port = 4002
        self.trace_sleep_time = 0
        self.trace_msg_max_gather = 2

        #read hsi config variables
        self.hsi_status_ip = "127.0.0.1"
        self.hsi_block_udp_port = 4001 
        self.hsi_sleep_time = 0

        #read raw config variables
        self.raw_udp_ip = "127.0.0.1"
        self.raw_udp_port = 4000

        self.hsi_cmds = {
            "0": {"name": "Exit", "func": self.exit, "help": "Exits the Program"},
            "1": {"name": "Help", "func": self.help, "help": "Displays the help Menu"},
            "2a":{"name": "NMT STATE STOPPED", "func": self.change_nmt_state,
                  "args": {"nmt_state": "STOP"},
                  "help": "Changes NMT STATE to STOP."},
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
                  "args": {"index": self.th_command_index, "subindex": "ReadyMode", "type": "<I", "default": "1"},
                  "help": "Writes a UINT-32 to the Thruster Ready Mode."},
            "6": {"name": "Run Steady State", "func": self.get_write_value,
                  "args": {"index": self.th_command_index, "subindex": "SteadyState", "type": "<I"},
                  "help": "Writes a UINT-32 to the Thruster Steady State."},
            "7": {"name": "Thruster Shutdown", "func": self.get_write_value,
                  "args": {"index": self.th_command_index, "subindex": "Shutdown", "type": "<B", "default": "1"},
                  "help": "Shutdown down the thruster."},
            "8": {"name": "Status", "func": self.get_status_index,
                  "args": {"index": self.th_command_index},
                  "help": "Prints Status of Ready Mode, Steady State, and ThrusterStatus continuously."},
            "9": {"name": "Write Set Thrust", "func": self.get_write_value,
                  "args": {"index": self.th_command_index, "subindex": "Thrust", "type": "<I", "hex_en": False},
                  "help": "Writes a throttle set point to the System Controller."},
            "10": {"name": "Condition", "func": self.get_write_value,
                   "args": {"index": self.th_command_index, "subindex": "Condition", "type": "<I"},
                   "help": "Run the conditioning sequence."},
            "11": {"name": "Test", "func": self.get_write_value,
                   "args": {"index": self.th_command_index, "subindex": "BIT", "type": "<I"},
                   "help": "Run the BIT sequence."},
            "12": {"name": "Query Block HSI", "func": self.query_block_hsi,
                   "args": {"index": 0x3100, "subindex": 0x1, "type": "<I"},
                   "help": "Queries the HSI values using a segmented transfer"},
            "13": {"name": "Read Fault Status", "func": self.read_fault_status,
                   "args": {"index": 0x2831, "subindex": 0x1, "type": "<I"},
                   "help": "Read the Error Stats."},
            "15": {"name": "Print Stats", "func": self.print_conditoning_stats,
                   "args": {"index": 0x4001, "subindex": 0x0, "type": "<I", "default": "1"},
                   "help": "Reset Conditioning Stats."},
            "16":  {"name": "Soft Starter Kit", "func": self.run_soft_start,
                   "args": {"index": 0x4000, "subindex": 0x2, "type": "<I", "default": "1"},
                   "help": "Attempt a soft start(TM)."},
            "17": {"name": "Run Auto Start", "func": self.get_write_value,
                   "args": {"index": self.th_command_index, "subindex": "AutoStart", "type": "<I"},
                   "help": "Writes a UINT-32 to the Thruster Auto Start."},
            "18": {"name": "Classic/Soft Start Select ", "func": self.classic_start_enable,
                   "args": {"index": self.th_command_index, "subindex": "AutoStart", "type": "<I"},
                   "help": "Writes a UINT-32 to the Thruster Auto Start."}       
        }
        self.trace_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # trace port
        self.hsi_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # hsi port
        self.help(None)
        self.connect_to_ecp()
        self.abort_ignition = False

    def classic_start_enable(self, args):
        psi = 0
        index = 0x4002
        subindex = 0x10
        val = self.node.sdo.upload(index, subindex)
        in_val = int.from_bytes(val, "little")
        print("\n\n+++ Which ignition method would you like to use? +++");
        print("currently configured: ",  "Classic Start" if  in_val == 0 else "Soft Start")
        select = input("1 = Soft Start    2 = Classic Start>" )
        if select == "1":
            psi = input("Enter soft start increment in PSI: ")
        psi = int(float(psi) * 1000)

        msg = "Enable Classic Start"
        if psi != 0:
            msg = "Enable Soft Start with increment: " 
        setpoint = psi   
        setpoint_payload = bytearray(struct.pack("<I", setpoint))
        print(msg, setpoint, "(mpsi)")
        print("\njust a moment...")
        self.node.sdo.download(index, subindex, setpoint_payload)
        val = self.node.sdo.upload(index, subindex)
        in_val = int.from_bytes(val, "little")        
        if in_val == setpoint:
            print("\nIgnition Method Enabled! written: ", setpoint, " read: ", in_val, "\n\n")
            print("\n")
            good_1 = 1
        else:
            print("\nIgnition method Enable Failed!: written: ", setpoint, " read: ", in_val, "\n\n");

    def run_soft_start(self, args):
        print("\n\nHello you talented and good looking operator ;)\n\n")  
        time.sleep(1) 
        print("\nThis is a script that will help you perform a soft start(TM) and enable the keeper when attempting a 'bolstered ignition'(TM pending).\n\n")
        valid = False
        index = 0
        subindex = 0
        limit_value = 0
        sleep_time = 1
        self.abort_ignition = False
        while not valid:
            print("Enable Lightning mode? (faster prompting and updates)")
            print("+++ It is recommened to disable lightning mode on first use +++")
            lightning_mode = input("y/n> ")
            if lightning_mode.lower() == "back":
                return
            if lightning_mode.lower() == "y":
                sleep_time = 0
                valid = True
            elif lightning_mode.lower() == "n":
                valid = True
                sleep_time = 1
            else:
                print("\n 'y' or 'n' you goose") 

        valid = False
        index = 0
        subindex = 0
        limit_value = 0
        while not valid:
            print("Enter setpoint number to edit: (example: setpoint> 2 to edit setpoint 2)")
            setpoint = input("setpoint> ")
            if setpoint.lower() == "back":
                return
            if len(setpoint) > 0 and int(setpoint) > 0 and int(setpoint) <= 10:
                valid = True
                good = 0
                index = 0x4002
                subindex = 2
                setpoint = int(setpoint)
                setpoint_payload = bytearray(struct.pack("<I", setpoint))
                print("setting setpoint: ... ", setpoint_payload)
                print("\nwait for it...")
                self.node.sdo.download(index, subindex, setpoint_payload)
                time.sleep(sleep_time)
                val = self.node.sdo.upload(index, subindex)
                in_val = int.from_bytes(val, "little")        
                if in_val == setpoint:
                    print("\nsetpoint set successfully! setpoint written: ", setpoint, "setpoint read: ", in_val, "\n\n")
                    print("nice\n")
                    good_1 = 1
                else:
                    print("setpoint set failed: setpoint written: ", setpoint, "setpoint read: ", in_val);
            else:
                print("\n!!!!!! invalid setpoint: ", setpoint) 
                print("!!!!!! setpoint must be >0 and <= 10\n")

        valid = False
        while not valid:
            print("enter anode pressure step size as a decimal to the tenths place (example: anode pressure step> 1.5 for 1.5 PSI step size): - or 'back' to return to main menu.")
            anode_pressure_step = input("anode pressure step> ")
            if anode_pressure_step.lower() == "back":
                return
            if len(anode_pressure_step) > 0 and float(anode_pressure_step) > 0.0 and float(anode_pressure_step) < 5.0:
                valid = True
                index = 0x4002
                subindex = 4
                anode_pressure_step = float(anode_pressure_step)
                aps_payload = bytearray(struct.pack("<f", anode_pressure_step))
                print("\n\nsetting anode pressure: ... ", aps_payload)
                print("\nwait for it...")
                self.node.sdo.download(index, subindex, aps_payload)
                time.sleep(sleep_time)
                val = self.node.sdo.upload(index, subindex)
                in_val = struct.unpack('<f', val)      
                if round(in_val[0], 1) == round(anode_pressure_step, 1):
                    print("anode pressure set successfully! pressure written: ", anode_pressure_step, "pressure read: ", in_val[0])
                    print("\n\nsick dude\n")
                    good_2 = 1
                else:
                    print("anode pressure set failed: anode pressure written: ", anode_pressure_step, "anode pressure read: ", in_val[0]);
            else:
                print("\n!!!!!! invalid pressure step: ", anode_pressure_step) 
                print("!!!!!! pressure step must be >0.0 and <= 5.0\n")
       

        valid = False
        while not valid:
            print("\n\nWould you like to bolster your ignition today?")
            bolstered_ignition = input("turn keeper on at ignition? 'y' or 'n'> ")
            if bolstered_ignition.lower() == "back":
                return
            if bolstered_ignition.lower() == "y" or bolstered_ignition.lower() == "n":
                valid = True
                print("right on\n")
            else:
                print("\n I said 'y' or 'n' you goose\n") 
        time.sleep(sleep_time) 
        print("+++ One order of soft start to setpoint ", setpoint, " with an anode pressure step size = ", anode_pressure_step, " and a bolstered ignition ('", bolstered_ignition, "') coming right up... +++\n")
        time.sleep(sleep_time)
        valid = False
        if good_1 == 1 and good_2 == 1:
            while not valid:
                print("\n\nsay when...")
                print("enter 'y' to attempt the softstart - or 'back' to return to main menu.")
                go = input("punch it? > ")
                if go.lower() == "back":
                    return
                if go.lower() == "y":
                    valid = True
                else:
                    print("I said 'y' or 'back' you goose")
        else:
            print("\n!!!!!!! something went wrong, see the above error messages or contact Ben: 720 243 1744 !!!!!!")
            
        if valid:
            time.sleep(sleep_time)
            print("\nIn the words of the great Rick Moranis...\n")
            time.sleep(sleep_time)
            print("\n\nLUDICROUS SPEED!!\n\n\n") 
            time.sleep(sleep_time)
            print("GO!!!!!\n\n")
            time.sleep(sleep_time + 1)
            self.soft_start_go(setpoint, anode_pressure_step, bolstered_ignition)

    
    def abort_thread(self):
        inpt = input("\n\n\n +++ You can abort the ignition at any time by entering any key stroke +++ \n\n\n")

        if inpt or inpt == '':
            self.abort_ignition = True

    def soft_start_go(self, setpoint, anode_pressure_step_size, bolstered_ignition):
            print("sofstart go") 
            anode_ps = anode_pressure_step_size
            ignition_stable = 0
            abort_thread = Thread(target=self.abort_thread)
            abort_thread.start()

            if bolstered_ignition.lower() == "y" or bolstered_ignition.lower() == "n":
                print("bolstering ignition initializing...")
                index = 0x4200 
                subindex = 4 
                #Select the Steady State Sequence:
                cmd = 1 
                cmd_payload = bytearray(struct.pack("<I", cmd))
                print(cmd_payload)
                print("select steady state")
                self.node.sdo.download(index, subindex, cmd_payload)
                #######################################################

                subindex = 5 
                #Select the 14th step of the sequence:
                #(to confirm we’re on the right step, read 0x4200, 6, should be 0x01040706 )
                cmd = 14
                cmd_payload = bytearray(struct.pack("<I", cmd))
                print(cmd_payload)
                print("select step 14")
                self.node.sdo.download(index, subindex, cmd_payload)

                if bolstered_ignition.lower() == "y":
                    ########################################################
                    subindex = 6 
 
                    cmd = 16910086 # 0x01020706 = adjust keeper current command code in sequence engine 
                    cmd_payload = bytearray(struct.pack("<I", cmd))

                    print(cmd_payload)
                    print("change sequence step to 'adjust keeper current' command code...")
                    self.node.sdo.download(index, subindex, cmd_payload)


                    ##########################################################
                    subindex = 7 
 
                    cmd =  500# 500 milli amps 
                    cmd_payload = bytearray(struct.pack("<I", cmd))
                    print(cmd_payload)
                    print("set keeper current to 500 milliamps")
                    self.node.sdo.download(index, subindex, cmd_payload)
                    ###########################################################
                    
                    time.sleep(1)

                    print("\n\n ... Keeper armed and ready ... \n\n")
                else:
                    ########################################################
                    subindex = 6 
 
                    cmd = 17041158 # 0x01040706 = turn keeper off command code 
                    cmd_payload = bytearray(struct.pack("<I", cmd))

                    print(cmd_payload)
                    print("change sequence step to 'turn keeper off' command code...")
                    self.node.sdo.download(index, subindex, cmd_payload)


                    ##########################################################
                    subindex = 7 
 
                    cmd =  0# 500 milli amps 
                    cmd_payload = bytearray(struct.pack("<I", cmd))
                    print(cmd_payload)
                    print("ignored argument")
                    self.node.sdo.download(index, subindex, cmd_payload)
                    ###########################################################
                    
                    time.sleep(1)
                    print("\n\n ... Bolstering ignition disabled ... \n\n")
            while(anode_ps < 14.0 and not ignition_stable and not self.abort_ignition):
                print("anode pressure = ", anode_ps)

                #attempt ignition
                #check state for 25 seconds
                #ignition_stable?
                #    yes: bolstering ignition?
                #           yes: edit sequence to turn keeper current to 0.5A
                #           no:  edit sequence to turn keeper off 
                #    no: take it to the top 
                index = 0x4002
                subindex = 4
                
                aps_payload = bytearray(struct.pack("<f", anode_ps))
                print("\n\nsetting anode pressure: ... ", aps_payload)
                print("\nwait for it...")
                self.node.sdo.download(index, subindex, aps_payload)
                time.sleep(1)
                val = self.node.sdo.upload(index, subindex)
                in_val = struct.unpack('<f', val)      
                if round(in_val[0], 1) == round(anode_ps, 1):
                    print("anode pressure set successfully! pressure written: ", anode_ps, "pressure read: ", in_val[0], "\n\n")
                else:
                    print("anode pressure set failed: anode pressure written: ", anode_ps, "anode pressure read: ", in_val[0], "\n\n");

                index = 0x4000
                subindex = 2
                cmd=1 # does nothing
                cmd_payload = bytearray(struct.pack("<I", cmd))
                print(cmd_payload)
                self.node.sdo.download(index, subindex, cmd_payload)
                time.sleep(3)

                print("================= Ignition attempt at ", anode_ps, " PSI ===================")
                subindex = 5
                val = self.node.sdo.upload(index, subindex)
                in_val = int.from_bytes(val, "little")
                while in_val == 11 and self.abort_ignition == False:
                    index = 0x4000 
                    subindex = 5 
                    val = self.node.sdo.upload(index, subindex)
                    in_val = int.from_bytes(val, "little") 
                    # 0xB = 11 = transitioning to steady state
                    if in_val == 11:
                        print("thruster state is: transitioning to steady state...")
                    # 0xC = 12 = steady state
                    if in_val == 12:
                        print("thruster state is: steady state")
                        time.sleep(1)
                        print("Houston, we have successful ignition \n\n")
                        ignition_stable = 1
                        break
                    # 0xAC = 172 - steady state with keeper on
                    if in_val == 172:
                        print("thruster state is: steady state, and that KEEPER IS ON BABY!!")
                        time.sleep(1)
                        print("Houston, we have successful bolstered ignition \n\n")
                        ignition_stable = 1
                        break
                    # 0xA = 10 - ready mode
                    if in_val == 10:
                        print("ignition timed out")
                        time.sleep(1)
                        ignition_stable = 0
                        break
                    time.sleep(2)


                anode_ps += anode_pressure_step_size
                time.sleep(1)
            if not ignition_stable:
                print("\n\nLooks like that didn't work, you may need to refine your search to a smaller anode pressure step size")
            if not ignition_stable or self.abort_ignition == True:
                print("\n\nDon't Give Up! Lighting a thruster is a bit about probabilities, but I won't tell you the odds you swashbuckling space pirate\n\n")

            
    def print_conditoning_stats(self, args):
        """
        print_conditoning_stats, 
        """
        index = args.get("index")
        subindex = args.get("subindex")

             
        count = self.read(index, subindex, "<B", True)
        step = self.read(index, 0x1, "<I", True)
        step_status = self.read(index, 0x2, "<I", True)
        self.mr_logger.log(LogType.SYS, count)
        r = int(count/3)
        for v in range(0, r-1):
            seq_stat_cond = self.read(index, 0x2 + (v*3), "<I", True)
            elapsed_ms = self.read(index, 0x3 + (v*3), "<I", True)
            monitor_err = self.read(index, 0x4 + (v*3), "<I", True)
            seq_stat_cond = '0x' + hex(seq_stat_cond)[2:].zfill(8)
            monitor_err = '0x' + hex(monitor_err)[2:].zfill(8)
            self.mr_logger.log(LogType.SYS, f"[{v}] seq_stat_cond-{seq_stat_cond}, elapsed_ms-{elapsed_ms}, monitor_err-{monitor_err}")

        print("Erase Conditioning Stats?")
        erase = input("y/n> ")
        if erase == "y":
            print("Are you sure?..")
            erase = input("y/n> ")       
        if erase == "y":
            val = struct.pack("<I", 0x63637772)
            #Write to conditioning clear CANopen object (0x5401, 1)
            self.node.sdo.download(0x4000, 8,
                                       bytearray(val))
            print("Erasing Conditioning Stats...")

            count = self.read(index, subindex, "<B", True)
            step = self.read(index, 0x1, "<I", True)
            step_status = self.read(index, 0x2, "<I", True)
            self.mr_logger.log(LogType.SYS, count)
            r = int(count/3)
            for v in range(0, r-1):
                seq_stat_cond = self.read(index, 0x2 + (v*3), "<I", True)
                elapsed_ms = self.read(index, 0x3 + (v*3), "<I", True)
                monitor_err = self.read(index, 0x4 + (v*3), "<I", True)
                seq_stat_cond = '0x' + hex(seq_stat_cond)[2:].zfill(8)
                monitor_err = '0x' + hex(monitor_err)[2:].zfill(8)
                self.mr_logger.log(LogType.SYS, f"[{v}] seq_stat_cond-{seq_stat_cond}, elapsed_ms-{elapsed_ms}, monitor_err-{monitor_err}")

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
                    self.mr_logger.log(LogType.SYS, f"{e}")
                    sys.exit(1)
            self.node = self.network.add_node(self.system_id, self.eds_file)
            self.network.add_node(self.node)
            if self.serial_port != "can":
                self.raw_q = self.node.network.bus.get_int_q()
                self.mr_logger.set_raw_queue(self.raw_q)
            self.node.sdo.RESPONSE_TIMEOUT = 5 
            self.node.emcy.add_callback(self.handle_emcy)
            self.network.subscribe(0x722, self.notify_bootup)

            # activate half duplex mode if specified
            if self.half_duplex:
                try:
                    self.network.bus.half_duplex_mode()
                except AttributeError:
                    self.mr_logger.log(LogType.SYS, "The installed version of python-can does not support half-duplex ExoSerialCan connections")

            # check to see if device is connected
            attempts = 0
            while self.nmt_state is None and attempts < 3:
                self.nmt_state = self.read(self.th_command_index, self.thruster_status_subindex, "<I")
                attempts += 1

            # check to see if msg was recieved
            if self.nmt_state is None:
                self.mr_logger.log(LogType.SYS, "System Controller Failed to Connect.")
                if self.half_duplex:
                    # Failed connection is fatal in half-duplex mode
                    self.mr_logger.log(LogType.SYS, "Exiting...")
                    time.sleep(2)
                    exit(1)
                else:
                    # Wait for bootup message if running full-duplex
                    self.mr_logger.log(LogType.SYS, "Waiting for bootup message.")
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
                # self.read_serial_number()
                self.mr_logger.log(LogType.SYS, "System Controller Connected!")
        except KeyboardInterrupt:
            exit(0)
        except Exception as a:
            self.mr_logger.log(LogType.SYS, traceback.print_exc())

    def notify_bootup(self, can_id, data, timestamp):
        self.bootup_msg = True

    def get_var(self, index_str, subindex_str):
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
        # self.thread_lock.acquire()
        state = args.get("nmt_state")
        if state == "OPERATIONAL":
            self.mr_logger.log(LogType.SYS, "Switching State Operational")
            self.node.nmt.send_command(0x1)
            # self.wait_for_thruster_state(TCS.TCS_STANDBY)
        elif state == "PREOPERATIONAL":
            self.mr_logger.log(LogType.SYS, "Switching State Pre-Operational")
            self.node.nmt.send_command(0x80)
            # self.wait_for_thruster_state(TCS.TCS_CO_PREOP)
        elif state == "INIT":
            self.mr_logger.log(LogType.SYS, "Switching State Init")
            self.node.nmt.send_command(0x81)
            # self.wait_for_thruster_state(TCS.TCS_CO_PREOP)
        elif state == "STOP":
            self.mr_logger.log(LogType.SYS, "Switching State Stop")
            self.thread_run = False
            self.node.nmt.send_command(0x2)
        # self.thread_lock.release()
        self.start_threads()

    def read_fault_status(self, args):
        faults = []
        for i in range(0,5):
            subidx = 2+i
            val = self.read(0x2831, subidx, "<I")
            self.mr_logger.log(LogType.SYS, f"{i}:{hex(val)}")
            faults.append(val)
        return faults

    def wait_for_thruster_state(self, tcs_state:TCS, log_state=True, max_delay=20, poll_time=1):
        """blocks until the correct thruster state is returned or the max delay is hit

        Args:
            tcs_state (TCS): the desired thruster state to look for.
            log_state (bool, optional): will print the status of each read to the log !noisy!. Defaults to True.
            max_delay (int, optional): the max amount of reads before the function exits ~15 seconds. Defaults to 15.
            poll_time (int, optional): how fast to query the ecp for thruster state changes in seconds.
        """
        success = True
        current_state = 0
        cnt = 0
        comp = operator.is_not #default comparison unless in operational
        if TCS.TCS_STANDBY:
            comp = operator.gt
        while comp(tcs_state.value,current_state) and cnt <= max_delay:
            #query the unit, thrustercommand, status
            current_state = self.read(0x4000, 0x5, "<I")
            if current_state is None:
                current_state = TCS.TCS_CO_INVALID.value #set to invalid state if we don't know what it is
            # if log_state:
                # self.mr_logger.log(LogType.SYS,f"desired thruster_state: {tcs_state.value}, current_state: {current_state}")
            cnt+=1
            time.sleep(poll_time)

        #check to make sure we didn't timeout, if we did return an error
        if cnt >= max_delay:
            success = False
        return success        

    def handle_emcy(self, emgcy_error):
        """
        handle_emcy, on emcy msg this function prints the error to console and udp port
        """
        message = f"EMCYTimestamp: {emgcy_error.timestamp}, EMCYCode: {emgcy_error.code}," \
                  f" EMCYData: 0x{emgcy_error.data.hex()}"

        code = hex(emgcy_error.code)
        #parse data from emgcy msg data section
        error_type = None
        fault_code = None
        line_num = None
        error_cnt = None
        data = emgcy_error.data.hex()
        if len(data) == 10:
            self.mr_logger.log(LogType.SYS,"EMERGENCY MESSAGE")
            try:
                line_in_bytes = bytes.fromhex(data[4:8])
                line_num = struct.unpack("<H", line_in_bytes)[0]
            except ValueError as e:
                self.mr_logger.log(LogType.SYS,e)
            error_type = data[0:2]
            fault_code = data[2:4]
            error_cnt = data[9:10]
        reg = hex(emgcy_error.register)
        time = emgcy_error.timestamp

        self.mr_logger.log(LogType.SYS,f"Error Type: {error_type}")
        self.mr_logger.log(LogType.SYS,f"Fault Code: {fault_code}")
        self.mr_logger.log(LogType.SYS,f"Line NO: {line_num}")
        self.mr_logger.log(LogType.SYS,f"Error Cnt: {error_cnt}")

        self.send_udp_packet(message, self.trace_udp_ip, self.trace_udp_port)
        # self.mr_logger.log(LogType.SYS, message)

    def read_cond_values(self, args):
        index = args.get("index")
        subindex = args.get("subindex")

        #get the count
        cnt = self.read(index,subindex,python_type="<B")
        for i in range(1, cnt):
            val = self.read(index, subindex+i, python_type="<I")
            self.mr_logger.log(LogType.SYS, hex(val))

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
        self.thrust_point = thrust_point
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
            # self.thread_lock.acquire()
            if self.nmt_state != "Stopped":
                statuses = self.get_status(self.th_command_index, True)
                if statuses[2] is not None:
                    try:
                      self.notify_updated_state(int(statuses[2], 16))
                      self.get_trace_msg()
                      self.get_block_hsi()
                    except Exception as e:
                        self.mr_logger.log(LogType.SYS, f"{e}", )
            # self.thread_lock.release()
            time.sleep(self.trace_sleep_time)

    def get_block_hsi(self):
        """
        get_block_hsi, gets hsi data and sends it out for parsing.
        """
        data = self.node.sdo.upload(0x3100, 0x1)
        #save it to the log file
        self.mr_logger.log(LogType.HSI, data)
        if self.hsi_status_ip != "127.0.0.1": #send it locally first
            self.trace_sock.sendto(data, ("127.0.0.1", self.hsi_block_udp_port))
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
            raw_vals = struct.unpack_from(parse_str, data)
            for i,value in enumerate(self.hsi_defs.block_hsi):
                name = value.get("name")
                hex_en = value.get("hex")
                parsed_val = raw_vals[i]
                if hex_en:
                    parsed_val = hex(parsed_val)
                self.mr_logger.log(LogType.SYS,f"{name} - {parsed_val}")
        except canopen.sdo.exceptions.SdoCommunicationError as comms_err: \
                self.mr_logger.log(LogType.SYS,f"Query Failed: {comms_err}")
        except canopen.sdo.exceptions.SdoAbortedError as aborted_err: \
                self.mr_logger.log(LogType.SYS,f"Query Failed: {aborted_err}")
        except Exception as e:
            self.mr_logger.log(LogType.SYS,f"Query Failed: {e}")
    
    def read_serial_number(self):
        """
            Reads the 128bit serial number from the NodeID index 
            and returns the hex number.  Returns None on failure.
        """
        try:
            index = 0x5022
            if index is not None:
                ser = bytearray()
                ser0 = self.read(index,2,"noparse")
                ser1 = self.read(index,3,"noparse")
                ser2 = self.read(index,4,"noparse")
                ser3 = self.read(index,5,"noparse")
                ser.extend(ser0)
                ser.extend(ser1)
                ser.extend(ser2)
                ser.extend(ser3)
                if len(ser) == 16:
                    vals = struct.unpack_from("<IIII", ser)
                    serial_num = (vals[0] << 96) | (vals[1] << 64) | (vals[2] << 32) | vals[3]
                    hex_result = hex(serial_num) 
                    self.mr_logger.log(LogType.SYS, f"Unit Serial Number: {hex_result}")
                    return hex_result
                else:
                    return None
        except Exception as e:
                    self.mr_logger.log(LogType.SYS, f"Failed to log Serial Number from the unit. {e}")

    def start_threads(self):
        """
        start_threads, starts 2 gather threads for trace and hsi messages.
        """
        if not self.thread_run:
            if self.debug:
                self.mr_logger.log(LogType.SYS, f"Starting Trace / Status thread. Sending HSI to {self.hsi_status_ip}:{self.hsi_block_udp_port}.")
            self.thread_run = True
            self.listen_thread = Thread(target=self.gather_status_and_trace, daemon=True)
            if self.telem_en:
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
        hex_en = args.get("hex_en")
        val_type_str = "decimal"

        if hex_en is not None and hex_en is not False:
            val_type_str = "hex"
            hex_en = True
        else:
            hex_en = False

        if type(index) is str and type(subindex) is str:
            var = self.get_var(index, subindex)
            index = var.get("index")
            subindex = var.get("subindex")

        valid = False
        if index != None and subindex != None and python_type != None:
            if default is not None:  # if we have a default value just write it and dont prompt user.
                self.write(index, subindex, default, python_type, hex_en)
            else:
                while not valid:
                    self.mr_logger.log(LogType.SYS, f"Enter {val_type_str} value to send to ECP - or 'x' to return to previous menu.")
                    inp = input("write> ")
                    if inp.lower() == "back" or inp.lower() == "x":
                        return
                    # filter for steady state (2) or auto start (9) commands.  If it is either of these commands, they need a duration time
                    if index == 0x4000 and subindex == 2 or subindex == 9:
                        print("set a burn duration timeout? ( 0 for no, or timeout in seconds (max 65535)):")
                        timeout = input("timeout in seconds>")
                        if timeout.lower() == "back" or timeout.lower() == "x":
                            return
                        # python "shift" of 16 bits
                        inp = str(int(inp) + (int(timeout)<<16))                     
                    if len(inp) > 0:
                        self.write(index, subindex, inp, python_type, hex_en)
                        valid = True


    def write(self, index, subindex, val, python_type, hex_en=True):
        """
        write, uses a index, subindex, and a type to ask for a hex value and then send this data over serial to the
        Engine System Controller.
        """
        try:
            self.write_mutex.acquire()
            if self.nmt_state != 0x4:  # check to see if stopped
                if hex_en:
                    int_val = int(val, 16)
                else:
                    int_val = int(val)
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
                var_str = f"[rm:{self.mode_status}:ss:{self.state_status}:tp:{self.thrust_point}:ts:{self.thruster_status}]".zfill(10)
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
    parser.add_argument('--notelem', action='store_true', help='Enable or Disable Telemetry', default="")
    parser.add_argument('--testname', action='store',
                        help='Overwrites the default log file name and puts the log data in its own folder.')
    parser.add_argument('--half-duplex', action='store_true', help='Enable Half Duplex Mode for the Exoserial CAN Bus.',)
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
        thrus_cmd = ThrusterCommand(id, args.serial_port, args.eds_file, listen_mode, debug, args.testname, not args.notelem, args.half_duplex)
        try:
            thrus_cmd.console()
        except Exception as e:
            print(traceback.print_exc())
