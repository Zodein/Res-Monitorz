from info import Info, SubInfo, default_text
import flet as ft
import pynvml


class GpuInfo(Info):
    info_id = "GPU"

    def __init__(self, event_fallback, config, update_time=0.5):
        self.event_fallback = event_fallback
        self.bgcolor = ft.colors.GREEN_600
        self.title = "GPU"
        self.info_id = "GPU"
        self.update_time = update_time
        self.handle = None
        pynvml.nvmlInit()
        if pynvml.nvmlDeviceGetCount() == 1:
            self.gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        self.subinfos = [
            SubInfo("gpu_usage", "Usage", default_text(), True),
            SubInfo("gpu_mem_usage", "Memory Usaage", default_text(), True),
        ]
        super().__init__(event_fallback, config)

    def kill(self):
        pynvml.nvmlShutdown()

    def update(self):
        _info = pynvml.nvmlDeviceGetMemoryInfo(self.gpu_handle)
        for info in self.subinfos:
            if not info.active:
                continue
            if info.info_id == "gpu_usage":
                info.text.value = "{:02}".format(pynvml.nvmlDeviceGetUtilizationRates(self.gpu_handle).gpu)
            elif info.info_id == "gpu_mem_usage":
                info.text.value = "{:02}".format(int(_info.used / _info.total * 100))
