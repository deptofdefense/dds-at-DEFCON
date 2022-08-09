import glob # needed for file view
import netCDF4 # needed for weather files
import sys # needed to exit
from datetime import datetime, timedelta # needed for time calcs
import numpy as np # needed for stuff
import pandas as pd 
import pvlib # needed for pv calc
import math
from scipy import rand # needed for wind calcs

import serial # needed for serial comms
import serial.tools.list_ports # needed to list com ports
import time # needed for sleep
import struct # needed for serial messages
import random # needed for random



class MicrogridTester:

    def __init__(self, actual, injected, sol, wnd):
        """
        Init method

        Args:
            actual (str): The file path to the NetCDF4 file representing the real weather
            injected (str): The file path to the NetCDF4 file representing the injected weather
            sol (str): The COM port to use to talk to the solar grid
            wnd (str): The COM port to use to talk to the wind turbine
        """

        self.blockTime = 1 # number of seconds to run for each block
        self.subTime = 0.25 # how long each sub interval of the block should be

        # Set up serial interfaces
        if sol != "None":
            self.sol = serial.Serial(sol, 9600, timeout=0.1)
        else:
            self.sol = "None"

        if wnd != "None":
            self.wnd = serial.Serial(wnd, 9600, timeout=0.1)
        else:
            self.wnd = "None"

        self.actual = netCDF4.Dataset(actual, 'r+')
        self.inject = netCDF4.Dataset(injected, 'r+')

        # pull lat lon values from actual file
        actualLatMin = self.actual.geospatial_lat_min
        actualLonMin = self.actual.geospatial_lon_min
        actualLatMax = self.actual.geospatial_lat_max
        actualLonMax = self.actual.geospatial_lon_max

        # pull lat lon values from inject file
        injectLatMin = self.inject.geospatial_lat_min
        injectLonMin = self.inject.geospatial_lon_min
        injectLatMax = self.inject.geospatial_lat_max
        injectLonMax = self.inject.geospatial_lon_max

        # calc the average lat lon
        self.actLat = float((float(actualLatMax) + float(actualLatMin)) / 2)
        self.actLon = float((float(actualLonMax) + float(actualLonMin)) / 2)
        self.injLat = float((float(injectLatMax) + float(injectLatMin)) / 2)
        self.injLon = float((float(injectLonMax) + float(injectLonMin)) / 2)

        # figure out the run length based on if inject or real is shorter
        runLength = 0
        if len(self.actual['time']) < len(self.inject['time']):
            runLength = len(self.actual['time']) 
        else:
            runLength = len(self.inject['time']) 

        self.startTime = datetime.utcnow() # stay in UTC
        self.endTime = self.startTime + timedelta(hours=runLength)

        print(f"Actual Lat Lon: {str(self.actLat)} {str(self.actLon)}")
        print(f"Inject Lat Lon: {str(self.injLat)} {str(self.injLon)}")
        print(f"Start Time (UTC): {str(self.startTime)}")
        print(f"End Time (UTC): {str(self.endTime)}")

        #tempData = self.get_solar_positions(float(self.actLat), float(self.actLon), self.startTime, self.endTime)
        #print(str(tempData))

    def testFiles(self):

        testLen = 0 # default
        solarAngle = 0 # default

        if len(self.actual['time']) < len(self.inject['time']): # check which has a shorter run time
            testLen = len(self.actual['time'])
        else:
            testLen = len(self.inject['time'])

        print(f"Running {str(testLen)} tests using the provided files")
        solarJump = int(180 / int(testLen))
        #print(str(solarJump))

        actWindAngle = self.calcWindAngle(self.actual, 0, 0, testLen)
        injWindAngle = self.calcWindAngle(self.inject, 0, 0, testLen)
        #print(f"actual angles: {str(actWindAngle)}")
        #print(f"inject angles: {str(injWindAngle)}")

        actWindSpeed = self.getWindSpeed(self.actual, 0, 0, testLen)
        injWindSpeed = self.getWindSpeed(self.inject, 0, 0, testLen)
        #print(f"actual speed: {str(actWindSpeed)}")
        #print(f"inject speed: {str(injWindSpeed)}")

        actCloudCoverage = self.getCloudCoverage(self.actual, 0, 0, testLen)
        injCloudCoverage = self.getCloudCoverage(self.inject, 0, 0, testLen)
        #print(f"Actual cloud coverage: {str(actCloudCoverage)}")
        #print(f"Inject cloud coverage: {str(injCloudCoverage)}")

        actualTemperature = self.getTemperature(self.actual, 0, 0, testLen)
        injTemperature = self.getTemperature(self.inject, 0, 0, testLen)
        #print(f"Actual Temperature: {str(actualTemperature)}")
        #print(f"Inject Temperature: {str(injTemperature)}")

        # Run through all the hours
        for i in range(testLen):

            print(f"Running simulation for hour {str(i)}")

            self.payloadInterface('sol', 'srv', [solarAngle, solarAngle, solarAngle, solarAngle])

            easterEgg = 0 # easter egg value
            windWarn = 0 # total number of wind errors for the block
            solWarn = 0 # total number of solar errors for the block
            smoke = False # boolean for if doing the smoke special case

            # check for easter eggs
            if float(injTemperature[i]) == 69 or float(injTemperature[i]) == 342.15 or float(injTemperature[i]) == 293.706: # disco mode
                easterEgg = 1
            elif float(injTemperature[i]) == 0: # absolute zero
                easterEgg = 2
            elif float(injTemperature[i]) >= 373.15:  # melting mode
                easterEgg = 3

            # check location
            if self.actLat != self.injLat or self.actLon != self.injLon:
                # if location is different add 1 warning point to each
                windWarn = windWarn + 1
                solWarn = solWarn + 1

            # check temps
            if abs(actualTemperature[i] - injTemperature[i]) >= 30:
                windWarn = windWarn + 3
                solWarn = solWarn + 3
            elif abs(actualTemperature[i] - injTemperature[i]) >= 20:
                windWarn = windWarn + 2
                solWarn = solWarn + 2
            elif abs(actualTemperature[i] - injTemperature[i]) >= 10:
                windWarn = windWarn + 1
                solWarn = solWarn + 1
            
            # check solar
            if abs(actCloudCoverage[i] - injCloudCoverage[i]) >= 90:
                solWarn = solWarn + 6
            elif abs(actCloudCoverage[i] - injCloudCoverage[i]) >= 60:
                solWarn = solWarn + 3
            elif abs(actCloudCoverage[i] - injCloudCoverage[i]) >= 30:
                solWarn = solWarn + 1

            # check wind
            if abs(actWindSpeed[i] - injWindSpeed[i]) >= 75:
                windWarn = windWarn + 6
            elif abs(actWindSpeed[i] - injWindSpeed[i]) >= 55:
                windWarn = windWarn + 3
            elif abs(actWindSpeed[i] - injWindSpeed[i]) >= 25:
                windWarn = windWarn + 1


            #print(f"Easter Egg: {str(easterEgg)} \nWindWarn: {str(windWarn)} \nSolWarn: {str(solWarn)} \nSol Angle: {str(solarAngle)} \n")

            if easterEgg:
                if easterEgg == 1: # disco easter egg
                    self.payloadInterface('wnd', 'spn', [round(actWindSpeed[i])])
                    for i in range(round(self.blockTime / self.subTime)):
                        self.payloadInterface('sol', 'egg', [1])  
                        self.payloadInterface('wnd', 'all', [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)])
                        time.sleep(self.subTime)
                elif easterEgg == 2: # absolute zero easter egg
                    self.payloadInterface('wnd', 'spn', [0])
                    self.payloadInterface('sol', 'all', [0, 0, 0])
                    self.payloadInterface('wnd', 'all', [0, 0, 0])
                    time.sleep(self.blockTime)
                else:
                    self.payloadInterface('wnd', 'all', [255, 76, 0])
                    self.payloadInterface('sol', 'all', [255, 76, 0])
                    self.payloadInterface('wnd', 'smk', [self.blockTime])
                    time.sleep(self.blockTime)
            else: #Run normal
                if windWarn < 6:
                    self.payloadInterface('wnd', 'spn', [round(actWindSpeed[i])])
                    for i in range(round(self.blockTime / self.subTime)):
                        if solWarn < 3:
                            self.payloadInterface('sol', 'sol', [random.randint(0, 100), random.randint(150, 255), random.randint(0, 100)])  
                        elif solWarn < 5:
                            self.payloadInterface('sol', 'sol', [random.randint(150, 255), random.randint(150, 255), random.randint(0, 100)])
                        else: 
                            self.payloadInterface('sol', 'sol', [random.randint(150, 255), random.randint(0, 100), random.randint(0, 100)])
                        
                        if windWarn < 3:
                            self.payloadInterface('sol', 'wnd', [random.randint(0, 100), random.randint(150, 255), random.randint(0, 100)])
                        elif windWarn < 5:
                            self.payloadInterface('sol', 'wnd', [random.randint(150, 255), random.randint(150, 255), random.randint(0, 100)])
                        else:
                            self.payloadInterface('sol', 'wnd', [random.randint(150, 255), random.randint(0, 100), random.randint(0, 100)])
                        time.sleep(self.subTime)
                else:
                    if solWarn < 3:
                        self.payloadInterface('sol', 'sol', [random.randint(0, 100), random.randint(0, 100), random.randint(150, 255)])  
                    elif solWarn < 5:
                        self.payloadInterface('sol', 'sol', [random.randint(150, 255), random.randint(0, 100), random.randint(150, 255)])
                    else: 
                        self.payloadInterface('sol', 'sol', [random.randint(150, 255), random.randint(0, 100), random.randint(0, 100)])

                    self.payloadInterface('sol', 'wnd', [255, 0, 0])
                    self.payloadInterface('wnd', 'smk', [self.blockTime])
                    time.sleep(self.blockTime)
            
            solarAngle = solarAngle + solarJump
            #time.sleep(5)
        
        self.payloadInterface('sol', 'rst', [1])
        #time.sleep(0.1)
        self.payloadInterface('wnd', 'rst', [1])
        #time.sleep(0.1)
        


    def calcWindAngle(self, dataSet, x, y, runTime):

        angleList = []

        for i in range(int(runTime)):
            
            #print(str(dataSet.variables['u-component_of_wind_height_above_ground'][i, int(x), int(y), 0]))
            uComp = (float(dataSet.variables['u-component_of_wind_height_above_ground'][i, int(x), int(y), 0]))
            vComp = (float(dataSet.variables['v-component_of_wind_height_above_ground'][i, int(x), int(y), 0]))

            angleVal = math.fmod(180.0 + ((180.0 / math.pi) * math.atan2(vComp, uComp)), 360)
            angleList.append(angleVal)

        return angleList

    def getWindSpeed(self, dataSet, x, y, runTime):

        speedList = []

        for i in range(runTime):
            speedList.append(float(dataSet.variables['Wind_speed_gust_surface'][i, int(x), int(y)]))

        return speedList

    def getCloudCoverage(self, dataSet, x, y, runTime):

        cloudCoverage = []

        for i in range(runTime):
            cloudCoverage.append(float(dataSet.variables['Total_cloud_cover_entire_atmosphere'][i, int(x), int(y)]))

        return cloudCoverage

    def getTemperature(self, dataSet, x, y, runTime):

        tempList = []

        for i in range(runTime):
            tempList.append(float(dataSet.variables['Temperature_height_above_ground'][i, int(x), int(y), 0]))
            #print(str(dataSet.variables['Temperature_height_above_ground'][i, int(x), int(y)]))

        return tempList

    def payloadInterface(self, system, cmd, payloadArray):
        '''Handles sending commands to the payload over serial and returns the response'''

        fmt = "3s" + "B"*len(payloadArray)

        #print(fmt)
        #print(cmd)
        #print(payloadArray)

        packedData = struct.pack(fmt, cmd.encode(), *payloadArray)

        #print(fmt)
        if system == 'sol': # if sending message to solar grid
            if self.sol != "None": # if grid exists
                try:
                    self.sol.reset_input_buffer()
                    self.sol.reset_output_buffer()
                    self.sol.write(packedData)
                    self.sol.flush()
                    time.sleep(0.1)

                    data = self.sol.read(32)
                    while len(data.decode()) < 1:
                        self.sol.write(packedData)
                        self.sol.flush()
                        time.sleep(0.1)
                        data = self.sol.read(32)
                        time.sleep(0.1)
                    #print(data.decode())
                except IOError:
                    print("ERROR, SOL TIMEOUT")
        elif system == 'wnd': #if sending message to wind turbine
            if self.wnd != "None": #if turbine exists
                try:
                    self.wnd.reset_input_buffer()
                    self.wnd.reset_output_buffer()
                    self.wnd.write(packedData)
                    self.wnd.flush()
                    time.sleep(0.1)

                    data = self.wnd.read(32)
                    while len(data.decode()) < 1:
                        self.wnd.write(packedData)
                        self.wnd.flush()
                        time.sleep(0.1)
                        data = self.wnd.read(32)
                        time.sleep(0.1)
                    #print(data.decode())

                    if "ERROR" in data.decode():
                        #print("test")
                        self.wnd.write(packedData)
                        self.wnd.flush()
                        time.sleep(0.1)
                        data = self.wnd.read(32)
                        time.sleep(0.1)

                except IOError:
                    print("ERROR, WND TIMEOUT")


if __name__ == "__main__":
    files = glob.glob('./*.nc')

    if len(files) < 1:
        print("No netCDF4 files found in current directory")
        print("Please make sure that all netCDF files are using '.nc' as a file extension")
        sys.exit(1)
    else:
        print("List of '.nc' files:")
        for i in range(len(files)):

            temp = str(files[i]).split('\\')
            files[i] = temp[len(temp) - 1]

            print(f'File {str(i)} : {str(files[i])}')

    actChoice = input('Enter the number of the file to use for actual data, or anything to exit: ')
    injChoice = input('Enter the number of the file to use for inject data, or anything to exit: ')


    if str(actChoice).isdigit() and str(injChoice).isdigit():
        if int(actChoice) < len(files) and int(injChoice) < len(files):
            print(f'Using {str(files[int(actChoice)])} for actual data')
            print(f'Using {str(files[int(injChoice)])} for inject data')

            tester = MicrogridTester(str(files[int(actChoice)]), str(files[int(injChoice)]), 'COM13', 'COM32')
            #tester = MicrogridTester(str(files[int(actChoice)]), str(files[int(injChoice)]), 'None', 'None')
            tester.testFiles()
            

