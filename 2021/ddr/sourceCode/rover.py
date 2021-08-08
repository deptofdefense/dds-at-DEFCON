from __future__ import print_function
import time
import sys
import math
import qwiic_scmd

from rfModule import LRS # needed for LRT
import binascii # needed for hex
from octoliner import Octoliner # needed for line follower
import threading # needed for threading


class Rover:
    """
    The Rover motor controller
    """

    def __init__(self):
        self.myMotor = qwiic_scmd.QwiicScmd()
        self.R_MTR = 0
        self.L_MTR = 1
        self.FWD = 0
        self.BWD = 1

        # right motor direction
        self.rmd = 0
        # left motor direction
        self.lmd = 0
        # right motor power
        self.rmp = 0
        # left motor power
        self.lmp = 0
        
        self.busy = False

        # line detector
        self.octo = Octoliner()
        self.seenLine = False

        if self.myMotor.connected == False:
            print("Motor Driver not connected. Check connections.", \
                file=sys.stderr)
            return
        self.myMotor.begin()
        print("Motor initialized.")
        time.sleep(.250)

        # Zero Motor Speeds
        self.myMotor.set_drive(0,0,0)
        self.myMotor.set_drive(1,0,0)

        #myMotor.enable()
        #print("Motor enabled")
        self.calibrateOcto()

        #start detect thread
        #threading.Thread(target=self.lineDetectThread(), daemon=True).start()

    def calibrateOcto(self):
        """
        Calibrates the octoliner
        """

        if self.octo.optimize_sensitivity_on_black():
            print(f"Line sensor sucessfully calibrated, using sensitivity of: {str(self.octo.get_sensitivity())}")
        else:
            print("Auto calibration failed, using default sensitivity")
            self.octo.set_sensitivity(0.8)

        avgList = []

        for i in range(20):
            tmpList = self.octo.analog_read_all()
            avg = 0
            for x in tmpList:
                avg = avg + x

            avgList.append((avg / len(tmpList)))
        
        total = 0
        for x in avgList:
            total = total + x

        blackAvg = total / len(avgList)
        self.cutoff = blackAvg / 2

        print(f"Average Black level: {str(blackAvg)} \nCutoff at: {str(self.cutoff)}")

    def lineDetectThread(self):
        """
        Thread that keeps running to look for the white tape edging
        """
        
        while True:

            tmpList = self.octo.analog_read_all()
            avg = 0
            for x in tmpList:
                avg = avg + x

            avg = avg / len(tmpList)

            if avg <= self.cutoff:
                if not self.seenLine: # first time seeing the white line
                    print("Line detected")
                    
                    self.seenLine = True
                    
                    # change directions of the motors to drive away from the line
                    if self.lmd == self.BWD:
                        self.lmd = self.FWD
                    else:
                        self.lmd = self.BWD
                    
                    if self.rmd == self.BWD:
                        self.rmd = self.FWD
                    else:
                        self.rmd = self.BWD

                    self.myMotor.set_drive(self.L_MTR, self.lmd, self.lmp)
                    self.myMotor.set_drive(self.R_MTR, self.rmd, self.rmp)
            else:
                if self.seenLine:
                    print("back to black")
                    self.seenLine = False
                    

        
    def isBusy(self):
        """
        Gets the avaliability of the motor controller

        Returns:
            bool: True if busy, false if free
        """
        return self.busy

    def drive(self, lrtList):
        """
        Handles driving the rover in forwards or reverse
        Args:
            lrtList (list): list of LRT commands
        """
        self.busy = True
        self.myMotor.enable()

        sleepTime = 0
        self.lmp = 0
        self.rmp = 0

        for lrt in lrtList:

            if lrt.left > 127: # left is going in reverse
                self.lmp = round(254 * (((lrt.left - 128))/127))
                self.lmd = self.BWD
                
            else: # left is going forward
                self.lmp = round(254 * (((lrt.left))/127))
                self.lmd = self.FWD
                
            if lrt.right > 127: # right is going in reverse
                self.rmp = round(254 * (((lrt.right - 128))/127))
                self.rmd = self.BWD
                
            else: # right is going forward
                self.rmp = round(254 * (((lrt.right))/127))
                self.rmd = self.FWD
                
            sleepTime = (lrt.time * 10) / 1000
            self.myMotor.set_drive(self.L_MTR, self.lmd, self.lmp)
            self.myMotor.set_drive(self.R_MTR, self.rmd, self.rmp)
            time.sleep(sleepTime)
     
        self.myMotor.set_drive(0,0,0)
        self.myMotor.set_drive(1,0,0)
        self.myMotor.disable()
        self.busy = False
        

        
       
if __name__ == "__main__":
    rover = Rover()
    rover.myMotor.enable()

    while True:
        cmd = input()

        if cmd == 'w':
            #rover.drive('fwd', 1)
            rover.myMotor.set_drive(0,0,254)
            rover.myMotor.set_drive(1,0,254)
        elif cmd == 's':
            #rover.drive('bwd', 1)
            rover.myMotor.set_drive(0,1,254)
            rover.myMotor.set_drive(1,1,254)
        elif cmd == 'a':
            #rover.turn('lft', 1)
            rover.myMotor.set_drive(0,0,254)
            rover.myMotor.set_drive(1,1,254)
        elif cmd == 'd':
            #rover.turn('rgt', 1)
            rover.myMotor.set_drive(0,1,254)
            rover.myMotor.set_drive(1,0,254)
        else:
            rover.myMotor.set_drive(0,0,0)
            rover.myMotor.set_drive(1,0,0)
        
        
        
        