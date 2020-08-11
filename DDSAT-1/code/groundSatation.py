import threading    # needed for threading
import time         # needed for sleep
import random       # used for selection of sound effects
import binascii # needed for encoding

import pygame   # used for playing audio sound effects

from rfEmulator import RFEmulator # for RF encoding and decoding

class GroundStation:
    ''' Used as the ground station in DDSat'''

    def __init__(self, CFG):
        
        self.cfg = CFG

        self.commandNum = 0

        self.rf = RFEmulator()

        #pygame.mixer.init(channels=2)
        #pygame.init()
        #self.background_channel = pygame.mixer.Channel(0)
        #self.effect_channel = pygame.mixer.Channel(1)
        #self.background_str = random.choice(self.cfg["audio"]["background"])
        #self.bg_audio_loop = pygame.mixer.Sound(self.background_str)
        #self.background_channel.play( self.bg_audio_loop, loops=-1)

    def updateCmdNum(self, newNum):
        ''' updates the command number and role over if its too high '''
        if int(newNum) > 250:
            self.commandNum = 0
        else:
            self.commandNum = newNum

    def generateCmdMsg(self, msg):
        '''Generates the Command Message based on the given string string'''

        payload = binascii.b2a_hex(msg.encode()).decode()

        cmd = '43' # C in hex

        # format command number
        fmtCNum = format(self.commandNum, '02x')
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
        return  self.rf.encodeHex(fullMsg)

    def decodeMsg(self, response):
        '''Decodes the command message and returns the following values: \nfmt:boolean thats true if message was properly formated \ncmdNum: the new command num \npayload: the message payload'''

        msgLen = ''
        msgCRC = ''
        msgCmdNum = ''
        msgPayload = ''
        msgTemp = ''

        cmdMsg = self.rf.decodeManBase(response)

        if cmdMsg[0:2] == '52' or cmdMsg[0:2] == '53': # checks if the message starts with 'C', the command identifier
            if len(cmdMsg) >= 24: # check to see if message is at least min length
                msgCmdNum = int(cmdMsg[2:4], 16)
                #print(str(msgCmdNum))
                if True:
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

