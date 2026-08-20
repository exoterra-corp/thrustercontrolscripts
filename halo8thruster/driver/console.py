from halo8thruster.driver.mr_logger import LogType

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
                        except Exception as e:
                            self.mr_logger.log(LogType.SYS,f"{e}")
            except KeyboardInterrupt as e:
                self.exit(None)
            except EOFError:
                self.exit(None)
                
    def register_func(self, name, func, help):
        None

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


    def get_write_value(self, args):
        """
        get_write_value, looks for a default value and if one is found just writes it, otherwise its prompts the user
        for a hex value to write.
        """
        index = args.get("index")
        subindex = args.get("subindex")
        python_type = args.get("type")
        default = args.get("default")
        hex_en = args.get("hex_en")
        val_type_str = "decimal"

        if hex_en is not None and hex_en is not False:
            val_type_str = "hex"
            hex_en = True
        else:
            hex_en = False

        valid = False
        if index != None and subindex != None and python_type != None:
            if default is not None:  # if we have a default value just write it and dont prompt user.
                self.write(index, subindex, default, python_type, hex_en)
            else:
                while not valid:
                    self.mr_logger.log(LogType.SYS, f"Enter {val_type_str} value to send to ECP - or 'x' to return to previous menu.")
                    inp = input("write> ")
                    if inp.lower() == "back" or inp.lower() == "x":
                        return
                    # filter for steady state (2) or auto start (9) commands.  If it is either of these commands, they need a duration time
                    if index == 0x4000 and subindex == 2 or subindex == 9:
                        print("set a burn duration timeout? ( 0 for no, or timeout in seconds (max 65535)):")
                        timeout = input("timeout in seconds>")
                        if timeout.lower() == "back" or timeout.lower() == "x":
                            return
                        # python "shift" of 16 bits
                        inp = str(int(inp) + (int(timeout)<<16))                     
                    if len(inp) > 0:
                        self.write(index, subindex, inp, python_type, hex_en)
                        valid = True