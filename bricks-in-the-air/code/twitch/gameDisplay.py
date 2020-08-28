from PyQt5.QtCore import Qt # needed for gui
from PyQt5.QtGui import *  # needed for gui
from PyQt5.QtWidgets import * # needed for gui

import sys # needed for gui
import os   # to make sure files exist

import time # needed for sleep
import threading # needed for threads
import random


class GameDisplay(QMainWindow):
    ''' Custom Class to handle the game overlay window '''

    def __init__(self, CFG):
        super().__init__()
        self.cfg = CFG
        self.font_size_users = 14
        self.font_size_cmd = 20

        self.time_limit = int(self.cfg["cue"]["time"])

        # set the title
        self.setWindowTitle("Text Overlay Window")

        # makes the background transparent when xcompmgr is running
        self.setAttribute(Qt.WA_TranslucentBackground)

        # setting  the geometry of window
        self.setGeometry(0, 0, self.cfg["display"]["width"], self.cfg["display"]["height"])

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.lay = QVBoxLayout(self.central_widget)

        self.imageLabel = QLabel(self)
        self.pixmap = QPixmap()
        self.imageLabel.setPixmap(self.pixmap)
        self.imageLabel.resize(self.cfg["display"]["width"], self.cfg["display"]["height"])

        self.lay.addWidget(self.imageLabel)
        #self.show()

        # Command Label
        self.cmdLabel = QLabel("cmdLabel", self)
        self.cmdLabel.setStyleSheet("color: rgb(0, 0, 0);")
        self.cmdLabel.setText("")
        self.cmdLabel.setFont(QFont('Arial', self.font_size_cmd))
        self.cmdLabel.resize(self.cfg["display"]["width"], self.cfg["display"]["height"])
        self.cmdLabel.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)

        #self.lay.addWidget(self.cmdLabel)

        # UserList Label
        self.lstLabel = QLabel("lstLabel", self)
        self.lstLabel.setStyleSheet("color: rgb(0, 0, 0);")
        self.lstLabel.setText("")
        self.lstLabel.setFont(QFont('Arial', self.font_size_users))
        self.lstLabel.resize(self.cfg["display"]["width"], self.cfg["display"]["height"])
        self.lstLabel.setAlignment(Qt.AlignRight)

        #self.lay.addWidget(self.lstLabel)

        # show all the widgets
        self.resize(self.cfg["display"]["width"], self.cfg["display"]["height"])
        self.show()


    def dispCmd(self, cmdMsg):
        ''' Causes a string representing the command message to be displayed on the bottom of the screen '''

        try:
            self.cmdLabel.setText(str(cmdMsg))
            self.cmdLabel.update()
            threading.Thread(target=self.clearCmdMsg, daemon=True).start()
        except Exception as err:
            print("Error in gameDisplay.dispCmd()")
            print(repr(err))

    def clearCmdMsg(self):
        time.sleep(5)
        self.cmdLabel.setText("")
        self.cmdLabel.update()


    def dispUser(self, userMsg, time_remaining=60):
        ''' Updates the user list '''

        try:
            if userMsg != None:
                if len(userMsg) > 0:
                    msg = "Active Users (limit {})\n".format(self.cfg["cue"]["limit"])
                    count = 1
                    for brickUser in userMsg:
                        msg += str(count) + " min: " + brickUser.getName() + "\n"
                        count += 1

                    self.lstLabel.setText("{}".format(msg))
                    self.lstLabel.update()
        except Exception as err:
            print("Error in gameDisplay.dispUser()")
            print(repr(err))

        #threading.Thread(target=self.updateTimeRemaining, args=(userMsg, self.time_limit), daemon=True).start()

    def updateTimeRemaining(self, userMsg, time_remaining):
        if time_remaining > 0:
            msg = "Active Users (limit {})\nTime Remaining: {}\n".format(self.cfg["cue"]["limit"], time_remaining)
            count = 1
            if userMsg != None:
                for brickUser in userMsg:
                    msg += str(count) + ": " + brickUser.getName() + "\n"
                    count += 1

            self.lstLabel.setText("{}".format(msg))
            self.lstLabel.update()

            time.sleep(1)
            time_remaining -= 1
            self.updateTimeRemaining(userMsg, time_remaining)


    def dispImage(self, fileStr):
        # Image Overlay
        try:
            if fileStr != None:
                if os.path.isfile(fileStr):
                    #print(fileStr)
                    self.pixmap = QPixmap(fileStr)
                    self.pixmap = self.pixmap.scaledToWidth(self.cfg["display"]["width"])
                    self.pixmap = self.pixmap.scaledToHeight(self.cfg["display"]["height"])
                    self.imageLabel.setPixmap(self.pixmap)
                else:
                    print("gameDisplay.dispImage() file not found")
                    self.imageLabel.clear()
            else:
                print("gameDisplay.dispImage() file not provided")
                self.imageLabel.clear()
            self.resize(self.cfg["display"]["width"], self.cfg["display"]["height"])
            self.imageLabel.update()
        except Exception as err:
            print("Error in gameDisplay.dispImage()")
            print(repr(err))


class DisplayManager():
    ''' Custom class for managing the display '''

    def __init__(self, cfg):
        self.cfg = cfg
        self.display = None

    def __startDisplayThread(self):
        ''' private class for starting the display as a separate thread '''

        # create pyqt5 app
        App = QApplication(sys.argv)

        # create the instance of our Window
        self.display = GameDisplay(self.cfg)

        # start the app
        sys.exit(App.exec())

    def startDisplay(self):
        ''' Starts the game overlay '''
        t = threading.Thread(target=self.__startDisplayThread, daemon=True)
        t.start()
        #time.sleep(1)

    def updateUserList(self, userMsg):
        ''' public interface for updating the user list '''
        if self.display != None:
            self.display.dispUser(userMsg)

    def updateCmdMsg(self, cmdMsg):
        ''' public interface for updating the command message '''
        if self.display != None:
            self.display.dispCmd(cmdMsg)

    def updateImage(self, fileStr):
        if self.display != None:
            self.display.dispImage(fileStr)

def main():

    cfg = {}
    cfg["display"] = {}
    cfg["display"]["width"] = 1080
    cfg["display"]["height"] = 720

    cfg["cue"] = {}
    cfg["cue"]["limit"] = 5

    # create pyqt5 app
    App = QApplication(sys.argv)

    # create the instance of our Window
    display = GameDisplay(cfg)

    # start the app
    sys.exit(App.exec())

if __name__ == "__main__":
    main()
