"""
DEFCON 30 Hack The Microgrid Solar Array
​
This code is intended to be run on the Solar Array portion of the workshop
"""

import board  # needed for everything
import neopixel  # needed for led control
import struct  # needed for serial
import busio  # needed for serial
import random  # needed for random

from adafruit_crickit import crickit  # needed to talk to crickit

# For signal control, we'll chat directly with seesaw, use 'ss' to shorted typing!
ss = crickit.seesaw

# Setup LEDs
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=1)
houses = neopixel.NeoPixel(board.A1, 6, brightness=1)  # have six houses

# set up serial
uart = busio.UART(board.TX, board.RX, baudrate=115200, timeout=0.1)


def initial_setup():
    global pixels, ss, houses

    print("initial setup")

    # initialize the servo angles
    crickit.servo_1.angle = 90
    crickit.servo_2.angle = 90
    crickit.servo_3.angle = 90
    crickit.servo_4.angle = 90

    # initialize the LEDs
    pixels.fill((0x0, 0x0, 0x10))
    houses.fill((0x0, 0x0, 0x10))
    pixels.show()
    houses.show()


def process_serial_input():

    if uart.in_waiting >= 6:
        try:
            data = uart.read()

            cmd_msg = struct.unpack("3s", data[:3])[0]
            cmd = "".join([chr(b) for b in cmd_msg])

            # print(len(data))
            # print(cmd)

            if len(data) == 3:
                # return a payload of None
                return (cmd, None)
            else:
                return (cmd, data[3:])

        except:
            print("Serial processing error")
            return None
    else:
        return None


def serial_loop():

    #  Check the input buffer prior to any action
    data = process_serial_input()

    if data is not None:

        cmd = data[0]
        payload = data[1]

        if cmd == "led":
            # print("process led cmd")
            pixels[payload[0]] = (payload[1], payload[2], payload[3])
            uart.write("LED \n".encode())
        elif cmd == "top":
            for i in range(0, 5):
                pixels[i] = (payload[0], payload[1], payload[2])
            uart.write("TOP \n".encode())
        elif cmd == "btm":
            for i in range(5, 10):
                pixels[i] = (payload[0], payload[1], payload[2])
            uart.write("BTM \n".encode())
        elif cmd == "cir":
            pixels.fill([payload[0], payload[1], payload[2]])
            uart.write("CIR \n".encode())
        elif cmd == "all":
            pixels.fill([payload[0], payload[1], payload[2]])
            houses.fill([payload[1], payload[0], payload[2]])
            uart.write("ALL \n".encode())
        elif cmd == "hse":
            houses[payload[0]] = (payload[2], payload[1], payload[3])
            uart.write("HSE \n".encode())
        elif cmd == "wnd":
            houses[0] = (payload[1], payload[0], payload[2])
            houses[1] = (payload[1], payload[0], payload[2])
            houses[2] = (payload[1], payload[0], payload[2])
            uart.write("WND \n".encode())
        elif cmd == "sol":
            houses[3] = (payload[1], payload[0], payload[2])
            houses[4] = (payload[1], payload[0], payload[2])
            houses[5] = (payload[1], payload[0], payload[2])
            uart.write("SOL \n".encode())
        elif cmd == "srv":
            crickit.servo_1.angle = payload[0]
            crickit.servo_2.angle = payload[1]
            crickit.servo_3.angle = payload[2]
            crickit.servo_4.angle = payload[3]
            uart.write("SRV \n".encode())
        elif cmd == "rst":
            initial_setup()
            uart.write("RST \n".encode())
        elif cmd == "who":
            uart.write("SOL \n".encode())
        elif cmd == "egg":
            for i in range(0,10):
                pixels[i] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                
            for i in range(0,6):
                houses[i] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            uart.write("EGG \n".encode())
            
        else:
            uart.reset_input_buffer()
            print(f"Unknown command: {cmd}")
            uart.write("ERROR, UNKNOWN COMMAND\n".encode())


# Main method that launches everything
def main():
    initial_setup()
    while True:
        serial_loop()


if __name__ == "__main__":
    main()
