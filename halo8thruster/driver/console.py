from halo8thruster.driver.mr_logger import LogType
from halo8thruster.driver.exceptions import PPUError

class Console():
    def __init__(self, mr_logger, console_table: dict):
        self.mr_logger = mr_logger
        self.running = True
        self.default_console_table = {
            "0": {"name": "exit", "func": self.exit, "help": "Exits the program"},
            "1": {"name": "help", "func": self.help, "help": "Displays the help menu"},
        }
        self.default_console_table |= console_table

    def _resolve(self, inp: str) -> dict | None:
        """Return the command dict for inp, matching on key or name (case-insensitive)."""
        if inp in self.default_console_table:
            return self.default_console_table[inp]
        for cmd in self.default_console_table.values():
            if cmd.get("name", "").lower() == inp:
                return cmd
        return None

    def start_console(self):
        self.help(None)
        while self.running:
            try:
                self.mr_logger.log(LogType.SYS, ">", end='', print_val=False)
                inp = input(">").lower().strip()
                self.mr_logger.log(LogType.SYS, inp, end='', print_val=False)
                cmd = self._resolve(inp)
                if cmd is not None:
                    func = cmd.get("func")
                    try:
                        args = cmd.get("args")
                    except Exception:
                        args = None
                    name = cmd.get("name")
                    if func is not None:
                        self.mr_logger.log(LogType.SYS, name)
                        try:
                            v = func(args) if args is not None else func()
                            if v is not None:
                                self.mr_logger.sys(v)
                        except PPUError as e:
                            self.mr_logger.log(LogType.SYS, f"[{type(e).__name__}] {e}")
                        except Exception as e:
                            self.mr_logger.log(LogType.SYS, f"[Error] {e}")
            except KeyboardInterrupt:
                self.exit(None)
            except EOFError:
                self.exit(None)

    def register_func(self, key, name, func, help, group=None):
        entry = {"name": name, "func": func, "help": help}
        if group is not None:
            entry["group"] = group
        self.default_console_table[key] = entry

    def help(self, args):
        """Print commands grouped by their 'group' field; ungrouped commands appear first."""
        table = self.default_console_table

        # Collect groups in insertion order; None = no group (printed first as "General")
        seen_groups = {}
        for key, cmd in table.items():
            g = cmd.get("group")
            if g not in seen_groups:
                seen_groups[g] = []
            seen_groups[g].append((key, cmd))

        # Print ungrouped first, then named groups
        order = [None] + [g for g in seen_groups if g is not None]
        for g in order:
            if g not in seen_groups:
                continue
            entries = seen_groups[g]
            if g is not None:
                self.mr_logger.log(LogType.SYS, f"--- {g} ---")
            for key, cmd in entries:
                name = cmd.get("name", "")
                label = f"{key}|{name}" if name else key
                self.mr_logger.log(LogType.SYS, f"  {label:<20} : {cmd.get('help', '')}")

    def exit(self, args):
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
