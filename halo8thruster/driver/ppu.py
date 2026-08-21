from halo8thruster.driver.console import Console
from halo8thruster.driver.comms import Comms
from halo8thruster.driver.state import State
from halo8thruster.driver.mr_logger import MrLogger, LogType

class PPU():
    def __init__(self, ):
        self.mr = MrLogger("logs")
        self.com = Comms(self.mr)
        self.state = State(self.com)

        


if __name__ == "__main__":
    print("this class is supposed to be overridden when writing a script. checkout the docs!")

