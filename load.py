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
    CONFIG.status = tk.StringVar(value="--")
    CONFIG.uploads = tk.StringVar(value="--")

    post_event({}, config.get("cmdrs")[0], "LTT-4961", None)


def plugin_prefs(parent):
    global CONFIG
    frame = nb.Frame(parent)
    frame.columnconfigure(1, weight=1)

    nb.Label(frame, text="NULL Tracker Configuration").grid(padx=10, row=8, sticky=tk.W)

    nb.Label(frame, text="NULL Tracker Server").grid(padx=10, row=10, sticky=tk.W)
    nb.Entry(frame, textvariable=CONFIG.server).grid(padx=10, row=10, column=1, sticky=tk.EW)

    nb.Label(frame, text="NULL Tracker API Key").grid(padx=10, row=11, sticky=tk.W)
    nb.Entry(frame, textvariable=CONFIG.apikey).grid(padx=10, row=11, column=1, sticky=tk.EW)

    nb.Label(frame, text="Status             ").grid(padx=10, row=12, sticky=tk.W)
    nb.Label(frame, textvariable=CONFIG.status).grid(padx=10, row=12, column=1, sticky=tk.EW)
    nb.Label(frame, textvariable=CONFIG.uploads).grid(padx=10, row=13, column=1, sticky=tk.EW)

    return frame


def prefs_changed():
    global CONFIG
    config.set("NULLTrackerServer", CONFIG.server.get())
    config.set("NULLTrackerAPIKey", CONFIG.apikey.get())
    post_event({}, config.get("cmdrs")[0], "LTT-4961", None)


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

    post_event(entry, cmdr, system, station)


def get_profile(cmdr):
    """
    Get the current player's standing
    :param cmdr:
    :return:
    """
    global CONFIG
    paths = [CONFIG.server.get().rstrip("/"),
             'api',
             CONFIG.apikey.get()]
    url = "/".join(paths)

    resp = requests.get(url, headers=HTTP_HEADERS)
    if resp:
        if resp.status_code == 200:
            data = json.loads(resp.content)
            if data and "commanders" in data:
                if cmdr in data["commanders"]:
                    return data
    return None


__overlay__ = None


def hits_overlay_notify(message):
    """
    If installed, display a message on EDMCOverlay/HITS
    :param message:
    :return:
    """
    try:
        global __overlay__
        if not __overlay__:
            import edmcoverlay
            __overlay__ = edmcoverlay.Overlay()
        __overlay__.send_message("null-track-notify", message, "#339933", 50, 1100, ttl=6, size="normal")

    except Exception as err:
        print err


def post_event(entry, cmdr, system, station):
    """
    Send a journal event to NULL
    :param entry:
    :param url:
    :return:
    """
    global CONFIG
    paths = [CONFIG.server.get().rstrip("/"),
             'api',
             CONFIG.apikey.get(),
             urllib.quote(cmdr),
             urllib.quote(system)]
    if station is not None:
        paths.append(station)
    url = "/".join(paths)

    try:
        if entry and len(entry):
            form_encoded = {"event": json.dumps(entry)}
            resp = requests.post(url, data=form_encoded, headers=HTTP_HEADERS)
            if resp:
                hits_overlay_notify("NULL update sent..")

        profile = get_profile(cmdr)
        if profile:
            CONFIG.status.set("OK: This week: {}cr".format(
                profile["contributions"]["current_week"]["total_value"]))
            CONFIG.uploads.set("Sent {} updates".format(
                profile["contributions"]["current_week"]["influence_updates"]["count"]))
    except Exception as err:
        print err
        CONFIG.status.set("error {}".format(err))
