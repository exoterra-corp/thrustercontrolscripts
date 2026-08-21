"""
ExoTerra Resource Mr Logger Library.
description:
Provides and interface to gather and log messages to files.
"""

from collections import namedtuple
from queue import Queue, SimpleQueue, Empty
from socket import socket, AF_INET, SOCK_DGRAM
from os.path import exists
from os import mkdir
from threading import Thread
from time import sleep
from struct import unpack
from enum import Enum
import time, datetime, struct, json
from csv import DictWriter
from halo8thruster.driver.defines import HSIDefines

_LogItem = namedtuple("_LogItem", ["log_type", "msg", "timestamp"])

class LogType(Enum):
    """
    LogType enum stores the various log types for mr logger and other classes to use.  This is how Mr Logger knows which
    message to store in which file.
    """
    RAW = 0
    TRACE = 1
    HSI = 2
    SYS = 3

class MrLogger:
    """
    Mr Logger takes care of the logs directory along with recording raw,hsi,trace,and the sys log from thruster_command
    """
    def __init__(self, root_dir, log_name=""):
        """
        init, creates 2 threads for mr logger one for raw serial messages, the other for trace, hsi, and sys messages.
        It also creates a folder for each startup and under this folder 4 files are created to store each type of log message.
        """
        self.raw_q = Queue()
        self.q = SimpleQueue()
        self.udp_ip         = "127.0.0.1"
        self.raw_udp_port   = 4000
        self.hsi_udp_port   = 4001
        self.trace_udp_port = 4002
        # create logging dir
        self.create_folder(root_dir)
        now = datetime.datetime.now()
        time_string = now.strftime("%Y_%m_%d_%H_%M_%S")
        self.log_dir = root_dir + f"/unnamed_{time_string}"
        if len(log_name) > 0:  # create a custom test folder
            self.log_dir = root_dir + f"/{log_name}_{time_string}"
        self.create_folder(self.log_dir)
        self.hsi_log_csv = open(self.log_dir + f"/{time_string}_{log_name}_hsi_log.csv", "w+")
        self.hsi_log_json = open(self.log_dir + f"/{time_string}_{log_name}_hsi_log.json", "w+")
        self.hsi_log_json.write("{")
        self.trace_log = open(self.log_dir + f"/{time_string}_{log_name}_trace_log.txt", "w+")
        self.raw_log = open(self.log_dir + f"/{time_string}_{log_name}_raw_serial_log.txt", "w+")
        self.sys_log = open(self.log_dir + f"/{time_string}_{log_name}_sys_log.txt", "w+")
        # create a thread to handle incoming messages.
        self.run = True
        self.handle_thread = Thread(target=self.handle_hsi_trace_sys_queue, daemon=True)
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.network_handle_thread = Thread(target=self.handle_raw_queue, daemon=True)
        #start threads
        self.handle_thread.start()
        self.network_handle_thread.start()
        self.hsi_def = HSIDefines()
        self.hsi_msg_cnt = 0
        fieldnames = ["timestamp"] + list(self.hsi_def.hsi.keys())
        self.hsi_csv_writer = DictWriter(self.hsi_log_csv, fieldnames=fieldnames)
        self.hsi_csv_writer.writeheader()

    def set_raw_queue(self, q):
        """
        set_raw_queue, sets the local Queue reference into the exoserial library.
        by a thread and into a file for storage.
        """
        self.raw_q = q

    def create_folder(self, folder_name):
        """
        create_folder, checks to make sure a folder exists and if it doesn't creates it.
        """
        if not exists(folder_name):
            print(f"Creating {folder_name}.")
            try:
                mkdir(folder_name)
                return True
            except OSError as e:
                print(f"Error {folder_name} could not be created. {e}")
        return False

    def log(self, log_type:LogType, msg, end="\n", print_val=True):
        """
        log, creates a log message and adds it to the Queue.
        log_type: LogType, is the enum above.
        msg: str, the message to store.
        end: str, what to put at the end of a msg, default newline.
        print_Val: bool, whether or not to print the logged message.
        """
        if log_type.value >= 0 and log_type.value <= 3:
            self.q.put(_LogItem(log_type, msg, time.time()))
            if log_type.value == LogType.SYS.value and print_val:
                print(msg, end=end)
            return True
        else:
            return False

    def handle_hsi_trace_sys_queue(self):
        """
        handle_hsi_trace_sys_queue, reads the internal Queue and writes hsi trace and sys data to the appropriate log.
        """
        while self.run:
            try:
                m = self.q.get(timeout=0.1)
            except Empty:
                continue
            try:
                log_type = m.log_type.value
                msg = m.msg
                ts = m.timestamp
                str_time = datetime.datetime.fromtimestamp(ts)
                if log_type == LogType.HSI.value:
                    if len(msg) == 122:
                        csv_row = self.hsi_def.parse_hsi_packet(msg)
                        csv_row["timestamp"] = str(str_time)
                        self.hsi_csv_writer.writerow(csv_row)
                        self.hsi_log_csv.flush()
                        if self.hsi_msg_cnt != 0:
                            self.hsi_log_json.write(",")
                        self.hsi_log_json.write(f'\"{str(self.hsi_msg_cnt)}\":{json.dumps(csv_row)}')
                        self.hsi_msg_cnt += 1
                        self.sock.sendto(msg, (self.udp_ip, self.hsi_udp_port))
                elif log_type == LogType.TRACE.value:
                    decoded_msg = f"{str_time}:{msg.decode('ascii')}\n"
                    self.trace_log.write(decoded_msg)
                    self.trace_log.flush()
                    self.sock.sendto(msg, (self.udp_ip, self.trace_udp_port))
                elif log_type == LogType.SYS.value:
                    self.sys_log.write(f"{str_time}:{msg}\n")
                    self.sys_log.flush()
            except Exception as e:
                print(e)

    def handle_raw_queue(self):
        """
        handle_raw_queue, handles reading the Queue and decoding and then writing any data into a file with a timestamp.
        """
        while self.run:
            try:
                data = self.raw_q.get(timeout=0.01)
            except (Empty, AttributeError):
                continue
            now = datetime.datetime.now()
            time_string = now.strftime("%Y_%m_%d_%H_%M_%S.%f")
            time_string_disp = now.strftime("%M:%S.%f")
            if data[0] == 0xA:
                # sent from the gui
                tx_bytes = data[1:]  # remove the first byte
                header = (tx_bytes[0] & 0xF8)
                if (header) == 0xa8:
                    cob_id = (tx_bytes[0] & 0x7) << 8
                    cob_id |= (tx_bytes[1] & 0xFF)
                    data_length = (tx_bytes[2] & 0xF)
                    payload = tx_bytes[3:11]
                    msg = f" id:{hex(cob_id)}: dl:{data_length}: d:{payload.hex()}"
                    self.raw_log.write(f"[S:{time_string}]:{tx_bytes.hex()}:{msg}\n")
                    # self.sock.sendto(data, (self.udp_ip, self.raw_udp_port))

            elif data[0] == 0xB:
                # recv from sam
                rx_bytes = data[1:]  # remove the first byte
                header = (rx_bytes[0] & 0xF8)
                if (header) == 0xa8:
                    cob_id = (rx_bytes[0] & 0x7) << 8
                    cob_id |= (rx_bytes[1] & 0xFF)
                    data_length = (rx_bytes[2] & 0xF)
                    payload = rx_bytes[3:11]
                    msg = f" id:{hex(cob_id)}: dl:{data_length}: d:{payload.hex()}"
                    self.raw_log.write(f"[R:{time_string}]:{rx_bytes.hex()}:{msg}\n")
                    # self.sock.sendto(data, (self.udp_ip, self.raw_udp_port))

    def sys(self, msg, end="\n"):   self.log(LogType.SYS, msg, end)
    def trace(self, msg):           self.log(LogType.TRACE, msg)
    def hsi(self, msg):             self.log(LogType.HSI, msg)
    def raw(self, msg):             self.log(LogType.RAW, msg)

    def close(self):
        """
        close, closes out the threads and then the open files.
        """
        self.run = False
        if self.handle_thread.is_alive():
            self.handle_thread.join()
        if self.network_handle_thread.is_alive():
            self.network_handle_thread.join()
        self.hsi_log_csv.close()
        self.hsi_log_json.write("}")
        self.hsi_log_json.close()
        self.trace_log.close()
        self.raw_log.close()
