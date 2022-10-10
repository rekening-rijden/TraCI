import os, sys
from concurrent.futures import ThreadPoolExecutor
from re import X
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

sumoBinary = "C:/Program Files (x86)/Eclipse/Sumo/bin/sumo-gui"
sumoConfig = [sumoBinary, "-c", "osm.sumocfg"]

import traci

responseTimes = []

url = "https://restcountries.com/v3.1/all"

def send_request(x, y, vId):
    geolocation = traci.simulation.convertGeo(x, y)
    print(vId + ': ' + str(geolocation[0]) + ', ' + str(geolocation[1]))

def runner(_vehicleList, locationList):
    threads = []
    with ThreadPoolExecutor(max_workers=500) as executor:
        for i in range(len(_vehicleList)):
            threads.append(send_request(locationList[i][0], locationList[i][1], _vehicleList[i]))

class ExampleListener(traci.StepListener):
    def step(self, t):
        vehicleIdList = traci.vehicle.getIDList()
        locationList = []
        for vehicleId in vehicleIdList:
            x, y = (traci.vehicle.getPosition(vehicleId))
            locationList.append([x, y])
        print(vehicleIdList)
        runner(vehicleIdList, locationList)
        return True

listener = ExampleListener()

traci.start(sumoConfig)
traci.addStepListener(listener)

step = 0
while step < 2500:
    traci.simulationStep()
    step += 1

traci.close(False)
