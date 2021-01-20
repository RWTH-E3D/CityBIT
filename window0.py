# import of libraries
from PySide2 import QtWidgets
import csv

# import of functions
import gui_functions as gf
import TWOd_operations as TWOd
import cbit_functions as cbit_f




def gatherInfo0(self, value_dict, inter_dict):
    """gathering variable info from window 0"""
    cbit_f.check_CRS(self)
    # getting CRS info
    if self.crs_checked:
        value_dict["iCRS"] = self.txtB_iCRS.text()
        value_dict["oCRS"] = self.txtB_oCRS.text()
    else:
        return False, value_dict, inter_dict


    # getting ground reference
    if self.groundSurface_list != []:
        if len(self.groundSurface_list) > 2:
            value_dict["cList"] = self.groundSurface_list
            [xCen, yCen] = TWOd.calc_center(self.groundSurface_list)
            value_dict["xCen"] = xCen
            value_dict["yCen"] = yCen
            inter_dict["groundSurface"] = False
        else:
            gf.messageBox(self, 'Error', 'Please enter more coordinates or enter center')
            return False, value_dict, inter_dict

    elif self.txtB_xCenter.text() != '' and self.txtB_yCenter.text() != '':
        x_text = self.txtB_xCenter.text()
        y_text = self.txtB_yCenter.text()
        check = cbit_f.x_y_check(self, x_text, y_text, to_center=True)

        value_dict["xCenOrig"] = x_text
        value_dict["yCenOrig"] = y_text

        if check:
            value_dict["cList"] = None
            value_dict["xCen"] = float(self.txtB_xCenter.text())
            value_dict["yCen"] = float(self.txtB_yCenter.text())
            inter_dict["groundSurface"] = True

        else:
            value_dict["cList"] = None
            value_dict["xCen"] = None
            value_dict["yCen"] = None
            inter_dict["groundSurface"] = True
            gf.messageBox(self, 'Error', 'The entered center coordinates are not valid')
            return False, value_dict, inter_dict
    
    
    else:
        gf.messageBox(self, 'Error', 'Please enter either 3 or more coordiantes or a center point')
        return False, value_dict, inter_dict


    if inter_dict["groundSurface"]:
        # getting area
        if self.txtB_area.text() != '':
            try:
                value_dict["area"] = float(self.txtB_area.text())
            except:
                msg = 'Failed to convert ' + self.txtB_area.text() + ' (area) to float'
                gf.messageBox(self, 'Error', msg)
                return False, value_dict, inter_dict

            if value_dict["area"] <= 0:
                msg = 'Please enter an area larger than zero. (You entered ' + self.txtB_area.text() + ' )'
                gf.messageBox(self, 'Error', msg)
                return False, value_dict, inter_dict
            else:
                inter_dict["area"] = False
        else:
            value_dict["area"] = None
            inter_dict["area"] = True

        # getting side ratio
        if self.txtB_ratio.text() != '':
            try:
                value_dict["sideRatio"] = float(self.txtB_ratio.text())
            except:
                msg = 'Failed to convert ' + self.txtB_ratio.text() + ' (side ratio) to float'
                gf.messageBox(self, 'Error', msg)
                return False, value_dict, inter_dict

            if value_dict["sideRatio"] >= 1:
                inter_dict["sideRatio"] = False
            else:
                msg = 'Side ratio (' + self.txtB_ratio.text() + ') needs to be >= 1'
                gf.messageBox(self, 'Error', msg)
                return False, value_dict, inter_dict
        else:
            value_dict["sideRatio"] = None
            inter_dict["sideRatio"] = True
        
        # getting buildingHeading
        if self.txtB_heading.text() != '':
            try:
                angle = float(self.txtB_heading.text())
            except:
                msg = 'Failed to convert ' + self.txtB_heading.text() + ' (building heading) to float'
                gf.messageBox(self, 'Error', msg)
                return False, value_dict, inter_dict

            if 0 <= angle < 360:
                value_dict["bHeading"] = angle
                inter_dict["bHeading"] = False
            elif angle < 0:
                gf.messageBox(self, 'Error', 'building heading is too small\nplease enter a value between [0,360)')
                return False, value_dict, inter_dict
            elif angle >= 360:
                gf.messageBox(self, 'Error', 'building heading is too large\nplease enter a value between [0,360)')
                return False, value_dict, inter_dict

        else:
            value_dict["bHeading"] = None
            inter_dict["bHeading"] = True

    else:
        value_dict["area"] = None
        inter_dict["area"] = False

        value_dict["sideRatio"] = None
        inter_dict["sideRatio"] = False

        value_dict["bHeading"] = None
        inter_dict["bHeading"] = False


    # getting ground slab height
    if self.txtB_surfaceHeight.text() != '':
        try:
            value_dict["sHeight"] = float(self.txtB_surfaceHeight.text())
            inter_dict["sHeight"] = False
        except:
            msg = 'Failed to convert ' + self.txtB_surfaceHeight.text() + ' (surfaceHeight) to float'
            gf.messageBox(self, 'Error', msg)
            return False, value_dict, inter_dict
    else:
        value_dict["sHeight"] = None
        inter_dict["sHeight"] = True

    return True, value_dict, inter_dict



def updateWindow0(self, value_dict):
    """updating window 0 based on previous inputs"""
    self.txtB_iCRS.setText(value_dict["iCRS"])
    self.txtB_oCRS.setText(value_dict["oCRS"])
    if value_dict["cList"] != None:
        self.rB_list.setChecked(True)
        self.groundSurface_list = value_dict["cList"]
        self.txtB_iCRS.setReadOnly(True)
        self.txtB_oCRS.setReadOnly(True)
        for point in self.groundSurface_list:
            point_to_table(self, point)
        update_area_and_center(self)
    else:
        if value_dict["xCen"] != None:
            self.txtB_xCenter.setText(value_dict["xCenOrig"])
        if value_dict["xCen"] != None:
            self.txtB_yCenter.setText(value_dict["yCenOrig"])
        if value_dict["area"] != None:
            self.txtB_area.setText(str(value_dict["area"]))
        if value_dict["sideRatio"] != None:
            self.txtB_ratio.setText(str(value_dict["sideRatio"]))
        if value_dict["bHeading"] != None:
            self.txtB_heading.setText(str(value_dict["bHeading"]))

    if value_dict["sHeight"] != None:
        self.txtB_surfaceHeight.setText(str(value_dict["sHeight"]))



def point_to_table(self, point):
    """function to add points (point = [X, Y]) to table of groundsurface"""
    rowPosition = self.tbl_groundSurface.rowCount()
    self.tbl_groundSurface.insertRow(rowPosition)
    for i in range(len(point)):
        newItem = QtWidgets.QTableWidgetItem(str(point[i]))
        self.tbl_groundSurface.setItem(rowPosition, i, newItem)
    self.tbl_groundSurface.horizontalHeader().show()




def two_p_to_square(gS_list):
    """calculates two coordinates to square, transforms coordinates and sorts list"""
    X1, Y1 = gS_list[0]                 # getting coordinates of first point
    X2, Y2 = gS_list[1]                 # getting coordinates of second point

    # calculating interim results
    Xc = (X1 + X2)/2                    # xCenter
    Yc = (Y1 + Y2)/2                    # yCenter
    Xd = (X1 - X2)/2                    # xDistance
    Yd = (Y1 - Y2)/2                    # yDistance

    # calculating new points
    X3 = round(Xc - Yd, 8)
    Y3 = round(Yc + Xd, 8)
    X4 = round(Xc + Yd, 8)
    Y4 = round(Yc - Xd, 8)

    # appending new coordinates
    gS_list = gS_list + [[X3, Y3], [X4, Y4]]

    # # sorting coordinates
    # gS_list = sorter(gS_list, self, False)
    
    return gS_list



def three_p_to_rectangle(gS_list):
    """tries to calculate rectangle from given points"""
    # getting vectors 
    x21 = gS_list[0][0]-gS_list[1][0]
    x23 = gS_list[2][0]-gS_list[1][0]

    y21 = gS_list[0][1]-gS_list[1][1]
    y23 = gS_list[2][1]-gS_list[1][1]

    s = x21 * x23 + y21 * y23

    # checking if vectors are orthogonal to each other based of scalar product
    if round(s, 2) == 0:
        # calculating coordinates of new point
        X4 = gS_list[1][0] + x21 + x23
        Y4 = gS_list[1][1] + y21 + y23
        gS_list.append([X4,Y4])
        return gS_list
    else:
        print("vectors are not orthogonal to each other. Can't create rectangle")
        return []



def square_rectangle(self):
    """to create a square from two points or a rectangle from three points"""
    # checking how many coordinates are present
    if len(self.groundSurface_list) == 2:
        gS_list = two_p_to_square(self.groundSurface_list)
        pass
    elif len(self.groundSurface_list) == 3:
        gS_list = three_p_to_rectangle(self.groundSurface_list)
        pass
    else:
        print('your entered coordinates are not suitable for this function')
        return

    if gS_list != []:
        gS_list = sorter(self, gS_list, False)
        self.groundSurface_list = gS_list.copy()
        update_area_and_center(self)
        # deleting old coordinates in table
        while self.tbl_groundSurface.rowCount() > 0:
            self.tbl_groundSurface.removeRow(0)
        # adding coordinates in sorted order
        for point in self.groundSurface_list:
            point_to_table(self, point)
    else:
        # problems with calculating new coordinates
        pass


def sorter(self, coor, question= True):
    """sorting coordinates to avoid wrong order"""
    pp = TWOd.sorting(coor)
    # checking for all possible sequences
    if coor == pp:
        return coor
    elif coor == list(reversed(pp)):
        return coor
    lang = pp + pp                                      # for different starting point
    lang_r = list(reversed(pp)) + list(reversed(pp))    # for differnet starting point and reversed order
    for i, short in enumerate(lang):
        if i == len(coor):
            break
        if short == coor[0]:
            if lang[i:i+len(coor)] == coor:
                return coor
    for i, short in enumerate(lang_r):
        if i == len(coor):
            break
        if short == coor[0]:
            if lang_r[i:i+len(coor)] == coor:
                return coor

    # pop up for comparing coordinates, suggested vs input
    if question == True:
        msg = str('CityGML ATB suggests an alternative order.\n' + ','.join([str(p) for p in pp]) + '\nDo you want to use the suggested order?')
        choice = QtWidgets.QMessageBox.question(self, 'Attention!', msg, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.No:
            return coor
    else:
        # skipping question
        pass
    return pp


def update_area_and_center(self):
    """updates the area and center of area within the gui"""
    self.txtB_area.setText('')
    self.txtB_heading.setText('')
    self.txtB_ratio.setText('')
    if len(self.groundSurface_list) > 0:
        self.txtB_area.setReadOnly(True)
        self.txtB_heading.setReadOnly(True)
        self.txtB_ratio.setReadOnly(True)
    else:
        self.txtB_area.setReadOnly(False)
        self.txtB_heading.setReadOnly(False)
        self.txtB_ratio.setReadOnly(False)

    # checking if there are enough coordinates to calculate area
    if len(self.groundSurface_list) > 2:
        a = round(TWOd.AREA(self.groundSurface_list), 3)
        self.txtB_area.setText(str(a))
    # to few points to calculate area
    else:
        self.txtB_area.setText('')

    # checking if square/rectangle button should be enabled
    if len(self.groundSurface_list) == 2 or len(self.groundSurface_list) == 3:
        self.btn_sqrRec.setEnabled(True)
    else:
        self.btn_sqrRec.setEnabled(False)

    if len(self.groundSurface_list) > 0:
        self.btn_delPoint.setEnabled(True)




def load_csv(self):
    """to load coordinates of groundSurface from .csv file"""
    if self.crs_checked == True:
        pass
    else:
        cbit_f.check_CRS(self)
        if self.crs_checked == True:
            pass
        else:
            return
    
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
                if cbit_f.x_y_check(self, x, y, to_list=True):
                    pass
                else:
                    print('error occured in line', i)
            f.close()
        update_area_and_center(self)
        self.txtB_heading.setEnabled(False)
        self.txtB_heading.setText('')
        self.txtB_ratio.setEnabled(False)
        self.txtB_ratio.setText('')
    except:
        print('error loading coordinates from csv')


def add_point(self):
    """to add points to area of groundSurface"""
    if self.crs_checked == True:
        pass
    else:
        cbit_f.check_CRS(self)
        if self.crs_checked == True:
            pass
        else:
            return
    
    if(cbit_f.x_y_check(self, self.txtB_xCenter.text(), self.txtB_yCenter.text(), to_list=True)):
        self.txtB_xCenter.setText('')
        self.txtB_yCenter.setText('')
        update_area_and_center(self)
        
        # if points are given, the entered heading and side ratio are not considered
        self.txtB_heading.setEnabled(False)
        self.txtB_heading.setText('')
        self.txtB_ratio.setEnabled(False)
        self.txtB_ratio.setText('')
    else:
        pass



def del_point(self):
    """to remove last point from groundSurface"""
    # getting rowCount
    rowCount = self.tbl_groundSurface.rowCount()
    
    # if there is something in the table
    if rowCount > 0:
        # checking if there are the same number of points in both the table and the list
        if rowCount == len(self.groundSurface_list):
            # deleting row/entry of last point
            self.tbl_groundSurface.removeRow(rowCount-1)
            self.groundSurface_list = self.groundSurface_list[:-1]
        else:
            # unequal number of points in table and list
            print('Error! table has a has', rowCount, 'rows, but groundSurface_list has', len(self.groundSurface_list), 'entries')
        
        # case that the last element has just been deleted
        if rowCount == 1:
            self.txtB_iCRS.setReadOnly(False)
            self.txtB_oCRS.setReadOnly(False)
            self.tbl_groundSurface.horizontalHeader().hide()
            self.crs_checked = False
            self.btn_delPoint.setEnabled(False)

    update_area_and_center(self)



def center_of_list(self):
    """changing gui elements depending if center of coordiantes should be entered or list of coordiantes"""
    if self.rB_center.isChecked():
        self.btn_addPoint.setEnabled(False)
        self.btn_loadCSV.setEnabled(False)
        
        self.txtB_area.setEnabled(True)
        self.txtB_ratio.setEnabled(True)
        self.txtB_heading.setEnabled(True)

        self.lbl_xCenter.setText('Center longitude:')
        self.txtB_xCenter.setPlaceholderText('Center longitude')
        self.lbl_yCenter.setText('Center latitude:')
        self.txtB_yCenter.setPlaceholderText('Center latitude')

        while self.tbl_groundSurface.rowCount() > 0:
            del_point(self)



    elif self.rB_list.isChecked():
        self.btn_addPoint.setEnabled(True)
        self.btn_loadCSV.setEnabled(True)

        self.txtB_area.setEnabled(False)
        self.txtB_ratio.setEnabled(False)
        self.txtB_heading.setEnabled(False)

        self.lbl_xCenter.setText('Longitude:')
        self.txtB_xCenter.setPlaceholderText('Longitude')
        self.lbl_yCenter.setText('Latitude:')
        self.txtB_yCenter.setPlaceholderText('Latitude')

    