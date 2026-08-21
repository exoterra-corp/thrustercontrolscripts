import threading

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Input, RichLog, Static

from halo8thruster.driver.mr_logger import LogType

# HSI fields grouped for display in the telemetry table
_HSI_SECTIONS = [
    ("Keeper",  ["k_v_sepic", "k_v_in", "k_i_out", "k_dac_out", "k_last_err", "k_cur_oft", "k_msg_cnt", "k_can_err"]),
    ("Anode",   ["a_vx", "a_vy", "a_vout", "a_iout", "a_dac", "a_hs_temp", "a_last_err", "a_cur_oft", "a_msg_cnt", "a_can_err"]),
    ("Mag Out", ["mo_v_out", "mo_i_out", "mo_dac_out", "mo_last_err", "mo_msg_cnt", "mo_can_err"]),
    ("Mag In",  ["mi_v_out", "mi_i_out", "mi_dac_out", "mi_last_err", "mi_msg_cnt", "mi_can_err"]),
    ("Valves",  ["va_anode_v", "va_cathode_hf_v", "va_cathode_lf_v", "va_temperature",
                 "va_tank_pressure", "va_cathode_pressure", "va_anode_pressure",
                 "va_regulator_pressure", "va_msg_cnt", "va_can_err"]),
    ("HK",      ["hk_mA_28V", "hk_mV_14V", "hk_mA_14V", "hk_mV_7VA", "hk_mA_7VA"]),
    ("EFC",     ["count_meccemsb", "count_ueccemsb", "count_meccelsb", "count_ueccelsb"]),
    ("SYS-MEM", ["region_stat", "failed_repairs", "repair_stat"]),
]


class ConsoleApp(App):
    CSS = """
    Screen {
        layout: vertical;
        overflow: hidden;
    }

    #header-bar {
        height: 1;
        background: $primary-darken-2;
        color: $text;
        padding: 0 1;
    }

    #body {
        height: 1fr;
        layout: horizontal;
    }

    #left {
        width: 1fr;
        border: round $primary;
    }

    #console-log {
        height: 1fr;
    }

    #console-input {
        height: 3;
        dock: bottom;
    }

    #right {
        width: 1fr;
        layout: vertical;
    }

    #raw-pane {
        height: 1fr;
        border: round $accent;
    }

    #hsi-pane {
        height: 1fr;
        border: round $success;
    }
    """

    def __init__(self, console):
        super().__init__()
        self._con = console

    def compose(self) -> ComposeResult:
        if self._con._header is not None:
            yield Static(self._format_header(), id="header-bar")

        with Horizontal(id="body"):
            with Vertical(id="left"):
                yield RichLog(id="console-log", highlight=False, markup=False, wrap=True)
                yield Input(placeholder=">", id="console-input")

            if self._con._show_raw or self._con._show_hsi:
                with Vertical(id="right"):
                    if self._con._show_raw:
                        yield RichLog(id="raw-pane", highlight=False, markup=False, wrap=False)
                    if self._con._show_hsi:
                        yield DataTable(id="hsi-pane", show_cursor=False)

    def on_mount(self) -> None:
        if self._con._show_hsi:
            table = self.query_one("#hsi-pane", DataTable)
            table.border_title = "HSI Telemetry"
            table.add_column("Subsystem", key="subsystem", width=9)
            table.add_column("Field", key="field", width=24)
            table.add_column("Value", key="value", width=14)
            for section, fields in _HSI_SECTIONS:
                for i, field in enumerate(fields):
                    table.add_row(section if i == 0 else "", field, "—", key=field)
            self._con._mr.add_listener(LogType.HSI, self._on_hsi)

        if self._con._show_raw:
            self.query_one("#raw-pane", RichLog).border_title = "Raw CAN"
            self._con._mr.add_listener(LogType.RAW, self._on_raw)

        self._con._mr.add_listener(LogType.SYS, self._on_sys)

        log = self.query_one("#console-log", RichLog)
        log.border_title = "Console"
        self._con._write_help(log.write)

        self.query_one("#console-input", Input).focus()

    # --------------------------------------------------------- header

    def _format_header(self) -> str:
        if not self._con._header:
            return ""
        return "  |  ".join(f"{k}: {v}" for k, v in self._con._header.items())

    def refresh_header(self) -> None:
        self.query_one("#header-bar", Static).update(self._format_header())

    # --------------------------------------------------------- listeners (called from background threads)

    def _on_sys(self, msg, end="\n") -> None:
        try:
            self.call_from_thread(self.query_one("#console-log", RichLog).write, str(msg))
        except Exception:
            pass

    def _on_raw(self, msg: str) -> None:
        try:
            self.call_from_thread(self.query_one("#raw-pane", RichLog).write, msg)
        except Exception:
            pass

    def _on_hsi(self, parsed: dict) -> None:
        try:
            self.call_from_thread(self._update_hsi_table, parsed)
        except Exception:
            pass

    def _update_hsi_table(self, parsed: dict) -> None:
        table = self.query_one("#hsi-pane", DataTable)
        for field, value in parsed.items():
            try:
                table.update_cell(field, "value", str(value))
            except Exception:
                pass

    # --------------------------------------------------------- input

    def on_input_submitted(self, event: Input.Submitted) -> None:
        inp = event.value.strip().lower()
        event.input.clear()
        if not inp:
            return
        self._con._mr.log(LogType.SYS, inp, print_val=False)
        threading.Thread(target=self._con._dispatch, args=(inp,), daemon=True).start()

    def action_quit(self) -> None:
        threading.Thread(target=self._con._exit, args=(None,), daemon=True).start()
