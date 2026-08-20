from halo8thruster.driver.console import Console
from halo8thruster.driver.mr_logger import MrLogger, LogType

ct = {}

if __name__ == "__main__":
    mr = MrLogger("logs")
    c = Console(mr,{})
    c.start_console()