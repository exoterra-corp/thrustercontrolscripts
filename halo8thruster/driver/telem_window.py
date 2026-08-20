import threading
import webbrowser
import time
from flask import Flask, jsonify

"""
Flask-based replacement for HSIExcelWindow.
Exposes the same write_display(row, col, val) interface but
hosts a webpage instead of a wx grid.  Open http://localhost:5050
in any browser — it polls /data every 500 ms automatically.
"""

SECTIONS = [
    {"name": "Keeper",       "data_row": 1,  "labels": ["VSEPIC (mV)", "VIN (mV)", "IOUT (mA)", "DAC (counts)", "LASTERR", "CUR_OFT (counts)", "MSG_CNT", "CAN_ERR"]},
    {"name": "Anode",        "data_row": 4,  "labels": ["VX (mV)", "VY (mV)", "VOUT (mV)", "IOUT (mA)", "DAC (counts)", "LASTERR", "CUR_OFT (counts)", "HS_TEMP", "MSG_CNT", "CAN_ERR"]},
    {"name": "Magnet Outer", "data_row": 7,  "labels": ["VOUT (mV)", "IOUT (mA)", "DAC (counts)", "LASTERR", "MSG_CNT", "CAN_ERR"]},
    {"name": "Magnet Inner", "data_row": 10, "labels": ["VOUT (mV)", "IOUT (mA)", "DAC (counts)", "LASTERR", "MSG_CNT", "CAN_ERR"]},
    {"name": "Valves",       "data_row": 13, "labels": ["ANODE_V (mV)", "CAT_HF_V (mV)", "CAT_LF_V (mV)", "TEMP (C)", "TANK_PRESSURE (mPSI)", "CAT_PRESSURE (mPSI)", "ANODE_PRESSURE (mPSI)", "REG_PRESSURE m(PSI)", "MSG_CNT", "CAN_ERR"]},
    {"name": "HK",           "data_row": 16, "labels": ["CURRENT_28V (mA)", "VOLTAGE_14V (mV)", "CURRENT_14V (mA)", "VOLTAGE_7A (mV)", "CURRENT_7A (mA)"]},
    {"name": "EFC",          "data_row": 19, "labels": ["CNT_MECCEMSB", "CNT_UECCEMSB", "CNT_MECCELSB", "CNT_UECCELSB"]},
    {"name": "SYS-MEM",      "data_row": 22, "labels": ["REGION_STAT", "FAILED_REPAIRS", "REPAIR_STAT"]},
]

_HTML = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>HSI Monitor</title>
  <style>
    body { font-family: monospace; background: #1e1e1e; color: #d4d4d4; margin: 20px; }
    h1   { font-size: 1.1em; color: #9cdcfe; margin-bottom: 16px; }
    table { border-collapse: collapse; margin-bottom: 18px; }
    th   { background: #2d2d2d; color: #9cdcfe; padding: 4px 10px; text-align: left;
           border: 1px solid #444; font-size: 0.8em; }
    td   { padding: 4px 10px; border: 1px solid #333; font-size: 0.85em; }
    .section-header { background: #252526; color: #ce9178; font-weight: bold;
                      font-size: 0.9em; padding: 6px 8px; }
    .val { color: #b5cea8; }
    .stale { color: #555; }
    #status { font-size: 0.75em; color: #608b4e; margin-bottom: 12px; }
  </style>
</head>
<body>
  <h1>HSI Realtime Monitor</h1>
  <div id="status">connecting...</div>
  <div id="tables"></div>
  <script>
    const SECTIONS = """ + str([{"name": s["name"], "data_row": s["data_row"], "labels": s["labels"]} for s in SECTIONS]).replace("'", '"') + """;

    // build tables once
    const container = document.getElementById('tables');
    const cells = {};  // "row,col" -> td element

    SECTIONS.forEach(sec => {
      const wrap = document.createElement('div');
      const hdr  = document.createElement('div');
      hdr.className = 'section-header';
      hdr.textContent = sec.name;
      wrap.appendChild(hdr);

      const tbl = document.createElement('table');
      const thead = tbl.createTHead();
      const tr_h  = thead.insertRow();
      sec.labels.forEach(lbl => {
        const th = document.createElement('th');
        th.textContent = lbl;
        tr_h.appendChild(th);
      });

      const tbody = tbl.createTBody();
      const tr_d  = tbody.insertRow();
      sec.labels.forEach((_, col) => {
        const td = tr_d.insertCell();
        td.className = 'val stale';
        td.textContent = '—';
        cells[sec.data_row + ',' + col] = td;
      });

      wrap.appendChild(tbl);
      container.appendChild(wrap);
    });

    // poll for updates
    async function poll() {
      try {
        const r = await fetch('/data');
        const d = await r.json();
        Object.entries(d).forEach(([key, val]) => {
          const td = cells[key];
          if (td) { td.textContent = val; td.classList.remove('stale'); }
        });
        document.getElementById('status').textContent =
          'last update: ' + new Date().toLocaleTimeString();
      } catch(e) {
        document.getElementById('status').textContent = 'connection lost...';
      }
    }
    poll();
    setInterval(poll, 500);
  </script>
</body>
</html>
"""


class FlaskHSIWindow:
    """Drop-in replacement for HSIExcelWindow — same write_display() interface."""

    PORT = 5050

    def __init__(self):
        self._data = {}          # "row,col" -> str value
        self._app = Flask(__name__)
        self._app.logger.disabled = True
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        @self._app.route('/')
        def index():
            return _HTML

        @self._app.route('/data')
        def data():
            return jsonify(self._data)

        t = threading.Thread(target=self._serve, daemon=True)
        t.start()
        # give the server a moment then open browser
        threading.Thread(target=self._open_browser, daemon=True).start()
        print(f"HSI web monitor: http://localhost:{self.PORT}")

    def _serve(self):
        self._app.run(host='127.0.0.1', port=self.PORT, use_reloader=False, threaded=True)

    def _open_browser(self):
        time.sleep(0.8)
        webbrowser.open(f'http://localhost:{self.PORT}')

    def write_display(self, row, col, val):
        self._data[f'{row},{col}'] = str(val)
