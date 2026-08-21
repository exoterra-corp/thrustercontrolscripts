from enum import Enum
import struct, canopen
from threading import Lock
from halo8thruster.driver.mr_logger import MrLogger, LogType
from halo8thruster.driver.od_defines import *



class Comms:
    def __init__(
        self,
        mr_logger,
        serial_port: str = "/dev/ttyUSB0",
        system_id: int = 0x22,
        sdo_timeout: float = 5.0,
        half_duplex: bool = False,
        debug:bool = False
    ) -> None:
        self.mr_logger = mr_logger
        self.serial_port = serial_port
        self.system_id = system_id
        self.sdo_timeout = sdo_timeout
        self.network = canopen.Network()
        self.write_mutex = Lock()
        self.network.connect(bustype="exoserial", channel=self.serial_port, baudrate=115200)
        self.node = self.network.add_node(self.system_id)
        self.network.add_node(self.node)
        self.raw_q = self.node.network.bus.get_int_q()
        self.mr_logger.set_raw_queue(self.raw_q)
        self.node.sdo.RESPONSE_TIMEOUT = sdo_timeout
        self.node.emcy.add_callback(self.subscribe_emcy)
        self.network.subscribe(NMT_BOOTUP_COB_ID, self.subscribe_bootup)
        self.debug = debug

    def __enter__(self): return self

    def __exit__(self, *exc): self.disconnect()

    def subscribe_bootup(self, callback) -> None:
        """Register NMT bootup callback on COB-ID 0x722."""
        self.network.subscribe(0x722, callback)

    def subscribe_emcy(self, callback) -> None:
        self.mr_logger.log(LogType.SYS, f"EMCY MESSAGE: {callback}")


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

    def disconnect(self) -> None:
        if self.network:
            self.network.disconnect()

    def write(self, index, subindex, val, python_type):
        """
        Write a value to the device over SDO. val may be an int, or a string in
        decimal ("26"), hex ("0x1A"), octal ("0o17"), or binary ("0b101") form.
        """
        try:
            self.write_mutex.acquire()
            int_val = val if isinstance(val, int) else int(val, 0)
            packed = struct.pack(python_type, int_val)
            self.node.sdo.download(index, subindex, bytearray(packed))
            if self.debug:
                self.mr_logger.sys(f"Wrote:{hex(index)}-{hex(subindex)}: 0x{packed.hex()}")
        except struct.error as e:
            self.mr_logger.sys(f"Write Failed (pack): {e}")
        except canopen.sdo.exceptions.SdoCommunicationError as e:
            self.mr_logger.sys(f"Write Failed: {e}")
        except canopen.sdo.exceptions.SdoAbortedError as e:
            self.mr_logger.sys(f"Write Failed: {e}")
        except Exception as e:
            self.mr_logger.sys(f"Write Failed: {e}")
        finally:
            self.write_mutex.release()

    def query(self, args):
        """
        query, uses a index, subindex to read the field from the Engine System Controller and print it in hex.
        """
        index = args.get("index")
        subindex = args.get("subindex")

        in_val = self.read(index, subindex, "<I")
        self.mr_logger.log(LogType.SYS, f"Query:{hex(index)}-{hex(subindex)}: {hex(in_val)}")

    def read(self, index, subindex, python_type, show_failure=True):
        if index is None or subindex is None:
            self.mr_logger.sys(f"Read Failed: invalid index={index} subindex={subindex}")
            return None
        try:
            self.write_mutex.acquire()
            val = self.node.sdo.upload(index, subindex)
            return val if python_type == "noparse" else struct.unpack(python_type, val)[0]
        except canopen.sdo.exceptions.SdoCommunicationError as e:
            if show_failure:
                self.mr_logger.sys(f"Read Failed {hex(index)}:{hex(subindex)}: {e}")
        except canopen.sdo.exceptions.SdoAbortedError as e:
            if show_failure:
                self.mr_logger.sys(f"Read Failed {hex(index)}:{hex(subindex)}: {e}")
        except Exception as e:
            if show_failure:
                self.mr_logger.sys(f"Read Failed {hex(index)}:{hex(subindex)}: {e}")
        finally:
            self.write_mutex.release()
        return None


    #     """
    #     connect_to_ecp, sets up the serial interface with exoserial and adds the node to the network.
    #     """
    #     try:
    #         self.network = canopen.Network()
    #         if self.serial_port == "can":
    #             self.network.connect(bustype='pcan', channel='PCAN_USBBUS1', bitrate=1000000)  # 1MHZ
    #         else:


    #         # activate half duplex mode if specified
    #         if self.half_duplex:
    #             try:
    #                 self.network.bus.half_duplex_mode()
    #             except AttributeError:
    #                 self.mr_logger.log(LogType.SYS, "The installed version of python-can does not support half-duplex ExoSerialCan connections")

    #         # check to see if device is connected
    #         attempts = 0
    #         while self.nmt_state is None and attempts < 3:
    #             
    #             attempts += 1

    #         # check to see if msg was recieved
    #         if self.nmt_state is None:
    #             self.mr_logger.log(LogType.SYS, "System Controller Failed to Connect.")
    #             if self.half_duplex:
    #                 # Failed connection is fatal in half-duplex mode
    #                 self.mr_logger.log(LogType.SYS, "Exiting...")
    #                 time.sleep(2)
    #                 exit(1)
    #             else:
    #                 # Wait for bootup message if running full-duplex
    #                 self.mr_logger.log(LogType.SYS, "Waiting for bootup message.")
    #                 while not self.bootup_msg:
    #                     time.sleep(0.01)
    #                 self.mr_logger.log(LogType.SYS, "System Controller Connected!")

    #         # read the state on bootup
    #         self.get_status(IDX_THRUSTER_CMD)
    #         cur_state = ""
    #         if self.nmt_state is not None:
    #             self.notify_updated_state(self.nmt_state)
    #             if self.nmt_state == 0x2:  # preop state
    #                 cur_state = "Pre Operational"
    #                 self.start_threads()
    #             elif self.nmt_state >= 0x7 or self.nmt_state == 0x3:
    #                 cur_state = "Operational"
    #                 self.start_threads()
    #             elif self.nmt_state == 0x1:
    #                 cur_state = "Bootup - Init"
    #             self.nmt_state_str = cur_state
    #             # self.read_serial_number()
    #             self.mr_logger.log(LogType.SYS, "System Controller Connected!")
    #     except KeyboardInterrupt:
    #         exit(0)
    #     except Exception as a:
    #         None
    #         # self.mr_logger.log(LogType.SYS, traceback.print_exc())