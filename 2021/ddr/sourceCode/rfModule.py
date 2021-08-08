import binascii # needed for conversions

class LRS:
    
    def __init__(self, left, right, time):
        """
        Class representing the tuple of the left motor, right motor, and time values

        Args:
            left (int): 0 to 255 for left motor power, values above 127 are in reverse
            right (int): 0 to 255 for right motor power, values above 127 are in reverse
            time (int): 0 to 255 for time in tens of milliseconds
        """
        
        if left > 255:
            self.left = 255
        else:
            self.left = left
        
        if right > 255:
            self.right = 255
        else:
            self.right = right  
        
        if time > 255:
            self.time = 255
        else:
            self.time = time
            
    def getASCIITuple(self):
        """
        returns the LRS tuple as an ascii string
        Returns:
            [type]: [description]
        """
        return f"{str(self.left)} {str(self.right)} {str(self.time)}"
    
    def getHexTuple(self):
        
        return f"{format(self.left, '02x')}{format(self.right, '02x')}{format(self.time, '02x')}"
            

class RFMod:
    """
    Module to emulate RF messages over twitch
    """
    
    def __init__(self):
        self.cmdNum = 0
        
    def updateCmdNum(self, cmdNum):
        """
        updates the stored command number to the new value

        Args:
            cmdNum (int): the new command number
        """
        
        self.cmdNum = cmdNum
        
        if self.cmdNum > 255:
            self.cmdNum = self.cmdNum - 255
        
    def incCmdNum(self):
        """
        increments the command number by one and does rollover if needed
        """
        
        self.cmdNum = self.cmdNum + 1
        
        if self.cmdNum > 255:
            self.cmdNum = 0
        
    def checkCmdNum(self, num):
        
        if self.cmdNum == num: # if expected command number
            return True
        elif ((num - self.cmdNum) >= 0 and (num - self.cmdNum) < 10) or (((num + 255) - self.cmdNum) >= 0 and ((num + 255) - self.cmdNum) < 10):
            return True
        else:
            return False
        
    def generateMsg(self, cmdType, tupleList):
        """
        Generates the command message using the given inputs

        Args:
            cmdType (int): 1 for a type 1 message or anything else for type 2
            tupleList (list): list of arrays representing the movement commands in LRT format

        Returns:
            string: the base64 encoded message
        """
        msg = ''
        
        cmdCount = len(tupleList)
        
        if cmdType == 1: # generate a type 1 command
            temp = f"1 {str(self.cmdNum)} 1 {tupleList[0].getASCIITuple()}"
            msg = binascii.b2a_base64(temp.encode()).decode('latin1')
        else: # generate a type 2 style message
            temp = f"{format(cmdType, '02x')}{format(self.cmdNum, '02x')}{format(cmdCount, '02x')}"
            
            for lrs in tupleList: # go through the list
                temp = temp + lrs.getHexTuple()
                
            #print(temp)
            #print(format(binascii.crc32(bytes.fromhex(temp)), '04x'))
            
            temp = temp + format(binascii.crc32(bytes.fromhex(temp)), '08x')

            msg = binascii.b2a_base64(bytes.fromhex(temp)).decode('latin1')
                
        return msg
    
    def decodeMsg(self, msg):
        """
        decodes the rf emulator messages back into its actual values

        Args:
            msg (str): the rf emulator generated message to decode

        Returns:
            bool: Ture if valid message, false if otherwise
            str: Response message to transmit to the user
            list: List of LRT commands in the message
        """
        try:
            
            temp = binascii.a2b_base64(msg).hex()
            
            lrs = LRS(0,0,0)
            response = "Error"
            
            if temp[0:2] == '31': # type 1 message
                #print('type1')
                temp = binascii.unhexlify(temp).decode()
                cmdList = temp.split()
                
                if len(cmdList) == 6: # check to see if right message length
                    
                    if self.checkCmdNum(int(cmdList[1])): # check if valid command number
                        
                        if cmdList[2] == '1': # check if valid message count
                            
                            lrs = LRS(int(cmdList[3]), int(cmdList[4]), int(cmdList[5]))
                            
                            response = f'1 movement command sent : {lrs.getASCIITuple()}'
                            
                            newNum = int(cmdList[1]) + 1
                            self.updateCmdNum(newNum)
                            #print(f"newCmdNum: {str(self.cmdNum)}")
                            return True, response, [lrs]
                        else:
                            response = "Error, invalid command count"
                            return False, response, [lrs]
                    else:
                        response = "Error, invalid command number"
                        return False, response, [lrs]
                else:
                    response = "Error, invalid message length"
                    return False, response, [lrs]
                    
            elif temp[0:2] == '02': # print type 2 message
                
                if len(temp) >= 14: # check total message length
                    
                    test = temp[0:(len(temp)-8)]

                    if temp == (test + format(binascii.crc32(bytes.fromhex(test)), '08x')): # CRC generated correctly
                        
                        testCN = int(test[2:4], 16)
                        testMC = int(test[4:6], 16)
                        payload = test[6:]

                        if self.checkCmdNum(testCN): # command number is correct

                            if testMC <= 4: # test that within max payload size

                                if (testMC * 6) == len(payload): # test that payload and movement command count match

                                    lrsList = []
                                    lrsString = ""

                                    for i in range(testMC):
                                        source = payload[(i*6):((i*6) + 6)]
                                        left = int(source[0:2], 16)
                                        right = int(source[2:4], 16)
                                        time = int(source[4:6], 16)

                                        lrsList.append(LRS(left, right, time))
                                        lrsString = lrsString + " " + lrsList[len(lrsList)-1].getHexTuple()
                                    
                                    response = f"{str(testMC)} movement commands sent:{lrsString}"
                                    self.updateCmdNum((testCN + 1))

                                    return True, response, lrsList

                                else:
                                    response = "Payload size does not match given number of movement commads"
                                    return False, response, [lrs]
                            else:
                                response = "Error, max of 4 movement commands allowed per a single message"
                                return False, response, [lrs]
                        else:
                            response = "Error, incorrect command number"
                            return False, response, [lrs]
                    else: # CRC incorrect
                        response = "CRC value incorrect"
                        return False, response, [lrs]
                else: # total message too short
                    response = "Total message to short, you need at least 7 bytes to play"
                    return False, response, [lrs]
                
            else:
                #print("Someones experimenting")
                response = "Error, invalid message type.  No easter eggs in this rush job"
                return False, response, [lrs]
            
        
        except binascii.Error:
            print("binascii error")
            lrs = LRS(0,0,0)
            response = "Error, command not encoded in base64"
            return False, response, [lrs]
        except: 
            print('unknown error')
            lrs = LRS(0,0,0)
            response = "Error, something really unexpected happened"
            return False, response, [lrs]
            
        
    
    
if __name__ == "__main__":

    test = LRS(25,255,125)
    rfMod = RFMod()
    
    rfMod.updateCmdNum(255)
    
    #for i in range(12):
    #    print(str(rfMod.checkCmdNum(i)))
    
    #print(test.getASCIITuple())
    #print(test.getHexTuple())
    
    msg = rfMod.generateMsg(1, [test])    
    print(msg)
    
    #valid, response, movements = rfMod.decodeMsg(msg)
    #print(response)
    #valid, response, movements = rfMod.decodeMsg(msg)
    #print(response)
    #valid, response, movements = rfMod.decodeMsg('asdfg')
    #print(response)
    msg = rfMod.generateMsg(2, [test, test, test, test])    
    print(msg)
    
    valid, response, movements = rfMod.decodeMsg(msg)
    print(response)
    
    #temp = binascii.a2b_base64(msg)
    
    #print(str(temp.hex()))