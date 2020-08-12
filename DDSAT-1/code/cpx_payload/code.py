import time # needed for sleep
import board # needed for everything
import struct # needed for serial
import random # needed for random
import neopixel # needed for LEDs
import busio # needed for serial
import analogio # needed for light sensor
import adafruit_thermistor # needed for temp sensor

# set up serial
uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=.1)

#set up leds
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=.2)

#set up light sensor
light = analogio.AnalogIn(board.LIGHT)

#set up temp sensor
thermistor = adafruit_thermistor.Thermistor(board.TEMPERATURE, 10000, 10000, 25, 3950)

# basic setup
def initial_setup():
    pixels.brightness = .1
    pixels.fill([255,255,255])
    pixels.show()

# process serial comms
def process_serial_input():
    """ Generic serial processing """

    if uart.in_waiting >= 6:
        try:
            data = uart.read()  # read up to 32 bytes

            #uart.write(data) # for debugging

            cmd_msg = (struct.unpack('3s', data[:3])[0])
            cmd = ''.join([chr(b) for b in cmd_msg])

            #print(len(data))
            #print(cmd)

            if len(data) == 3:
                # return a payload of None
                return (cmd, None)
            else:
                return (cmd, data[3:])
        except Exception as err:
            print("serial procesing error")
            return None
    else:

        # data = uart.read(1)  # read up to 32 bytes

        # uart.write(data) # for debugging

        return None

def serial_loop():

    # Check the input buffer prior to any action
    data = process_serial_input()

    if data is not None:

        cmd = data[0]
        payload = data[1]

        if cmd == "led":
            #print("process led cmd")
            pixels[payload[0]] = (payload[1], payload[2], payload[3])
            uart.write("LED \n".encode())
        elif cmd == "top":
            pixels[0] = (payload[0], payload[1], payload[2])
            pixels[1] = (payload[0], payload[1], payload[2])
            pixels[2] = (payload[0], payload[1], payload[2])
            pixels[3] = (payload[0], payload[1], payload[2])
            pixels[4] = (payload[0], payload[1], payload[2])
            uart.write("TOP \n".encode())
        elif cmd == "btm":
            pixels[5] = (payload[0], payload[1], payload[2])
            pixels[6] = (payload[0], payload[1], payload[2])
            pixels[7] = (payload[0], payload[1], payload[2])
            pixels[8] = (payload[0], payload[1], payload[2])
            pixels[9] = (payload[0], payload[1], payload[2])
            uart.write("BTM \n".encode())
        elif cmd == "top":
            pixels[0] = (payload[0], payload[1], payload[2])
            pixels[1] = (payload[0], payload[1], payload[2])
            pixels[2] = (payload[0], payload[1], payload[2])
            pixels[3] = (payload[0], payload[1], payload[2])
            pixels[4] = (payload[0], payload[1], payload[2])
            uart.write("TOP \n".encode())
        elif cmd == "all":
            pixels.fill([payload[0], payload[1], payload[2]])
            uart.write("ALL \n".encode())
        elif cmd == "lit":
            uart.write(f"LIT {str(light.value)} \n".encode())
        elif cmd == "tmp":
            uart.write(f"TMP {str(thermistor.temperature)}\n".encode())
        elif cmd == "rst":
            initial_setup()
            uart.write("RST \n".encode())
        else:
            uart.write("ERROR, UNKNOWN COMMAND\n".encode())



if __name__ == "__main__":
    initial_setup()

    while True:
        serial_loop()