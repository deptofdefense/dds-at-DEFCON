from PyQt5.QtCore import Qt # needed for gui
from PyQt5.QtGui import *  # needed for gui
from PyQt5.QtWidgets import * # needed for gui

import sys # needed for gui

import time # needed for sleep
import threading # needed for threads

class GameDisplay(QMainWindow):
    ''' Custom Class to handle the game overlay window '''

    def __init__(self, sizeX, sizeY):
        super().__init__() 
  
        # set the title 
        self.setWindowTitle("Text Overlay Window") 
  
        # makes the background transparent when xcompmgr is running
        #self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
  
        # setting  the geometry of window 
        self.setGeometry(0, 100, sizeX, sizeY) 

        # Command Label
        self.cmdLabel = QLabel("cmdLabel", self)
        self.cmdLabel.setStyleSheet("color: rgb(0, 255, 255);")
        self.cmdLabel.setText("")  
        self.cmdLabel.setFont(QFont('Helvetica', 20))
        self.cmdLabel.resize(sizeX, sizeY)
        self.cmdLabel.setAlignment(Qt.AlignBottom | Qt.AlignHCenter) 

        # UserList Label
        self.lstLabel = QLabel("lstLabel", self)
        self.lstLabel.setStyleSheet("color: rgb(0, 255, 255);")
        self.lstLabel.setText("Vote Count: ")  
        self.lstLabel.setFont(QFont('Helvetica', 20))
        self.lstLabel.resize(sizeX, sizeY)
        self.lstLabel.setAlignment(Qt.AlignRight)

        # Help Label
        self.helpLabel = QLabel("helpLabel", self)
        self.helpLabel.setStyleSheet("color: rgb(0, 255, 255);")
        self.helpLabel.setText("Chat Commands: \n!help \n!vote \n!send \n!auth \n!cheat \n!theme \n!music")  
        self.helpLabel.setFont(QFont('Helvetica', 20))
        self.helpLabel.resize(sizeX, sizeY)
        self.helpLabel.setAlignment(Qt.AlignLeft)
        
  
        # show all the widgets 
        self.show() 

    def dispCmd(self, cmdMsg):
        ''' Causes a string representing the command message to be displayed on the bottom of the screen '''

        self.cmdLabel.setText(str(cmdMsg))
        #self.show
        time.sleep(2)
        self.cmdLabel.setText("")
        #self.show

    def dispUser(self, userMsg):
        ''' Updates the user list '''

        self.lstLabel.setText("Vote Count: \n" + str(userMsg))

class DisplayManager():
    ''' Custom class for managing the display '''

    def __startDisplayThread(self, sizeX, sizeY):
        ''' private class for starting the display as a separate thread '''

        # print("test")

        # create pyqt5 app 
        App = QApplication(sys.argv) 
  
        # create the instance of our Window 
        self.display = GameDisplay(sizeX, sizeY)
  
        # start the app 
        sys.exit(App.exec()) 

    def startDisplay(self, sizeX, sizeY):
        ''' Starts the game overlay '''
        threading.Thread(target=self.__startDisplayThread, args=(sizeX, sizeY, ), daemon=True).start()
        time.sleep(1)
        
    def updateUserList(self, userMsg):
        ''' public interface for updating the user list '''
        self.display.dispUser(userMsg)

    def updateCmdMsg(self, cmdMsg):
        ''' public interface for updating the command message '''
        threading.Thread(target=self.display.dispCmd, args=(cmdMsg, ), daemon=True).start()