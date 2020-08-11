"""
DEFCON 28 Circuit Playground Express - Satellelite

This code is intended to be run on the "Satellite" portion
of the workshop.
"""
import board # needed for everything
import digitalio # needed for serial
import time # needed for sleep
import neopixel # needed for led control
import pulseio # needed for IR communication
import adafruit_irremote # Needed to use the IR library

from adafruit_crickit import crickit # needed to talk to crickit

# For signal control, we'll chat directly with seesaw, use 'ss' to shorted typing!
ss = crickit.seesaw

# set up smoker
smoker = crickit.SIGNAL1    # connect the smoker input to signal I/O #1
ss.pin_mode(smoker, ss.OUTPUT) # make signal pin an output so that we can write to it
ss.digital_write(smoker, False) # when false the smoker is off, when true it is on

# Setup LEDs
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=.2)

# Setup for IR Receivcing
# Create a 'pulseio' input, to listen to infrared signals on the IR receiver
pulsein = pulseio.PulseIn(board.IR_RX, maxlen=120, idle_state=True)
# Create a decoder that will take pulses and turn them into numbers
decoder = adafruit_irremote.GenericDecode()

# Colors used by the LEDs
BLUE = (0, 0, 0x10)
BLACK = (0, 0, 0)
RED = (0x10,0,0)
PURPLE = (0x10, 0x0, 0x10)
WHITE = (0x10,0x10,0x10)
GREEN = (0, 0x10, 0)

def initial_setup():
    global pixels, smoker, ss

    print("initial setup")

    # initialize the servo angles
    crickit.servo_1.angle = 90
    crickit.servo_2.angle = 90
    crickit.servo_3.angle = 90
    crickit.servo_4.angle = 90

    # initialize the LEDs
    pixels.fill(BLUE)
    pixels.show()

    #initialize smoker
    ss.digital_write(smoker, False)
    crickit.dc_motor_1.throttle = 0

def setState(step):

    global smoker, smoker_delay

    if (int(step) == 0):
        # initial state
        initial_setup()
    elif (int(step) == 1):
        # user password state
        initial_setup()
        pixels[0] = PURPLE
        pixels.show()
    elif (int(step) == 2):
        # Master password state
        initial_setup()
        pixels[0] = RED
        pixels.show()
    elif (int(step) == 3):
        # sec ant
        initial_setup()
        pixels[0] = RED
        pixels[1] = RED
        pixels.show()
        crickit.servo_4.angle = 180
    elif (int(step) == 4):
        # pri ant
        initial_setup()
        pixels[0] = RED
        pixels[1] = RED
        pixels[2] = RED
        pixels.show()
        crickit.servo_4.angle = 180
        crickit.servo_3.angle = 0
    elif (int(step) == 5):
        # solar 1
        initial_setup()
        pixels[0] = RED
        pixels[1] = RED
        pixels[2] = RED
        pixels[3] = RED
        pixels.show()
        crickit.servo_4.angle = 180
        crickit.servo_3.angle = 0
        crickit.servo_1.angle = 0
    elif (int(step) == 6):
        # solar 2
        initial_setup()
        pixels[0] = RED
        pixels[1] = RED
        pixels[2] = RED
        pixels[4] = RED
        pixels.show()
        crickit.servo_4.angle = 180
        crickit.servo_3.angle = 0
        crickit.servo_2.angle = 180
    elif (int(step) == 7):
        # solar both
        pixels.fill(BLUE)
        pixels[0] = RED
        pixels[1] = RED
        pixels[2] = RED
        pixels[3] = RED
        pixels[4] = RED
        pixels.show()
        crickit.servo_4.angle = 180
        crickit.servo_3.angle = 0
        crickit.servo_2.angle = 180
        crickit.servo_1.angle = 0
        ss.digital_write(smoker, False)
    elif (int(step) == 8):
        # temp
        pixels.fill(RED)
        pixels[9] = BLUE
        pixels[8] = BLUE
        pixels[7] = BLUE
        pixels[6] = BLUE
        pixels.show()
        crickit.servo_4.angle = 180
        crickit.servo_3.angle = 0
        crickit.servo_2.angle = 180
        crickit.servo_1.angle = 0
        ss.digital_write(smoker, False)
    elif (int(step) == 9):
        # override
        pixels.fill(RED)
        pixels[9] = BLUE
        pixels[8] = BLUE
        pixels[7] = BLUE
        pixels.show()
        crickit.servo_4.angle = 180
        crickit.servo_3.angle = 0
        crickit.servo_2.angle = 180
        crickit.servo_1.angle = 0
        ss.digital_write(smoker, False)
    elif (int(step) == 10):
        # update
        pixels.fill(RED)
        pixels[9] = BLUE
        pixels[8] = BLUE
        pixels.show()
        crickit.servo_4.angle = 180
        crickit.servo_3.angle = 0
        crickit.servo_2.angle = 180
        crickit.servo_1.angle = 0
        ss.digital_write(smoker, False)
    elif (int(step) == 11):
        # launch
        pixels.fill(RED)
        pixels[9] = BLUE
        pixels.show()
        crickit.servo_4.angle = 180
        crickit.servo_3.angle = 0
        crickit.servo_2.angle = 180
        crickit.servo_1.angle = 0

        # Turn ON all the effects
        ss.digital_write(smoker, True)
        crickit.dc_motor_1.throttle = 1
        # Run time of 10 sec to preserve fluid
        time.sleep(10)
        ss.digital_write(smoker, False)
        crickit.dc_motor_1.throttle = 0

    elif (int(step) == 12):
        # smoker off
        pixels.fill(RED)
        pixels[9] = BLUE
        pixels.show()
        crickit.servo_4.angle = 180
        crickit.servo_3.angle = 0
        crickit.servo_2.angle = 180
        crickit.servo_1.angle = 0

        # Turn off all the effects
        ss.digital_write(smoker, False)
        crickit.dc_motor_1.throttle = 0
    elif (int(step) == 13):
        #freeplay discovered
        pixels.fill(RED)
        pixels.show()
        crickit.servo_4.angle = 180
        crickit.servo_3.angle = 0
        crickit.servo_2.angle = 180
        crickit.servo_1.angle = 0

        # Turn off all the effects
        ss.digital_write(smoker, False)
        crickit.dc_motor_1.throttle = 0

    else:
        # Turn off all the effects
        ss.digital_write(smoker, False)
        crickit.dc_motor_1.throttle = 0

        #do nothing else, its free play


# Main loop of the program, decodes the IR messages
def ir_recieve():
    global decoder, pulsein

    #print("attempting ir recieve")

    pulses = decoder.read_pulses(pulsein, blocking=True)
    if pulses is not None:
        try:
            # Attempt to convert received pulses into numbers
            received_code = decoder.decode_bits(pulses)
            print("NEC Infrared code received: ", received_code)

            # ensure the recieved code is proper length
            if len(received_code) is not 4:
                return

            # LED Change command, change by LED position
            if received_code[0] < 10:
                # Need to fix possible index out of range issue
                print(received_code)
                # Interesting error from observation but the IR signal has to
                # diverstiy otherwise it will through an error:
                # Example if code sent was [0,0,0,0]
                # Failed to decode:  ('Pulses do not differ',)
                pixels[received_code[0]] = (received_code[1], received_code[2], received_code[3])

            # Servo angle change
            elif received_code[0] == 10:
                # verify angle is within valid range
                if received_code[2] >=0 and received_code[2] <= 180:
                    if received_code[1] == 1:
                    # Servo_1
                        crickit.servo_1.angle = received_code[2]
                        time.sleep(1)
                    elif received_code[1] == 2:
                        # Servo_2
                        crickit.servo_2.angle = received_code[2]
                        time.sleep(1)
                    elif received_code[1] == 3:
                        # Servo_3
                        crickit.servo_3.angle = received_code[2]
                        time.sleep(1)
                    elif received_code[1] == 4:
                        # Servo_4
                        crickit.servo_4.angle = received_code[2]
                        time.sleep(1)

            # Reset command
            elif received_code[0] == 255:
                setState(received_code[1])

        except adafruit_irremote.IRNECRepeatException:
            # We got an unusual short code, probably a 'repeat' signal
            print("NEC repeat!")

        except adafruit_irremote.IRDecodeException as e:
            # Something got distorted or maybe its not an NEC-type remote?
            print("Failed to decode: ", e.args)
        except MemoryError as e:
            print("Memory allocation error")

# Main method that launches everthing
def main():
    initial_setup()

    while True:
        ir_recieve()
        time.sleep(.1)

if __name__ == '__main__':
    main()