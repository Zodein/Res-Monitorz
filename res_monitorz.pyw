import flet
import flet as ft
import threading
import psutil
import time
import pynvml
from threading import Thread

import pystray as pys
from PIL import Image, ImageDraw

update_time = 0.5


def create_tray_image(width=64, height=64, color1="purple", color2="black"):
    image = Image.new("RGB", (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)
    return image


def default_text(size=30, font_family="Segoe UI", text_align="CENTER", width=100):
    return ft.Text(size=size, font_family=font_family, text_align=text_align, width=width)


class Info:
    bgcolor = ft.colors.ORANGE_600
    title = ""
    texts = {}

    def kill(self):
        return

    def get_layout(self):
        return [ft.Text(self.title, size=15, font_family="Segoe UI", text_align="RIGHT", width=40), *self.texts.values()]

    def update(self):
        return


class CpuInfo(Info):
    def __init__(self, update_time=0.5):
        self.bgcolor = ft.colors.TEAL_600
        self.title = "CPU"
        self.update_time = update_time
        self.running = True
        self.cpu_percent = 0.0
        self.thread = Thread(target=self.cpu_update_loop)
        self.thread.start()
        self.texts = {}
        for i in ["cpu_usage_text", "mem_usage_text"]:
            self.texts[i] = default_text()

    def cpu_update_loop(self):
        while self.running:
            self.cpu_percent = psutil.cpu_percent()
            time.sleep(self.update_time)

    def kill(self):
        self.running = False
        self.thread.join()

    def update(self):
        self.texts["cpu_usage_text"].value = "{:02}".format(int(self.cpu_percent))
        self.texts["mem_usage_text"].value = "{:02}".format(int(psutil.virtual_memory().percent))


class GpuInfo(Info):
    def __init__(self, update_time=0.5):
        self.bgcolor = ft.colors.GREEN_600
        self.title = "GPU"
        self.update_time = update_time
        self.handle = None
        pynvml.nvmlInit()
        if pynvml.nvmlDeviceGetCount() == 1:
            self.gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        self.texts = {}
        for i in ["gpu_usage_text", "gpu_mem_usage_text"]:
            self.texts[i] = default_text()

    def kill(self):
        pynvml.nvmlShutdown()

    def update(self):
        info = pynvml.nvmlDeviceGetMemoryInfo(self.gpu_handle)
        self.texts["gpu_usage_text"].value = "{:02}".format(pynvml.nvmlDeviceGetUtilizationRates(self.gpu_handle).gpu)
        self.texts["gpu_mem_usage_text"].value = "{:02}".format(int(info.used / info.total * 100))


class NetworkInfo(Info):
    def __init__(self, update_time=0.5):
        self.bgcolor = ft.colors.BLUE_GREY_600
        self.title = "NET"
        self.update_time = update_time
        self.running = True
        self.down = 0.0
        self.up = 0.0
        self.thread = Thread(target=self.network_update_loop)
        self.thread.start()
        self.texts = {}
        for i in ["down_text", "up_text"]:
            self.texts[i] = default_text()

    def network_update_loop(self):
        info = psutil.net_io_counters()
        last = (time.time(), info.bytes_recv, info.bytes_sent)
        while self.running:
            info = psutil.net_io_counters()
            info_time = time.time()
            self.down = (info.bytes_recv - last[1]) / (info_time - last[0]) / (1024 * 1024)
            self.up = (info.bytes_sent - last[2]) / (info_time - last[0]) / (1024 * 1024)
            last = (info_time, info.bytes_recv, info.bytes_sent)
            time.sleep(self.update_time)

    def kill(self):
        self.running = False
        self.thread.join()

    def update(self):
        self.texts["down_text"].value = "{:0.2f}".format(self.down)
        self.texts["up_text"].value = "{:0.2f}".format(self.up)


class MainWindow:
    page = None
    infos: list[Info] = [info() for info in [CpuInfo, GpuInfo, NetworkInfo]]

    @staticmethod
    def init(page: ft.Page):
        MainWindow.page = page
        MainWindow.page.title = "Res Monitorz"
        MainWindow.page.vertical_alignment = "center"
        MainWindow.page.window.always_on_top = True
        MainWindow.page.window.frameless = True
        MainWindow.page.window.maximizable = False
        MainWindow.page.window.resizable = False
        MainWindow.page.window.width = 240
        MainWindow.page.window.height = 192
        MainWindow.page.spacing = 0
        MainWindow.page.padding = 0
        MainWindow.page.bgcolor = ft.colors.BLUE_600
        MainWindow.page.window.skip_task_bar = True
        MainWindow.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        MainWindow.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        MainWindow.page.add(
            *[
                ft.WindowDragArea(
                    ft.Container(
                        ft.Row(
                            info.get_layout(),
                            alignment="center",
                            spacing=0,
                        ),
                        bgcolor=info.bgcolor,
                        height=64
                    )
                )
                for info in MainWindow.infos
            ]
        )

        def tray_quit(icon, item):
            tray.stop()
            MainWindow.page.window.destroy()

        tray = pys.Icon("Res Monitorz", create_tray_image(), menu=pys.Menu(pys.MenuItem("Quit", tray_quit)))
        Thread(target=tray.run).start()

        thread = Thread(target=MainWindow.update_page)
        thread.start()

    def update_page():
        while MainWindow.page.loop.is_running():
            [info.update() for info in MainWindow.infos]
            MainWindow.page.update()
            time.sleep(update_time)


flet.app(target=MainWindow.init)
[info.kill() for info in MainWindow.infos]
