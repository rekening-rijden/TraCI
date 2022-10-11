import os, sys
import config
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

#Array to save responsetimes for performance testing
responseTimes = []

#Converts simulation coordinates to geo coordinates
def send_request(x, y, vId):
    geolocation = traci.simulation.convertGeo(x, y)
    #Retreive tha current lane the vehicle is on
    laneId = traci.vehicle.getLaneID(vId)
    #Get the lanespeed for the current lane and convert from m/s to mp/h
    laneSpeed = round(traci.lane.getMaxSpeed(laneId) * 2.23694, 0)
    roadType = ""
    print(laneSpeed)
    #Match lane speed to road type
    match laneSpeed:
        case 20:
            roadType = "Built-up area"
        case 30:
            roadType = "Built-up area"
        case 60:
            roadType = "Single carriageway"
        case 70:
            roadType = "Dual carriageway / Motorway"
    print(vId + ': ' + str(geolocation[0]) + ', ' + str(geolocation[1]) + ', ' + roadType)

#Multithreading Runner
def runner(_vehicleList, locationList):
    threads = []
    with ThreadPoolExecutor(max_workers=config.multithreading['workerAmount']) as executor:
        for i in range(len(_vehicleList)):
            threads.append(send_request(locationList[i][0], locationList[i][1], _vehicleList[i]))

#Listener for steps from server
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

#Connection is closed after step limit is reached
traci.close(False)
