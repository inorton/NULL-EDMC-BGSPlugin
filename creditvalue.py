"""
Try and work out the credit value of events
"""

FOODS = [
    "Algae",
    "Animal Meat",
    "Coffee",
    "Fish",
    "Food Cartridges",
    "Fruit and Vegetables",
    "Grain",
    "Synthetic Meat",
    "Tea"
]
MEDICINES = [
    "Advanced Medicines",
    "Agri-Medicines",
    "Basic Medicines",
    "Combat Stabilisers",
    "Performance Enhancers",
    "Progenitor Cells"
]

# will get populated at runtime with job types from the server
JOBTYPES = {}


def match_jobtype(name):
    """
    Search JOBTYPES and find a match
    :param name:
    :return:
    """
    for job in JOBTYPES:
        if job["name"] == name:
            return job
    return None


class MissionResult(object):
    """
    Represent a mission/activity and it's value
    """
    def __init__(self):
        self.job = None
        self.value = 0


def MarketSell(event):
    """
    Calculate the income from a commodity sale
    :param event:
    :return:
    """
    income = event["TotalSale"]
    cost = event["AvgPricePaid"] * event["Count"]
    profit = income - cost

    ret = MissionResult()
    if event["Type"] in FOODS:
        ret.job = match_jobtype("Trade (Food)")
    elif event["Type"] in MEDICINES:
        ret.job = match_jobtype("Trace (Medicine)")
    else:
        ret.job = match_jobtype("Trade/Donation")

    ret.value = profit
    return ret


def get_job(eventdata):
    """
    Get the credit value for an event
    :param eventdata:
    :return:
    """
    if eventdata:
        if "event" in eventdata:
            event = eventdata["event"]
            attribs = globals()
            if event in attribs:
                return attribs[event](eventdata)

    return None
