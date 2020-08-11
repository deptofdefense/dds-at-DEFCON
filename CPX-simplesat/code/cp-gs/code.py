"""
DDS DEFCON 28 Ground Station code
"""

import pulseio
import board
import struct
import busio

import time # needed for sleep

import adafruit_irremote # Needed to use the IR library
import neopixel # Needed for LEDs

import random # needed for debugging
from adafruit_circuitplayground import cp # for debugging

# Setup for IR Transmitting
# Create a 'pulseio' output, to send infrared signals on the IR transmitter @ 38KHz
pwm = pulseio.PWMOut(board.IR_TX, frequency=38000, duty_cycle=2 ** 15)
pulseout = pulseio.PulseOut(pwm)
# Create an encoder that will take numbers and turn them into NEC IR pulses
encoder = adafruit_irremote.GenericTransmit(header=[9500, 4500], one=[550, 550], zero=[550, 1700], trail=0)

# Colors used by the LEDs
BLUE = (0, 0, 0x10)
BLACK = (0, 0, 0)
RED = (0x10,0,0)
PURPLE = (0x10, 0x0, 0x10)
WHITE = (0x10,0x10,0x10)

# Setup for Neopixel LEDs
# pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=.2)
cp.pixels.fill(BLACK)
cp.pixels.show()

uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=.1)

# Event Variables
cmdNum = 0
angle_1 = 90
angle_2 = 90
angle_3 = 90
angle_4 = 90

def initial_setup():
    # global pixels

    cp.pixels.brightness = 0.6
    cp.pixels.fill(WHITE)
    cp.pixels.show()

def process_serial_input():
    """ Generic serial processing """
    global uart

    if uart.in_waiting >= 6:
        try:
            data = uart.read()  # read up to 32 bytes

            #uart.write(data) # for debugging

            cmd_num = struct.unpack('I', data[:4])[0]
            cmd_msg = (struct.unpack('3s', data[4:7])[0])
            cmd = ''.join([chr(b) for b in cmd_msg])

            print(len(data))
            print(cmd)

            if len(data) == 7:
                # return a payload of None
                return (cmd_num, cmd, None)
            else:
                return (cmd_num, cmd, data[7:])
        except Exception as err:
            print("serial procesing error")
            return None
    else:

        # data = uart.read(1)  # read up to 32 bytes

        # uart.write(data) # for debugging

        return None


def serial_loop():
    global uart, encoder

    # Check the input buffer prior to any action
    data = process_serial_input()

    if data is not None:

        cmd = data[1]
        payload = data[2]

        if cmd == "led":
            print("process led cmd")
            encoder.transmit(pulseout, [ payload[0], payload[1], payload[2], payload[3] ])
            #time.sleep(.1)

        elif cmd == "rst":
            print("process rst cmd")
            encoder.transmit(pulseout, [ 255, payload[0], 0, 0 ])

        elif cmd == "arm":
            print("process arm cmd")
            # encoder requires to send 4 bytes... zero fill at the end
            encoder.transmit(pulseout, [10, payload[0], payload[1], 0])
            #time.sleep(.1)
    #time.sleep(1)


def button_debug():

    while True:

        # test arm
        if cp.button_a:
            encoder.transmit(pulseout, [10 , random.randint(1, 4), random.randint(0, 180), 0])

        if cp.button_b:
            encoder.transmit(pulseout, [ random.randint(0, 9), random.randint(0, 255), random.randint(0, 255), random.randint(0, 255) ])


def main():
    initial_setup()
    while True:
        serial_loop()
        #button_debug()


if __name__ == "__main__":
    main()