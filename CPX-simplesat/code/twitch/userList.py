# Code for managing twitch user list
# Created for defcon28 Aerospace Village

import time # needed for sleep
import threading # needed for userThread
import random # needed for zone generation
import json
import os
from os import path

class SatUser:
    """ Base class for keeping track of a unique user of a Satellite System """



    # Initialization method
    def __init__(self, name):
        """ Initialization method: note name needs to be unique """

        self.log_folder = "/user_logs/"

        if not os.path.exists(os.getcwd() + self.log_folder):
            os.makedirs(os.getcwd() + self.log_folder)

        fileStr = os.getcwd() + self.log_folder + name + ".log"
        if(path.isfile(fileStr)):
            print("user previously played... initialze their previous state.")
            try:
                with open(fileStr, 'r') as fh:
                    data = json.load(fh)
                    self.name = data["name"]
                    self.currentStep = int(data["currentStep"])
                    self.maxStep = int(data["maxStep"])
                    self.timeOut = int(data["timeOut"])
                    self.zone = int(data["zone"])

                    # new logging changes
                    self.log_name = data["log_name"]
                    self.join_time = data["join_time"]
                    self.complete_steps = data["complete_steps"]

            except Exception as err:
                print("Error loading preivously saved user information.")
                print(repr(err))
        else:
            print("brand new user, make from scratch.")

            self.name = str(name)
            self.currentStep = 0
            self.maxStep = 0
            self.timeOut = 3
            self.zone = random.randint(100, 255)

            # new logging changes
            self.log_name = os.getcwd() + self.log_folder + self.name + ".log"
            self.join_time = time.time()
            self.complete_steps = {}
            self.log_event()

    def getZone(self):
        ''' Returns the users zone, which was randomly generated at initialization '''
        return self.zone

    def __eq__(self, other):
        """ Overwrites equal method to check names """
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

        return self.currentStep

    def getMaxStep(self):
        """ Returns the max step the user has completed """

        return self.maxStep

    def setCurrentStep(self, currentStep):
        """ Sets the current step """

        self.currentStep = int(currentStep)

        if self.currentStep > self.maxStep:
            self.maxStep = self.currentStep

        #log the completed step and time
        if str(self.currentStep) in self.complete_steps:
            self.complete_steps[str(self.currentStep)].append(time.time())
        else:
            self.complete_steps[str(self.currentStep)] = [time.time()]

        self.log_event()

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


    def log_event(self):
        with open(self.log_name,"w") as f:
            f.write(json.dumps(self.__dict__))

class UserList:
    """ List of active users """

    def __init__(self):
        """ init method """

        self.userList = []
        self.currentUser = SatUser("temp")

    def addUser(self, name):
        """ Checks if user already exists, and if not adds them to the list.  \nReturns True if name is added, False otherwise """

        for user in self.userList:
            if (user.matchName(name)):
                return False

        #if user list is empty
        if not self.userList:
            self.setCurrentUser(SatUser(name))

        self.userList.append(SatUser(name))
        return True

    def removeUser(self, name):
        ''' Checks if user already exists and removes them from the list.  \nReturns true if removed, false otherwise '''

        for user in self.userList:
            if (user.matchName(name)):
                self.userList.remove(user)
                return True

        return False

    def startUserThread(self):
        """ Starts the user thread """

        t = threading.Thread(target=self.userThread, daemon=True)
        t.start()

    def userThread(self):
        """ Runs through list and updates the current user every 60 seconds """

        tempUser = SatUser("temp")

        while True:
            for user in self.userList:
                if (user.updateTimeout() >= 0):
                    self.currentUser = user
                    time.sleep(60)
                else:
                    self.userList.remove(user)

            # done to make sure current user is never null
            self.currentUser = tempUser

    def getCurrentUser(self):
        """ Grabs the current user as dictated by userThread """

        return self.currentUser

    def setCurrentUser(self, user):
        """ Grabs the current user as dictated by userThread """

        self.currentUser = user

    def getUserList(self):
        """ Returns the list of current Users """

        return self.userList

    def getNextUserList(self, nextCount):
        ''' Returns the next X users in the list formated by Name : time \nnextCount : how long the next user list should be '''

        startPoint = 0

        if nextCount > len(self.userList):
            nextCount = len(self.userList)

        for user in self.userList:
            if user.matchName(self.currentUser.name):
                break
            else:
                startPoint = startPoint + 1

        if (startPoint >= len(self.userList)) or (len(self.userList) == 0):
            return "N/A"

        msg = ""
        for i in range(nextCount):
            msg = msg + f"\n{self.userList[startPoint].getName()} : {i} min "
            startPoint = startPoint + 1

            if startPoint >= len(self.userList):
                startPoint = 0

        return msg


if __name__ == "__main__":
    # test method isolate/check/test SatUser state saving/changing
    dan = SatUser("dan")
    for i in range(15):
        dan.setCurrentStep(i)

    dan = SatUser("dan")
    for i in range(0, 15, 2):
        dan.setCurrentStep(i)
    print(dan.getMaxStep())
