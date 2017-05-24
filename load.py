"""
The NULL BGS Tracker Plugin

(c) 2017 Ian Norton,  BSD License
"""
import json
import requests
import urllib
import Tkinter as tk

import myNotebook as nb
from config import config

HTTP_HEADERS = {
    "user-agent": "edmc-NULLTracker-0.1"
}

DEFAULT_SERVER = "https://ui.ltt4961.space"
EVENTS = ["Location", "FSDJump", "Docked"]


class NULLTrackerConfig(object):
    def __init__(self):
        self.server = None
        self.apikey = None

CONFIG = NULLTrackerConfig()


def plugin_start():
    """
    Start up our EDMC Plugin
    :return:
    """
    global CONFIG
    server = config.get("NULLTrackerServer")
    if not server:
        config.set("NULLTrackerServer", DEFAULT_SERVER)

    CONFIG.server = tk.StringVar(value=config.get("NULLTrackerServer"))
    CONFIG.apikey = tk.StringVar(value=config.get("NULLTrackerAPIKey"))


def plugin_prefs(parent):
    global CONFIG
    frame = nb.Frame(parent)
    frame.columnconfigure(1, weight=1)

    nb.Label(frame, text="NULL Tracker Configuration").grid(padx=10, row=8, sticky=tk.W)
    nb.Label(frame, text="NULL Tracker Server").grid(padx=10, row=10, sticky=tk.W)

    nb.Entry(frame, textvariable=CONFIG.server).grid(padx=10, row=10, column=1, sticky=tk.EW)

    nb.Label(frame, text="NULL Tracker API Key").grid(padx=10, row=12, sticky=tk.W)

    nb.Entry(frame, textvariable=CONFIG.apikey).grid(padx=10, row=12, column=1, sticky=tk.EW)

    return frame


def prefs_changed():
    global CONFIG
    config.set("NULLTrackerServer", CONFIG.server.get())
    config.set("NULLTrackerAPIKey", CONFIG.apikey.get())


def journal_entry(cmdr, system, station, entry, state):
    """
    Make sure the service is up and running
    :param cmdr:
    :param system:
    :param station:
    :param entry:
    :param state:
    :return:
    """
    if "event" not in entry:
        return
    if entry["event"] not in EVENTS:
        return

    global CONFIG
    paths = [CONFIG.server.get().rstrip("/"),
	         'api',
             CONFIG.apikey.get(),
             urllib.quote(cmdr),
             urllib.quote(system)]
    if station is not None:
        paths.append(station)
    url = "/".join(paths)


    form_encoded = {"event": json.dumps(entry)}
    try:
        resp = requests.post(url, data=form_encoded, headers=HTTP_HEADERS)
        if resp:
            print resp
    except Exception as err:
        print err
