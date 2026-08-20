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

    def disconnect(self) -> None:
        if self.network:
            self.network.disconnect()

    def write(self, index, subindex, val, python_type, hex_en=True):
        """
        write, uses a index, subindex, and a type to ask for a hex value and then send this data over serial to the
        Engine System Controller.
        """
        try:
            self.write_mutex.acquire()
            if hex_en:
                int_val = int(val, 16)
            else:
                int_val = int(val)
            val = struct.pack(python_type, int_val)
            self.node.sdo.download(index, subindex,
                                    bytearray(val))
            if self.debug:
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

        in_val = self.read(index, subindex, "<I")
        self.mr_logger.log(LogType.SYS, f"Query:{hex(index)}-{hex(subindex)}: {hex(in_val)}")

    def read(self, index, subindex, python_type, show_failure=True):
        if index != None and subindex != None:
            try:
                self.write_mutex.acquire()
                # if self.:  # check to see if stopped
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