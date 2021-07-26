# Code for managing the game part of cpx simpleSat
# Created for defcon28 aerospace village

import threading    # needed for threading
import time         # needed for sleep
import struct       # needed for serial
import random       # used for selection of sound effects

import serial   # needed for serial
import pygame   # used for playing audio sound effects
import os
import math     # used for math.inf for non hex provided numbers
import binascii


class BricksInTheAir:
    ''' Used to manage progressing through the Bricks in the Air game '''

    def __init__(self, CFG):

        self.cfg = CFG

        i2c_device = self.cfg["hardware"]["i2c"]
        i2c_value = self.cfg["hardware"]["value"]
        i2c_frequency = self.cfg["hardware"]["frequency"]

        # board modue needs this variable set
        os.environ[i2c_device] = str(i2c_value)

        # with ^^ the os env set we can now import busio
        import board
        import busio

        self.fcc_address = self.cfg["hardware"]["fcc_address"]
        self.engine_address = self.cfg["hardware"]["engine_address"]
        self.gear_address = self.cfg["hardware"]["gear_address"]

        self.i2c = busio.I2C(board.SCL, board.SDA, frequency=i2c_frequency)

        # Verify that everything is communicating as expected
        avail = self.i2c.scan()
        print("fcc_address present: {}".format("True" if self.fcc_address in avail else "False"))
        print("engine_address present: {}".format("True" if self.engine_address in avail else "False"))
        print("gear_address present: {}".format("True" if self.gear_address in avail else "False"))

        # configure the audio sound effect outputs
        pygame.mixer.init(channels=4)
        pygame.init()
        self.background_channel = pygame.mixer.Channel(0)
        self.engine_sound_channel = pygame.mixer.Channel(1)
        self.sound_effect_channel = pygame.mixer.Channel(2)

        try:
            bg_audio_loop = pygame.mixer.Sound(self.cfg["audio"]["background"])
            self.background_channel.play(bg_audio_loop, loops=-1)
        except FileNotFoundError as err:
            print("pygame background audio: file not found: " + self.cfg["audio"]["background"])

        """
        try:
            effect = pygame.mixer.Sound(self.cfg["audio"]["engine_speed_2"])
            self.engine_sound_channel.play(effect, loops=-1)
        except FileNotFoundError as err:
            print("pygame effect audio: file not found: " + self.cfg["audio"]["engine_speed_2"])
        """

    def checkCmd(self, user, cmd):
        """
        Checks the user command and passes to the appropriate function
        """

        passed_step = user.checkAnswer(cmd)
        if passed_step == True:
            # limitations to VR and time to build, some answers just need to be faked
            # allow the config file to guide the gameplay.
            response = ""
            if user.getFakeI2CResponse() != None:
                 response = user.getFakeI2CResponse()
            else:
                # do the stuff to indicate complete
                response = "0x" + self.process_cmd(user, cmd)[2:-1]

            if "0x55 0x11" in cmd:
                # this is a set engine speed command... update the sound effect.
                value = int(cmd.split()[-1],16) #take the last value and convert to int
                #self.set_engine_sound(value)
                user.setEngineSpeed(value)

            user.incrementCurrentStepIndex()

            return "\n\nI2C Response: " + response + "\n\nCongratulations, you've completed this step.\n"

        else:
            # nothing to do here?
            # response = self.process_cmd(user, cmd)
            return "Incorrect cmd sent to answer the current question."


    def process_cmd(self, user, cmd):
        # Need to send i2c, change scene, provide sound effect
        x = cmd.split()
        addr = str_to_hex(x[0])
        payload = []
        for i in range(1, len(x)):
            payload.append(str_to_hex(x[i]))

        response = None
        response = self.write_read_i2c(addr, payload, 1)

        # handle the possible i2c effect
        i2c_effect = user.getI2CEffect()
        if(i2c_effect):
            for i2c_command in i2c_effect:
                tmp_command = i2c_command.split()
                tmp = []
                for x in tmp_command:
                    tmp.append(str_to_hex(x))
                self.write_read_i2c(tmp[0], tmp[1:])

                if len(tmp_command) == 3:
                    if tmp[0] == self.engine_address and tmp[1] == 0x11:     # set speed change
                        user.setEngineSpeed(int(tmp[2]))

        # handle the possible sound effect
        sound_effect_str = user.getAudio()
        if(sound_effect_str):
            print(sound_effect_str)
            try:
                effect = pygame.mixer.Sound(sound_effect_str)
                self.background_channel.set_volume(.4)
                self.engine_sound_channel.set_volume(.4)
                # restore the background audio AFTER the effect has completed
                threading.Thread(target=self.restore_normal_volume, args=(effect.get_length(),), daemon=True).start()

                self.sound_effect_channel.play(effect)
            except FileNotFoundError as err:
                print("sound effect: file not found")

        # handle the possible scene change
        return str(binascii.hexlify(response))

    def restore_normal_volume(self, delay):
        # Simple function to restore the background volume AFTER a delay
        time.sleep(delay)
        self.background_channel.set_volume(1)
        self.engine_sound_channel.set_volume(1)


    def write_read_i2c(self, address, command, buf_size=1):

        try:
            self.i2c.writeto(address, command)
            buf = None
            #print("wrote to address: 0x{:x}, value: {}".format(address, command))
            if buf_size > 0:
                buf = bytearray(buf_size)
                self.i2c.readfrom_into(address, buf)

            return buf
        except Exception as err:
            print("BricksInTheAir.write_read_i2c error: address: " + str(address) + " command: " + str(command))
            print(repr(err) )

    def reset_board(self):
        self.write_read_i2c(self.fcc_address, [0xFE])
        self.write_read_i2c(self.engine_address, [0xFE])
        self.write_read_i2c(self.gear_address, [0xFE])


    def run_prolouge(self, user):
        if user != None:
            prologue = user.get_prologue()
            #print(prologue)
            if prologue != None:
                for i2c_command in prologue:
                    tmp_command = i2c_command.split()
                    tmp = []
                    for x in tmp_command:
                        tmp.append(str_to_hex(x))
                    self.write_read_i2c(tmp[0], tmp[1:])

                    # adjusting users engine speed
                    if "0x55 0x11" in i2c_command:
                        tmp = i2c_command.split()
                        if len(tmp) >= 3:
                            user.setEngineSpeed(int(tmp[2], 16))



    def set_engine_speed(self, speed, sound=False):
        #print("bia.set_engine_speed: " + str(speed))
        if speed == 0:  # perform the manual STOP_ENGINE
            x = self.write_read_i2c(self.engine_address, [0x15, 0x01])
            #print(x)
        else:
            x = self.write_read_i2c(self.engine_address, [0x11, speed])
            #print(x)

        if sound:
            self.set_engine_sound(speed)

    def set_engine_sound(self, value):
        if value >= 1 and value <= 7:
            try:
                effect = pygame.mixer.Sound(self.cfg["audio"]["engine_speed_"+str(value)])
                self.engine_sound_channel.stop()
                self.engine_sound_channel.play(effect, loops=-1)
            except FileNotFoundError as err:
                print("pygame effect audio: file not found")
        else:
            self.engine_sound_channel.stop()


def str_to_hex(hex_str):
    try:
        return int(hex_str, 16)
    except ValueError:
        return math.inf
