import threading
import tqdm
from halo8thruster.driver.comms import Comms
from halo8thruster.driver.mr_logger import MrLogger
from halo8thruster.driver.exceptions import CommsTimeout
from halo8thruster.driver.od_defines import *

BOOTUP_TIMEOUT = 20.0

class Update:
    def __init__(self, comms: Comms, mr_logger: MrLogger):
        self.com = comms
        self.mr = mr_logger
        self._boot_event = threading.Event()

    def download(self, image_path: str) -> None:
        """Segment-download a firmware image to the device (OD 0x5500:1)."""
        with open(image_path, "rb") as f:
            data = f.read()
        total = len(data)
        self.mr.sys(f"Downloading {total} bytes from '{image_path}'…")

        with tqdm.tqdm(total=total, unit="B", unit_scale=True, desc="Flashing", ncols=70) as bar:
            prev = 0

            def _progress(sent, _total):
                nonlocal prev
                bar.update(sent - prev)
                prev = sent

            sent = self.com.write_blob_progress(IDX_UPDATE, UPDATE_SUB_DATA, data, progress_cb=_progress)

        if sent != total:
            raise RuntimeError(f"Download incomplete: {sent}/{total} bytes transferred")
        self.mr.sys("Download complete.")

    def verify(self) -> str:
        """Trigger CRC verify (0x5500:2) and return the 8-char hex result."""
        self.mr.sys("Verifying image…")
        self.com.write(IDX_UPDATE, UPDATE_SUB_VERIFY, 0, "<I")
        result = self.com.read(IDX_UPDATE, UPDATE_SUB_VERIFY)
        hex_result = result.hex().zfill(8)
        self.mr.sys(f"Verify result: 0x{hex_result}")
        return hex_result

    def install(self) -> bool:
        """Trigger flash (0x5500:3), wait for NMT bootup. Returns True on success."""
        self._boot_event.clear()
        self.com.subscribe_bootup(self._on_bootup)
        self.mr.sys("Installing image (device will reboot)…")
        try:
            self.com.write(IDX_UPDATE, UPDATE_SUB_INSTALL, 0, "<B")
        except CommsTimeout:
            pass  # expected — device reboots mid-SDO transfer
        if self._boot_event.wait(timeout=BOOTUP_TIMEOUT):
            self.mr.sys("Device booted successfully.")
            return True
        self.mr.sys(f"Device did not reboot within {BOOTUP_TIMEOUT:.0f}s.")
        return False

    def run(self, image_path: str, skip_download: bool = False) -> None:
        """Full sequence: download (unless skip_download) → verify → install."""
        if not skip_download:
            self.download(image_path)
        self.verify()
        if not self.install():
            raise TimeoutError("Device did not reboot after install.")

    def _on_bootup(self, msg):
        self._boot_event.set()
