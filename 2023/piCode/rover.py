import pi_servo_hat # needed for servo control
import math # needed for floor
import qwiic_scmd # needed for motor control
import RPi.GPIO as GPIO # needed to controller smoke machine
import time # needed for sleep
import socket # needed for UDP sockets
import random # needed for random number generator
from threading import Thread # needed for multithreading
import sys # needed for exit

class Rover:

    def __init__(self):

        # UDP Socket
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverSocket.bind(('0.0.0.0', 7331))

        self.responseSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Smoke Machine
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(20, GPIO.OUT) # Smoke Machine Trigger
        GPIO.setup(21, GPIO.OUT) # Air Pump Trigger
        GPIO.output(20, GPIO.LOW)
        GPIO.output(21, GPIO.LOW)

        # IR Sensors
        self.leftSensor = 14
        self.rightSensor = 15
        GPIO.setup(self.leftSensor, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.rightSensor, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Motor stuff
        self.myMotor = qwiic_scmd.QwiicScmd()
        self.R_MTR = 0
        self.L_MTR = 1
        self.FWD = 1
        self.BWD = 0
        self.currentL = 1 # current direction of Left motor
        self.currentR = 1 # current direction of Right motor
        self.currentLP = 0
        self.currentRP = 0
        self.maxSpeed = 250
        self.myMotor.begin()
        time.sleep(.250) # Zero Motor Speeds
        self.myMotor.set_drive(0,0,0)
        self.myMotor.set_drive(1,0,0)
        self.myMotor.enable()

        # Servo stuff
        self.servo = pi_servo_hat.PiServoHat()
        self.servo.restart()
        self.servo.move_servo_position(0, 90, 180)

        # Check that tells if the rover is busy
        self.busy = False

        self.hackedResponse = ["You're a hacker Harry", "Help, I've been hacked and I can't get up", "1337 H4X0R D373C73D", "Does anyone else smell toast?", "This is why you can't have nice things", ".........................You're In....................", "Do you solemnly swear that you are up to no good?"]

        # start IR thread
        self.irThread = Thread(target=self.lineSensorThread, daemon=True)
        self.irThread.start()

    def parseCommand(self, commandString):

        self.busy = True

        for line in str(commandString).splitlines():
            command = line.split(',')

            if len(command) >= 3: # Expecting at least three fields, command, angle, and time

                if str(command[0]).lower() == 'forward': # forward command
                    self.myMotor.set_drive(self.R_MTR, self.FWD, self.maxSpeed)
                    self.myMotor.set_drive(self.L_MTR, self.FWD, self.maxSpeed)
                    self.currentR = self.FWD
                    self.currentL = self.FWD
                    self.currentLP = self.maxSpeed
                    self.currentRP = self.maxSpeed
                    
                    sleepTime = command[2].split()[0]

                    if float(sleepTime) > 10: # check to keep run time reasonable
                        sleepTime = 10
                    elif float(sleepTime) == 0: # check to make sure no rapid motor shifts
                        sleepTime = 1 

                    time.sleep(float(sleepTime))
                    self.myMotor.set_drive(self.R_MTR, self.FWD, 0)
                    self.myMotor.set_drive(self.L_MTR, self.FWD, 0)
                    self.currentR = self.FWD
                    self.currentL = self.FWD
                    self.currentLP = 0
                    self.currentRP = 0
                        
                elif str(command[0]).lower() == 'reverse': # reverse command
                    self.myMotor.set_drive(self.R_MTR, self.BWD, self.maxSpeed)
                    self.myMotor.set_drive(self.L_MTR, self.BWD, self.maxSpeed)
                    self.currentR = self.BWD
                    self.currentL = self.BWD
                    self.currentLP = self.maxSpeed
                    self.currentRP = self.maxSpeed
                    
                    sleepTime = command[2].split()[0]

                    if float(sleepTime) > 10: # check to keep run time reasonable
                        sleepTime = 10
                    elif float(sleepTime) == 0: # check to make sure no rapid motor shifts
                        sleepTime = 1 

                    time.sleep(float(sleepTime))
                    self.myMotor.set_drive(self.R_MTR, self.FWD, 0)
                    self.myMotor.set_drive(self.L_MTR, self.FWD, 0)
                    self.currentR = self.FWD
                    self.currentL = self.FWD
                    self.currentLP = 0
                    self.currentRP = 0

                
                elif str(command[0]).lower() == 'turn': # turn command

                    angle = float(command[1].split()[0])

                    if float(angle) > 1080: # if doing more than 3x 360, max out
                        angle = 1080
                    elif float(angle) < -1080:
                        angle = -1080

                    runTime =  (abs(float(angle)) / 180) * 2.0
                    print(str(runTime))

                    if angle > 0: # Turn Right
                        self.myMotor.set_drive(self.R_MTR, self.BWD, self.maxSpeed)
                        self.myMotor.set_drive(self.L_MTR, self.FWD, self.maxSpeed)
                        self.currentR = self.BWD
                        self.currentL = self.FWD
                        self.currentLP = self.maxSpeed
                        self.currentRP = self.maxSpeed
                    else: # Turn Left
                        self.myMotor.set_drive(self.R_MTR, self.FWD, self.maxSpeed)
                        self.myMotor.set_drive(self.L_MTR, self.BWD, self.maxSpeed)
                        self.currentR = self.FWD
                        self.currentL = self.BWD
                        self.currentLP = self.maxSpeed
                        self.currentRP = self.maxSpeed
                    
                    time.sleep(runTime)
                    self.myMotor.set_drive(self.R_MTR, self.FWD, 0)
                    self.myMotor.set_drive(self.L_MTR, self.FWD, 0)
                    self.currentR = self.FWD
                    self.currentL = self.FWD
                    self.currentLP = 0
                    self.currentRP = 0

                elif str(command[0]).lower() == 'set': # pan camera to set angle

                    angle = command[1].split()[0]
                    self.setCameraAngle(float(angle))

                elif str(command[0]).lower() == 'adjust': # pan camera to a relative angle

                    angle = command[1].split()[0]
                    self.adjustCameraAngle(float(angle))
                
                else: # unknown command
                    chatResponse = f"HACKED: {str(random.choice(self.hackedResponse))}" 
                    print(chatResponse)
                    self.responseSocket.sendto(str.encode(chatResponse), (self.responseAddr, 7331))
                    self.smoker(10)
            
            else:
                errorMsg = (f"Error, unknown formatting: {line}")
                print(errorMsg)
                self.responseSocket.sendto(str.encode(errorMsg), (self.responseAddr, 7331))


        self.busy = False

    def smoker(self, runTime):

        time.sleep(0.25)
        
        self.myMotor.set_drive(self.R_MTR, self.BWD, self.maxSpeed)
        self.myMotor.set_drive(self.L_MTR, self.FWD, self.maxSpeed)
        self.currentR = self.BWD
        self.currentL = self.FWD
        self.currentLP = self.maxSpeed
        self.currentRP = self.maxSpeed
        time.sleep(0.25)
        GPIO.output(20, GPIO.HIGH) # turn on smoke machine
        GPIO.output(21, GPIO.HIGH) # turn on air pump
        

        time.sleep(float(runTime))

        GPIO.output(20, GPIO.LOW) # turn off smoke machine
        GPIO.output(21, GPIO.LOW) # turn off air pump
        self.myMotor.set_drive(0,0,0)
        self.myMotor.set_drive(1,0,0)
        self.currentR = self.FWD
        self.currentL = self.FWD
        self.currentLP = 0
        self.currentRP = 0

    def reset(self):
        
        self.servo.move_servo_position(0, 90, 180) # face camera forward
        GPIO.output(20, GPIO.LOW) # turn off smoke machine
        GPIO.output(21, GPIO.LOW) # turn off air pump
        self.myMotor.set_drive(0,0,0)
        self.myMotor.set_drive(1,0,0)
        self.currentR = self.FWD
        self.currentL = self.FWD
        self.currentLP = 0
        self.currentRP = 0
        self.busy = False

    def setCameraAngle(self, angle):

        if angle > 180:
            angle = 180
        elif angle < 0:
            angle = 0

        self.servo.move_servo_position(0, math.floor(angle), 180)

    def adjustCameraAngle(self, angle):

        currentAngle = self.servo.get_servo_position(0, 180)
        newAngle = currentAngle + angle

        if newAngle > 180: 
            newAngle = 180
        elif newAngle < 0:
            newAngle = 0

        self.servo.move_servo_position(0, math.floor(newAngle), 180)

    def socketListener(self):

        while True:

            #print("Listening")
            data, addr = self.serverSocket.recvfrom(1024)

            self.responseAddr = addr[0]

            #print(str(self.responseAddr))

            reply = data.decode()

            if len(reply) > 0: 

                if not self.busy:

                    msg = ""

                    msgList = str(reply).splitlines()

                    if len(msgList) > 5:
                        sizeString = f"Received {str(len(msgList))} commands, only performing the first five"
                        msgList = msgList[0:5]
                        self.responseSocket.sendto(str.encode(sizeString), (self.responseAddr, 7331))

                    for line in msgList:
                            data = line.split(']')[0]
                            msg = msg + data[1:] + '\n'
                    #print(msg) 

                    self.parseCommand(msg)

                else:
                    responseMsg = "Rover is busy finishing previous command"
                    self.responseSocket.sendto(str.encode(responseMsg), (self.responseAddr, 7331))

    def lineSensorThread(self): 

        while True:
            if GPIO.input(self.leftSensor): # check to see if left or right sensor can no longer see the paper
                print("Black line detected")
                
                if self.currentL == self.FWD: # switch left motor from forward to reverse
                    self.myMotor.set_drive(self.L_MTR, self.BWD, self.currentLP)
                    self.currentL = self.BWD
                else: # switch left motor from reverse to forward
                    self.myMotor.set_drive(self.L_MTR, self.FWD, self.currentLP)
                    self.currentL = self.FWD

                if self.currentR == self.FWD: # switch right motor from forward to reverse
                    self.myMotor.set_drive(self.R_MTR, self.BWD, self.currentRP)
                    self.currentR = self.BWD
                else: # switch right motor from reverse to forward
                    self.myMotor.set_drive(self.R_MTR, self.FWD, self.currentRP)
                    self.currentR = self.FWD
                
                time.sleep(2) # sleep long enough for us to get off the line
            time.sleep(0.1) # check every 0.1 seconds

                


if __name__ == "__main__":

    print("starting rover")

    rover = Rover()
    try:

        
        rover.socketListener()

        # will only be run once thread ends
        GPIO.cleanup()
    finally:
        print("Ending everything.")
        rover.reset()
        GPIO.cleanup()
        
        rover.myMotor.disable()
        sys.exit(0)

    

