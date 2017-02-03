import time
import json
import os

path = ''
name_list = os.listdir(path)
full_list = [os.path.join(path,i) for i in name_list]
time_sorted_list = sorted(full_list, key=os.path.getmtime)
fname = [os.path.basename(i) for i in time_sorted_list]
print fname[-1]

fin = open(fname[-1], "r")
fUpdated = False

print "Reading log name: " +  fin.name
while True:
    line = fin.readline()
    if not line:
        time.sleep(1)
        if fUpdated:
            print "Current star: " + starSystem
            print "Current station: " + stationName
            print " "
            fUpdated = False
    else:
        data = json.loads(line)
        if data["event"] == "Docked":
            stationName = data["StationName"]
            fUpdated = True
        elif data["event"] == "SupercruiseExit":
            starSystem = data["StarSystem"]
            fUpdated = True


fin.close()
