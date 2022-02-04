#!/usr/bin/python3
import canopen, argparse, struct, time, sys, socket, traceback, datetime, wx
from canopen.nmt import NmtError, NMT_STATES
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

STATUS_CONSOLE_PRINT_DELAY = 1
THRUSTER_COMMAND_INDEX = "ThrusterCommand"
TRACE_MSG_INDEX = "Trace"
MODE_STATUS_SUBINDEX = "ReadyMode"
STATE_STATUS_SUBINDEX = "SteadyState"
THRUSTER_STATUS_SUBINDEX = "Status"
CONDITION_STATUS_SUBINDEX = "Condition"
THRUST_POINT_SUBINDEX = "Thrust"
TRACE_MSG_SUBINDEX = "TraceMessageTail"
BIT_STATUS_SUBINDEX = "BIT"

TRACE_UDP_IP = "127.0.0.1"
TRACE_UDP_PORT = 4002
TRACE_SLEEP_TIME = 0
TRACE_MSG_MAX_GATHER = 2

HSI_STATUS_IP = "127.0.0.1"
HSI_UDP_PORT = 4001
HSI_BLOCK_UDP_PORT = 4003
HSI_SLEEP_TIME = 0
TRACE_MSG_GATHER_CNT = 2
STATUS_CONSOLE_PRINT_DELAY = 1

RAW_UDP_IP = "127.0.0.1"
RAW_UDP_PORT = 4000


class HSIDefs:
    def __init__(self):
        self.keeper_index = "KeeperDiag"
        self.anode_index = "AnodeDiag"
        self.mag_outer_index = "MagnetOuterDiag"
        self.mag_inner_index = "MagnetInnerDiag"
        self.valves_index = "ValveDiag"
        self.hk_index = "HKDiag"
        self.hsi = {
            "a_vx": {"index": self.anode_index, "subindex": "ADC0", "type": "<H", "row": 4, "col": 0x0},  # 32bit
            "a_vy": {"index": self.anode_index, "subindex": "ADC1", "type": "<H", "row": 4, "col": 0x1},  # 32bit
            "a_vout": {"index": self.anode_index, "subindex": "ADC2", "type": "<H", "row": 4, "col": 0x2},  # 32bit
            "a_iout": {"index": self.anode_index, "subindex": "ADC3", "type": "<H", "row": 4, "col": 0x3},
            "a_dac": {"index": self.anode_index, "subindex": "ADC4", "type": "<H", "row": 4, "col": 0x4},
            "a_hs_temp": {"index": self.anode_index, "subindex": "ADC7", "type": "<H", "row": 4, "col": 0x7},
            "a_last_err": {"index": self.anode_index, "subindex": "ADC5", "type": "<H", "row": 4, "col": 0x5},
            "a_cur_oft": {"index": self.anode_index, "subindex": "ADC6", "type": "<H", "row": 4, "col": 0x6},
            "a_msg_cnt": {"index": self.anode_index, "subindex": "ADC8", "type": "<H", "row": 4, "col": 0x8},
            "a_can_err": {"index": self.anode_index, "subindex": "ADC9", "type": "<H", "row": 4, "col": 0x9},

            "k_v_sepic": {"index": self.keeper_index, "subindex": "ADC0", "type": "<H", "row": 1, "col": 0x0},  # 32bit
            "k_v_in": {"index": self.keeper_index, "subindex": "ADC1", "type": "<H", "row": 1, "col": 0x1},  # 32bit
            "k_i_out": {"index": self.keeper_index, "subindex": "ADC2", "type": "<H", "row": 1, "col": 0x2},
            "k_dac_out": {"index": self.keeper_index, "subindex": "ADC3", "type": "<H", "row": 1, "col": 0x3},
            "k_last_err": {"index": self.keeper_index, "subindex": "ADC4", "type": "<H", "row": 1, "col": 0x4},
            "k_cur_oft": {"index": self.keeper_index, "subindex": "ADC5", "type": "<H", "row": 1, "col": 0x5},
            "k_msg_cnt": {"index": self.keeper_index, "subindex": "ADC6", "type": "<H", "row": 1, "col": 0x6},
            "k_can_err": {"index": self.keeper_index, "subindex": "ADC7", "type": "<H", "row": 1, "col": 0x7},

            "mo_v_out": {"index": self.mag_inner_index, "subindex": "ADC0", "type": "<H", "row": 7, "col": 0},
            "mo_i_out": {"index": self.mag_inner_index, "subindex": "ADC1", "type": "<H", "row": 7, "col": 1},
            "mo_dac_out": {"index": self.mag_inner_index, "subindex": "ADC2", "type": "<H", "row": 7, "col": 2},
            "mo_last_err": {"index": self.mag_inner_index, "subindex": "ADC3", "type": "<H", "row": 7, "col": 3},
            "mo_msg_cnt": {"index": self.mag_inner_index, "subindex": "ADC4", "type": "<H", "row": 7, "col": 4},
            "mo_can_err": {"index": self.mag_inner_index, "subindex": "ADC5", "type": "<H", "row": 7, "col": 5},

            "mi_v_out": {"index": self.mag_outer_index, "subindex": "ADC0", "type": "<H", "row": 10, "col": 0},
            "mi_i_out": {"index": self.mag_outer_index, "subindex": "ADC1", "type": "<H", "row": 10, "col": 1},
            "mi_dac_out": {"index": self.mag_outer_index, "subindex": "ADC2", "type": "<H", "row": 10, "col": 2},
            "mi_last_err": {"index": self.mag_outer_index, "subindex": "ADC3", "type": "<H", "row": 10, "col": 3},
            "mi_msg_cnt": {"index": self.mag_outer_index, "subindex": "ADC4", "type": "<H", "row": 10, "col": 4},
            "mi_can_err": {"index": self.mag_outer_index, "subindex": "ADC5", "type": "<H", "row": 10, "col": 5},

            "va_anode_v": {"index": self.valves_index, "subindex": "ADC0", "type": "<H", "row": 13, "col": 0},
            "va_cathode_hf_v": {"index": self.valves_index, "subindex": "ADC1", "type": "<H", "row": 13, "col": 1},
            "va_cathode_lf_v": {"index": self.valves_index, "subindex": "ADC2", "type": "<H", "row": 13, "col": 2},
            "va_temperature": {"index": self.valves_index, "subindex": "ADC3", "type": "<H", "row": 13, "col": 3},
            # signed 32bit
            "va_tank_pressure": {"index": self.valves_index, "subindex": "ADC4", "type": "<H", "row": 13, "col": 4},
            # 32bit
            "va_cathode_pressure": {"index": self.valves_index, "subindex": "ADC5", "type": "<H", "row": 13,
                                    "col": 5},
            "va_anode_pressure": {"index": self.valves_index, "subindex": "ADC6", "type": "<H", "row": 13, "col": 6},
            "va_regulator_pressure": {"index": self.valves_index, "subindex": "ADC7", "type": "<H", "row": 13, "col": 7},
            "va_msg_cnt": {"index": self.valves_index, "subindex": "ADC8", "type": "<H", "row": 13, "col": 8},
            "va_can_err": {"index": self.valves_index, "subindex": "ADC9", "type": "<H", "row": 13, "col": 9},

            "hk_mA_28V": {"index": self.hk_index, "subindex": "ADC0", "type": "<H", "row": 16, "col": 0},
            "hk_mV_14V": {"index": self.hk_index, "subindex": "ADC1", "type": "<H", "row": 16, "col": 1},
            "hk_mA_14V": {"index": self.hk_index, "subindex": "ADC2", "type": "<H", "row": 16, "col": 2},
            "hk_mV_7VA": {"index": self.hk_index, "subindex": "ADC3", "type": "<H", "row": 16, "col": 3},
            "hk_mA_7VA": {"index": self.hk_index, "subindex": "ADC4", "type": "<H", "row": 16, "col": 4},

            "count_meccemsb": {"index": self.hk_index, "subindex": "ADC0", "type": "<H", "row": 19, "col": 0},
            "count_ueccemsb": {"index": self.hk_index, "subindex": "ADC1", "type": "<H", "row": 19, "col": 1},
            "count_meccelsb": {"index": self.hk_index, "subindex": "ADC2", "type": "<H", "row": 19, "col": 2},
            "count_ueccelsb": {"index": self.hk_index, "subindex": "ADC3", "type": "<H", "row": 19, "col": 3},

            "region_stat": {"index": self.hk_index, "subindex": "ADC0", "type": "<I", "row": 22, "col": 0},
            "failed_repairs": {"index": self.hk_index, "subindex": "ADC1", "type": "<I", "row": 22, "col": 1},
            "repair_stat": {"index": self.hk_index, "subindex": "ADC2", "type": "<I", "row": 22, "col": 2},
        }
        self.block_hsi = [
            # anode
            {"name": "a_vx", "type": "<I", "hex": False},
            {"name": "a_vy", "type": "<I", "hex": False},
            {"name": "a_vout", "type": "<I", "hex": False},
            {"name": "a_iout", "type": "<H", "hex": False},
            {"name": "a_dac", "type": "<H", "hex": False},
            {"name": "a_hs_temp", "type": "<H", "hex": False},
            {"name": "a_last_err", "type": "<H", "hex": False},
            {"name": "a_cur_oft", "type": "<H", "hex": False},
            {"name": "a_msg_cnt", "type": "<H", "hex": False},
            {"name": "a_can_err", "type": "<H", "hex": False},

            # keeper
            {"name": "k_v_sepic", "type": "<I", "hex": False},
            {"name": "k_v_in", "type": "<H", "hex": False},
            {"name": "k_i_out", "type": "<H", "hex": False},
            {"name": "k_dac_out", "type": "<H", "hex": False},
            {"name": "k_last_err", "type": "<H", "hex": False},
            {"name": "k_cur_oft", "type": "<H", "hex": False},
            {"name": "k_msg_cnt", "type": "<H", "hex": False},
            {"name": "k_can_err", "type": "<H", "hex": False},

            # magnet
            {"name": "mo_v_out", "type": "<H", "hex": False},
            {"name": "mo_i_out", "type": "<H", "hex": False},
            {"name": "mo_dac_out", "type": "<H", "hex": False},
            {"name": "mo_last_err", "type": "<H", "hex": False},
            {"name": "mo_msg_cnt", "type": "<H", "hex": False},
            {"name": "mo_can_err", "type": "<H", "hex": False},

            #magnet inner
            {"name": "mi_v_out", "type": "<H", "hex": False},
            {"name": "mi_i_out", "type": "<H", "hex": False},
            {"name": "mi_dac_out", "type": "<H", "hex": False},
            {"name": "mi_last_err", "type": "<H", "hex": False},
            {"name": "mi_msg_cnt", "type": "<H", "hex": False},
            {"name": "mi_can_err", "type": "<H", "hex": False},

            # valves
            {"name": "va_anode_v", "type": "<H", "hex": False},
            {"name": "va_cathode_hf_v", "type": "<H", "hex": False},
            {"name": "va_cathode_lf_v", "type": "<H", "hex": False},
            {"name": "va_temperature", "type": "<i", "hex": False},
            {"name": "va_tank_pressure", "type": "<I", "hex": False},
            {"name": "va_cathode_pressure", "type": "<H", "hex": False},
            {"name": "va_anode_pressure", "type": "<H", "hex": False},
            {"name": "va_regulator_pressure", "type": "<H", "hex": False},
            {"name": "va_msg_cnt", "type": "<H", "hex": False},
            {"name": "va_can_err", "type": "<H", "hex": False},

            # hk mem
            {"name": "hk_mA_28V", "type": "<H", "hex": False},
            {"name": "hk_mV_14V", "type": "<H", "hex": False},
            {"name": "hk_mA_14V", "type": "<H", "hex": False},
            {"name": "hk_mV_7VA", "type": "<H", "hex": False},
            {"name": "hk_mA_7VA", "type": "<H", "hex": False},

            # efc
            {"name": "count_meccemsb", "type": "<H", "hex": True},
            {"name": "count_ueccemsb", "type": "<H", "hex": True},
            {"name": "count_meccelsb", "type": "<H", "hex": True},
            {"name": "count_ueccelsb", "type": "<H", "hex": True},

            # sys-mem
            {"name": "region_stat", "type": "<I", "hex": True},
            {"name": "failed_repairs", "type": "<I", "hex": True},
            {"name": "repair_stat", "type": "<I", "hex": True},
        ]


class MrLogger():
    """
    Log Folder Format
    """

    def __init__(self, root_dir, log_name):
        # log types
        self.RAW = 0
        self.TRACE = 1
        self.HSI = 2
        self.SYS = 3
        self.q = Queue(10)
        # create logging dir
        self.create_folder(root_dir)
        now = datetime.datetime.now()
        time_string = now.strftime("%Y_%m_%d_%H_%M_%S")
        self.log_dir = root_dir + f"/unnamed_{time_string}"
        if len(log_name) > 0:  # create a custom test folder
            self.log_dir = root_dir + f"/{log_name}_{time_string}"
        self.create_folder(self.log_dir)
        self.hsi_log = open(self.log_dir + f"/{time_string}_{log_name}_hsi_log.txt", "w+")
        self.trace_log = open(self.log_dir + f"/{time_string}_{log_name}_trace_log.txt", "w+")
        self.raw_log = open(self.log_dir + f"/{time_string}_{log_name}_raw_serial_log.txt", "w+")
        self.sys_log = open(self.log_dir + f"/{time_string}_{log_name}_sys_log.txt", "w+")
        # create a thread to handle incoming messages.
        self.run = True
        self.handle_thread = Thread(target=self.handle_q, daemon=True)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.sock.bind((RAW_UDP_IP, RAW_UDP_PORT))
        self.network_handle_thread = Thread(target=self.handle_raw, daemon=True)

        self.handle_thread.start()
        self.network_handle_thread.start()

    def create_folder(self, folder_name):
        if not exists(folder_name):
            print(f"Creating {folder_name}.")
            try:
                os.mkdir(folder_name)
                return True
            except OSError as e:
                print(f"Error {folder_name} could not be created. {e}")
        return False

    def log(self, log_type, msg, end="\n", print_val=True):
        if log_type >= 0 and log_type <= 3:  # valid log mesage
            self.q.put({"type": log_type, "msg": msg})
            if log_type == self.SYS and print_val:
                print(msg, end=end)
            return True
        else:
            return False

    def handle_q(self):
        while self.run:
            try:
                if not self.q.empty():
                    m = self.q.get()
                    try:
                        type = m.get("type")
                        msg = m.get("msg")
                        if type == self.HSI:
                            self.hsi_log.write(f"{msg}\n")
                        elif type == self.TRACE:
                            decoded_msg = f"{msg.decode('ascii')}\n"
                            self.trace_log.write(decoded_msg)
                            self.trace_log.flush()
                        elif type == self.SYS:
                            self.sys_log.write(f"{msg}\n")
                            self.sys_log.flush()
                    except KeyError:
                        None
                        # failed to parse log message
                else:
                    time.sleep(0.1)
            except Exception as e:
                print(e)
                print(traceback.extract_tb())

    def handle_raw(self):
        while self.run:
            data, addr = self.sock.recvfrom(1024)  # buffer size is 1024 bytes
            now = datetime.datetime.now()
            time_string = now.strftime("%Y_%m_%d_%H_%M_%S.%f")
            time_string_disp = now.strftime("%M:%S.%f")
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
                    self.raw_log.write(f"[S:{time_string}]:{tx_bytes.hex()}:{msg}\n")

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
                    self.raw_log.write(f"[R:{time_string}]:{rx_bytes.hex()}:{msg}\n")
            else:
                # garbage
                None
            time.sleep(0.01)

    def close(self):
        self.run = False
        if self.handle_thread.is_alive():
            self.handle_thread.join()
        if self.network_handle_thread.is_alive():
            self.sock.sendto(bytes(" ", "ascii"), (RAW_UDP_IP, RAW_UDP_PORT))  # send a packet to get out of waiting
            self.network_handle_thread.join()
        self.hsi_log.close()
        self.trace_log.close()
        self.raw_log.close()


class ConfigLoader():
    def __init__(self, config_file):
        if not exists(config_file):
            print("")


class ThrusterCommand:
    """
    ThrusterCommand,
    Contains function definitions for communicating with the ecp, and definitions on what indexes and sub-idxs to
    communicate with.
    """
    hsi = {
        "k_vsepic": {"index": KEEPER_INDEX, "subindex": 0x1, "row": 1, "col": 0x0},
        "k_vin": {"index": KEEPER_INDEX, "subindex": 0x2, "row": 1, "col": 0x1},
        "k_iout": {"index": KEEPER_INDEX, "subindex": 0x3,"row": 1, "col": 0x2},
        "k_dacout": {"index": KEEPER_INDEX, "subindex": 0x4,"row": 1, "col": 0x3},
        "k_lasterr": {"index": KEEPER_INDEX, "subindex": 0x5,"row": 1, "col": 0x4},
        "k_cur_oft": {"index": KEEPER_INDEX, "subindex": 0x6,"row": 1, "col": 0x5},
        "k_msg_cnt": {"index": KEEPER_INDEX, "subindex": 0x7,"row": 1, "col": 0x6},
        "k_can_err": {"index": KEEPER_INDEX, "subindex": 0x8,"row": 1, "col": 0x7},

        "a_vx": {"index": ANODE_INDEX, "subindex": 0x1,"row": 4, "col": 0x0},
        "a_vy": {"index": ANODE_INDEX, "subindex": 0x2,"row": 4, "col": 0x1},
        "a_vout": {"index": ANODE_INDEX, "subindex": 0x3,"row": 4, "col": 0x2},
        "a_iout": {"index": ANODE_INDEX, "subindex": 0x4,"row": 4, "col": 0x3},
        "a_dac": {"index": ANODE_INDEX, "subindex": 0x5,"row": 4, "col": 0x4},
        "a_last_err": {"index": ANODE_INDEX, "subindex": 0x6,"row": 4, "col": 0x5},
        "a_cur_oft": {"index": ANODE_INDEX, "subindex": 0x7,"row": 4, "col": 0x6},
        "a_hs_temp": {"index": ANODE_INDEX, "subindex": 0x8,"row": 4, "col": 0x7},
        "a_msg_cnt": {"index": ANODE_INDEX, "subindex": 0x9,"row": 4, "col": 0x8},
        "a_can_err": {"index": ANODE_INDEX, "subindex": 0xA,"row": 4, "col": 0x9},

        "mo_vout": {"index": MAG_INNER_INDEX, "subindex": 0x1,"row": 7, "col": 0},
        "mo_iout": {"index": MAG_INNER_INDEX, "subindex": 0x2,"row": 7, "col": 1},
        "mo_dac_out": {"index": MAG_INNER_INDEX, "subindex": 0x3,"row": 7, "col": 2},
        "mo_last_err": {"index": MAG_INNER_INDEX, "subindex": 0x4,"row": 7, "col": 3},
        "mo_msg_cnt": {"index": MAG_INNER_INDEX, "subindex": 0x5,"row": 7, "col": 4},
        "mo_can_err": {"index": MAG_INNER_INDEX, "subindex": 0x6,"row": 7, "col": 5},

        "mi_vout": {"index": MAG_OUTER_INDEX, "subindex": 0x1,"row": 10, "col": 0},
        "mi_iout": {"index": MAG_OUTER_INDEX, "subindex": 0x2,"row": 10, "col": 1},
        "mi_dac_out": {"index": MAG_OUTER_INDEX, "subindex": 0x3,"row": 10, "col": 2},
        "mi_last_err": {"index": MAG_OUTER_INDEX, "subindex": 0x4,"row": 10, "col": 3},
        "mi_msg_cnt": {"index": MAG_OUTER_INDEX, "subindex": 0x5,"row": 10, "col": 4},
        "mi_can_err": {"index": MAG_OUTER_INDEX, "subindex": 0x6,"row": 10, "col": 5},

        "vo_anode_v": {"index": VALVES_INDEX, "subindex": 0x1,"row": 13, "col": 0x0},
        "vo_cath_hf_v": {"index": VALVES_INDEX, "subindex": 0x2,"row": 13, "col": 0x1},
        "vo_cath_lf_v": {"index": VALVES_INDEX, "subindex": 0x3,"row": 13, "col": 0x2},
        "vo_temp": {"index": VALVES_INDEX, "subindex": 0x4,"row": 13, "col": 0x3},
        "vo_tank_pressure": {"index": VALVES_INDEX, "subindex": 0x5,"row": 13, "col": 0x4},
        "vo_cathode_pressure": {"index": VALVES_INDEX, "subindex": 0x6,"row": 13, "col": 0x5},
        "vo_anode_pressure": {"index": VALVES_INDEX, "subindex": 0x7,"row": 13, "col": 0x6},
        "vo_reg_pressure": {"index": VALVES_INDEX, "subindex": 0x8,"row": 13, "col": 0x7},
        "vo_msg_cnt": {"index": VALVES_INDEX, "subindex": 0x9,"row": 13, "col": 0x8},
        "vo_can_err": {"index": VALVES_INDEX, "subindex": 0xA,"row": 13, "col": 0x9},
	#not used in version 1.4.0
        #"current_28v": {"index": HK_INDEX, "subindex": 0x1, "row": 16, "col": 0x0},
        #"sense_14v": {"index": HK_INDEX, "subindex": 0x2, "row": 16, "col": 0x1},
        #"current_14v": {"index": HK_INDEX, "subindex": 0x3, "row": 16, "col": 0x2},
        #"sense_7a": {"index": HK_INDEX, "subindex": 0x4, "row": 16, "col": 0x3},
        #"current_7a": {"index": HK_INDEX, "subindex": 0x5, "row": 16, "col": 0x4},
    }

    def __init__(self, ecp_id, ser_port, listen_mode, debug):
        """
        __init__, sets up serial port and cmds definitions and launches the help menu.
        """
        self.th_command_index = "ThrusterCommand"
        self.trace_msg_index = "Trace"
        self.debug = debug
        self.test_name = test_name
        self.mr_logger = MrLogger("logs", test_name)
        self.version = "0.0.7"
        self.serial_port = ser_port
        self.eds_file = eds_file
        self.hsi_defs = HSIDefs()
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
            "12": {"name": "Query Block HSI", "func": self.query_block_hsi,
                   "args": {"index": 0x3100, "subindex": 0x1, "type": "<I"},
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
                    self.mr_logger.log(self.mr_logger.SYS, "Selected can network type")
                self.network.connect(bustype='pcan', channel='PCAN_USBBUS1', bitrate=1000000)  # 1MHZ
            else:
                if self.debug:
                    self.mr_logger.log(self.mr_logger.SYS, "Selected serial network type")
                self.network.connect(bustype="exoserial", channel=self.serial_port, baudrate=115200)
            self.node = self.network.add_node(self.system_id, self.eds_file)
            self.network.add_node(self.node)
            self.node.sdo.RESPONSE_TIMEOUT = 2
            self.node.emcy.add_callback(self.handle_emcy)
            self.network.subscribe(0x722, self.notify_bootup)
            # check to see if device is connected
            self.nmt_state = self.read(self.th_command_index, THRUSTER_STATUS_SUBINDEX, "<I")
            # check to see if msg was recieved
            if self.nmt_state is None:
                self.mr_logger.log(self.mr_logger.SYS, "System Controller Failed to Connect.  Waiting for bootup msg.")
                while not self.bootup_msg:
                    time.sleep(0.01)
                self.mr_logger.log(self.mr_logger.SYS, "System Controller Connected!")
                # when connected read the state
                self.nmt_state = self.read(self.th_command_index, THRUSTER_STATUS_SUBINDEX, "<I")
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
                self.mr_logger.log(self.mr_logger.SYS, "System Controller Connected!")

        except Exception as a:
            self.mr_logger.log(self.mr_logger.SYS, traceback.print_exc())

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
                self.mr_logger.log(self.mr_logger.SYS,
                                   f"Error Not found.  Check if {index_str} and {subindex_str} are in the eds file.")
            else:
                index = var.index
                subindex = var.subindex
        except KeyError as e:
            self.mr_logger.log(self.mr_logger.SYS, f"{traceback.print_exc()} {e}")
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
            self.mr_logger.log(self.mr_logger.SYS,f"Updated State: {cur_state}")
            self.nmt_state_str = cur_state
            self.nmt_state = state

    def change_nmt_state(self, args):
        """
        change_nmt_state, is called by the NmtMaster callback when the state changes.
        """
        if self.debug:
            self.mr_logger.log(self.mr_logger.SYS, "Thread Stopped")
        state = args.get("nmt_state")
        if state == "OPERATIONAL":
            self.mr_logger.log(self.mr_logger.SYS, "Switching State Operational")
            self.node.nmt.send_command(0x1)
            self.start_threads()
        elif state == "PREOPERATIONAL":
            self.mr_logger.log(self.mr_logger.SYS, "Switching State Pre-Operational")
            self.node.nmt.send_command(0x80)
            self.start_threads()
        elif state == "INIT":
            self.mr_logger.log(self.mr_logger.SYS, "Switching State Init")
            self.node.nmt.send_command(0x81)
        elif state == "STOP":
            self.mr_logger.log(self.mr_logger.SYS, "Switching State Stop")
            self.thread_run = False
            self.node.nmt.send_command(0x2)

    def handle_emcy(self, error):
        """
        handle_emcy, on emcy msg this function prints the error to console and udp port
        """
        message = f"EMCYTimestamp: {error.timestamp}, EMCYCode: {error.code}," \
                  f" EMCYData: {error.data}"

        self.send_udp_packet(message, TRACE_UDP_IP, TRACE_UDP_PORT)
        self.mr_logger.log(self.mr_logger.SYS,message)

    def get_status_index(self, args):
        """
        get_status_index, gets the status and checks to make sure that the threads are enabled if operational.
        """
        index = args.get("index")
        noprint = args.get("noprint")
        statuses = self.get_status(index, noprint)
        if statuses[2] >= '0x7':
            self.start_threads()
        self.mr_logger.log(self.mr_logger.SYS, "8 to enable / disable console status print")

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
            self.mr_logger.log(self.mr_logger.SYS, msg)
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
            self.mr_logger.log(self.mr_logger.SYS, "Starting Query Thread")
        while getattr(self, "thread_run"):
            if self.nmt_state != "Stopped":
                statuses = self.get_status(self.th_command_index, True)
                if statuses[2] is not None:
                    self.notify_updated_state(int(statuses[2], 16))
                    self.get_trace_msg()
                    self.get_block_hsi()
            time.sleep(TRACE_SLEEP_TIME)

    def get_hsi_msgs(self):
        """
        get_hsi_msgs, this gathers hsi messages and sends it over udp, runs in thread.
        """
        for a in self.hsi_defs.hsi.items():
            item_name = a[0]
            index = a[1].get("index")
            subindex = a[1].get("subindex")
            type = a[1].get("type")
            parsed_val = self.get_var(index, subindex)
            index = parsed_val.get("index")
            subindex = parsed_val.get("subindex")
            if type is None:
                type = "<H"
            val = self.read(index, subindex, type)
            if val is not None:
                msg = f"{item_name.ljust(10, ' ')}:index:{hex(index)}:subindex:{hex(subindex)}:val:{val}"
                self.send_udp_packet(msg, HSI_UDP_IP, HSI_UDP_PORT)
        time.sleep(HSI_SLEEP_TIME)

    def get_block_hsi(self):
        data = self.node.sdo.upload(0x3100, 0x1)
        self.trace_sock.sendto(data, (HSI_UDP_IP, HSI_BLOCK_UDP_PORT))

    def query_block_hsi(self, args):
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
                self.mr_logger.log(self.mr_logger.SYS,f"{name} - {parsed_val}")
            else:
                self.mr_logger.log(self.mr_logger.SYS, f"Cant parse the bytearray because its not divisable by 2.  Len Data: {len(data)}")
        except canopen.sdo.exceptions.SdoCommunicationError as comms_err: \
                self.mr_logger.log(self.mr_logger.SYS,f"Query Failed: {comms_err}")
        except canopen.sdo.exceptions.SdoAbortedError as aborted_err: \
                self.mr_logger.log(self.mr_logger.SYS,f"Query Failed: {aborted_err}")
        except Exception as e:
            self.mr_logger.log(self.mr_logger.SYS,f"Query Failed: {e}")

    def start_threads(self):
        """
        start_threads, starts 2 gather threads for trace and hsi messages.
        """
        if not self.thread_run:
            if self.debug:
                self.mr_logger.log(self.mr_logger.SYS, f"Starting Trace / Status thread. Sending HSI to {HSI_UDP_IP}:{HSI_UDP_PORT}.")
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
                    self.mr_logger.log(self.mr_logger.SYS,
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
                self.mr_logger.log(self.mr_logger.SYS, f"Wrote:{hex(index)}-{hex(subindex)}: 0x{val.hex()}")
        except struct.error as e:
            self.mr_logger.log(self.mr_logger.SYS, f"{e}")
        except canopen.sdo.exceptions.SdoCommunicationError as comms_err:
            self.mr_logger.log(self.mr_logger.SYS, f"Write Failed: {comms_err}")
        except canopen.sdo.exceptions.SdoAbortedError as aborted_err:
            self.mr_logger.log(self.mr_logger.SYS, f"Write Failed: {aborted_err}")
        except Exception as e:
            self.mr_logger.log(self.mr_logger.SYS, f"Write Failed: {e}")
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
        self.mr_logger.log(self.mr_logger.SYS, f"Query:{hex(index)}-{hex(subindex)}: {hex(in_val)}")

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
                    self.mr_logger.log(self.mr_logger.SYS, f"Query Failed {hex(index)}:{hex(subindex)}: {comms_err}")
            except canopen.sdo.exceptions.SdoAbortedError as aborted_err:
                if show_failure:
                    self.mr_logger.log(self.mr_logger.SYS, f"Query Failed {hex(index)}:{hex(subindex)}: {aborted_err}")
            except Exception as e:
                if show_failure:
                    self.mr_logger.log(self.mr_logger.SYS, f"Query Failed {hex(index)}:{hex(subindex)}: {e}")
            finally:
                self.write_mutex.release()
        else:
            self.mr_logger.log(self.mr_logger.SYS, "Error with args to write function, check index and subindex")
        return None

    def get_trace_msg(self):
        """
            get_trace_msg, gets a trace msg by first looking at the head and the tail to see if there is one to get.
            if the head and the tail are == then there are no messages just return.
        """
        try:
            for i in range(0, TRACE_MSG_MAX_GATHER):
                # msg = self.read(self.trace_msg_index, TRACE_MSG_SUBINDEX, "noparse", False)
                msg = self.node.sdo.upload(0x5001, 0x6)
                if msg is not None:
                    self.mr_logger.log(self.mr_logger.TRACE, msg)
                    self.send_udp_packet(msg, TRACE_UDP_IP, TRACE_UDP_PORT)
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
                self.mr_logger.log(self.mr_logger.SYS, f"{var_str}>", end='', print_val=False)
                inp = input(f"{var_str}>").lower().strip()
                self.mr_logger.log(self.mr_logger.SYS, f"{inp}", end='', print_val=False)
                if inp in self.hsi_cmds.keys():
                    cmd = self.hsi_cmds.get(inp)
                    func = cmd.get("func")
                    args = cmd.get("args")
                    name = cmd.get("name")
                    if func != None:
                        self.mr_logger.log(self.mr_logger.SYS,f"{name}")
                        try:
                            func(args)
                        except Exception as e:
                            self.mr_logger.log(self.mr_logger.SYS,f"{e}")
            except KeyboardInterrupt as e:
                sys.exit(0)

    def help(self, args):
        """
        help, reads the predefined cmds and prints them in a table.
        """
        self.mr_logger.log(self.mr_logger.SYS, "============= ExoTerra Thruster Command Help Menu =============")
        for v in self.hsi_cmds:
            x = self.hsi_cmds.get(v)
            self.mr_logger.log(self.mr_logger.SYS, f"{v} - {x.get('name')} : [{x.get('help')}]")

    def exit(self, args):
        """
        exit, exits the program.
        """
        self.mr_logger.close()
        self.thread_run = False
        self.running = False


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
            print(traceback.print_tb())
