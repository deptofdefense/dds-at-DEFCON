# Code for managing the game part of cpx simpleSat
# Created for defcon28 aerospace village


import threading    # needed for threading
import time         # needed for sleep
import struct       # needed for serial
import random       # used for selection of sound effects

import serial   # needed for serial
import pygame   # used for playing audio sound effects

from userList import SatUser    # needed for tracking user progress

import os


class SimpleSat:
    ''' Used to manage progressing through the cpx simple sat game '''

    def __init__(self, CFG):

        self.cfg = CFG
        self.port = serial.Serial(self.cfg["hardware"]["serial"],
                                  baudrate=self.cfg["hardware"]["baud"],
                                  timeout=1)

        pygame.mixer.init(channels=2)
        pygame.init()
        self.background_channel = pygame.mixer.Channel(0)
        self.effect_channel = pygame.mixer.Channel(1)
        self.background_str = random.choice(self.cfg["audio"]["background"])
        self.bg_audio_loop = pygame.mixer.Sound(self.background_str)
        self.background_channel.play( self.bg_audio_loop, loops=-1)

    def checkCmd(self, user, cmd):
        ''' Checks the user command and passes to the appropriate function

        -user the current SatUser
        - cmd the full command string

        returns the step they should advance to and the string to give to them '''

        cmdList = str(cmd).split()

        if len(cmdList) >= 2:
            if cmdList[1].lower() == "login":
                return self.userLogin(user, cmd)
            elif cmdList[1].lower() == "ant":
                return self.controllerAnt(user, cmd)
            elif cmdList[1].lower() == "bat":
                return self.solarCmd(user, cmd)
            elif cmdList[1].lower() == "temp":
                return self.tempCmd(user, cmd)
            elif cmdList[1].lower() == "orbit":
                return self.orbitCmd(user, cmd)
            elif cmdList[1].lower() == "led":
                return self.ledCmd(user, cmd)
            elif cmdList[1].lower() == "servo":
                return self.armCmd(user, cmd)
            elif cmdList[1].lower() == "help":
                return self.helpCmd(user, cmd)
            else:
                return "Error, subcommand not found.  Valid subcommands are: login, ant, bat, temp, orbit, help"
        else:
            return "Valid subcommands are: login, ant, bat, temp, orbit, help"

    def helpCmd(self, user, cmd):
        '''Handles all help messages and background info of subcommands'''

        cmdList = cmd.split()

        if len(cmdList) >= 3:
            if cmdList[2].lower() == 'help':
                return "Help is the subcommand that provides background and game commentary on the different subcommands"
            elif cmdList[2].lower() == 'login':
                return "The login subcommand is used to gain initial access to the ground station.  In this game there are two user accounts, one is a normal user and one is an admin.  To find out the username and password look through the ICD and other online documents for hints.  This will be the first subcommand you have to solve"
            elif cmdList[2].lower() == 'ant':
                if len(cmdList) >= 4:
                    if cmdList[3].lower() == 'calc':
                        return "The calc function lets you find out what zone to set the antenna to.  It's designed to take 3 values as lat lon alt, however you do not need to give it your real lat lon alt"
                    elif cmdList[3].lower() == 'set':
                        return "The set function is what lets you set the control antennas to target a specific zone"
                    elif cmdList[3].lower() == 'status':
                        return "The status function is fluff command in this game"
                    else:
                        return "The valid functions are calc, set, and status"
                else:
                    return "The ant subcommand deals with setting and checking the two control antennas of the satellite.  Rather than targeting a specific location, control antennas tend to target specific zone or regions of the planet.  Depending on the purpose of the satellite that zone could be a large or narrow region.  Most systems will also have a backup control antenna that can be used to regain control if the primary in cases when the primary connection suddenly drops"
            elif cmdList[2].lower() == 'bat':
                if len(cmdList) >= 4:
                    if cmdList[3].lower() == 'enable':
                        return "The enable function lets you set the solar panel to a charging state.  Note not actually used in this game"
                    elif cmdList[3].lower() == 'disable':
                        return "The disable function lets you set the solar panel to a discharging state.  The fact that this is the only function that works just shows how much life sucks for a SimpleSat"
                    else:
                        return "The valid functions are enable and disable"
                else:
                    return "The bat command deals with solar power management.  It also teaches the user how to interact with systems that they are not able to directly touch.  A skill useful for other games"
            elif cmdList[2].lower() == 'temp':
                if len(cmdList) >= 4:
                    if cmdList[3].lower() == 'set':
                        return "The set function lets to set the min and max operating temperature in Celsius"
                    elif cmdList[3].lower() == 'status':
                        return "The status function lets you see what the default temperature range that you need to overwhelm is.  Note this info is also in the ICD"
                    else:
                        return "The valid functions are set and status"
                else:
                    return "The temp subcommand deals with temperature management.  Fun fact: when you don't have an atmosphere its a real pain to stay at the right operating temperature"
            elif cmdList[2].lower() == 'orbit':
                if len(cmdList) >= 4:
                    if cmdList[3].lower() == 'mode':
                        return "The mode function is used to switch between manual and automatic orbit control.  While it may seem like fluff here, it could be more important in other challenges"
                    elif cmdList[3].lower() == 'set':
                        return "The set function is used to update the orbital parameters.  In a different game, it might be how you spin a satellite around the room...if thats what your into"
                    elif cmdList[3].lower() == 'ignite':
                        return "This is the command you run to win the game...do you really need to know more?"
                    elif cmdList[3].lower() == 'status':
                        return "This is a fluff command in this game"
                    else:
                        return "The valid functions are mode, set, status, and ignite"
                return "The orbit subcommand deals with setting and enabling different orbital parameters.  In order to win the game, one must activate the ignite function"
            elif cmdList[2].lower() == 'servo':
                return "This is one of the freeplay commands unlocked after winning the game.  It allows the user to manually set the angle on any of the four servos, ordered 1 through 4"
            elif cmdList[2].lower() == 'led':
                return "This is one of the freeplay commands unlocked after winning the game.  It allows the user to set the RGB values of any one of the LEDs, ordered 0 through 9"
            else:
                return "Error, unknown subcommand, valid subcommands are: login, bat, ant, temp, orbit, help, and the free play commands"  
        else:
            return "Error, format is !cmd help <subcommand>"

    def orbitCmd(self, user, cmd):
        ''' Handles the orbital commands for the satellite '''

        cmdList = cmd.split()

        if len(cmdList) == 3:
            if cmdList[2] == "ignite":
                if user.getCurrentStep() < 2:
                    return "Error, user does not have access to this command"
                elif user.getCurrentStep() < 9:
                    return "Error, system is in automatic flight mode"
                elif user.getCurrentStep() == 9:
                    self.cmdThread("error", "led", [8, 10, 0, 10])
                    return "Error, no difference detected from current orbit"
                elif user.getCurrentStep() == 10:
                    self.cmdThread("launch", "led", [8, 10, 0, 0])
                    user.setCurrentStep(11)
                    time.sleep(0.4)
                    self.reset(user.getCurrentStep())
                    return "Congratulations, you won the main game.  Now see if you can find the hidden commands!  To claim your free swag, send us your twitch handle in Discord at av-cpx-simplesat-text and tag CK or email DDS-at-DEFCON@dds.mil"
                else:
                    return "Error, this step has already been completed"
            elif cmdList[2] == "status":
                if user.getCurrentStep() == 0:
                    return "Error, user does not have access to this command"
                elif user.getCurrentStep() < 8:
                    return "System operating with automatic controls, orbit parameters: TBD"
                elif user.getCurrentStep() == 8:
                    return "Error Flight mode locked down, user input required, orbit parameters: TBD"
                elif user.getCurrentStep() == 9:
                    return "System operating with manual controls enabled, orbit parameters: TBD"
                elif user.getCurrentStep() == 10:
                    return "Error Flight mode locked down, user input required, orbit parameters: Manual"
            else:
                return "Error, improper command format.  Valid commands are !cmd orbit status, !cmd orbit ignite, !cmd orbit mode man/auto, !cmd orbit set inclination/eccentricity x"
        elif len(cmdList) == 4:
            if cmdList[2] == "mode":
                if user.getCurrentStep() < 2:
                    return "Error, user does not have access to this command"
                elif user.getCurrentStep() < 8:
                    return "Error, mode locked into automatic"
                elif user.getCurrentStep() == 8:
                    if cmdList[3] == "auto":
                        return "Unfortunately the point of the game is to take manual control of the satellite, so this mode does nothing"
                    elif cmdList[3] == "man":
                        self.cmdThread("orbitMode", "led", [6, 10, 0, 0])
                        user.setCurrentStep(9)
                        return "Flight mode set to manual" + " ------ " + self.statusMsg(user)
                    else:
                        return "Error, improper command format.  Valid commands are !cmd orbit status, !cmd orbit ignite, !cmd orbit mode man/auto, !cmd orbit set inclination/eccentricity x"
                else:
                    return "Error, improper command format.  Valid commands are !cmd orbit status, !cmd orbit ignite, !cmd orbit mode man/auto, !cmd orbit set inclination/eccentricity x"
            else:
                return "Error, improper command format.  Valid commands are !cmd orbit status, !cmd orbit ignite, !cmd orbit mode man/auto, !cmd orbit set inclination/eccentricity x"
        elif len(cmdList) == 5:
            if cmdList[2] == "set":
                if user.getCurrentStep() < 2:
                    return "Error, user does not have access to this command"
                elif user.getCurrentStep() < 9:
                    return "Error, system operating in automatic flight mode"
                elif user.getCurrentStep() == 9:
                    if cmdList[3] == "inclination" or cmdList[3] == "eccentricity":
                        self.cmdThread("orbitMode", "led", [7, 10, 0, 0])
                        user.setCurrentStep(10)
                    else:
                        return "Error, improper subcommand, valid commands are !cmd orbit set inclination x or !cmd orbit set eccentricity x"
                    return "Orbit paramaters different than those stored, manual ignition authorized" + " ------ " + self.statusMsg(user)
                else:
                    return "Error, step completed"
            else:
                return "Error, improper command format.  Valid commands are !cmd orbit status, !cmd orbit ignite, !cmd orbit mode man/auto, !cmd orbit set inclination/eccentricity x"
        else:
            return "Error, improper command format.  Valid commands are !cmd orbit status, !cmd orbit ignite, !cmd orbit mode man/auto, !cmd orbit set inclination/eccentricity x"

    def controllerAnt(self, user, cmd):
        ''' Handles the steps relating to the controller antennas and zone calc
        - user: The SatUser sending the command
        - cmd: The command the user sent

        returns a string representing the response, and updates current step internally '''

        cmdList = str(cmd).split()

        if (cmdList[2] == "status"):
            if (len(cmdList) == 4):
                if (cmdList[3] == "pri"):
                    if (user.getCurrentStep() >= 4):
                        return "Primary Antenna Status: -60 dBm reception,  Excellent signal connection" + " ------ " + self.statusMsg(user)
                    elif (user.getCurrentStep() > 0):
                        return "Primary Antenna Status: -120 dBm reception,  Poor signal connection" + " ------ " + self.statusMsg(user)
                    else:
                        return "ERROR, user does not have access to this function" + " ------ " + self.statusMsg(user)
                elif (cmdList[3] == "sec"):
                    if (user.getCurrentStep() >= 3):
                        return "Secondary Antenna Status: -60 dBm reception,  Excellent signal connection" + " ------ " + self.statusMsg(user)
                    elif (user.getCurrentStep() > 0):
                        return "Secondary Antenna Status: -120 dBm reception,  Poor signal connection" + " ------ " + self.statusMsg(user)
                    else:
                        return "ERROR, user does not have access to this function" + " ------ " + self.statusMsg(user)
                else:
                    return "Error, command should be !cmd ant status pri or !cmd ant status sec" + " ------ " + self.statusMsg(user)
            else:
                return "Error, command should be !cmd ant status pri or !cmd ant status sec" + " ------ " + self.statusMsg(user)
        elif (cmdList[2] == "set"):
            if (len(cmdList) == 5):
                if (cmdList[3] == "sec"):
                    if (user.getCurrentStep() >= 3):
                        return "Error, this step has already been completed" + " ------ " + self.statusMsg(user)
                    elif (user.getCurrentStep() == 2):
                        if (int(cmdList[4]) == user.getZone()):
                            # The actual step to do stuff
                            self.cmdThread("arm", "arm", [4, 180], 0.3)
                            self.cmdThread("ant", "led", [1, 10, 0, 0])
                            user.setCurrentStep(3)
                            return f"Secondary Antenna now targeting zone: {user.getZone()}" + " ------ " + self.statusMsg(user)
                        else:
                            self.cmdThread("arm", "arm", [4, 180], 0.5)
                            self.cmdThread("arm", "arm", [4, 90])
                            return f"Error, Zone: {cmdList[4]} is not the correct zone to set to." + " ------ " + self.statusMsg(user)
                    else:
                        return "Error, user does not have the access level to access this command" + " ------ " + self.statusMsg(user)
                elif (cmdList[3] == "pri"):
                    if (user.getCurrentStep() >= 4):
                        return "Error, this step has already been completed" + " ------ " + self.statusMsg(user)
                    elif (user.getCurrentStep() == 3):
                        if (int(cmdList[4]) == user.getZone()):
                            self.cmdThread("arm", "arm", [3, 0], 0.3)
                            self.cmdThread("ant", "led", [2, 10, 0, 0])
                            user.setCurrentStep(4)
                            return f"Primary Antenna now targeting zone: {user.getZone()}" + " ------ " + self.statusMsg(user)
                        else:
                            self.cmdThread("arm", "arm", [3, 0], 0.5)
                            self.cmdThread("arm", "arm", [3, 90])
                            return f"Error, Zone: {cmdList[4]} is not the correct zone to set to." + " ------ " + self.statusMsg(user)
                    elif (user.getCurrentStep() == 2):
                        if (int(cmdList[4]) == user.getZone()):
                            self.cmdThread("arm", "arm", [3, 0], 0.5)
                            self.cmdThread("arm", "arm", [3, 90])
                            return f"Primary Antenna Realignment overridden by SpaceDotCom HQ Ground Station" + " ------ " + self.statusMsg(user)
                        else:
                            self.cmdThread("arm", "arm", [3,0], 0.5)
                            self.cmdThread("arm", "arm", [3,90])
                            return f"Error, Zone: {cmdList[4]} is not the correct zone to set to." + " ------ " + self.statusMsg(user)
                    else:
                        return "Error, user does not have the access level to access this command" + " ------ " + self.statusMsg(user)
                else:
                    return "Error, improper command format, command should be !cmd ant set pri xyz or !cmd ant set sec xyz " + " ------ " + self.statusMsg(user)
            else:
                return "Error, improper command format, command should be !cmd ant set pri xyz or !cmd ant set sec xyz " + " ------ " + self.statusMsg(user)
        elif (cmdList[2] == "calc"):
            if (len(cmdList) == 6):
                return f"After a series of complicated calculations, your ground station is located in zone: {user.getZone()} " + " ------ " + self.statusMsg(user)
            else:
                return "Error, format should be !cmd ant calc latitude longitude altitude"
        else:
            return "Error, valid ant commands are: !cmd ant status, !cmd ant set, and !cmd ant calc"

    def solarCmd(self, user, cmd):
        ''' Commands that control the solar panels within the game
        returns a string with the game response '''

        cmdList = cmd.split()

        if (len(cmdList) == 4):
            if (cmdList[2] == "enable"):
                return "...Our apologizes, but the point of this game is to break the satellite, not fix it.  That's what HAS is for"
            elif (cmdList[2] == "disable"):
                if (cmdList[3] == "pri"):
                    if (user.getCurrentStep() < 2):
                        return "Error, user does not have the access level to control the battery system"
                    elif (user.getCurrentStep() < 4):
                        self.cmdThread("arm", "arm", [1, 0], 0.5)
                        self.cmdThread("arm", "arm", [1, 90])
                        return "Error, command overridden by SpaceDotCom HQ Ground Station"
                    elif (user.getCurrentStep() == 4):
                        self.cmdThread("arm", "arm", [1, 0], 0.3)
                        self.cmdThread("none", "led", [3, 10, 0, 0])
                        user.setCurrentStep(5)
                        return "Primary Solar Panel disabled, system in reduced charging state" + " ------ " + self.statusMsg(user)
                    elif (user.getCurrentStep() == 5):
                        return "Error, step already completed"
                    elif (user.getCurrentStep() == 6):
                        self.cmdThread("arm", "arm", [1, 0], 0.3)
                        self.cmdThread("none", "led", [3, 10, 0, 0])
                        user.setCurrentStep(7)
                        return "Primary Solar Panel disabled, battery now in discharge mode.  WARNING: Temperature control backup disabled to save battery life" + " ------ " + self.statusMsg(user)
                    elif (user.getCurrentStep() >= 7):
                        return "Error, step already completed"
                    else:
                        return f"error, this is an invalid state in solarCmd: {user.getCurrentStep()}"
                elif (cmdList[3] == "sec"):
                    if (user.getCurrentStep() < 2):
                        return "Error, user does not have the access level to control the battery system"
                    elif (user.getCurrentStep() < 4):
                        self.cmdThread("arm", "arm", [2, 180], 0.5)
                        self.cmdThread("arm", "arm", [2, 90])
                        return "Error, command overridden by SpaceDotCom HQ Ground Station"
                    elif (user.getCurrentStep() == 4):
                        self.cmdThread("arm", "arm", [2, 180], 0.3)
                        self.cmdThread("none", "led", [4, 10, 0, 0])
                        user.setCurrentStep(6)
                        return "Secondary Solar Panel disabled, system in reduced charging state" + " ------ " + self.statusMsg(user)
                    elif (user.getCurrentStep() == 5):
                        self.cmdThread("arm", "arm", [2, 180], 0.3)
                        self.cmdThread("none", "led", [4, 10, 0, 0])
                        user.setCurrentStep(7)
                        return "Secondary Solar Panel disabled, battery now in discharge mode.  WARNING: Temperature control backup disabled to save battery life" + " ------ " + self.statusMsg(user)
                    elif (user.getCurrentStep() == 6):
                        return "Error, step already completed"
                    elif (user.getCurrentStep() >= 7):
                        return "Error, step already completed"
                    else:
                        return f"error, this is an invalid state in solarCmd: {user.getCurrentStep()}"
                else:
                    return "Error, improper format.  The command format is !cmd bat enable/disable pri/sec"
            else:
                return "Error, improper format.  The command format is !cmd bat enable/disable pri/sec"
        elif len(cmdList) == 3 and cmdList[2] == "status":
            if (user.getCurrentStep() <= 4):
                return "Battery rapidly charging, backup TCU enabled"
            elif user.getCurrentStep() == 5 or user.getCurrentStep() == 5:
                return "Battery slowly charging, backup TCU enabled"
            else:
                return "Battery discharging, backup TCU disabled"
        else:
            return "Error, improper format.  The command format is !cmd bat enable/disable pri/sec or !cmd bat status"

    def tempCmd(self, user, cmd):
        ''' Allows the user to set and interact with the temperature control unit '''

        cmdList = cmd.split()

        if len(cmdList) == 3:
            if cmdList[2] == "status":
                if user.getCurrentStep() == 0:
                    return "Error, user has not logged in and does not have access to this command"
                elif user.getCurrentStep() < 7:
                    return "TCU and backup are fully operational: Min: 0 C, Max: 40 C" + " ------ " + self.statusMsg(user)
                elif user.getCurrentStep() == 7:
                    return "Error, backup disabled.  Primary TCU: Min: 0 C, Max: 40 C" + " ------ " + self.statusMsg(user)
                else:
                    return "Error, TCU disabled" + " ------ " + self.statusMsg(user)
            else:
                return "Error, valid command formats are: !cmd temp status and !cmd temp set min max"
        elif len(cmdList) == 5:
            if cmdList[2] == "set":
                if((int(cmdList[3]) < 0) or (int(cmdList[4]) > 40)):
                    if user.getCurrentStep() < 2:
                        return "Error, user does not have access to this command" + " ------ " + self.statusMsg(user)
                    elif user.getCurrentStep() < 4:
                        return "Error, command overridden by SpaceDotCom HQ groundstation" + " ------ " + self.statusMsg(user)
                    elif user.getCurrentStep() < 7:
                        self.cmdThread("error", "led", [5, 10, 0, 10])
                        return "Error, primary TCU was restored by battery powered backup" + " ------ " + self.statusMsg(user)
                    elif user.getCurrentStep() == 7:
                        user.setCurrentStep(8)
                        self.cmdThread("temp", "led", [5, 10, 0, 0])
                        return "Warning, TCU operating outside of normal range.  Automatic Flight controls are disabled, initializing failsafe mode" + " ------ " + self.statusMsg(user)
                    else:
                        return "Error, TCU disabled" + " ------ " + self.statusMsg(user)
                else:
                    return "Error, adjustment will have no effect on the satellite"
            else:
                return "Error, valid command formats are: !cmd temp status and !cmd temp set min max"
        else:
            return "Error, valid command formats are: !cmd temp status and !cmd temp set min max"

    def ledCmd(self, user, cmd):
        ''' Allows the user to individually set any of the leds to a color of their choosing.  Should only be used after they won the game '''

        cmdList = cmd.split()

        if (user.getCurrentStep() >= 11):

            if (user.getCurrentStep() == 11) or user.getCurrentStep() == 12:
                user.setCurrentStep(13)
                self.cmdThread("win", "rst", [user.getCurrentStep()])
                time.sleep(0.3)

            if (len(cmdList) == 6):
                self.cmdThread("led", "led", [int(cmdList[2]), int(cmdList[3]), int(cmdList[4]), int(cmdList[5])])
                return f"{user.getName()} set led {cmdList[2]} to [{cmdList[3]}, {cmdList[4]}, {cmdList[5]}]"
            else:
                return "Error, format should be !cmd led n R G B"
        else:
            return "Error, this command is reserved for after you beat the game"

    def armCmd(self, user, cmd):
        ''' Allows the user to individually set any of the servos to an angle their choosing.  Should only be used after they won the game '''

        cmdList = cmd.split()

        if (user.getCurrentStep() >= 11):

            if (user.getCurrentStep() == 11) or user.getCurrentStep() == 12:
                user.setCurrentStep(13)
                self.cmdThread("win", "rst", [user.getCurrentStep()])
                time.sleep(0.3)

            if (len(cmdList) == 4):
                self.cmdThread("arm", "arm", [int(cmdList[2]), int(cmdList[3])])
                return f"{user.getName()} set servo {cmdList[2]} to {cmdList[3]}"
            else:
                return "Error, format should be !cmd servo n angle"
        else:
            return "Error, this command is reserved for after you beat the game"

    def statusMsg(self, user):
        ''' Generates a status message for the user based on their current step
        user - the sat user to base the status off of
        returns a string representing the status'''

        if user.getCurrentStep() == 0:
            return "System Status: Error, user has not yet logged in"
        elif user.getCurrentStep() == 1:
            return "System Status: Access Level: User, Primary controller signal: weak, Secondary controller signal: weak, Battery Status: Rapid Charging, Temperature Control: 20C, Orbit Control: Automatic, Recommend Maintainer evaluation"
        elif user.getCurrentStep() == 2:
            return "System Status: Access Level: Root, Primary controller signal: weak, Secondary controller signal: weak, Battery Status: Rapid Charging, Temperature Control: 20C, Orbit Control: Automatic, Recommend Realigning Control Antennas"
        elif user.getCurrentStep() == 3:
            return "System Status: Access Level: Root, Primary controller signal: weak, Secondary controller signal: Strong, Battery Status: Rapid Charging, Temperature Control: 20C, Orbit Control: Automatic"
        elif user.getCurrentStep() == 4:
            return "System Status: Access Level: Root, Primary controller signal: Strong, Secondary controller signal: Strong, Battery Status: Rapid Charging, Temperature Control: 20C, Orbit Control: Automatic"
        elif user.getCurrentStep() == 5:
            return "System Status: Access Level: Root, Primary controller signal: Strong, Secondary controller signal: Strong, Battery Status: Charging, Temperature Control: 20C, Orbit Control: Automatic"
        elif user.getCurrentStep() == 6:
            return "System Status: Access Level: Root, Primary controller signal: Strong, Secondary controller signal: Strong, Battery Status: Charging, Temperature Control: 20C, Orbit Control: Automatic"
        elif user.getCurrentStep() == 7:
            return "System Status: Access Level: Root, Primary controller signal: Strong, Secondary controller signal: Strong, Battery Status: discharging, Temperature Control: 20C, Orbit Control: Automatic"
        elif user.getCurrentStep() == 8:
            return "System Status: Access Level: Root, Primary controller signal: Strong, Secondary controller signal: Strong, Battery Status: discharging, Temperature Control: ERROR, Orbit Control: Automatic"
        elif user.getCurrentStep() == 9:
            return "System Status: Access Level: Root, Primary controller signal: Strong, Secondary controller signal: Strong, Battery Status: discharging, Temperature Control: ERROR, Orbit Control: Manual"
        elif user.getCurrentStep() == 10:
            return "System Status: Access Level: Root, Primary controller signal: Strong, Secondary controller signal: Strong, Battery Status: discharging, Temperature Control: ERROR, Orbit Control: Manual"
        elif user.getCurrentStep() == 11:
            return "System Status: Access Level: Root, Primary controller signal: Strong, Secondary controller signal: Strong, Battery Status: discharging, Temperature Control: ERROR, Orbit Control: Manual"
        elif user.getCurrentStep() == 12:
            return "System Status: Free Play unlocked, try to find the commands to directly control the servos and leds"
        else:
            return "Something funny happened to your step counter"


    def userLogin(self, user, cmd):
        ''' handles the steps involving the user logging into the system.
        - user is the SatUser sending the command
        - cmd is the login command string

        returns a string containing the response to the user and updates the SatUser's current step internally '''

        cmdList = str(cmd).split()

        if (len(cmdList) == 4):
            if (user.getCurrentStep() >= 2):
                return "Error, user has already completed this step" + " ------ " + self.statusMsg(user)
            else:
                if (cmdList[2] == user.getName()):
                    if (cmdList[3].lower() == "password"):

                        #serial request
                        self.cmdThread("userLogin", "led", [0, 10, 0, 10])
                        user.setCurrentStep(1)

                        return f"Welcome back {cmdList[2]}, Your last login: 12/21/1999" + " ------ " + self.statusMsg(user)
                    else:
                        return "Error, incorrect password" + " ------ " + self.statusMsg(user)
                elif (cmdList[2] == self.cfg["game"]["username"]):
                    if (cmdList[3] == self.cfg["game"]["password"]) or (str(cmdList[3]).lower() == str(self.cfg["game"]["password"]).lower()):

                        #serial request
                        self.cmdThread("rootLogin", "led", [0, 10, 0, 0])
                        user.setCurrentStep(2)

                        return "Maintenance login accepted." + " ------ " + self.statusMsg(user)
                    else:
                        return "Error, incorrect password" + " ------ " + self.statusMsg(user)
                else:
                    return "Error, unknown username" + " ------ " + self.statusMsg(user)
        else:
            return "Error, incorrect format, format should be !cmd login username password" + " ------ " + self.statusMsg(user)


    # resets the ground station which in turn resets the satellite
    def reset(self, step):
        self.cmdThread("error", "rst", [step])


    # handles sending json data in separate thread
    def cmdThread(self, audioSelect, cmdWord, payloadArray, delay=0):

        fmt = "I3s" + "B" * len(payloadArray)

        # Use the 'splat' operator on payloadArray to pass as individual variables
        packedData = struct.pack(fmt, 0, cmdWord.encode(), (*payloadArray))

        # Wrap the actual Serial request into a daemon thread
        threading.Thread(target=self.serial_thread, args=(packedData,), daemon=True).start()

        sound_effect_str = None

        if (audioSelect == "arm"):
            sound_effect_str = random.choice(self.cfg["audio"]["arm"])
        elif (audioSelect == "led"):
            sound_effect_str = random.choice(self.cfg["audio"]["led"])
        elif (audioSelect == "userLogin"):
            sound_effect_str = random.choice(self.cfg["audio"]["userLogin"])
        elif (audioSelect == "rootLogin"):
            sound_effect_str = random.choice(self.cfg["audio"]["rootLogin"])
        elif (audioSelect == "ant"):
            sound_effect_str = random.choice(self.cfg["audio"]["ant"])
        elif (audioSelect == "temp"):
            sound_effect_str = random.choice(self.cfg["audio"]["temp"])
        elif (audioSelect == "orbitMode"):
            sound_effect_str = random.choice(self.cfg["audio"]["orbitMode"])
        elif (audioSelect == "launch"):
            sound_effect_str = random.choice(self.cfg["audio"]["launch"])
        elif (audioSelect == "error"):
            sound_effect_str = random.choice(self.cfg["audio"]["error"])
        elif (audioSelect == "win"):
            sound_effect_str = random.choice(self.cfg["audio"]["win"])
        else:
            sound_effect_str = None
        
        if(sound_effect_str):
            effect = pygame.mixer.Sound(sound_effect_str)
            self.background_channel.set_volume(.4)
            # restore the background audio AFTER the effect has completed
            threading.Thread(target=self.restore_background_volume, args=(effect.get_length(),), daemon=True).start()

            self.effect_channel.play(effect)

        time.sleep(delay)

    def setTheme(self, user, cmd):
        ''' sets the background music'''

        cmdList = cmd.split()

        if len(cmdList) >= 2:
            if cmdList[1].lower() == 'random':
                self.background_str = random.choice(self.cfg["audio"]["background"])
                self.bg_audio_loop = pygame.mixer.Sound(self.background_str)
                self.background_channel.play( self.bg_audio_loop, loops=-1)
                tempStr = self.background_str.split(".")[0]
                return f"Setting background music to {tempStr}"
            elif cmdList[1].lower() == 'list':
                return "Audio choices are: bensoundScifi, SpaceAmbience, Futuristic1, EonAmbient, SirusBeatOne"
            elif cmdList[1].lower() == 'bensoundscifi':
                self.background_str = 'audio/bensoundScifi.wav'
                self.bg_audio_loop = pygame.mixer.Sound(self.background_str)
                self.background_channel.play( self.bg_audio_loop, loops=-1)
                return "Setting background music to bensoundScifi"
            elif cmdList[1].lower() == 'spaceambience':
                self.background_str = 'audio/SpaceAmbience.wav'
                self.bg_audio_loop = pygame.mixer.Sound(self.background_str)
                self.background_channel.play( self.bg_audio_loop, loops=-1)
                return "Setting background music to SpaceAmbience"
            elif cmdList[1].lower() == 'futuristic1':
                self.background_str = 'audio/Futuristic1.wav'
                self.bg_audio_loop = pygame.mixer.Sound(self.background_str)
                self.background_channel.play( self.bg_audio_loop, loops=-1)
                return "Setting background music to Futuristic1"
            elif cmdList[1].lower() == 'eonambient':
                self.background_str = 'audio/EonAmbient.wav'
                self.bg_audio_loop = pygame.mixer.Sound(self.background_str)
                self.background_channel.play( self.bg_audio_loop, loops=-1)
                return "Setting background music to EonAmbient"
            elif cmdList[1].lower() == 'sirusbeatone':
                self.background_str = 'audio/SirusBeatOne.wav'
                self.bg_audio_loop = pygame.mixer.Sound(self.background_str)
                self.background_channel.play( self.bg_audio_loop, loops=-1)
                return "Setting background music to SirusBeatOne"
            else:
                return 'Error, improper format.  Run "!theme random" to randomly set the theme, or "!theme list" to list the music, or "!theme <x>" to set to a specific song'
        else:
            return 'Error, improper format.  Run "!theme random" to randomly set the theme, or "!theme list" to list the music, or "!theme <x>" to set to a specific song'

    def restore_background_volume(self, delay):
        # Simple function to restore the background volume AFTER a delay
        time.sleep(delay)
        self.background_channel.set_volume(1)

    def serial_thread(self, packedData):
        # Simple function to make the Serial call
        self.port.write(packedData)
        self.port.flush
