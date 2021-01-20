# import of libraries
import os
from PySide2 import QtWidgets, QtGui, QtCore



def screenSizer(self, posx, posy, width, height, app):
    """func to get size of screen and scale window accordingly"""
    sizefactor = round(app.primaryScreen().size().height()*0.001)   # factor for scaling window, depending on height
    posx *= sizefactor
    posy *= sizefactor
    width *= sizefactor
    height *= sizefactor
    return posx, posy, width, height, sizefactor



def windowSetup(self, posx, posy, width, height, pypath, title, winFac = 1):
    """func for loading icon, setting size and title"""
    try:                                                            # try to load e3d Icon
        self.setWindowIcon(QtGui.QIcon(os.path.join(pypath, r'pictures\e3dIcon.png')))
    except:
        print('error finding file icon')
    self.setGeometry(posx, posy, width * winFac, height * winFac)   # setting window size
    self.setFixedSize(width * winFac, height * winFac)              # fixing window size
    self.setWindowTitle(title)



def messageBox(self, header, message):
    """pop up message box with header and message"""
    self.message_complete = QtWidgets.QMessageBox.information(self, header, message)



def questionBox(self, header, question):
    """pop up question box with header and question"""
    choice = QtWidgets.QMessageBox.question(self, header, question, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    if choice == QtWidgets.QMessageBox.Yes:
        return True
    else:
        return False


def select_folder(self, textbox, msg):
    """func to select directory"""
    path = QtWidgets.QFileDialog.getExistingDirectory(self, msg)                                      # starts directory selection dialog
    if path:                                                                                            # checks if valid directory has been selected
        textbox.setText(path)                                                                           # displaying path
        return path
    else:
        textbox.setText('')                                                                             # resetting textbox for path
        messageBox(self, 'Important', 'Valid Folder not selected')                                      # message-box informing about unsuccessful selection
    return ''


def next_window(self, window, close=True):
    """calls next window, closes current if True"""
    self.next_window_jump = window
    self.next_window_jump.show()
    if close == True:
        self.hide()



def dimensions(self):
    """gets current dimensions of window"""
    posx = self.geometry().x()
    posy = self.geometry().y()
    return posx, posy



def load_banner(self, path, sizefactor, banner_size=150):
    """loading image from path to self.vbox"""
    try:
        self.banner = QtWidgets.QLabel(self)
        self.banner.setPixmap(QtGui.QPixmap(path))
        self.banner.setScaledContents(True)
        self.banner.setMinimumHeight(banner_size*sizefactor)
        self.banner.setMaximumHeight(banner_size*sizefactor)
        self.vbox.addWidget(self.banner)
    except:
        print('error finding banner picture')



def reset_dicts(values, inters, value_dict, inter_dict):
    """reseting values to None in dict"""
    for value in values:
        value_dict[value] = None
    for inter in inters:
        inter_dict[inter] = True
    return value_dict, inter_dict


def windowTitle(self, title):
    """for setting window title"""
    txt = 'CityBIT - ' + title
    self.setWindowTitle(txt)