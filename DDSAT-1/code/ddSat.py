# Code for managing the satellite part of DDSat1
# Created for defcon28 Aerospace village

import threading    # needed for threading
import time         # needed for sleep
import struct       # needed for serial
import random       # used for random
import serial   # needed for serial
import random # needed for random
import binascii # needed for hex decoding

from gpiozero import CPUTemperature # needed for cpu temperature

from adafruit_servokit import ServoKit

import pygame   # used for playing audio sound effects

from rfEmulator import RFEmulator # needed for fake RF conversions

class DDSat:
    '''The main class for playing hte DDSat game.'''

    def __init__(self, com1, com2):
        '''Initialization function that takes in the two com ports to use for serial as input'''

        # serial setup
        self.pay1 = serial.Serial(str(com1), 9600, timeout=0.5)
        self.pay2 = serial.Serial(str(com2), 9600, timeout=0.5)

        # cmd num
        self.cmdNum = 0
        
        # payload 1
        self.pay1Temp = 0
        self.pay1Lite = 0
        self.pay1Stat = "Operational"

        # payload 2
        self.pay2Temp = 0
        self.pay2Lite = 0
        self.pay2Stat = "Operational"

        # servo controls
        self.kit = ServoKit(channels=16)
        self.batt1 = self.kit.servo[0]
        self.cam01 = self.kit.servo[1]
        self.batt2 = self.kit.servo[2]

        self.batt1.angle = 90
        self.batt2.angle = 90
        self.cam01.angle = 90


        self.rfConvert = RFEmulator()

    def decodeCmdMsg(self, cmdMsg):
        '''Decodes the command message and returns the following values: \nfmt:boolean thats true if message was properly formated \ncmdNum: the new command num \npayload: the message payload'''

        msgLen = ''
        msgCRC = ''
        msgCmdNum = ''
        msgPayload = ''
        msgTemp = ''

        if cmdMsg[0:2] == '43': # checks if the message starts with 'C', the command identifier
            if len(cmdMsg) >= 24: # check to see if message is at least min length
                msgCmdNum = int(cmdMsg[2:4], 16)
                #print(str(msgCmdNum))
                if (((msgCmdNum - self.cmdNum) > 0 and ((msgCmdNum - self.cmdNum) < 25)) or ((self.cmdNum >= 240) and (msgCmdNum <= 10)) ):
                    msgLen = int(cmdMsg[4:6], 16)
                    #print(str(msgLen))
                    if (msgLen * 2) == (len(cmdMsg) - 14):
                        msgTemp = cmdMsg[0 : (len(cmdMsg) - 8)]
                        #print(msgTemp)
                        msgCRC = cmdMsg[(len(cmdMsg) - 8) :]
                        testCRC = format(binascii.crc32(msgTemp.encode()), '08x')
                        #print(f"{msgCRC} : {testCRC}")
                        if msgCRC.lower() == testCRC :
                            msgPayload = cmdMsg[6 : (6 + (msgLen * 2))]
                            return True, msgCmdNum, msgPayload
                        else: # failed CRC check
                            print('failed CRC check')
                            return False, 0, "NULL" 
                    else: # failed to have valid message length field
                        print('failed to have valid message length field')
                        print(f"MsgLen: {str(msgLen*2)} : {str((len(cmdMsg) - 14))}")
                        return False, 0, "NULL"    
                else: # failed to meet cmdNum requirements
                    print("failed to meet cmdNum requirements")
                    return False, 0, "NULL"
            else: # failed to meet min length
                print("failed to meet min length")
                return False, 0, "NULL"    
        else: # started with value other than 'C'
            print("started with value other than 'C'")
            return False, 0, "NULL"
        
    def processCmd(self, cmd):
        ''' processes the base64 encoded commands'''

        demod = self.rfConvert.decodeManBase(cmd)
        response = ""

        valid, newCNum, msg = self.decodeCmdMsg(demod)

        if valid:

            #print("Valid message")

            self.cmdNum = int(newCNum)

            print(f"New Command Number: {str(self.cmdNum)}")

            target = binascii.a2b_hex(msg[0:10]).decode()

            #print(target)

            if target.upper() == 'PAY01':
                response = self.processPAY01(msg)
            elif target.upper() == 'PAY02':
                response = self.processPAY02(msg)
            elif target.upper() == 'BAT01':
                response = self.processBattery(msg, 1)
            elif target.upper() == 'BAT02':
                response = self.processBattery(msg, 2)
            elif target.upper() == 'CAM01':
                response = self.processCAM(msg)
            else:
                response = "ERROR, UNKNOWN TARGET"
        else:
            response = "ERROR, INVALID MESSAGE"

        #print(f"In process cmd: {response}")

        return self.generateRspMsg(response)

    def processCAM(self, msg):
        '''handles the camera commands'''

        response  = ""

        temp = binascii.a2b_hex(str(msg)).decode()

        if len(temp) >= 7:
            cmd = temp[5]

            angle = temp[6:]

            print(angle)

            if cmd.upper() == 'A':
                try:
                    angle = int(angle)

                    if angle >= 0 and angle <= 180:
                        self.cam01.angle = angle

                        return f"CAM01A{angle}"
                    else:
                        return "ERROR INVALID ANGLE"
                except ValueError:
                    return "ERROR ANGLE NOT A NUMBER"
            else:
                return "ERROR, INVALID SUBCOMMAND"



    def processBattery(self, msg, panelNum):
        ''' handles validating and acting on battery commands '''

        response = ""

        temp = binascii.a2b_hex(str(msg)).decode()

        if len(temp) >= 7:
            cmd = temp[5]

            angle = temp[6:]

            #print(angle)

            if cmd.upper() == 'A':
                try:
                    angle = int(angle)

                    if angle >= 0 and angle <= 180:
                        if panelNum == 1:
                            self.batt1.angle = angle

                            return f"BAT01: {angle}"
                        elif panelNum == 2:
                            self.batt2.angle = angle

                            return f"BAT02: {angle}"
                        else:
                            return f"ERROR UNKNOWN BATTERY"
                    else:
                        return f"ERROR INVALID ANGLE"
                except ValueError:
                    print("non int value for battery")

                    return "ERROR NON-INT VALUE FOR ANGLE"
            else:
                response = "ERRORN UNKNOWN SUBCOMMAND"

        else:
            response = "ERROR IMPROPER FORMAT"
        
        return response

    
    def payloadInterface(self, payNum, cmd, payloadArray):
        '''Handels sending commands to the payload over serial and returns the response'''

        fmt = "3s" + "B"*len(payloadArray)
        packedData = struct.pack(fmt, cmd.encode(), *payloadArray)

        #print(fmt)
        try:
            if payNum == 1:
                self.pay1.write(packedData)
                self.pay1.flush

                data = self.pay1.readline()
                if len(data.decode()) > 0:
                    #print(f"In payload interface: {data.decode()}")
                    return data.decode()
                else:
                    self.pay1Stat = "Disabled"
                    return "ERROR TIMEOUT"
            elif payNum == 2:
                self.pay2.write(packedData)
                self.pay2.flush

                data = self.pay2.readline()
                if len(data.decode()) > 0:
                    #print(f"In payload interface: {data.decode()}")
                    return data.decode()
                else:
                    self.pay2Stat = "Disabled"
                    return "ERROR TIMEOUT"
        except IOError:
            return "ERROR TIMEOUT"
        
    
    def processColor(self, payNum, msg):
        
        color = msg[1:]
        payloadArray = [0,0,0]

        #print("in pcolor")

        # Easter Egg = ROYGBIV
        if color.upper() == "ROYGBIV":
            self.payloadInterface(payNum, "led", [0,255,0,0]) # RED
            self.payloadInterface(payNum, "led", [1,255,69,0]) # ORANGE
            self.payloadInterface(payNum, "led", [2,218,165,32]) # GOLD
            self.payloadInterface(payNum, "led", [3,255,255,0]) # YELLOW
            self.payloadInterface(payNum, "led", [4,0,255,0]) # GREEN
            self.payloadInterface(payNum, "led", [5,0,255,255]) # CYAN
            self.payloadInterface(payNum, "led", [6,0,0,255]) # BLUE
            self.payloadInterface(payNum, "led", [7,75,0,130]) # INDIGO
            self.payloadInterface(payNum, "led", [8,128,0,128]) # PURPLE
            self.payloadInterface(payNum, "led", [9,128,0,255]) # VIOLET

            response = "EASTER_EGG"

        if msg[0].upper() == 'A':
            if color.upper() == "RED":
                payloadArray = [255,0,0]
            elif color.upper() == "ORANGE":
                payloadArray = [255,69,0]
            elif color.upper() == "YELLOW":
                payloadArray = [255,255,0]
            elif color.upper() == "GREEN":
                payloadArray = [0,255,0]
            elif color.upper() == "CYAN":
                payloadArray = [0,255,255]
            elif color.upper() == "BLUE":
                payloadArray = [0,0,255]
            elif color.upper() == "INDIGO":
                payloadArray = [75,0,130]
            elif color.upper() == "VIOLET":
                payloadArray = [128,0,255]
            elif color.upper() == "PURPLE":
                payloadArray = [128,0,128]
            elif color.upper() == "GOLD":
                payloadArray == [218,165,32]
            elif color.upper() == "WHITE":
                payloadArray == [255,255,255]
            elif color.upper() == "BLACK":
                payloadArray == [0,0,0]
            elif color.upper() == "RANDOM":
                payloadArray = [random.randrange(255), random.randrange(255), random.randrange(255)]
            else:
                #print("error")
                response = "ERROR INVALID COLOR"
            response = f"PAY0{str(payNum)}" + self.payloadInterface(payNum, "all", payloadArray)
        elif msg[0].upper() == 'U':
            if color.upper() == "RED":
                payloadArray = [255,0,0]
            elif color.upper() == "ORANGE":
                payloadArray = [255,69,0]
            elif color.upper() == "YELLOW":
                payloadArray = [255,255,0]
            elif color.upper() == "GREEN":
                payloadArray = [0,255,0]
            elif color.upper() == "CYAN":
                payloadArray = [0,255,255]
            elif color.upper() == "BLUE":
                payloadArray = [0,0,255]
            elif color.upper() == "INDIGO":
                payloadArray = [75,0,130]
            elif color.upper() == "VIOLET":
                payloadArray = [128,0,255]
            elif color.upper() == "PURPLE":
                payloadArray = [128,0,128]
            elif color.upper() == "GOLD":
                payloadArray == [218,165,32]
            elif color.upper() == "WHITE":
                payloadArray == [255,255,255]
            elif color.upper() == "BLACK":
                payloadArray == [0,0,0]
            elif color.upper() == "RANDOM":
                payloadArray = [random.randrange(255), random.randrange(255), random.randrange(255)]
            else:
                #print("error")
                response = "ERROR INVALID COLOR"
            response = f"PAY0{str(payNum)}" + self.payloadInterface(payNum, "top", payloadArray)
        elif msg[0].upper() == 'B':
            if color.upper() == "RED":
                payloadArray = [255,0,0]
            elif color.upper() == "ORANGE":
                payloadArray = [255,69,0]
            elif color.upper() == "YELLOW":
                payloadArray = [255,255,0]
            elif color.upper() == "GREEN":
                payloadArray = [0,255,0]
            elif color.upper() == "CYAN":
                payloadArray = [0,255,255]
            elif color.upper() == "BLUE":
                payloadArray = [0,0,255]
            elif color.upper() == "INDIGO":
                payloadArray = [75,0,130]
            elif color.upper() == "VIOLET":
                payloadArray = [128,0,255]
            elif color.upper() == "PURPLE":
                payloadArray = [128,0,128]
            elif color.upper() == "GOLD":
                payloadArray == [218,165,32]
            elif color.upper() == "WHITE":
                payloadArray == [255,255,255]
            elif color.upper() == "BLACK":
                payloadArray == [0,0,0]
            elif color.upper() == "RANDOM":
                payloadArray = [random.randrange(255), random.randrange(255), random.randrange(255)]
            else:
                #print("error")
                response = "ERROR INVALID COLOR"
            response = f"PAY0{str(payNum)}" + self.payloadInterface(payNum, "btm", payloadArray)
        elif msg[0] == '0' or msg[0] == '1' or msg[0] == '2' or msg[0] == '3' or msg[0] == '4' or msg[0] == '5' or msg[0] == '6' or msg[0] == '7' or msg[0] == '8' or msg[0] == '9':
            if color.upper() == "RED":
                payloadArray = [int(msg[0]), 255,0,0]
            elif color.upper() == "ORANGE":
                payloadArray = [int(msg[0]), 255,69,0]
            elif color.upper() == "YELLOW":
                payloadArray = [int(msg[0]), 255,255,0]
            elif color.upper() == "GREEN":
                payloadArray = [int(msg[0]), 0,255,0]
            elif color.upper() == "CYAN":
                payloadArray = [int(msg[0]), 0,255,255]
            elif color.upper() == "BLUE":
                payloadArray = [int(msg[0]), 0,0,255]
            elif color.upper() == "INDIGO":
                payloadArray = [int(msg[0]), 75,0,130]
            elif color.upper() == "VIOLET":
                payloadArray = int(msg[0]), [128,0,255]
            elif color.upper() == "PURPLE":
                payloadArray = [int(msg[0]), 128,0,128]
            elif color.upper() == "GOLD":
                payloadArray == [int(msg[0]), 218,165,32]
            elif color.upper() == "WHITE":
                payloadArray == [int(msg[0]), 255,255,255]
            elif color.upper() == "BLACK":
                payloadArray == [int(msg[0]), 0,0,0]
            elif color.upper() == "RANDOM":
                payloadArray = [int(msg[0]), random.randrange(255), random.randrange(255), random.randrange(255)]
            else:
                #print("error")
                response = "ERROR INVALID COLOR"

            response = f"PAY0{str(payNum)}" + self.payloadInterface(payNum, "led", payloadArray)
        else:
            response = "ERROR"

        #print(f"color response: {response}")

        return response

    def processPAY01(self, msg):
        '''handels payload 01 commands from the user'''

        #print("in procpay")

        temp = binascii.a2b_hex(str(msg)).decode()

        payload = temp[5:] # Remove PAY01

        #print(payload)

        response = ""

        if payload[0].upper() == 'A' or payload[0].upper() == 'B' or payload[0].upper() == 'U' or payload[0] == '0' or payload[0] == '1' or payload[0] == '2' or payload[0] == '3' or payload[0] == '4' or payload[0] == '5' or payload[0] == '6' or payload[0] == '7' or payload[0] == '8' or payload[0] == '9': # set color command
             response = self.processColor(1, payload)
        elif payload[0].upper() == "L": # Light level request
            response =  self.payloadInterface(1,"lit", [1,1,1])
            tmp = response.split()
            if len(tmp) >= 2:
                self.pay1Lite = tmp[1]
        elif payload[0].upper() == "T": # temp level request
            response =  self.payloadInterface(1,"tmp", [1,1,1])
            tmp = response.split()
            if len(tmp) >= 2:
                self.pay1Temp = tmp[1]
        elif payload[0].upper() == "R": # reset request
            response =  self.payloadInterface(1,"rst", [1,1,1])
        else:
            response = "Error, something has gone horribly wrong"
        return response
        
    def processPAY02(self, msg):
        '''handels payload 02 commands from the user'''

        #print("in procpay")

        temp = binascii.a2b_hex(str(msg)).decode()

        payload = temp[5:] # Remove PAY02

        #print(payload)

        response = ""

        if payload[0].upper() == 'A' or payload[0].upper() == 'B' or payload[0].upper() == 'U' or payload[0] == '0' or payload[0] == '1' or payload[0] == '2' or payload[0] == '3' or payload[0] == '4' or payload[0] == '5' or payload[0] == '6' or payload[0] == '7' or payload[0] == '8' or payload[0] == '9': # set color command
             response = self.processColor(2, payload)
        elif payload[0].upper() == "L": # Light level request
            response =  self.payloadInterface(2,"lit", [1,1,1])
            tmp = response.split()
            if len(tmp) >= 2:
                self.pay2Lite = tmp[1]
        elif payload[0].upper() == "T": # temp level request
            response =  self.payloadInterface(2,"tmp", [1,1,1])
            tmp = response.split()
            if len(tmp) >= 2:
                self.pay2Temp = tmp[1]
        elif payload[0].upper() == "R": # reset request
            response =  self.payloadInterface(2,"rst", [1,1,1])
        else:
            response = "Error, something has gone horribly wrong"
        return response
        
    def statusCheck(self):
        ''' polls cpx and system'''

        msg =  f"PAY01TEMP: {self.pay1Temp} PAY01LIGHT: {self.pay1Lite} PAY02TEMP: {self.pay2Temp} PAY02LIGHT: {self.pay2Lite} SATTETEMP: {CPUTemperature().temperature} BAT01ANGLE: {round(self.batt1.angle)} BAT02ANGLE: {round(self.batt2.angle)} CAM01ANGLE: {round(self.cam01.angle)}"

        cmd = '53' # S in hex

        payload = binascii.b2a_hex(msg.encode()).decode()

        # format command number
        fmtCNum = format(self.cmdNum, '02x')
        if len(fmtCNum) > 2:
            fmtCNum = fmtCNum[(len(fmtCNum) - 2) :]

        # format message length
        payLen = round(len(payload) / 2)
        fmtLen = format(payLen, '02x')
        if len(fmtLen) > 2:
            fmtLen = fmtLen[(len(fmtLen) - 2) :]

        # get CRC
        msg = cmd + fmtCNum + fmtLen + payload
        crc = format(binascii.crc32(msg.encode()), '08x')

        #print(crc)

        fullMsg = msg + crc
        #print(fullMsg)
        return self.rfConvert.encodeHex(fullMsg)



    def generateRspMsg(self, msg):
        '''Generates the response Message based on the payload \msg: the message to encode'''

        cmd = '52' # R in hex

        payload = binascii.b2a_hex(msg.encode()).decode()

        # format command number
        fmtCNum = format(self.cmdNum, '02x')
        if len(fmtCNum) > 2:
            fmtCNum = fmtCNum[(len(fmtCNum) - 2) :]

        # format message length
        payLen = round(len(payload) / 2)
        fmtLen = format(payLen, '02x')
        if len(fmtLen) > 2:
            fmtLen = fmtLen[(len(fmtLen) - 2) :]

        # get CRC
        msg = cmd + fmtCNum + fmtLen + payload
        crc = format(binascii.crc32(msg.encode()), '08x')

        #print(crc)

        fullMsg = msg + crc
        #print(fullMsg)
        return self.rfConvert.encodeHex(fullMsg)