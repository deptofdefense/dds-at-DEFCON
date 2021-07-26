
from collections import OrderedDict
import time
import os
from os import path
import json

class BrickUser:
    """ Base class for keeping track of a unique Bricks in the Air user."""

    # Initialization method
    def __init__(self, name, cfg):
        """ Initialization method: note name needs to be unique """

        fileStr = os. getcwd() + cfg["logging"]["path"] + name + ".log"
        if(path.isfile(fileStr)):
            # Users has been here previously, reload their state.
            print("user previously played... initialze their previous state.")
            try:
                with open(fileStr, 'r') as fh:
                    data = json.load(fh)
                    self.name = data["name"]
                    self.steps = data["steps"]
                    self.scene_mapping = data["scene_mapping"]
                    self.log_name = os.getcwd() +  cfg["logging"]["path"] + name +".log"
                    self.currentStepIndex = str(data["currentStepIndex"])   # dict key, keep as a string. convert to int for math but store as string
                    self.maxStep = int(data["maxStep"])
                    self.timeOut = int(data["timeOut"])
                    self.join_timestamp = data["join_timestamp"]
                    self.engine_speed = data["engine_speed"]

            except Exception as err:
                print("Error loading preivously saved user information.")
                print(repr(err))

        else:
            print("brand new user, make from scratch.")
            self.name = str(name)
            self.steps = cfg["steps"]
            self.scene_mapping = cfg["scene_mapping"]
            self.log_name = os.getcwd() +  cfg["logging"]["path"] + name +".log"
            for x in self.steps:
                self.steps[x]["completed"] = [] # an empty list to keep track of how many times they complete it.
            self.currentStepIndex = "1"
            self.maxStep = 0
            self.timeOut = 3
            self.join_timestamp = time.time()
            self.engine_speed = 0
            self.log_event()


    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        """ Overwrites equal method to check names """
        if other != None:
            if (self.name == other.name):
                return True
        else:
            return False

    def matchName(self, name):
        """ Checks to see if the names are identical.  \nReturns True if they match, False otherwise """

        if (self.name == str(name)):
            return True
        else:
            return False

    def getCurrentStep(self):
        """ Returns the current step """
        return str(self.currentStepIndex)

    def setCurrentStep(self, desired_step):
        desired_step = str(desired_step)

        for item in self.scene_mapping:
            step = item[0]  # each step/scene pairing comes in as a list.
            scene = item[1]

            if desired_step == scene:
            # it's a valid step, but can/should the user be allowed to go there?

                # they've been there before... sure they can go back
                if len(self.steps[str(step)]["completed"]) > 0:
                    self.currentStepIndex = str(step)
                    self.log_event()
                    return "Step: {} set.".format(scene)
                # they are asking to goto the first non completed step.
                elif len(self.steps[str(int(step)-1)]["completed"]) > 0 and len(self.steps[str(step)]["completed"]) == 0:
                    self.currentStepIndex = str(step)
                    self.log_event()
                    return "Step: {} set.".format(scene)

        else:
            return "Invalid step requested."


    def getMaxStep(self):
        """ Returns the max step the user has completed """
        return self.maxStep

    def checkAnswer(self, provided_answer):
        """
        Check for a valid answer, if found return true and advance step
        """
        self.resetTimeout()

        provided_answer = self.parseStrHex(provided_answer)

        if provided_answer == None:
            # malformed string hex provided.. simply stop here.
            return False

        # Passed conversion to int... start looking for possible answers.
        for possible_answer in self.steps[self.currentStepIndex]["answer"]:
            print(possible_answer)
            possible_answer = self.parseStrHex(possible_answer)

            # some challenges are straight forward unique comparison
            if provided_answer == possible_answer:

                if provided_answer[0] == 0x55 and provided_answer[1] == 0x11:
                    # recieved a set engine speed command
                    engine_speed = provided_answer[2]
                    self.engine_speed = engine_speed

                self.update_game_progress()
                return True

            # possible that the answer is outside the valid range
            if "answer_lower" in self.steps[self.currentStepIndex] and "answer_upper" in self.steps[self.currentStepIndex]:
                if len(provided_answer) != len(possible_answer) + 1:
                    # recieved too many values... stop here
                    print("too many values:")
                    print(provided_answer)
                    print(possible_answer)
                    return False

                if provided_answer[0] == possible_answer[0] and provided_answer[1] == possible_answer[1]:
                    print("first to values checkout out")
                    upper = int(self.steps[self.currentStepIndex]["answer_upper"],16)
                    lower = int(self.steps[self.currentStepIndex]["answer_lower"],16)

                    if provided_answer[2] > upper or provided_answer[2] < lower:
                        print("provided answer outside valid range")
                        self.update_game_progress()
                        return True


        # nothing matched an acceptable answer
        return False

    def parseStrHex(self, provided_answer):
        """ helper method to convert string hex to comparable ints """
        partsStr = provided_answer.split()
        parts = []
        for x in partsStr:
            try:
                parts.append(int(x,16))
            except ValueError as err:
                print("incorrect parsing of hex str to int")
                return None
        return parts


    def getFakeI2CResponse(self):
        if "fake_i2c_response" in self.steps[self.currentStepIndex]:
            return self.steps[self.currentStepIndex]["fake_i2c_response"]
        else:
            return None

    def incrementCurrentStepIndex(self):
        index = int(self.currentStepIndex) + 1
        self.currentStepIndex = str(index)
        if int(self.maxStep) < int(self.currentStepIndex):
            self.maxStep = int(self.currentStepIndex)

        self.log_event()


    def getQuestion(self):
        self.resetTimeout()
        return self.steps[str(self.currentStepIndex)]["question"]

    def getHint(self):
        self.resetTimeout()
        return self.steps[self.currentStepIndex]["hint"]

    def getAudio(self):
        print("User getAudio")
        if "audio" in self.steps[self.currentStepIndex]:
            print(self.steps[self.currentStepIndex]["audio"])
            return self.steps[self.currentStepIndex]["audio"]
        else:
            print("no audio")
            return None

    def getI2CEffect(self):
        if "i2c_effect" in self.steps[self.currentStepIndex]:
            return self.steps[self.currentStepIndex]["i2c_effect"]
        else:
            return None

    def getImage(self):
        if "image" in self.steps[self.currentStepIndex]:
            return self.steps[self.currentStepIndex]["image"]
        else:
            return None

    def getName(self):
        """ Returns the name """
        return self.name

    def setName(self, name):
        """ Sets the name """
        self.currentStep = str(name)

    def updateTimeout(self):
        """ Subtracts one from the timeout and returns the value """
        self.timeOut = self.timeOut - 1
        return self.timeOut

    def resetTimeout(self):
        """ Resets the timeout to the default value (3) """
        self.timeOut = 3

    def getEngineSpeed(self):
        """ Get the user's set engine speed for audio sound file purposes. """
        return self.engine_speed

    def setEngineSpeed(self, speed):
        """ Get the user's set engine speed for audio sound file purposes. """
        self.engine_speed = speed


    def update_game_progress(self):
        self.steps[self.currentStepIndex]["completed"].append(time.time())
        self.log_event()

    def log_event(self):
        with open(self.log_name,"w") as f:
            f.write(json.dumps(self.__dict__))

    def get_prologue(self):
        try:
            if "prologue" in self.steps[self.currentStepIndex]:

                for item in self.steps[self.currentStepIndex]["prologue"]:
                    if "0x55 0x11" in item:
                        # engine speed in proluge, update user engine speed:
                        try:
                            speed = int(item.split(" ")[-1],16)
                            self.engine_speed = speed
                        except Exception as err:
                            print("BrickUser.get_prologue() parsing error")
                            print(repr(err))
                    elif item == "0x55 0x15 0x01":
                        # this is a prologue setting of engine OFF
                        self.engine_speed = 0

                return self.steps[self.currentStepIndex]["prologue"]
            else:
                return None
        except Exception as err:
            print(repr(err))

    def get_scene_hotkey(self):
        try:
            if "scene_hotkey" in self.steps[self.currentStepIndex]:
                return self.steps[self.currentStepIndex]["scene_hotkey"]
            else:
                return None
        except Exception as err:
            print("BrickUser.get_scene_hotkey() error")
            print(repr(err))
