from info import Info, SubInfo, default_text
import flet as ft
import psutil
import time
from threading import Thread


class NetworkInfo(Info):
    def __init__(self, event_fallback, config, network_interface, update_time=0.5):
        self.event_fallback = event_fallback
        self.bgcolor = ft.colors.BLUE_GREY_600
        self.title = network_interface
        self.update_time = update_time
        self.network_interface = network_interface
        self.info_id = network_interface
        self.running = True
        self.down = 0.0
        self.up = 0.0
        self.thread = Thread(target=self.network_update_loop)
        self.thread.start()
        self.subinfos = [
            SubInfo("down", "Download Per Sec", default_text(), True),
            SubInfo("up", "Upload Per Sec", default_text(), True),
        ]
        super().__init__(event_fallback, config)

    def network_update_loop(self):
        last = (time.time(), 0, 0)
        while self.running:
            info = psutil.net_io_counters(pernic=True)
            if self.network_interface not in info:
                time.sleep(self.update_time)
                continue
            info = info[self.network_interface]
            info_time = time.time()
            if info_time == last[0]:
                continue
            self.down = (info.bytes_recv - last[1]) / (info_time - last[0]) / (1024 * 1024)
            self.up = (info.bytes_sent - last[2]) / (info_time - last[0]) / (1024 * 1024)
            last = (info_time, info.bytes_recv, info.bytes_sent)
            time.sleep(self.update_time)

    def kill(self):
        self.running = False
        self.thread.join()

    def update(self):
        for info in self.subinfos:
            if not info.active:
                continue
            if info.info_id == "down":
                info.text.value = "{:0.2f}".format(self.down)
            elif info.info_id == "up":
                info.text.value = "{:0.2f}".format(self.up)
