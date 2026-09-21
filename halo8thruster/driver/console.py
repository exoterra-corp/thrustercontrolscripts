from halo8thruster.driver.mr_logger import LogType
from halo8thruster.driver.comms import Comms
from halo8thruster.driver.exceptions import PPUError
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
import threading


class Console:
    """
    Interactive REPL console with optional textual TUI.

    Plain mode (default): uses prompt_toolkit for dynamic prompt updates, no extra UI overhead.
    TUI mode (set header, show_raw, or show_hsi): launches a textual app with a
    header bar, console pane, and optional raw CAN / decoded HSI panes.
    """

    def __init__(self, 
                 mr_logger, 
                 comms: Comms,
                 commands, *,
                 header: dict | None = None,
                 show_raw: bool = False,
                 show_hsi: bool = False,
                 show_trace: bool = False):
        """
        mr_logger   MrLogger instance
        comms       Instance of the comms class to call for get write value
        commands    dict of {key: {name, func, help[, args][, group]}}
        header      initial {label: value} pairs shown in the header bar (TUI only)
        show_raw    show scrolling raw CAN packet pane (TUI only)
        show_hsi    show live decoded HSI telemetry table (TUI only)
        show_trace  show scrolling trace message pane (TUI only)
        """
        self._mr = mr_logger
        self._comms = comms
        self._header = dict(header) if header is not None else None
        self._show_raw = show_raw
        self._show_hsi = show_hsi
        self._show_trace = show_trace
        self._tui_mode = (header is not None) or show_raw or show_hsi or show_trace
        self._app = None
        self._args = ""
        
        # For prompt_toolkit plain mode
        self._prompt_session = None
        self._prompt_lock = threading.Lock()
        self._running = False

        # a list of functions to call before exiting
        self._exit_funcs = []

        self._table = {
            "0": {"name": "exit", "func": self._exit, "help": "exit the program"},
            "1": {"name": "help", "func": self._help, "help": "show this help"},
        }
        self._table.update(commands)

    # ------------------------------------------------------------------ public

    def start(self):
        """Launch either TUI or plain mode with prompt_toolkit."""
        if self._tui_mode:
            from halo8thruster.driver._console_tui import ConsoleApp
            self._app = ConsoleApp(self)
            self._app.run()
        else:
            self._run_plain_with_prompt_toolkit()

    def register_exit_func(self, func):
        """
        functions can be registered to be called on exit or cntrl-c
        """
        self._exit_funcs.append(func)

    def update_cmds(self, cmds: dict):
        """
        Adds the commands to the table after init.
        """
        self._table.update(cmds)
    
    def update_status_args(self, args: str):
        """
        Thread-safe update of the prompt args. Updates in real-time while user is typing.
        Works in both plain and TUI modes.
        """
        with self._prompt_lock:
            self._args = args
        
        # In TUI mode, notify the app to refresh
        if self._app is not None:
            self._app.call_from_thread(self._app.refresh_header)

    def update_header(self, key: str, value):
        """Thread-safe update of a header field value. No-op in plain mode."""
        if self._header is None:
            return
        self._header[key] = str(value)
        if self._app is not None:
            self._app.call_from_thread(self._app.refresh_header)

    # --------------------------------------------------------------- internals

    def _get_prompt(self) -> str:
        """
        Safely get the current prompt string with args.
        Thread-safe via lock.
        """
        with self._prompt_lock:
            return f"{self._args}> "

    def _resolve(self, inp: str) -> dict | None:
        if inp in self._table:
            return self._table[inp]
        for cmd in self._table.values():
            if cmd.get("name", "").lower() == inp:
                return cmd
        return None

    def _dispatch(self, inp: str):
        cmd = self._resolve(inp)
        if cmd is None:
            return
        func = cmd.get("func")
        args = cmd.get("args")
        if func is None:
            return
        self._mr.log(LogType.SYS, cmd.get("name", ""))
        try:
            v = func(args) if args is not None else func()
            if v is not None:
                self._mr.sys(str(v))
        except PPUError as e:
            self._mr.log(LogType.SYS, f"[{type(e).__name__}] {e}")
        except Exception as e:
            self._mr.log(LogType.SYS, f"[Error] {e}")

    def _write_help(self, output_fn):
        """Write help lines by calling output_fn(line) for each one."""
        seen_groups: dict = {}
        for key, cmd in self._table.items():
            g = cmd.get("group")
            if g not in seen_groups:
                seen_groups[g] = []
            seen_groups[g].append((key, cmd))

        order = [None] + [g for g in seen_groups if g is not None]
        for g in order:
            if g not in seen_groups:
                continue
            if g is not None:
                output_fn(f"--- {g} ---")
            for key, cmd in seen_groups[g]:
                name = cmd.get("name", "")
                label = f"{key}|{name}" if name else key
                output_fn(f"  {label:<20} : {cmd.get('help', '')}")

    def _help(self, args=None):
        self._write_help(lambda msg: self._mr.log(LogType.SYS, msg))

    def _exit(self, args=None):
        for f in self._exit_funcs:
            f()
        self._running = False
        self._mr.close()
        if self._app is not None:
            self._app.exit()

    def _run_plain_with_prompt_toolkit(self):
        """
        Plain mode using prompt_toolkit for dynamic prompt updates.
        Allows other threads to update the prompt (args) while user is typing.
        Uses patch_stdout() to prevent log output from interfering with input.
        """
        self._prompt_session = PromptSession()
        self._running = True
        self._help(None)
        
        while self._running:
            try:
                with patch_stdout():
                    # Get current prompt (thread-safe)
                    prompt_text = self._get_prompt()
                    
                    # PromptSession.prompt() is blocking, but prompt_toolkit handles
                    # it gracefully. The prompt will update on the next keystroke
                    # if update_status_args() is called from another thread.
                    inp = self._prompt_session.prompt(
                        prompt_text,
                        # Optional: add color/styling here if desired
                    ).lower().strip()
                
                # Log the input
                self._mr.log(LogType.SYS, inp, print_val=False)
                
                # Dispatch the command
                self._dispatch(inp)
                
            except KeyboardInterrupt:
                self._mr.log(LogType.SYS, "\n[Interrupted]")
                self._exit(None)
            except EOFError:
                self._mr.log(LogType.SYS, "\n[EOF]")
                self._exit(None)
            except Exception as e:
                self._mr.log(LogType.SYS, f"[Error in prompt] {e}")

    def get_write_value(self, args):
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
            self._comms.write(index, subindex, default, python_type)
            return

        if self._prompt_session is None:
            self._mr.sys("This command needs a value and isn't supported in TUI mode "
                          "(no interactive prompt available) — set a 'default' or run without --tui.")
            return

        while True:
            self._mr.log(LogType.SYS, "Enter value to send (decimal or 0x hex) - or 'x' to cancel.")
            try:
                with patch_stdout():
                    inp = self._prompt_session.prompt("write> ")
            except (KeyboardInterrupt, EOFError):
                return
            
            if inp.lower() in ("back", "x"):
                return
            if inp:
                self._comms.write(index, subindex, inp, python_type)
                return