from halo8thruster.driver.console import Console
from halo8thruster.driver.comms import Comms
from halo8thruster.driver.mr_logger import MrLogger, LogType

class Tester():
    def __init__(self):
        self.cmds = {"2": {"name": "thing", "func": self.thing, "help": ""},}
        self.mr = MrLogger("logs")
        self.com = Comms(self.mr)
        self.c = Console(self.mr,self.cmds)
        self.c.start_console()


    def thing(self, args):
        val = self.com.read(0x4000, 0, "<B")
        print(val)

def main():
    Tester()

if __name__ == "__main__":
    main()