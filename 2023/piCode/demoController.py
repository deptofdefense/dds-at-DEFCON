# Code for controlling the rover with a bluetooth video game controller.  

import pygame # needed for controller code
from pygamecontroller import RobotController # needed for controller code
import pi_servo_hat # needed for servo control
import sys
import math
import qwiic_scmd # needed for motor control
import RPi.GPIO as GPIO # needed to controller smoke machine
import time

# Initializes objects

# Smoke Machine
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT) # Smoke Machine Trigger
GPIO.setup(21, GPIO.OUT) # Air Pump Trigger
GPIO.output(20, GPIO.LOW)
GPIO.output(21, GPIO.LOW)

# Motor stuff
myMotor = qwiic_scmd.QwiicScmd()
R_MTR = 0
L_MTR = 1
FWD = 1
BWD = 0

# Servo stuff
servo = pi_servo_hat.PiServoHat()
currentAngle = 90

def resetStuff():
        
    servo.move_servo_position(0, 90, 180) # face camera forward
    currentAngle = 90 # reset the current angle to the current servo position
    GPIO.output(20, GPIO.LOW) # turn off smoke machine
    GPIO.output(21, GPIO.LOW) # turn off air pump
    #myMotor.set_drive(0,0,0) # turn off right motors
    #myMotor.set_drive(1,0,0) # turn off left motors
    time.sleep(1)


#The controller program needs an initialization status callback function to send status codes
#to while the program looks for a supported game controller. This function will get called
#with status values counting up from 1 to 32 while it waits for a wireless controller to be
#paired using bluetooth, or for a usb dongle to be inserted or usb wired controller.
#If no supported controller is detected it will eventually be called with the status value -1
#Once a supported controller is detected it will return a status code of zero.
def initStatus(status):
    """ Function which displays status during initialization """
    if status == 0 :
        print("Supported controller connected")
        
        servo.restart()
        GPIO.output(20, GPIO.LOW)
        GPIO.output(21, GPIO.LOW)
        myMotor.begin()
        time.sleep(.250) # Zero Motor Speeds
        myMotor.set_drive(0,0,0)
        myMotor.set_drive(1,0,0)
        myMotor.enable()
		
    elif status < 0 :
        print("No supported controller detected")
    else:
        print("Waiting for controller {}".format(status) )


#--- Start of example call back functions for different type of controls on game controllers ---
def analogueTriggerChangeHandler(val):
    """ Handler function for an analogue trigger """
    print("Analogue Trigger Value Changed: {}".format(val) )

def panRight(val):
    """
    Handler for panning the camera to the right when the right analog trigger is pulled

    Args:
        val (_type_): how much the right trigger is being pressed in
    """
    
    if val > 0:
        angle = 180 - (val * 180)
        servo.move_servo_position(0, math.floor(angle), 180)

def panLeft(val):
    """
    Handler for panning the camera to the left when the left analog trigger is pulled

    Args:
        val (_type_): how much the left trigger is being pressed in
    """
    if val > 0:
        angle = (val * 180)
        servo.move_servo_position(0, math.floor(angle), 180)


def analogueStickChangeHandler(valLR, valUD):
    """ Handler function for an analogue joystick """
    print("Analogue Stick Changed: L/R:{} U/D:{}".format(valLR,valUD) )

def rightMotorChangeHandler(valLR, valUD):
    """ Handler function for the right joystick """
    
    mul = 1.2 # so that max speed happens slightly before joystick is max
    
    if valUD < 0: # go forward
        speed = math.ceil( 250 * (-1 * valUD * mul) )
        if speed >= 250:
            speed = 250
        myMotor.set_drive(R_MTR,FWD,speed)
    else: # go backwards
        speed = math.ceil( 250 * (valUD * mul) )
        if speed >= 250:
            speed = 250
        myMotor.set_drive(R_MTR,BWD,speed)
    time.sleep(0.1) # too many speed changes at once crashes the system

def leftMotorChangeHandler(valLR, valUD):
    """ Handler function for the Left joystick """
    mul = 1.2 # so that max speed happens slightly before joystick is max
    
    if valUD < 0: # go forward
        speed = math.ceil( 250 * (-1 * valUD * mul) )
        if speed >= 250:
            speed = 250
        myMotor.set_drive(L_MTR,FWD,speed)
    else: # go backwards
        speed = math.ceil( 250 * (valUD * mul) )
        if speed >= 250:
            speed = 250
        myMotor.set_drive(L_MTR,BWD,speed)
    time.sleep(0.1) # too many speed changes at once crashes the system



def hatHandler(valLR, valUD):
    """ Handler function for an joystick hat """
    print("Digital Hat Changed: L/R:{} U/D:{}".format(valLR,valUD) )


def btnHandler(val):
    """ Handler function for a button """
    print("Button State Changed. Value={}".format(val) )

def smokeHandler(val):
    """ Handler function for the smoke machine"""
    if val == 1:
        GPIO.output(20, GPIO.HIGH)
        GPIO.output(21, GPIO.HIGH)
    else:
        GPIO.output(20, GPIO.LOW)
        GPIO.output(21, GPIO.LOW)


def triangleBtnHandler(val):
    """ Handler function for the triangle button """
    if val == 1 :
        print("resetting system")
        resetStuff()
    

#--------------------- End of example change handler call back functions --------------------


#This is the main function of the program.
def main():
    """ Main program code. This function creates an instance of the robot controller class
        and passes in all the call back functions which will be called when the state of the
        associated buttons, joysticks and triggers on the game controller changes.
    """
    #Check any hardware you are using is present and initialise it here
    print("Initializing hardware")
    
    #Use a try..finally structure so that the program exits gracefully on hitting any
    #errors in the callback functions and cleans up any hardware you are using.
    try:
        cnt = RobotController("Game Controller Template Program", initStatus,
                              leftTriggerChanged = panLeft,
                              rightTriggerChanged = panRight,
                              rightStickChanged = rightMotorChangeHandler,
                              leftStickChanged = leftMotorChangeHandler,
                              hatChanged = hatHandler,
                              startBtnChanged = btnHandler,
                              circleBtnChanged = smokeHandler,
                              triangleBtnChanged = triangleBtnHandler
                              )
        
        #Check if the controller class initialised successfully
        if cnt.initialised :
            keepRunning = True
            #You can put any code here you want to use to indicate that a supported game
            #controller is connected and the program is ready. (e.g. Flash some LEDs green)
        else:
            keepRunning = False
            #You can put any code here you want to use to indicate that no supported game
            #controller was detected (the program will exit afterwards). e.g. Flash some LEDs red
            
        # -------- Main Program Loop -----------
        while keepRunning == True :
            #You have to call the controllerStatus function in a loop, as this is what
            #triggers any callback functions for controller state changes. It also checks for
            #the quit event (occurs when the pygame window is closed by a user), and returns
            #False if this happens. So the return value is used to exit the loop on quit.
            keepRunning = cnt.controllerStatus()
    
    finally:
        #Clean up pygame and any hardware you may be using
        #(e.g. Turn off LEDs and power down motors)
        pygame.quit()
        if cnt.initialised :
            #Put any clean up code for your program here
            print("Cleaning up")
            
            GPIO.output(20, GPIO.LOW) # turn off smoke machine
            GPIO.output(21, GPIO.LOW) # turn off air pump
            GPIO.cleanup() # cleanup all GPIO
            
            myMotor.set_drive(0,0,0)
            myMotor.set_drive(1,0,0)
            myMotor.disable()
            
            servo.move_servo_position(0, 90, 180) # face camera forward
            
            


if __name__ == '__main__':
    main()
