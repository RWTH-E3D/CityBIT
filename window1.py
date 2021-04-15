# import of libraries
from PySide2 import QtWidgets, QtGui
import os

# import of functions
import gui_functions as gf
import TWOd_operations as TWOd
import vari as va



def gatherInfo1(self, value_dict, inter_dict):
    """gathering variable info from window 1"""
    buildingHeight = None
    if self.txtB_buildingHeight.text() != '':
        try:
            buildingHeight = float(self.txtB_buildingHeight.text())
        except:
            msg = 'Could not convert building height (' + self.txtB_buildingHeight.text() + ') to float.'
            gf.messageBox(self, 'Error', msg)
            return False, value_dict, inter_dict
        
        if buildingHeight > 0:
            value_dict["bHeight"] = buildingHeight
            inter_dict["bHeight"] = False
        else:
            msg = 'Building height (' + self.txtB_buildingHeight.text() + ') needs to be greater than 0m.'
            gf.messageBox(self, 'Error', msg)
            return False, value_dict, inter_dict
    else:
        value_dict["bHeight"] = None
        inter_dict["bHeight"] = True


    if self.txtB_roofHeight.text() != '':
        try:
            roofHeight = float(self.txtB_roofHeight.text())
        except:
            msg = 'Could not convert roof height (' + self.txtB_roofHeight.text() + ') to float.'
            gf.messageBox(self, 'Error', msg)
            return False, value_dict, inter_dict
        
        if roofHeight > 0:
            if buildingHeight != None and roofHeight > buildingHeight:
                msg = 'Roof height (' + self.txtB_roofHeight.text() + ') needs to be smaller the building height.'
                gf.messageBox(self, 'Error', msg)
                return False, value_dict, inter_dict
            value_dict["rHeight"] = roofHeight
            inter_dict["rHeight"] = False
        else:
            msg = 'Roof height (' + self.txtB_roofHeight.text() + ') needs to be greater than 0m.'
            gf.messageBox(self, 'Error', msg)
            return False, value_dict, inter_dict
    else:
        if self.cB_roofType.currentIndex() == 1:
            # in this case flat roof -> roofHeight not needed
            value_dict["rHeight"] = None
            inter_dict["rHeight"] = False
        else:
            value_dict["rHeight"] = None
            inter_dict["rHeight"] = True


    if self.cB_roofType.currentIndex() > 0:
        value_dict["rType"] = self.cB_roofType.currentText().split(' ')[-1]
        inter_dict["rType"] = False
    else:
        value_dict["rType"] = None
        inter_dict["rType"] = True


    if value_dict["rType"] != '1000' and value_dict["rType"] != '1070' and value_dict["rType"] != '1040 ' and self.cB_heading.count() > 0:
        if self.cB_heading.currentIndex() > 0:
            value_dict["rHeading"] = self.cB_heading.currentIndex() - 1
            inter_dict["rHeading"] = False        
        else:
            value_dict["rHeading"] = None
            inter_dict["rHeading"] = True
    else:
        value_dict["rHeading"] = None
        inter_dict["rHeading"] = False


    if self.cB_buildingFunction.currentIndex() > 0:
        value_dict["bFunction"] = self.cB_buildingFunction.currentText().split(' ')[-1]
        inter_dict["bFunction"] = False
    else:
        value_dict["bFunction"] = None
        inter_dict["bFunction"] = True

    value_dict["terrainIntersection"] = self.cB_terrainIntersection.currentText()
    if value_dict["terrainIntersection"] == 'off':
        inter_dict["terrainIntersection"] = False
    else:
        inter_dict["terrainIntersection"] = True

    if self.txtB_SAG.text() != '':
        try:
            sag = int(self.txtB_SAG.text())
        except:
            msg = 'Could not convert storeys above ground (' + self.txtB_SAG.text() + ') to integer.'
            gf.messageBox(self, 'Error', msg)
            return False, value_dict, inter_dict
        
        if sag >= 0:
            value_dict["SAG"] = sag
            inter_dict["SAG"] = False
        else:
            msg = 'Storey above ground (' + self.txtB_SAG.text() + ') needs to be greater or equal to 0.'
            gf.messageBox(self, 'Error', msg)
            return False, value_dict, inter_dict
    else:
        value_dict["SAG"] = None
        inter_dict["SAG"] = True

    if self.txtB_SBG.text() != '':
        try:
            sbg = int(self.txtB_SBG.text())
        except:
            msg = 'Could not convert storeys below ground (' + self.txtB_SBG.text() + ') to integer.'
            gf.messageBox(self, 'Error', msg)
            return False, value_dict, inter_dict
        
        if sbg >= 0:
            value_dict["SBG"] = sbg
            inter_dict["SBG"] = False
        else:
            msg = 'Storey below ground (' + self.txtB_SBG.text() + ') needs to be greater or equal to 0.'
            gf.messageBox(self, 'Error', msg)
            return False, value_dict, inter_dict
    else:
        value_dict["SBG"] = None
        inter_dict["SBG"] = True

    return True, value_dict, inter_dict


def updateWindow1(self, value_dict):
    """updating window 1 based on previous inputs"""
    if value_dict["bHeight"] != None:
        self.txtB_buildingHeight.setText(str(value_dict["bHeight"]))

    if value_dict["rHeight"] != None:
        self.txtB_roofHeight.setText(str(value_dict["rHeight"]))

    if value_dict["rType"] != None:
        rCode = value_dict["rType"]
        rWord = list(va.roofTypes.keys())[list(va.roofTypes.values()).index(float(value_dict["rType"]))]
        index = self.cB_roofType.findText(rWord + ' : ' + ' ' * (14 - len(rWord)) + str(rCode))
        self.cB_roofType.setCurrentIndex(index)

    # setting buildingHeadings
    if value_dict["cList"] != None:
        # calculating heading for roof surface if 4 points are given
        if len(value_dict["cList"]) == 4:
            # getting vectors 
            gS_list = value_dict["cList"].copy()
            x21 = gS_list[0][0]-gS_list[1][0]
            x23 = gS_list[2][0]-gS_list[1][0]

            y21 = gS_list[0][1]-gS_list[1][1]
            y23 = gS_list[2][1]-gS_list[1][1]

            # s = x21 * x23 + y21 * y23
            
            # s == 0 -> at least one 90 deg angle, second part confirms, that given area is parallelogram; parallelogram with 90deg angle -> rectangle
            # if s == 0 and [gS_list[3][0], gS_list[3][1]] == [gS_list[1][0] + x21 + x23, gS_list[1][1] + y21 + y23]:
            if [gS_list[3][0], gS_list[3][1]] == [gS_list[1][0] + x21 + x23, gS_list[1][1] + y21 + y23]:
                
                # getting rotation direction
                cent = TWOd.calc_center(gS_list)
                direction = TWOd.rotationDirection(cent, gS_list[0], gS_list[1])
                
                # calculating angles of orthogonals on the wallsurfaces
                gS_list.append(gS_list[0])
                wall_angles = ['']
                for i in range(4):
                    new_angle = TWOd.angle(gS_list[i], gS_list[i+1])
                    corrected_angle = TWOd.correct_angle(new_angle, direction)
                    wall_angles.append(str(round(corrected_angle, 3)))

                self.cB_heading.addItems(wall_angles)

        else:
            # if there is a number unequal to 4 of coordinates given -> no option to input heading
            self.cB_heading.setEnabled(False)

    # case for interpolation setting directions as headings
    else:
        self.cB_heading.addItems(['', 'NORTHish', 'EASTish', 'SOUTHish', 'WESTish'])
        pass


    if value_dict["rHeading"] != None:
        if self.cB_heading.count() > 0:
            self.cB_heading.setCurrentIndex(value_dict["rHeading"] + 1)

    if value_dict["bFunction"] != None:
        text = list(va.buildingFunctions.keys())[list(va.buildingFunctions.values()).index(float(value_dict["bFunction"]))]
        index = self.cB_buildingFunction.findText(text + ' : ' + ' ' * (40 - len(text)) + str(value_dict["bFunction"]))
        self.cB_buildingFunction.setCurrentIndex(index)

    index = self.cB_terrainIntersection.findText(value_dict["terrainIntersection"])
    if index >= 0:
        self.cB_terrainIntersection.setCurrentIndex(index)

    if value_dict["SAG"] != None:
        self.txtB_SAG.setText(str(value_dict["SAG"]))
    if value_dict["SBG"] != None:
        self.txtB_SBG.setText(str(value_dict["SBG"]))


def changeRoof(self, pypath):
    """updating window showing roofType example"""
    for i in self.banners:
        i.hide()
    self.banners[self.cB_roofType.currentIndex()].show()
    if self.cB_roofType.currentIndex() == 1:
        self.txtB_roofHeight.setEnabled(False)
    else:
        self.txtB_roofHeight.setEnabled(True)


def addRoofPictures(self, pypath, sizefactor):
    """function creating banner lables for all pictures"""
    self.banners = []
    for i, picture in enumerate(self.pictures):
        try:
            self.banners.append(QtWidgets.QLabel(self))
            self.banners[i].setPixmap(QtGui.QPixmap(os.path.join(pypath, r'pictures\roof', picture)))
            self.banners[i].setScaledContents(True)
            self.banners[i].setMinimumHeight(375*sizefactor)
            self.banners[i].setMaximumHeight(375*sizefactor)
            self.r_grid.addWidget(self.banners[i], 2, 0, 1, 4)
        except:
            print('error finding banner picture')


def createListForComboBox(dictionary, maxLength):
    """creating list for adding dictionary to combo box"""
    finished = []
    for key in dictionary:
        if key == '':
            finished.append('')
        else:
            finished.append(key + ' : ' + ' ' * (maxLength - len(key)) + str(dictionary[key]))
    return finished