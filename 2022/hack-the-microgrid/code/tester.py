import threading    # needed for threading
import time         # needed for sleep
import struct
from urllib import response       # needed for serial
import serial   # needed for serial
import random # needed for random
import binascii # needed for hex decoding
import serial.tools.list_ports # needed to identify COM ports


class SerialTester:

    def __init__(self, solar, wind):
        """
        Init method

        Args:
            solar (str): the com port for the solar module or none
            wind (str): the com port for the wind module or none
        """

        if solar != 'none':
            self.solar = serial.Serial(solar, 9600, timeout=0.1)
        else:
            self.solar = 'none'
        if wind != 'none':    
            self.wind = serial.Serial(wind, 9600, timeout=0.1)
        else:
            self.wind = 'none'

    def shutdown(self):
        if self.solar != 'none':
            self.solar.reset_input_buffer()
            self.solar.reset_output_buffer()
            self.solar.close()

        if self.wind != 'none':
            self.wind.reset_input_buffer()
            self.wind.reset_output_buffer()
            self.wind.close()


    def packData(self, cmd, payloadArray):
        fmt = "3s" + "B"*len(payloadArray)
        packedData = struct.pack(fmt, cmd.encode(), *payloadArray)

        return packedData


    def payloadInterface(self, payNum, cmd, payloadArray):
        '''Handels sending commands to the payload over serial and returns the response'''

        fmt = "3s" + "B"*len(payloadArray)
        packedData = struct.pack(fmt, cmd.encode(), *payloadArray)

        loop = True

        #print(fmt)
        try:
            if payNum == 'sol':
                while loop:

                    self.solar.write(packedData)
                    self.solar.flush()
                    time.sleep(0.1)
                    
                    data = self.solar.read(32)
                    
                    if str(cmd).upper() in str(data.decode()):
                        loop = False
                    if 'ERROR' in str(data.decode()):
                        loop = False

                self.solar.reset_input_buffer()
                self.solar.reset_output_buffer()

                return data.decode()

            elif payNum == 'wnd':
                while loop:

                    self.wind.write(packedData)
                    self.wind.flush()
                    time.sleep(0.1)
                    
                    data = self.wind.read(32)
                    
                    if str(cmd).upper() in str(data.decode()):
                        loop = False
                    if 'ERROR' in str(data.decode()):
                        loop = False

                self.wind.reset_input_buffer()
                self.wind.reset_output_buffer()

                return data.decode()
        except IOError:
            return "ERROR TIMEOUT"


if __name__ == "__main__":

    print("Running Serial tester")

    # create defalut addresses
    wnd = "none"
    sol = "none"
    tester = SerialTester(sol, wnd)

    # get list of COM ports
    comList = serial.tools.list_ports.comports()

    # interrogate each COM port
    for com in comList:
        #print(com.device)
        testCOM = serial.Serial(str(com.device), 9600, timeout=0.1)
        testCOM.write(tester.packData('who', [1]))
        testCOM.flush()
        response = testCOM.readline()
        while len(response.decode()) < 1:
            testCOM.write(tester.packData('who', [1]))
            testCOM.flush()
            time.sleep(0.1)
            response = testCOM.readline()

        if 'WND' in response.decode():
            print(f"Found Wind COM port at {str(com.device)}")
            wnd = str(com.device)
        elif 'SOL' in response.decode():
            print(f"Found Solar COM port at {str(com.device)}")
            sol = str(com.device)
        else:
            print(f"Found Unknown COM port at {str(com.device)}")
        
        # reset port for next pass
        testCOM.reset_input_buffer()
        testCOM.reset_output_buffer()
        testCOM.close()

    # reinitalize with new addresses
    tester = SerialTester(sol, wnd)

    print("Message format: [target] [command] [payload]")

    while True:
        try:
            cmdString = input("\nEnter command: ")
            cmdList = cmdString.split(" ")

            if len(cmdList) >= 3:
                target = cmdList[0]
                cmd = cmdList[1]
                payload = cmdList[2:]

                for i in range(len(payload)):
                    payload[i] = int(payload[i])

                if target == "sol":
                    print(tester.payloadInterface('sol', cmd, payload))
                elif target == "wnd":
                    print(tester.payloadInterface('wnd', cmd, payload))
                else:
                    print("Invalid target")
        except KeyboardInterrupt:
            print("\nExiting...")
            tester.shutdown()
            break
        except UnicodeDecodeError:
            print("\nInvalid decode")
            continue