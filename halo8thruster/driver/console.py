from halo8thruster.driver.mr_logger import LogType
from halo8thruster.driver.exceptions import PPUError

class Console():
    def __init__(self, mr_logger,console_table:dict):
        #default cmds, the console table passed in appends to this to fill it out
        self.default_console_table = {
            "0": {"name": "Exit", "func": self.exit, "help": "Exits the Program"},
            "1": {"name": "Help", "func": self.help, "help": "Displays the help Menu"},
        }
        self.mr_logger = mr_logger
        self.default_console_table |= console_table
        self.running = True
        pass

    def start_console(self, ):
        self.help(None)
        while self.running:
            try:
                self.mr_logger.log(LogType.SYS, f">", end='', print_val=False)
                inp = input(f">").lower().strip()
                self.mr_logger.log(LogType.SYS, f"{inp}", end='', print_val=False)
                if inp in self.default_console_table.keys():
                    cmd = self.default_console_table.get(inp)
                    func = cmd.get("func")
                    args = cmd.get("args")
                    name = cmd.get("name")
                    if func != None:
                        self.mr_logger.log(LogType.SYS,f"{name}")
                        try:
                            func(args)
                        except PPUError as e:
                            self.mr_logger.log(LogType.SYS, f"[{type(e).__name__}] {e}")
                        except Exception as e:
                            self.mr_logger.log(LogType.SYS, f"[Error] {e}")
            except KeyboardInterrupt as e:
                self.exit(None)
            except EOFError:
                self.exit(None)
                
    def register_func(self, key, name, func, help):
        self.default_console_table[key] = {"name": name, "func": func, "help": help}

    def help(self, args):
        """
        help, reads the predefined cmds and prints them in a table.
        """
        for v in self.default_console_table:
            x = self.default_console_table.get(v)
            self.mr_logger.log(LogType.SYS, f"{v} - {x.get('name')} : [{x.get('help')}]")

    def exit(self, args):
        """
        exit, exits the program.
        """
        self.mr_logger.close()
        self.running = False


    def get_write_value(self, comms, args):
        """
        Prompt the user for a value and write it via comms, or write a default if one is set.
        args keys: index, subindex, type, default (optional).
        Values may be decimal ("26") or hex ("0x1A") — comms.write auto-detects.
        """
        if args is None:
            return
        index = args.get("index")
        subindex = args.get("subindex")
        python_type = args.get("type")
        default = args.get("default")

        if index is None or subindex is None or python_type is None:
            return

        if default is not None:
            comms.write(index, subindex, default, python_type)
            return

        while True:
            self.mr_logger.log(LogType.SYS, "Enter value to send (decimal or 0x hex) - or 'x' to cancel.")
            inp = input("write> ")
            if inp.lower() in ("back", "x"):
                return
            if index == 0x4000 and (subindex == 2 or subindex == 9):
                print("Set a burn duration timeout? (0 for none, or seconds up to 65535):")
                timeout = input("timeout in seconds> ")
                if timeout.lower() in ("back", "x"):
                    return
                try:
                    inp = str(int(inp, 0) + (int(timeout) << 16))
                except ValueError:
                    self.mr_logger.log(LogType.SYS, "Invalid value — enter a number.")
                    continue
            if inp:
                comms.write(index, subindex, inp, python_type)
                return