from tornado import websocket, web, ioloop
from tornado.ioloop import PeriodicCallback
from pymongo import MongoClient
from bson.json_util import dumps

import signal
import time
import json
import sys
import os

#path = "C:\Users\javie\Saved Games\Frontier Developments\Elite Dangerous\\"
path = "/Users/javerdejo/Desktop/Elite/"

port = 3056
cl = []

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

client = MongoClient()
db = client.elite

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class System:
    def __init__(self, id, name, government, allegiance, security, economy, power, population, faction):
        self.id = id
        self.name = name
        self.government = government
        self.allegiance = allegiance
        self.security = security
        self.economy = economy
        self.power = power
        self.population = population
        self.faction = faction


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Station:
    def __init__(self, name, type):
        self.name = name
        self.type = type



# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def querySystemEDDB(systemName):
    document = db.systems.find_one({"name":systemName})
    data = json.loads(dumps(document))

    system = System (
    data['id'],
    data['name'],
    data['government'],
    data['allegiance'],
    data['security'],
    data['primary_economy'],
    data['power'],
    data['population'],
    data['controlling_minor_faction']
    )

    return system



# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def queryStationEDDB(stationName, idSystem):
    document = db.stations.find_one({'name':stationName, 'system_id':idSystem})
    data = json.loads(dumps(document))

    station = Station (
    data['name'],
    data['type']
    )

    return station

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def signal_handler(signal, frame):

    print " "
    print "Closing log file"
    fin.close()
    print "Bye ;)"
    sys.exit(0)



# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def getLogFile(path):

    name_list = os.listdir(path)
    full_list = [os.path.join(path,i) for i in name_list]
    time_sorted_list = sorted(full_list, key=os.path.getmtime)
    fname = [os.path.basename(i) for i in time_sorted_list]

    return path + fname[-1]



# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("elite_panel.html")



# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        if self not in cl:
            cl.append(self)

    def on_close(self):
        if self in cl:
            cl.remove(self)

    def on_message(self, message):
        print message



# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def loadLogFile():
    global logUpdated
    global starSystem
    global stationName
    global incomingMessage
    global government
    global faction


    logUpdated = False
    starSystem = ""
    stationName = ""
    incomingMessage = ""
    government = ""
    faction = ""
    JSONMessage = ""


    line = fin.readline()
    while line:
        data = json.loads(line)
        event = data["event"]

        if event == "Docked":
            stationName = data["StationName"]
            government  = data["StationGovernment_Localised"]
            faction  = data["StationFaction"]
            starSystem = data["StarSystem"]
            logUpdated = True
        elif event == "SupercruiseEntry":
            starSystem = data["StarSystem"]
            stationName = "-----"
            government  = "-----"
            faction  = "-----"
            logUpdated = True
        elif event == "FSDJump" or event == "SupercruiseExit":
            starSystem = data["StarSystem"]
            stationName = "-----"
            government  = "-----"
            faction  = "-----"
            logUpdated = True
        elif event == "Undocked":
            stationName = "-----"
            government  = "-----"
            faction  = "-----"
            logUpdated = True
        elif event == "ReceiveText":
            incomingMessage = data["Message_Localised"]
            logUpdated = True

        line = fin.readline()

    if logUpdated:
        print "Event: " + event
        if event == "Docked":
            system = querySystemEDDB(starSystem)

            JSONMessage = json.dumps({
            'event' : 'Docked',
            'system' : system.name,
            'government' : system.government,
            'allegiance' : system.allegiance,
            'security' : system.security,
            'economy' : system.economy,
            'power' : system.power,
            'population' : str(system.population),
            'faction' : system.faction,
            'station' : stationName
            })
        else:
            JSONMessage = json.dumps({'event' : 'Other', 'station' : stationName, 'system' : starSystem, 'incomingMessage' : incomingMessage, 'government' : government, 'faction' : faction})
        logUpdated = False

        for c in cl:
            c.write_message(JSONMessage)



# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def updateLogFile():
    global logUpdated
    global starSystem
    global stationName
    global incomingMessage
    global government
    global faction

    event = ""
    JSONMessage = ""

    line = fin.readline()
    while line:
        data = json.loads(line)
        event = data["event"]

        if event == "Docked":
            system = querySystemEDDB(data["StarSystem"])
            station = queryStationEDDB(data['StationName'], system.id)

            JSONMessage = json.dumps({
            'event' : 'Docked',
            'system' : system.name,
            'government' : system.government,
            'allegiance' : system.allegiance,
            'security' : system.security,
            'economy' : system.economy,
            'power' : system.power,
            'population' : str(system.population),
            'faction' : system.faction,
            'station' : station.name,
            'type' : station.type
            })

            for c in cl:
                c.write_message(JSONMessage)

        elif event == "ReceiveText":
            JSONMessage = json.dumps({
            'event' : 'ReceiveText',
            'incomingMessage' : data['Message_Localised']
            })

            for c in cl:
                c.write_message(JSONMessage)

        elif event == "FSDJump":
            system = querySystemEDDB(data["StarSystem"])

            JSONMessage = json.dumps({
            'event' : 'FSDJump',
            'system' : system.name,
            'government' : system.government,
            'allegiance' : system.allegiance,
            'security' : system.security,
            'economy' : system.economy,
            'power' : system.power,
            'population' : str(system.population),
            'faction' : system.faction,
            'jumpdist' : data['JumpDist'],
            'fuelused' : data['FuelUsed'],
            'fuellevel' : data['FuelLevel']
            })

            for c in cl:
                c.write_message(JSONMessage)

        elif event == "FuelScoop":
            JSONMessage = json.dumps({
            'event' : 'FuelScoop',
            'fuellevel' : data['Total']
            })

            for c in cl:
                c.write_message(JSONMessage)

        elif event == "SupercruiseEntry":
            system = querySystemEDDB(data["StarSystem"])

            JSONMessage = json.dumps({
            'event' : 'SupercruiseEntry',
            'system' : system.name,
            'government' : system.government,
            'allegiance' : system.allegiance,
            'security' : system.security,
            'economy' : system.economy,
            'power' : system.power,
            'population' : str(system.population),
            'faction' : system.faction,
            })

            for c in cl:
                c.write_message(JSONMessage)

        elif event == "SupercruiseExit":
            system = querySystemEDDB(data["StarSystem"])

            JSONMessage = json.dumps({
            'event' : 'SupercruiseExit',
            'system' : system.name,
            'government' : system.government,
            'allegiance' : system.allegiance,
            'security' : system.security,
            'economy' : system.economy,
            'power' : system.power,
            'population' : str(system.population),
            'faction' : system.faction,
            'body' : data['Body'],
            'bodytype' : data['BodyType']
            })

            for c in cl:
                c.write_message(JSONMessage)

        elif event == "Undocked":
            stationName = "-----"
            government  = "-----"
            faction  = "-----"
            logUpdated = True
        else:
            logUpdated = False

        line = fin.readline()



# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
signal.signal(signal.SIGINT, signal_handler)

app = web.Application([
    (r'/', IndexHandler),
    (r'/ws', SocketHandler),
])

fin = open(getLogFile(path), "r")

print "----------------------------------------------------------------------"
print "Elite Dangerous Event Monitor V0.1"
print "Logfile: " +  fin.name
print "Press Ctrl+C to exit"
print "----------------------------------------------------------------------"

loadLogFile()
app.listen(port)
PeriodicCallback(updateLogFile, 1000).start()
print "waiting connectios in port " + str(port)
ioloop.IOLoop.instance().start()
