from info import Info, SubInfo, default_text
import flet as ft
import psutil
import time
from threading import Thread


class DiskInfo(Info):
    def __init__(self, event_fallback, config, disk, update_time=0.5):
        self.event_fallback = event_fallback
        self.bgcolor = ft.colors.BLUE_GREY_600
        self.title = disk
        self.update_time = update_time
        self.disk = disk
        self.info_id = disk
        self.running = True
        self.read = 0.0
        self.write = 0.0
        self.thread = Thread(target=self.disk_update_loop)
        self.thread.start()
        self.subinfos = [
            SubInfo("write", "Write Per Sec", default_text(), True),
            SubInfo("read", "Read Per Sec", default_text(), True),
        ]
        super().__init__(event_fallback, config)

    def disk_update_loop(self):
        last = (time.time(), 0, 0)
        while self.running:
            info = psutil.disk_io_counters(perdisk=True)
            if self.disk not in info:
                time.sleep(self.update_time)
                continue
            info = info[self.disk]
            info_time = time.time()
            if info_time == last[0]:
                continue
            self.read = (info.read_bytes - last[1]) / (info_time - last[0]) / (1024 * 1024)
            self.write = (info.write_bytes - last[2]) / (info_time - last[0]) / (1024 * 1024)
            last = (info_time, info.read_bytes, info.write_bytes)
            time.sleep(self.update_time)

    def kill(self):
        self.running = False
        self.thread.join()

    def update(self):
        for info in self.subinfos:
            if not info.active:
                continue
            if info.info_id == "write":
                info.text.value = "{:02}".format(int(self.read))
            elif info.info_id == "read":
                info.text.value = "{:02}".format(int(self.write))
