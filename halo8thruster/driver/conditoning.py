from halo8thruster.driver.comms import Comms
from halo8thruster.driver.mr_logger import MrLogger, LogType
from halo8thruster.driver.defines import *

class Conditioning:
    def __init__(self, mr_logger: MrLogger, comms: Comms):
        self._mr = mr_logger
        self._comms = comms
    
    def start_conditioning(self, conditioning_val=1):
        self._mr.sys(f"Starting conditioning seq with: {conditioning_val}.")
        self._comms.write(IDX_THRUSTER_CMD, SUB_CONDITION, conditioning_val, "<I")

    def stop_conditioning(self):
        self._mr.sys(f"Stopping conditioning.")
        self._comms.write(IDX_THRUSTER_CMD, SUB_CONDITION, 0, "<I")
    
    def print_conditoning_stats(self):
        """
        print_conditoning_stats, 
        """
        count = self._comms.read(IDX_COND_STATS, 0x0, "<B")
        step = self._comms.read(IDX_COND_STATS, 0x1, "<I")
        step_status = self._comms.read(IDX_COND_STATS, 0x2, "<I")
        self._mr.log(LogType.SYS, count)
        r = int(count/3)
        for v in range(0, r-1):
            seq_stat_cond = self._comms.read(IDX_COND_STATS, 0x2 + (v*3), "<I")
            elapsed_ms = self._comms.read(IDX_COND_STATS, 0x3 + (v*3), "<I")
            monitor_err = self._comms.read(IDX_COND_STATS, 0x4 + (v*3), "<I")
            seq_stat_cond = '0x' + hex(seq_stat_cond)[2:].zfill(8)
            monitor_err = '0x' + hex(monitor_err)[2:].zfill(8)
            self._mr.log(LogType.SYS, f"[{v}] seq_stat_cond-{seq_stat_cond}, elapsed_ms-{elapsed_ms}, monitor_err-{monitor_err}")

    def erase_conditioning_stats(self):
        print("Erase Conditioning Stats?")
        erase = input("y/n> ")
        if erase == "y":
            self._mr.sys("Erasing Conditioning Stats...")
            self._comms.write(IDX_THRUSTER_CMD, SUB_COND_CLEAR, CMD_COND_CLEAR, "<I")
            self.print_conditoning_stats()
