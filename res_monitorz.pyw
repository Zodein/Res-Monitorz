import psutil
import flet
import flet as ft
import time
from threading import Thread
import pystray as pys
from PIL import Image, ImageDraw
import info as inff
import gpu_info
import cpu_info
import network_info
import disk_info
import yaml


update_time = 0.5


def create_tray_image(width=64, height=64, color1="purple", color2="black"):
    image = Image.new("RGB", (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)
    return image


class MainWindow:
    config = None
    config_file = "config.yaml"
    infos = []

    def __init__(self):
        self.options_layout = None
        with open(self.config_file, "a+") as file:
            pass
        with open(self.config_file, "r+") as file:
            self.config = yaml.safe_load(file)
            if self.config is None:
                self.config = {}

        self.infos: list[inff.Info] = [info(self.active_on_change, self.config) for info in [cpu_info.CpuInfo, gpu_info.GpuInfo]]
        self.infos.extend(network_info.NetworkInfo(self.active_on_change, self.config, network_interface=k) for k in psutil.net_io_counters(pernic=True).keys())
        self.infos.extend(disk_info.DiskInfo(self.active_on_change, self.config, disk=k) for k in psutil.disk_io_counters(perdisk=True).keys())

    def active_on_change(self, e, info, subinfo):
        if info.info_id not in self.config:
            self.config[info.info_id] = {}
        self.config[info.info_id][subinfo.info_id] = subinfo.active = subinfo.layout.visible = e.control.value
        self.write_config()
        info.layout.visible = any([subinfo.active for subinfo in info.subinfos])

    def write_config(self):
        with open(self.config_file, "w") as file:
            yaml.dump(self.config, file)

    def start(self, page: ft.Page):
        self.page = page
        self.page.title = "Res Monitorz"
        self.page.vertical_alignment = "center"
        self.page.window.always_on_top = True
        self.page.window.frameless = True
        self.page.window.maximizable = False
        self.page.window.resizable = False
        self.page.window.width = 320
        self.page.window.height = 320
        self.page.spacing = 0
        self.page.padding = 0
        self.page.bgcolor = ft.colors.WHITE10
        self.page.window.skip_task_bar = True
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.scroll = True

        self.options_layout = ft.Column([info.options_layout for info in self.infos], visible=False)
        self.info_layout = ft.WindowDragArea(ft.Column([info.layout for info in self.infos], spacing=0))

        self.page.add(self.info_layout)
        self.page.add(self.options_layout)

        self.tray = pys.Icon("Res Monitorz", create_tray_image(), menu=pys.Menu(pys.MenuItem("Options", self.tray_options), pys.MenuItem("Quit", self.tray_quit)))
        Thread(target=self.tray.run).start()
        Thread(target=self.update_page).start()

    def tray_quit(self, icon, item):
        self.tray.stop()
        self.page.window.destroy()

    def tray_options(self, icon, item):
        self.options_layout.visible = not self.options_layout.visible

    def update_page(self):
        while self.page.loop.is_running():
            [info.update() for info in self.infos]
            self.page.update()
            time.sleep(update_time)


main_window = MainWindow()
flet.app(target=main_window.start)
[info.kill() for info in main_window.infos]
