"""
Reply some logs into the plugin journal_entry func
"""
import load as nullplug
import sys
import fakeconfig

cmdr = sys.argv[1]
passwd = sys.argv[2]
address = sys.argv[3]

logs = [
    # load game
    {u'timestamp': u'2016-10-28T07:58:38Z',
     u'Loan': 0, u'GameMode': u'Open',
     u'Commander': u'Ian Norton',
     u'Credits': 7582585,
     u'Ship': u'Orca', u'ShipID': 41, u'event': u'LoadGame'},

    # Rank data
    {u'Federation': 4, u'Combat': 7, u'CQC': 0,
     u'timestamp': u'2016-10-28T07:58:38Z',
     u'Trade': 6, u'Explore': 5, u'Empire': 0,
     u'event': u'Rank'},

    # location
    {u'Government_Localised': u'Democracy', u'timestamp': u'2016-10-28T07:59:16Z', u'StationType': u'Orbis',
     u'Docked': True, u'StarPos': [69.438, 12.25, 97.781], u'Security': u'$SYSTEM_SECURITY_high;',
     u'event': u'Location', u'Economy': u'$economy_Agri;', u'Body': u'Vela City', u'StarSystem': u'HIP 74255',
     u'BodyType': u'Station', u'Government': u'$government_Democracy;', u'Economy_Localised': u'Agriculture',
     u'Faction': u'HIP 74255 Labour', u'Allegiance': u'Federation', u'StationName': u'Vela City',
     u'Security_Localised': u'High Security'},

    # Docked
    {u'StarSystem': u'HIP 74255', u'Government_Localised': u'Democracy', u'Faction': u'HIP 74255 Labour',
     u'timestamp': u'2016-10-28T07:59:16Z', u'Economy_Localised': u'Agriculture',
     u'Government': u'$government_Democracy;', u'Allegiance': u'Federation', u'StationType': u'Orbis',
     u'StationName': u'Vela City', u'Security_Localised': u'High Security', u'Security': u'$SYSTEM_SECURITY_high;',
     u'event': u'Docked', u'Economy': u'$economy_Agri;'},

    # Buy Beer
    {u'Count': 36, u'TotalCost': 2124, u'BuyPrice': 59, u'timestamp': u'2016-10-28T08:07:07Z', u'Type': u'beer',
     u'event': u'MarketBuy'},

    # Undock
    {u'timestamp': u'2016-10-28T08:08:04Z', u'event': u'Undocked', u'StationName': u'Vela City',
     u'StationType': u'Orbis'},

    # Jump
    {u'StarSystem': u'LTT 5746', u'Government_Localised': u'None', u'Government': u'$government_None;',
     u'timestamp': u'2016-10-28T08:09:38Z', u'Economy_Localised': u'None', u'FuelLevel': 28.261803, u'JumpDist': 13.258,
     u'Allegiance': u'', u'StarPos': [76.813, 13.813, 86.875], u'FuelUsed': 3.738197,
     u'Security_Localised': u'Low Security', u'Security': u'$SYSTEM_SECURITY_low;', u'event': u'FSDJump',
     u'Economy': u'$economy_None;'},

    # Jump
    {u'StarSystem': u'LTT 4961', u'Government_Localised': u'Democracy', u'Government': u'$government_Democracy;',
     u'timestamp': u'2016-10-28T08:13:27Z', u'Economy_Localised': u'High tech', u'Faction': u'NULL',
     u'JumpDist': 10.913, u'Allegiance': u'Independent', u'StarPos': [91.375, 13.375, 62.594], u'FuelUsed': 2.272106,
     u'Security_Localised': u'Medium Security', u'Security': u'$SYSTEM_SECURITY_medium;', u'event': u'FSDJump',
     u'FuelLevel': 22.844513, u'Economy': u'$economy_HighTech;'},

    # Exit cruise
    {u'Body': u'Conway City', u'timestamp': u'2016-10-28T08:15:33Z', u'BodyType': u'Station',
     u'event': u'SupercruiseExit', u'StarSystem': u'LTT 4961'},

    # Docking Req
    {u'timestamp': u'2016-10-28T08:16:13Z', u'event': u'DockingRequested', u'StationName': u'Conway City'},

    # Docked
    {u'StarSystem': u'LTT 4961', u'Government_Localised': u'Democracy', u'Faction': u'NULL',
     u'timestamp': u'2016-10-28T08:17:07Z', u'Economy_Localised': u'High tech',
     u'Government': u'$government_Democracy;', u'Allegiance': u'Independent', u'StationType': u'Coriolis',
     u'StationName': u'Conway City', u'Security_Localised': u'Medium Security',
     u'Security': u'$SYSTEM_SECURITY_medium;', u'event': u'Docked', u'Economy': u'$economy_HighTech;'},

    # Sell Beer
    {u'Count': 36, u'AvgPricePaid': 59, u'timestamp': u'2016-10-28T08:17:54Z', u'TotalSale': 6300, u'Type': u'beer',
     u'SellPrice': 175, u'event': u'MarketSell'}
]

# sell
sell = [x for x in logs if x["event"] == "MarketSell"]


fakeconfig.config.set(nullplug.CFG_CMDR, cmdr)
fakeconfig.config.set(nullplug.CFG_PASS, passwd)
fakeconfig.config.set(nullplug.CFG_SERVER, address)

nullplug.plugin_start()


for sellitem in sell:
    nullplug.journal_entry(cmdr, "LTT 4961", "Conway City", sellitem)

