"""
Submit some events to a null bgs server
"""
import time
import urllib2
import urllib
import json
from cookielib import LWPCookieJar


# events we care about
EVENTS = ["MarketSell"]


class SystemEntry(object):
    """
    How we identify systems
    """
    def __init__(self, nullid, name):
        self.id = nullid
        self.name = name
        self.stations = None

    def add_station(self, stid, name):
        """
        add a station
        :param stid:
        :param name:
        :return:
        """
        if self.stations is None:
            self.stations = []
        self.stations.append(StationEntry(stid, name))


class StationEntry(object):
    """
    How we represent a station
    """
    def __init__(self, nullid, name):
        self.id = nullid
        self.name = name


def set_headers(req, headers=None):
    """
    Set our headers
    :param req:
    :param headers: a dictionary of headers
    :return:
    """
    req.add_header("User-Agent", "NULL EDMC BGS Plugin")
    if headers:
        for name in headers:
            req.add_header(name, headers[name])


class NULLClient(object):
    """
    Client for submitting to a null server
    """
    def __init__(self):
        self.address = None
        self.commander = None
        self.password = None
        self.authenticated = False
        # the list of BGS tasks that are active
        self.tasks = []
        self.last_update_tasks = 0
        self.cookie = None
        self.cookiejar = LWPCookieJar()
        self.opener = None

    def post_urlform(self, url, formdata):
        """
        Post a form
        :param url:
        :param formdata:
        :return:
        """
        cookie = urllib2.HTTPCookieProcessor(self.cookiejar)
        opener = urllib2.build_opener(cookie)
        self.opener = opener

        data = urllib.urlencode(formdata)
        req = urllib2.Request(url, data)
        set_headers(req, {"Content-Type": "application/x-www-form-urlencoded"})

        res = opener.open(req)
        respdata = res.read()

        return respdata

    def connect(self, server):
        """
        Check the server exists
        :param server:
        :return:
        """
        urllib.urlopen(server)
        self.address = server

    def login(self, username, password):
        """
        Login
        :param username:
        :param password:
        :return:
        """
        self.commander = username
        self.password = password
        self.cookiejar.clear()
        self.post_urlform("{}/login".format(self.address), {"username": username, "password": password})

        if len(self.cookiejar):
            cookies = [x for x in self.cookiejar]
            for cookie in cookies:
                if cookie.name == "nullui":
                    self.authenticated = True

        self.update_tasks()

    def update_tasks(self):
        """
        Get the latest task list if it is old
        :return:
        """
        if not self.authenticated:
            return

        now = time.time()
        if now - self.last_update_tasks > 300:
            # get the tasks again
            req = urllib2.Request("{}/bgs/task/json".format(self.address))
            set_headers(req, {"Content-Type": "application/json"})
            res = self.opener.open(req)
            response = res.read()
            tasks = json.loads(response)
            tasklist = []
            # iterate the result and make objects
            for task in tasks:
                system = SystemEntry(task["id"], task["system_name"])
                if task["stations"] is not None:
                    for stid in task["stations"]:
                        system.add_station(stid, None)
                tasklist.append(system)
            self.tasks = tasklist
            # don't do it again for a while
            self.last_update_tasks = time.time()

    def match_location(self, systemname, stationname):
        """
        Return True if we are at all interested in this place
        :param systemname:
        :param stationname:
        :return:
        """
        if not self.authenticated:
            return False

        for system in self.tasks:
            if system.name == systemname:
                if system.stations is None:
                    return system.id
                else:
                    for station in system.stations:
                        if station.name == stationname:
                            return system.id

        return False

    def filter(self, systemname, stationname, eventdata):
        """
        Return True if the null server wants to know about this event at this location
        :param systemname:
        :param stationname:
        :param eventdata:
        :return:
        """
        if self.authenticated:
            if "event" in eventdata:
                if eventdata["event"] in EVENTS:
                    return self.match_location(systemname, stationname)

        return None

    def submit(self, taskid, eventdata):
        """
        Submit this event to this task
        :param taskid:
        :param eventdata:
        :return:
        """
        print taskid
        print eventdata
