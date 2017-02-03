import signal
import time
import json
import sys
import os

def signal_handler(signal, frame):
    print " "
    print "Closing log file"
    fin.close()
    print "Bye ;)"
    sys.exit(0)

path = './'
name_list = os.listdir(path)
full_list = [os.path.join(path,i) for i in name_list]
time_sorted_list = sorted(full_list, key=os.path.getmtime)
fname = [os.path.basename(i) for i in time_sorted_list]

fin = open(fname[-1], "r")
logUpdated = False

signal.signal(signal.SIGINT, signal_handler)
print "----------------------------------------------------------------------"
print "Elite Dangerous Panel Event Monitor"
print "Logfile name: " +  fin.name
print "Press Ctrl+C to exit"
print "----------------------------------------------------------------------"

while True:
    line = fin.readline()
    if not line:
        time.sleep(1)
        if logUpdated:
            print "> Star (" + starSystem + ") --- Station (" + stationName +")"
            logUpdated = False
    else:
        data = json.loads(line)
        if data["event"] == "Docked":
            stationName = data["StationName"]
            logUpdated = True
        elif data["event"] == "SupercruiseExit":
            starSystem = data["StarSystem"]
            logUpdated = True
