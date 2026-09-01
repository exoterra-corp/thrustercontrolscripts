import struct, canopen, time, datetime
from threading import Lock
from halo8thruster.driver.mr_logger import MrLogger, LogType
from halo8thruster.driver.defines import *
from halo8thruster.driver.exceptions import ConnectionError, CommsError, CommsTimeout, CommsAbort

class Comms:
    """A class to handle the canopen serial communication with the halo 8 ppu.
    Attributes:
        mr_logger: the logging instance to use,
        serial_port: the serial port path,
        system_id: the halo8 canopen node id,
        sdo_timeout: how long should the canopen stack wait for a timeout,
        debug: print the debug messages, also shows timing information. quite noisy when enabled.
        network: the canopen network using the exoserial interface.
        write_mutex: the mutex for the read and write functions
    """
    def __init__(
        self,
        mr_logger,
        serial_port: str = "/dev/ttyUSB0",
        system_id: int = 0x22,
        sdo_timeout: float = 5.0,
        half_duplex: bool = False,
        debug:bool = False
    ) -> None:
        """
        Sets up the canopen network and tries to connect to the ppu over the specified serial port.
        Args:
            mr_logger: the logging instance to use,
            serial_port: the serial port path,
            system_id: the halo8 canopen node id,
            sdo_timeout: how long should the canopen stack wait for a timeout,
            half_duplex: Only one message sent and received at a time. True if on a 485 variant, otherwise false.
            debug: print the debug messages, also shows timing information. quite noisy when enabled.
        Raises: 
            ConnectionError: If failed to connect to the ppu on the specified port.
        """
        self.mr_logger = mr_logger
        self.serial_port = serial_port
        self.system_id = system_id
        self.sdo_timeout = sdo_timeout
        self.debug = debug
        self.network = canopen.Network()
        self.write_mutex = Lock()
        try:
            t_boot = time.perf_counter()
            def _bt(label):
                if self.debug:
                    self.mr_logger.sys(f"[boot] {(time.perf_counter()-t_boot)*1000:7.1f}ms  {label}")

            self.mr_logger.sys(f"Connecting to {serial_port}…")
            self.network.connect(bustype="exoserial", channel=self.serial_port, baudrate=115200)
            _bt("network.connect() done")
            self.node = self.network.add_node(self.system_id)
            _bt(f"add_node(0x{self.system_id:02x})")
            self.network.add_node(self.node)
            _bt("network.add_node(node)")
            self.raw_q = self.node.network.bus.get_int_q()
            self.mr_logger.set_raw_queue(self.raw_q)
            _bt("get_int_q() + set_raw_queue()")
            self.node.sdo.RESPONSE_TIMEOUT = sdo_timeout
            self.node.emcy.add_callback(self.handle_emcy)
            _bt(f"ready (sdo_timeout={sdo_timeout}s)")
        except Exception as e:
            raise ConnectionError(f"Failed to connect on {serial_port}: {e}") from e

    def __enter__(self): return self

    def __exit__(self, *exc): self.disconnect()

    def subscribe_bootup(self, callback) -> None:
        """Register NMT bootup callback on COB-ID 0x722."""
        self.network.subscribe(0x722, callback)

    def handle_emcy(self, emgcy_error):
        """Parse and log a CANopen EMCY message from the device."""
        data = emgcy_error.data.hex()
        error_type = fault_code = line_num = error_cnt = None
        if len(data) == 10:
            try:
                line_num = struct.unpack("<H", bytes.fromhex(data[4:8]))[0]
            except (ValueError, struct.error):
                pass
            error_type = data[0:2]
            fault_code = data[2:4]
            error_cnt  = data[9:10]
        self.mr_logger.sys(f"EMCY — code:{hex(emgcy_error.code)} type:{error_type} fault:{fault_code} line:{line_num} cnt:{error_cnt}")

    def disconnect(self) -> None:
        if self.network:
            self.network.disconnect()

    def write(self, index, subindex, val, python_type):
        """
        Write a value to the device over SDO. val may be an int, or a string in
        decimal ("26"), hex ("0x1A"), octal ("0o17"), or binary ("0b101") form.
        Raises CommsTimeout, CommsAbort, or CommsError on failure.
        """
        try:
            self.write_mutex.acquire()
            int_val = val if isinstance(val, int) else int(val, 0)
            packed = struct.pack(python_type, int_val)
            t_sdo = time.perf_counter()
            self.node.sdo.download(index, subindex, bytearray(packed))
            if self.debug:
                elapsed_ms = (time.perf_counter() - t_sdo) * 1000
                self.mr_logger.sys(f"Wrote:{hex(index)}-{hex(subindex)}: 0x{packed.hex()} [{elapsed_ms:.1f}ms]")
        except struct.error as e:
            raise CommsError(f"Write pack error {hex(index)}:{hex(subindex)}: {e}") from e
        except canopen.sdo.exceptions.SdoCommunicationError as e:
            raise CommsTimeout(f"Write timeout {hex(index)}:{hex(subindex)}: {e}") from e
        except canopen.sdo.exceptions.SdoAbortedError as e:
            raise CommsAbort(f"Write aborted {hex(index)}:{hex(subindex)}: {e}") from e
        except (CommsError, CommsTimeout, CommsAbort):
            raise
        except Exception as e:
            raise CommsError(f"Write failed {hex(index)}:{hex(subindex)}: {e}") from e
        finally:
            self.write_mutex.release()

    def write_blob(self, index, subindex, data: bytes, force_segment: bool = True) -> None:
        """Write a raw byte buffer (e.g. firmware image) over SDO without struct packing."""
        try:
            self.write_mutex.acquire()
            t_sdo = time.perf_counter()
            self.node.sdo.download(index, subindex, bytearray(data), force_segment=force_segment)
            if self.debug:
                elapsed_ms = (time.perf_counter() - t_sdo) * 1000
                self.mr_logger.sys(f"WriteBlob:{hex(index)}-{hex(subindex)}: {len(data)}B [{elapsed_ms:.1f}ms]")
        except canopen.sdo.exceptions.SdoCommunicationError as e:
            raise CommsTimeout(f"WriteBlob timeout {hex(index)}:{hex(subindex)}: {e}") from e
        except canopen.sdo.exceptions.SdoAbortedError as e:
            raise CommsAbort(f"WriteBlob aborted {hex(index)}:{hex(subindex)}: {e}") from e
        except (CommsError, CommsTimeout, CommsAbort):
            raise
        except Exception as e:
            raise CommsError(f"WriteBlob failed {hex(index)}:{hex(subindex)}: {e}") from e
        finally:
            self.write_mutex.release()

    def write_blob_progress(
        self,
        index: int,
        subindex: int,
        data: bytes,
        progress_cb=None,
    ) -> int:
        """Segmented SDO download with an optional per-segment progress callback.

        Returns the total number of bytes sent.
        progress_cb(bytes_sent: int, total: int) is called after every SDO segment
        (~7 bytes); tqdm handles display rate-limiting on its own.
        """
        total = len(data)
        try:
            self.write_mutex.acquire()
            with self.node.sdo.open(
                index, subindex, "wb", size=total, force_segment=True, buffering=0
            ) as f:
                sent = 0
                while sent < total:
                    written = f.write(data[sent:])
                    if not written:
                        raise CommsError(
                            f"WriteBlob stalled at {sent}/{total} bytes"
                            f" {hex(index)}:{hex(subindex)}"
                        )
                    sent += written
                    if progress_cb:
                        progress_cb(sent, total)
            return sent
        except canopen.sdo.exceptions.SdoCommunicationError as e:
            raise CommsTimeout(f"WriteBlob timeout {hex(index)}:{hex(subindex)}: {e}") from e
        except canopen.sdo.exceptions.SdoAbortedError as e:
            raise CommsAbort(f"WriteBlob aborted {hex(index)}:{hex(subindex)}: {e}") from e
        except (CommsError, CommsTimeout, CommsAbort):
            raise
        except Exception as e:
            raise CommsError(f"WriteBlob failed {hex(index)}:{hex(subindex)}: {e}") from e
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

    def read(self, index, subindex, python_type="noparse"):
        """
        Read a value from the device over SDO.
        Returns the unpacked value, or raw bytes when python_type is "noparse".
        Raises CommsTimeout, CommsAbort, or CommsError on failure.
        """
        if index is None or subindex is None:
            raise CommsError(f"Read called with invalid index={index} subindex={subindex}")
        try:
            self.write_mutex.acquire()
            t_sdo = time.perf_counter()
            val = self.node.sdo.upload(index, subindex)
            if self.debug:
                elapsed_ms = (time.perf_counter() - t_sdo) * 1000
                self.mr_logger.sys(f"Read:{hex(index)}-{hex(subindex)}: 0x{val.hex()} [{elapsed_ms:.1f}ms]")
            return val if python_type == "noparse" else struct.unpack(python_type, val)[0]
        except canopen.sdo.exceptions.SdoCommunicationError as e:
            raise CommsTimeout(f"Read timeout {hex(index)}:{hex(subindex)}: {e}") from e
        except canopen.sdo.exceptions.SdoAbortedError as e:
            raise CommsAbort(f"Read aborted {hex(index)}:{hex(subindex)}: {e}") from e
        except (CommsError, CommsTimeout, CommsAbort):
            raise
        except Exception as e:
            raise CommsError(f"Read failed {hex(index)}:{hex(subindex)}: {e}") from e
        finally:
            self.write_mutex.release()

    def send_udp_packet(self, msg, ip, port):
        """send_udp_packet, sends a packet locally and to a specified other network host as well."""
        now = datetime.datetime.now()
        time_string = now.strftime("%Y_%m_%d_%H_%M_%S.%f")
        msg = f"{time_string}:{msg}".strip()
        if ip != "127.0.0.1":
            self.trace_sock.sendto(bytes(msg, "ascii"), ("127.0.0.1", port))  # redirect local as well
        self.trace_sock.sendto(bytes(msg, "ascii"), (ip, port))

