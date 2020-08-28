# This Python file uses the following encoding: utf-8
import sys
import os
from os import path
import json
import time

import zmq
from threading import Thread

from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PySide2 import QtCore, QtWidgets
from PySide2.QtGui import QFont


class TwitchGUI(QWidget):
    def __init__(self, address):
        super(TwitchGUI, self).__init__()
        self.load_ui()

        context = zmq.Context()

        self.socket = context.socket(zmq.REP)
        self.socket.bind(address)

        self.t = Thread(target=self.listen)
        self.t.start()

    def listen(self):
        while True:
            try:
                msg = self.socket.recv_json()

                if "cmd" in msg:
                    command = msg["cmd"]
                    self.commandLabel.setText(command)
                    Thread(target=self.clear_cmd_msg, daemon=True).start()

                if "user_list" in msg:
                    self.users.setText(msg["user_list"])

                if "image" in msg:
                    if path.exists(msg["image"]):
                        self.image.setPixmap(msg["image"])


            except Exception as err:
                print("Error updating the GUI")
                print(repr(err))

            self.socket.send_string("thanks")


    def load_ui(self):
        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)

        self.ui = loader.load(ui_file, self)

        self.users = self.ui.user_list
        self.image = self.ui.background_image
        self.commandLabel = self.ui.cmd_label

        self.setWindowTitle("TwitchGUI")
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        ui_file.close()

    def clear_cmd_msg(self):
        #print("clear cmd msg called... waiting")
        time.sleep(5)
        self.commandLabel.setText("")
        self.commandLabel.update()
        #print("clear cmd msg complete")


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication([])
    widget = TwitchGUI("tcp://127.0.0.1:8888")
    widget.show()
    sys.exit(app.exec_())
