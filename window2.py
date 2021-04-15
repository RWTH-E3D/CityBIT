# import of libraries
from PySide2 import QtWidgets
import pyproj
import csv



# import of functions
import gui_functions as gf







def point_to_table(self, point):
    """function to add points (point = [X, Y]) to table of groundsurface"""
    rowPosition = self.tbl_groundSurface.rowCount()
    self.tbl_groundSurface.insertRow(rowPosition)
    for i in range(len(point)):
        newItem = QtWidgets.QTableWidgetItem(str(point[i]))
        self.tbl_groundSurface.setItem(rowPosition, i, newItem)
    self.tbl_groundSurface.horizontalHeader().show()





def x_y_check_w2(self, x_in, y_in):
    """to check if x and y can be transformed to floats and if they are within the bounds of the crs"""
    X = None
    Y = None

    # checking if entered x can be converted to float
    if x_in != '':
        try:
            X = float(x_in)
        except:
            msg = 'Could not convert ' + x_in + ' to float'
            gf.messageBox(self, 'Warning!', msg)
            return False
    else:
        msg = 'X coordinate is an empty string'
        gf.messageBox(self, 'Warning!', msg)
        return False

    # checking if entered y can be converted to float
    if y_in != '':
        try:
            Y = float(y_in)
        except:
            msg = 'Could not convert ' + y_in + ' to float'
            gf.messageBox(self, 'Warning!', msg)
            return False
    else:
        msg = 'Y coordinate is an empty string'
        gf.messageBox(self, 'Warning!', msg)
        return False


    if X != None and Y != None:
        # checking if coordinates need to be transformed
        if self.txtB_iCRS.text() != '' and self.txtB_iCRS.text() != self.txtB_oCRS.text():
            x, y =  pyproj.transform(self.txtB_iCRS.text(), self.txtB_oCRS.text(), X, Y, always_xy=True)
        else:
            # coordinates don't need to be transformed
            x = X
            y = Y
        # checking if x coordinate is within bounds of the output CRS
        if self.x_min > x:
            msg = str(x) + ' is too small. Please choose a value equal or greater than ' + str(self.x_min)
            gf.messageBox(self, 'Warning!', msg)
            return False
        elif self.x_max < x:
            msg = str(x) + ' is too large. Please choose a value equal or smaller than ' + str(self.x_max)
            gf.messageBox(self, 'Warning!', msg)
            return False
        else:
            pass
        
        # checking if y coordinate is within bounds of the output CRS
        if self.y_min > y:
            msg = str(y) + ' is too small. Please choose a value equal or greater than ' + str(self.y_min)
            gf.messageBox(self, 'Warning!', msg)
            return False
        elif self.y_max < y:
            msg = str(y) + ' is too large. Please choose a value equal or smaller than ' + str(self.y_max)
            gf.messageBox(self, 'Warning!', msg)
            return False
        else:
            pass
        
    # adding points to table
    if [x, y] not in self.border_list:
        self.border_list.append([x, y])
        point_to_table(self, [x, y])
        self.txtB_iCRS.setReadOnly(True)
        self.txtB_oCRS.setReadOnly(True)
    else:
        # not adding duplicates
        print('point', [x, y], 'already in border_list')


    return True





def load_CSV_w2(self):
    """to load coordinates of groundSurface from .csv file for second window"""
    # file selection dialog for loading file
    tup = QtWidgets.QFileDialog.getOpenFileName(self, 'Select file', self.tr("*.csv"))
    csvpath = tup[0]

    # trying to read from file
    try:
        with open(csvpath, newline='') as f:    # opening file
            reader = csv.reader(f)              # reading file
            i = 0
            for x, y in reader:
                i -=- 1
                if x_y_check_w2(self, x, y):
                    pass
                else:
                    print('error occured in line', i)
            f.close()
    except:
        print('error loading coordinates from csv')



def add_point_w2(self):
    """to add points to area of groundSurface"""
    if(x_y_check_w2(self, self.txtB_xCoor.text(), self.txtB_yCoor.text())):
        self.txtB_xCoor.setText('')
        self.txtB_yCoor.setText('')
    else:
        pass


def del_point(self):
    """to remove last point from groundSurface"""
    # getting rowCount
    rowCount = self.tbl_groundSurface.rowCount()
    
    # if there is something in the table
    if rowCount > 0:
        # checking if there are the same number of points in both the table and the list
        if rowCount == len(self.border_list):
            # deleting row/entry of last point
            self.tbl_groundSurface.removeRow(rowCount-1)
            self.border_list = self.border_list[:-1]
        else:
            # unequal number of points in table and list
            print('Error! table has a has', rowCount, 'rows, but groundSurface_list has', len(self.groundSurface_list), 'entries')
        
        # case that the last element has just been deleted
        if rowCount == 1:
            self.tbl_groundSurface.horizontalHeader().hide()




def gatherInfo2(self, value_dict):
    """gathering variable info from window 2"""
    if self.txtB_u_GML_ID.text() != '':
        value_dict["u_GML_ID"] = self.txtB_u_GML_ID.text()
    else:
        value_dict["u_GML_ID"] = None
    if self.txtB_dataFolder.text() != '':
        value_dict["dataPath"] = self.txtB_dataFolder.text()
    value_dict["interMethod"] = self.cB_interMethod.currentText()
    if self.cB_sameAttrib.currentIndex() > 0:
        value_dict["sameAttrib"] = self.cB_sameAttrib.currentText()
    if self.txtB_exportPath.text() != '':
        value_dict["expoPath"] = self.txtB_exportPath.text()

    # setting default
    value_dict["selectBy"] = 'all'

    if self.gB_noB.isChecked():
        value_dict["noB"] = self.sB_noB.value()
        value_dict["selectBy"] = 'number of buildings'
    else:
        value_dict["noB"] = None

    if self.gB_radius.isChecked():
        value_dict["radius"] = self.sB_radius.value()
        value_dict["selectBy"] = 'radius'
    else:
        value_dict["radius"] = None

    if self.gB_coor.isChecked():
        value_dict["bList"] = self.border_list
        value_dict["selectBy"] = 'coordinates'
    else:
        value_dict["bList"] = None

    return value_dict



def updateWindow2(self, value_dict):
    """updating window 2 based on previous inputs"""
    if value_dict["u_GML_ID"] != None:
        self.txtB_u_GML_ID.setText(value_dict["u_GML_ID"])
    if value_dict["dataPath"] != None:
        self.txtB_dataFolder.setText(value_dict["dataPath"])
    if value_dict["interMethod"] != None:
        index = self.cB_interMethod.findText(value_dict["interMethod"])
        self.cB_interMethod.setCurrentIndex(index)
    if value_dict["sameAttrib"] != None:
        index = self.cB_sameAttrib.findText(value_dict["sameAttrib"])
        if index > 0:
            self.cB_sameAttrib.setCurrentIndex(index)
    if value_dict["expoPath"] != None:
        self.txtB_exportPath.setText(value_dict["expoPath"])
    self.txtB_iCRS.setText(value_dict["iCRS"])
    self.txtB_oCRS.setText(value_dict["oCRS"])

    if value_dict["bList"] != None:
        self.gB_coor.setChecked(True)
        self.border = value_dict["bList"]
        for point in self.border:
            point_to_table(self, point)
    
    if value_dict["noB"] != None:
        self.gB_noB.setChecked(True)
        self.sB_noB.setValue(value_dict["noB"])

    if value_dict["radius"] != None:
        self.gB_radius.setChecked(True)
        self.sB_radius.setValue(value_dict["radius"])