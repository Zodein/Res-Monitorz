from info import Info, SubInfo, default_text
import flet as ft
import time
import psutil
from threading import Thread


class CpuInfo(Info):
    info_id = "CPU"

    def __init__(self, event_fallback, config, update_time=0.5):
        self.event_fallback = event_fallback
        self.bgcolor = ft.colors.TEAL_600
        self.title = "CPU"
        self.info_id = "CPU"
        self.update_time = update_time
        self.running = True
        self.cpu_percent = 0.0
        self.thread = Thread(target=self.cpu_update_loop)
        self.thread.start()
        self.subinfos = [
            SubInfo("cpu_usage", "Usage", default_text(), True),
            SubInfo("mem_usage", "Memory Usage", default_text(), True),
        ]
        super().__init__(event_fallback, config)

    def cpu_update_loop(self):
        while self.running:
            self.cpu_percent = psutil.cpu_percent()
            time.sleep(self.update_time)

    def kill(self):
        self.running = False
        self.thread.join()

    def update(self):
        for info in self.subinfos:
            if not info.active:
                continue
            if info.info_id == "cpu_usage":
                info.text.value = "{:02}".format(int(self.cpu_percent))
            elif info.info_id == "mem_usage":
                info.text.value = "{:02}".format(int(psutil.virtual_memory().percent))
