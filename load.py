"""
A Skeleton EDMC Plugin
"""
import sys
import os
import ttk
import Tkinter as tk

from config import applongname, appversion
import myNotebook as nb
import null_submit

if "LOAD_FAKE_CONFIG" in os.environ:
    from fakeconfig import config
else:
    from config import config


CLIENT = None

CFG_CMDR = "null_plugin_cmdr"
CFG_PASS = "null_plugin_password"
CFG_SERVER = "null_server_address"


def logmsg(msg):
    """
    Write a debug log message
    :param msg:
    :return:
    """
    sys.stderr.write(msg + "\n")


def plugin_start():
    """
    Start this plugin
    :return:
    """
    logmsg("example plugin started")  # appears in %TMP%/EDMarketConnector.log in packaged Windows app
    client = get_client()
    if client is not None:
        if client.authenticated:
            logmsg("logged into null")


def get_client():
    """
    Get a logged in client if we can
    :return:
    """
    global CLIENT
    if CLIENT is None:
        cmdrname = config.get(CFG_CMDR)
        password = config.get(CFG_PASS)
        address = config.get(CFG_SERVER)
        if cmdrname and password and address:
            client = null_submit.NULLClient()
            client.connect(address)
            client.login(cmdrname, password)
            CLIENT = client

    return CLIENT


def plugin_prefs(parent):
    """
    Return a TK Frame for adding to the EDMC settings dialog.
    """
    frame = nb.Frame(parent)

    nb.Label(frame, text="{NAME} {VER}".format(NAME=applongname, VER=appversion)).grid(sticky=tk.W)
    nb.Label(frame).grid()  # spacer
    nb.Label(frame, text="Fly Safe!").grid(sticky=tk.W)
    nb.Label(frame).grid()  # spacer

    if cmdr_data.last is not None:
        datalen = len(str(cmdr_data.last))
        nb.Label(frame, text="FD sent {} chars".format(datalen)).grid(sticky=tk.W)

    return frame


def plugin_app(parent):
    """
    Return a TK Widget for the EDMC main window.
    :param parent:
    :return:
    """
    plugin_app.status = tk.Label(parent, text="---")
    return plugin_app.status


def system_changed(timestamp, system, coordinates):
    """
    Arrived in a new System
    :param timestamp: when we arrived
    :param system: the name of the system
    :param coordinates: tuple of (x,y,z) ly relative to Sol, or None if unknown
    :return:
    """
    if coordinates:
        sys.stderr.write("Arrived at {} ({},{},{})\n".format(system, *coordinates))
    else:
        sys.stderr.write("Arrived at {}\n".format(system))


def cmdr_data(data):
    """
    Obtained new data from Frontier about our commander, location and ships
    :param data:
    :return:
    """
    cmdr_data.last = data
    plugin_app.status['text'] = "Got new data ({} chars)".format(len(str(data)))
    sys.stderr.write("Got new data ({} chars)\n".format(len(str(data))))
cmdr_data.last = None


def journal_entry(cmdr, system, station, entry):
    """
    Got a journal entry event
    :param cmdr:
    :param system:
    :param station:
    :param entry:
    :return:
    """
    client = get_client()
    if client:
        taskid = client.filter(system, station, entry)
        if taskid is not None:
            # we can submit this job against this system!
            client.submit(taskid, entry)

