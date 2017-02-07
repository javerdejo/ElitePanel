from tornado import websocket, web, ioloop
from tornado.ioloop import PeriodicCallback

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

    logUpdated = False
    starSystem = ""
    stationName = ""
    incomingMessage = ""


    line = fin.readline()
    while line:
        data = json.loads(line)
        event = data["event"]

        if event == "Docked":
            stationName = data["StationName"]
            logUpdated = True
        elif event == "FSDJump" or event == "SupercruiseExit":
            starSystem = data["StarSystem"]
            logUpdated = True
        elif event == "Undocked":
            stationName = ""
            logUpdated = True
        elif event == "ReceiveText":
            incomingMessage = data["Message_Localised"]
            logUpdated = True

        line = fin.readline()



# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def updateLogFile():
    global logUpdated
    global starSystem
    global stationName
    global incomingMessage

    event = ""

    line = fin.readline()
    while line:
        data = json.loads(line)
        event = data["event"]

        if event == "Docked":
            stationName = data["StationName"]
            logUpdated = True
        elif event == "FSDJump" or event == "SupercruiseExit":
            starSystem = data["StarSystem"]
            logUpdated = True
        elif event == "Undocked":
            stationName = ""
            logUpdated = True
        elif event == "ReceiveText":
            incomingMessage = data["Message_Localised"]
            logUpdated = True

        line = fin.readline()

    JSONMessage = json.dumps({'stationName':stationName, 'starSystem':starSystem, 'incomingMessage':incomingMessage} )

    for c in cl:
        c.write_message(JSONMessage)



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
