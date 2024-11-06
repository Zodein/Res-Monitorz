import flet as ft


def default_text(size=30, font_family="Segoe UI", text_align="CENTER", width=100):
    return ft.Text(size=size, font_family=font_family, text_align=text_align, width=width)


class SubInfo:
    info_id = ""
    title = ""
    active = True

    def __init__(self, info_id, title, text, check_box, active=True):
        self.info_id = info_id
        self.title = title
        self.active = active
        self.text = text
        self.layout = text
        self.check_box = check_box


class Info:
    info_id = ""
    bgcolor = ft.colors.ORANGE_600
    title = ""
    layout = None
    options_layout = None
    subinfos: list[SubInfo] = []

    def __init__(self, event_fallback, config, update_time=0.5):
        self.read_config(config)
        for subinfo in self.subinfos:
            subinfo.check_box = ft.Checkbox(adaptive=True, label="", value=subinfo.active, on_change=lambda e, info=self, subinfo=subinfo: event_fallback(e, info, subinfo))
        self.options_layout = ft.Column(
            [
                ft.ListTile(
                    leading=subinfo.check_box,
                    title=ft.Text("{} - {}".format(self.title, subinfo.title), size=20, font_family="Segoe UI", text_align="LEFT", width=400),
                    toggle_inputs=True,
                    title_alignment="CENTER",
                    bgcolor=self.bgcolor,
                )
                for subinfo in self.subinfos
            ],
            spacing=0,
        )
        self.layout = ft.Container(
            ft.Row(
                self.get_layout(),
                alignment="center",
                spacing=0,
            ),
            bgcolor=self.bgcolor,
            height=64,
            visible=any(subinfo.active for subinfo in self.subinfos),
        )
        self.layout.visible = any([subinfo.active for subinfo in self.subinfos])
        for subinfo in self.subinfos:
            subinfo.layout.visible = subinfo.active
        return

    def kill(self):
        return

    def get_layout(self):
        return [ft.Text(self.title, size=15, font_family="Segoe UI", text_align="RIGHT", width=40), *[subinfo.text for subinfo in self.subinfos]]

    def update(self):
        return

    def read_config(self, config):
        if self.info_id not in config:
            config[self.info_id] = {}
        for subinfo in self.subinfos:
            if subinfo.info_id in config[self.info_id]:
                subinfo.active = config[self.info_id][subinfo.info_id]
            else:
                config[self.info_id][subinfo.info_id] = subinfo.active
        return
