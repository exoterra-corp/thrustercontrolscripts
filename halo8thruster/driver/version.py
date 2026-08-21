import datetime, os
from halo8thruster.driver.comms import Comms
from halo8thruster.driver.mr_logger import MrLogger, LogType
from halo8thruster.driver.exceptions import CommsError

_COMPONENT_NAMES = [
    "Thruster Control",
    "Keeper",
    "Anode",
    "Outer Magnet",
    "Inner Magnet",
    "Valves",
    "Thruster Control Bootloader",
]

class Version():
    """Reads and logs software and hardware version information from the PPU."""

    def __init__(self, comms: Comms, mr_logger: MrLogger):
        self.com = comms
        self.mr = mr_logger
        self.storage_path = "./logs/versions/"

    def read_sw(self, args=None):
        """Read software versions for all components and write to a timestamped file."""
        os.makedirs(self.storage_path, exist_ok=True)
        time_string = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        with open(f"{self.storage_path}sw_version_{time_string}.txt", "w") as version_file:
            version_file.write(f"========== Version Read Time {time_string} ==========\n")
            header = "Id: Version  : gitsha   : git sha 1 : Exec V 1  : git sha 2 : Exec V 2  : git sha 3 : Exec V 3 : Device Name"
            self.mr.sys(header)
            version_file.write(header + "\n")

            try:
                num_subindices = self.com.read(0x5000, 0, "noparse")
            except CommsError as e:
                self.mr.sys(f"Version read failed: {e}")
                return

            for i in range(7):
                device_name = _COMPONENT_NAMES[i] if i < len(_COMPONENT_NAMES) else ""
                try:
                    self.com.write(0x5000, 1, i, "<B")
                    version_line = ""
                    for j in range(2, num_subindices[0]):
                        v_g = bytearray(self.com.read(0x5000, j, "noparse"))
                        v_g[0], v_g[1] = v_g[1], v_g[0]
                        v_g[2], v_g[3] = v_g[3], v_g[2]
                        v_g[0:2], v_g[2:4] = v_g[2:4], v_g[0:2]
                        version_line += " : " + v_g.hex()
                    line = f"{i}{version_line} : {device_name}"
                except CommsError as e:
                    line = f"{i} : READ ERROR ({e}) : {device_name}"
                self.mr.sys(line)
                version_file.write(line + "\n")

    def read_hw(self, args=None):
        """Read and log the hardware version string."""
        val = self.com.read(0x1009, 0, "noparse")
        self.mr.sys(f"HW Version: {val}")
