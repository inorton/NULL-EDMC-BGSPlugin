"""
A Skeleton EDMC Plugin
"""
import sys
import os
import ttk
import Tkinter as tk
import myNotebook as nb

PLUGIN_NAME = "NULL BGS Data"
HERE = os.path.dirname(__file__)
sys.path.append(HERE)

import null_submit
from urllib2 import HTTPError

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


def set_status(msg):
    """
    Set the GUI status message
    :param msg:
    :return:
    """
    logmsg(msg)
    msg = "NULL BGS: {}".format(msg)
    if plugin_app.status:
        plugin_app.status["text"] = msg
    set_status.last = msg
set_status.last = "~"


def plugin_start():
    """
    Start this plugin
    :return:
    """
    logmsg("NULL BGS Data Plugin started")  # appears in %TMP%/EDMarketConnector.log in packaged Windows app
    get_client()


def get_client():
    """
    Get a logged in client if we can
    :return:
    """
    global CLIENT
    if CLIENT is None:
        client = None
        try:
            cmdrname = config.get(CFG_CMDR)
            password = config.get(CFG_PASS)
            address = config.get(CFG_SERVER)
            if cmdrname and password and address:
                client = null_submit.NULLClient()
                client.connect(address)
                client.login(cmdrname, password)
            else:
                set_status("No login details")
        except HTTPError as herr:
            set_status("Could not login: {}".format(herr.message))
        except IOError as emsg:
            logmsg("could not connect to the server: {}".format(emsg))
            set_status("Could not connect")

        if client:
            if client.authenticated:
                set_status("Online")

        CLIENT = client
    return CLIENT


prefs_form = dict()


def plugin_prefs(parent):
    """
    Return a TK Frame for adding to the EDMC settings dialog.
    """
    frame = nb.Frame(parent)
    frame.columnconfigure(1, weight=1)
    padx = 10
    pady = 2
    global prefs_form
    nb.Label(frame, text='Credentials').grid(padx=padx, sticky=tk.W, row=1)
    ttk.Separator(frame, orient=tk.HORIZONTAL).grid(columnspan=2, row=2, padx=padx, pady=pady, sticky=tk.EW)
    nb.Label(frame, text='Please log in with NULL details').grid(row=3, padx=padx, columnspan=2, sticky=tk.W)
    nb.Label(frame, text='Server Address').grid(row=4, padx=padx, sticky=tk.W)
    nb.Label(frame, text='Commander Name').grid(row=5, padx=padx, sticky=tk.W)
    nb.Label(frame, text='Password').grid(row=6, padx=padx, sticky=tk.W)

    prefs_form["server"] = nb.Entry(frame)
    prefs_form["server"].insert(0, config.get(CFG_SERVER) or '')
    prefs_form["server"].grid(row=4, column=1, padx=padx, sticky=tk.EW)

    prefs_form["cmdrname"] = nb.Entry(frame)
    prefs_form["cmdrname"].insert(0, config.get(CFG_CMDR) or '')
    prefs_form["cmdrname"].grid(row=5, column=1, padx=padx, sticky=tk.EW)

    prefs_form["password"] = nb.Entry(frame, show='*')
    prefs_form["password"].insert(0, config.get(CFG_PASS) or '')
    prefs_form["password"].grid(row=6, column=1, padx=padx, sticky=tk.EW)

    prefs_form["status"] = nb.Label(frame, text="")
    prefs_form["status"].grid(row=7, padx=padx, sticky=tk.W, columnspan=2)

    save = tk.Button(frame, text="Save Details", command=apply_prefs)
    save.grid(row=8, column=1, sticky=tk.E, padx=padx, pady=pady)

    return frame


def apply_prefs():
    """
    Save our configs
    :return:
    """
    server = prefs_form["server"].get()
    cmdr = prefs_form["cmdrname"].get()
    passwd = prefs_form["password"].get()

    config.set(CFG_CMDR, cmdr)
    config.set(CFG_SERVER, server)
    config.set(CFG_PASS, passwd)

    global CLIENT
    CLIENT = None
    get_client()
    if CLIENT and CLIENT.authenticated:
        prefs_form["status"]["text"] = "Login OK!"
    else:
        prefs_form["status"]["text"] = set_status.last


def plugin_app(parent):
    """
    Return a TK Widget for the EDMC main window.
    :param parent:
    :return:
    """
    plugin_app.status = tk.Label(parent, text=set_status.last)
    return plugin_app.status
plugin_app.status = None


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
    logmsg("Got new data ({} chars)".format(len(str(data))))
    if not CLIENT:
        get_client()
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
