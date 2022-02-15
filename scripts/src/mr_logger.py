"""
ExoTerra Resource Mr Logger Library.
description:
Provides and interface to gather and log messages to files.

contact:
joshua.meyers@exoterracorp.com
jeremy.mitchell@exoterracorp.com
"""

from queue import Queue
from socket import socket, AF_INET, SOCK_DGRAM
from datetime import datetime
from os.path import exists
from os import mkdir
from threading import Thread
from time import sleep
from traceback import extract_tb
from struct import unpack
from enum import Enum

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
    def __init__(self, conf_man, root_dir, log_name):
        """
        init, creates 2 threads for mr logger one for raw serial messages, the other for trace, hsi, and sys messages.
        It also creates a folder for each startup and under this folder 4 files are created to store each type of log message.
        """
        self.raw_q = Queue()
        self.q = Queue(10)
        self.conf_man = conf_man
        #try to get the config vars
        self.raw_udp_ip = self.conf_man.get("RAW", "RAW_UDP_IP")
        self.raw_udp_port = self.conf_man.get("RAW", "RAW_UDP_PORT", type = int)
        # create logging dir
        self.create_folder(root_dir)
        now = datetime.now()
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
        self.handle_thread = Thread(target=self.handle_hsi_trace_sys_queue, daemon=True)
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.network_handle_thread = Thread(target=self.handle_raw_queue, daemon=True)
        #start threads
        self.handle_thread.start()
        self.network_handle_thread.start()

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
        if log_type.value >= 0 and log_type.value <= 3:  # valid log mesage
            self.q.put({"type": log_type, "msg": msg})
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
                if not self.q.empty():
                    m = self.q.get()
                    try:
                        type = m.get("type")
                        msg = m.get("msg")
                        if type == LogType.HSI.value:
                            self.hsi_log.write(f"{msg}\n")
                        elif type == LogType.TRACE.value:
                            decoded_msg = f"{msg.decode('ascii')}\n"
                            self.trace_log.write(decoded_msg)
                            self.trace_log.flush()
                        elif type == LogType.SYS.value:
                            self.sys_log.write(f"{msg}\n")
                            self.sys_log.flush()
                    except KeyError:
                        None
                        # failed to parse log message
                else:
                    sleep(0.1)
            except Exception as e:
                print(e)

    def handle_raw_queue(self):
        """
        handle_raw_queue, handles reading the Queue and decoding and then writing any data into a file with a timestamp.
        """
        while self.run:
            # data, addr = self.sock.recvfrom(1024)  # buffer size is 1024 bytes
            data = None
            if not self.raw_q.empty():
                data = self.raw_q.get()
            else:
                continue
            now = datetime.now()
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

                    index = unpack("<H", rx_bytes[4:6])[0]
                    subindex = rx_bytes[6]
                    if index == 0x5001 and subindex == 0x3:
                        self.sock.sendto(data, (self.raw_udp_ip, 4001))
                    msg = f" id:{hex(cob_id)}: dl:{data_length}: d:{data.hex()}"
                    self.raw_log.write(f"[R:{time_string}]:{rx_bytes.hex()}:{msg}\n")
            else:
                # garbage
                None
            sleep(0.01)

    def close(self):
        """
        close, closes out the threads and then the open files.
        """
        self.run = False
        if self.handle_thread.is_alive():
            self.handle_thread.join()
        if self.network_handle_thread.is_alive():
            self.sock.sendto(bytes(" ", "ascii"), (self.raw_udp_ip, self.raw_udp_port))  # send a packet to get out of waiting
            self.network_handle_thread.join()
        self.hsi_log.close()
        self.trace_log.close()
        self.raw_log.close()
