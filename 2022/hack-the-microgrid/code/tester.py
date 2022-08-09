import threading    # needed for threading
import time         # needed for sleep
import struct       # needed for serial
import serial   # needed for serial
import random # needed for random
import binascii # needed for hex decoding



class SerialTester:

    def __init__(self, com1, com2):

        self.pay1 = serial.Serial(com1, 9600, timeout=0.1)
        self.pay2 = serial.Serial(com2, 9600, timeout=0.1)



    def payloadInterface(self, payNum, cmd, payloadArray):
        '''Handels sending commands to the payload over serial and returns the response'''

        fmt = "3s" + "B"*len(payloadArray)

        print(fmt)
        print(cmd)
        print(payloadArray)

        packedData = struct.pack(fmt, cmd.encode(), *payloadArray)

        #print(fmt)
        try:
            if payNum == 1:
                self.pay1.write(packedData)
                self.pay1.flush()

                time.sleep(0.1)

                data = self.pay1.read(32)

                while len(data.decode()) < 1:
                    self.pay1.write(packedData)
                    self.pay1.flush()
                    time.sleep(0.1)
                    
                    data = self.pay1.read(32)
                    time.sleep(0.1)
                return data.decode()
            elif payNum == 2:
                self.pay2.write(packedData)
                self.pay2.flush()

                time.sleep(0.1)

                data = self.pay2.read(32)

                while len(data.decode()) < 1:
                    self.pay2.write(packedData)
                    self.pay2.flush()
                    time.sleep(0.1)
                    
                    data = self.pay2.read(32)
                    time.sleep(0.1)
                return data.decode()
        except IOError:
            return "ERROR TIMEOUT"


if __name__ == "__main__":

    print("Running Serial tester")
    tester = SerialTester("COM32", "COM13")

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

                if target == "pay1":
                    print(tester.payloadInterface(1, cmd, payload))
                elif target == "pay2":
                    print(tester.payloadInterface(2, cmd, payload))
                else:
                    print("Invalid target")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except UnicodeDecodeError:
            print("\nInvalid decode")
            continue