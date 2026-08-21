from halo8thruster.driver.comms import Comms
from halo8thruster.driver.state import State, TCS, NMTD
from halo8thruster.driver.mr_logger import MrLogger
from halo8thruster.driver.exceptions import ConnectionError
from threading import Thread

class PPU():
    """
    Base class for PPU scripts. Wires up MrLogger, Comms, and State.
    Override this class in your script and add commands to self.cmds before
    passing them to Console.

    Can also be used as a context manager to ensure the connection is closed:
        with MyScript() as s:
            ...
    """

    def __init__(self, serial_port="/dev/ttyUSB0", system_id=0x22, log_name="", gather=False,debug=False):
        self.mr = MrLogger("logs", log_name)
        try:
            self.com = Comms(self.mr, serial_port=serial_port, system_id=system_id, debug=debug)
        except ConnectionError as e:
            self.mr.sys(f"Failed to connect: {e}")
            raise
        self.state = State(self.com, self.mr)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.com.disconnect()

    def gather(self):
        """
        gathers, status, trace and telemetry on a threaded loop
        """
        thruster_status = self.state.thruster_state_read()
        trace_msg = self.state.trace_read()
        block_telem = self.state.block_telem_read()
        pass
    
def parse_ppu_args(description=""):
    import argparse
    p = argparse.ArgumentParser(description=description)
    p.add_argument("serial_port", nargs="?", default="/dev/ttyUSB0")
    p.add_argument("system_id", nargs="?",  default="0x22")
    a = p.parse_args()
    return a.serial_port, int(a.system_id, 0)

if __name__ == "__main__":
    print("This class is meant to be subclassed by your script. See the docs.")
