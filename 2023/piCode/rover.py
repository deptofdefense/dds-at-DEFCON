import pi_servo_hat # needed for servo control
import sys
import math # needed for floor
import qwiic_scmd # needed for motor control
import RPi.GPIO as GPIO # needed to controller smoke machine
import time # needed for sleep
import socket # needed for UDP sockets
import random # needed for random number generator

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

        # Motor stuff
        self.myMotor = qwiic_scmd.QwiicScmd()
        self.R_MTR = 0
        self.L_MTR = 1
        self.FWD = 1
        self.BWD = 0
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

        self.hackedResponse = ["You're a hacker Harry", "Help, I've been hacked and I can't get up", "1337 H4X0R D373C73D", "Does anyone else smell toast?", "This is why you can't have nice things"]

    def parseCommand(self, commandString):

        
        self.busy = True

        for line in str(commandString).splitlines():
            command = line.split(',')

            if len(command) >= 3: # Expecting at least three fields, command, angle, and time

                if str(command[0]).lower() == 'forward': # forward command
                    self.myMotor.set_drive(self.R_MTR, self.FWD, self.maxSpeed)
                    self.myMotor.set_drive(self.L_MTR, self.FWD, self.maxSpeed)
                    
                    sleepTime = command[2].split()[0]

                    time.sleep(float(sleepTime))
                    self.myMotor.set_drive(self.R_MTR, self.FWD, 0)
                    self.myMotor.set_drive(self.L_MTR, self.FWD, 0)
                        
                elif str(command[0]).lower() == 'reverse': # reverse command
                    self.myMotor.set_drive(self.R_MTR, self.BWD, self.maxSpeed)
                    self.myMotor.set_drive(self.L_MTR, self.BWD, self.maxSpeed)
                    
                    sleepTime = command[2].split()[0]

                    time.sleep(float(sleepTime))
                    self.myMotor.set_drive(self.R_MTR, self.FWD, 0)
                    self.myMotor.set_drive(self.L_MTR, self.FWD, 0)

                
                elif str(command[0]).lower() == 'turn': # turn command

                    angle = float(command[1].split()[0])

                    runTime =  (abs(float(angle)) / 180) * 2.0
                    print(str(runTime))

                    if angle > 0: # Turn Right
                        self.myMotor.set_drive(self.R_MTR, self.BWD, self.maxSpeed)
                        self.myMotor.set_drive(self.L_MTR, self.FWD, self.maxSpeed)
                    else: # Turn Left
                        self.myMotor.set_drive(self.R_MTR, self.FWD, self.maxSpeed)
                        self.myMotor.set_drive(self.L_MTR, self.BWD, self.maxSpeed)
                    
                    time.sleep(runTime)
                    self.myMotor.set_drive(self.R_MTR, self.FWD, 0)
                    self.myMotor.set_drive(self.L_MTR, self.FWD, 0)

                elif str(command[0]).lower() == 'set': # pan camera to set angle

                    angle = command[1].split()[0]
                    self.setCameraAngle(float(angle))

                elif str(command[0]).lower() == 'adjust': # pan camera to a relative angle

                    angle = command[1].split()[0]
                    self.adjustCameraAngle(float(angle))
                
                else: # unknown command
                    chatResponse = random.choice(self.hackedResponse)
                    print(chatResponse)
                    self.responseSocket.sendto(str.encode(chatResponse), (self.responseAddr, 7331))
                    self.smoker(10)
            
            else:
                print(f"Error, unknown formatting: {line}")


        self.busy = False

    def smoker(self, runTime):

        time.sleep(0.25)
        self.myMotor.set_drive(0,0,0)
        self.myMotor.set_drive(1,0,0)
        time.sleep(0.25)
        GPIO.output(20, GPIO.HIGH) # turn on smoke machine
        GPIO.output(21, GPIO.HIGH) # turn on air pump
        

        time.sleep(float(runTime))

        GPIO.output(20, GPIO.LOW) # turn off smoke machine
        GPIO.output(21, GPIO.LOW) # turn off air pump
        self.myMotor.set_drive(0,0,0)
        self.myMotor.set_drive(1,0,0)

    def reset(self):
        
        self.servo.move_servo_position(0, 90, 180) # face camera forward
        GPIO.output(20, GPIO.LOW) # turn off smoke machine
        GPIO.output(21, GPIO.LOW) # turn off air pump
        self.myMotor.set_drive(0,0,0)
        self.myMotor.set_drive(1,0,0)
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

                msg = ""

                for line in str(reply).splitlines():
                        data = line.split(']')[0]
                        msg = msg + data[1:] + '\n'
                #print(msg) 

                self.parseCommand(msg)


if __name__ == "__main__":

    print("starting rover")

    rover = Rover()
    rover.socketListener()
