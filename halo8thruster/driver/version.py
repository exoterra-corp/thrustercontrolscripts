#!/usr/bin/python3
import datetime, os
from halo8thruster.driver.console import Console
from halo8thruster.driver.comms import Comms
from halo8thruster.driver.mr_logger import MrLogger, LogType

class Versions():
    def __init__(self):
        self.storage_path = "./logs/versions/"
        self.cmds = {
            "2": {"name": "read_sw_version", "func": self.read_sw_version, "help": "Read software versions"},
            "3": {"name": "read_hw_version", "func": self.read_hw_version, "help": "Read hardware version"},
        }
        self.mr = MrLogger("logs")
        self.com = Comms(self.mr)
        self.c = Console(self.mr, self.cmds)
        self.version_info_str = ["Thruster Control", "Keeper", "Anode", "Outer Magnet", "Inner Magnet", "Valves", "Thruster Control Bootloader"]
        self.c.start_console()

    def read_sw_version(self, args):
        os.makedirs(self.storage_path, exist_ok=True)
        now = datetime.datetime.now()
        time_string = now.strftime("%Y_%m_%d_%H_%M_%S")
        version_file = open(f"{self.storage_path}sw_version_{time_string}.txt", "w")
        version_file.write(f"========== Version Read Time {time_string} ==========\n")

        num_components = 7
        num_subindices = self.com.read(0x5000, 0, "noparse")

        header = "Id: Version  : gitsha   : git sha 1 : Exec V 1  : git sha 2 : Exec V 2  : git sha 3 : Exec V 3 : Device Name "
        self.mr.log(LogType.SYS, header)
        version_file.write(header + "\n")

        for i in range(num_components):
            device_name = self.version_info_str[i] if i < len(self.version_info_str) else ""
            version_line = ""
            self.com.write(0x5000, 1, str(i), "<B", hex_en=False)
            for j in range(2, num_subindices[0]):
                v_g = bytearray(self.com.read(0x5000, j, "noparse"))
                v_g[0], v_g[1] = v_g[1], v_g[0]
                v_g[2], v_g[3] = v_g[3], v_g[2]
                v_g[0:2], v_g[2:4] = v_g[2:4], v_g[0:2]
                version_line += " : " + str(v_g.hex())
            line = f"{i}{version_line} : {device_name}"
            self.mr.log(LogType.SYS, line)
            version_file.write(line + "\n")
        version_file.close()

    def read_hw_version(self, args):
        val = self.com.read(0x1009, 0, "noparse")
        self.mr.log(LogType.SYS, f"HW Version: {val}")

def main():
    Versions()

if __name__ == "__main__":
    main()
