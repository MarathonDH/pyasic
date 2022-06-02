import asyncio

import PySimpleGUI as sg
from tools.cfg_util.record.layout import record_window
from tools.cfg_util.record.func import (
    start_recording,
    stop_recording,
    pause_recording,
    resume_recording,
)


async def record_ui(ips: list):
    # if not len(ips) > 0:
    #     return
    while True:
        event, values = record_window.read(0.001)
        if event in (None, "Close", sg.WIN_CLOSED):
            break

        if event == "start_recording":
            if values["record_file"]:
                asyncio.create_task(start_recording(ips, values["record_file"]))
        if event == "stop_recording":
            asyncio.create_task(stop_recording())
        if event == "resume_recording":
            asyncio.create_task(resume_recording())
        if event == "pause_recording":
            asyncio.create_task(pause_recording())

        if event == "__TIMEOUT__":
            await asyncio.sleep(0.001)
