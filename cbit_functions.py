# import of libraries
from PySide2 import QtWidgets
import os
import pyproj
import math
import numpy as np
import pandas as pd
import lxml.etree as ET
from datetime import date, datetime
import glob
import matplotlib.path as mplP
import uuid
from scipy.interpolate import griddata
from scipy.spatial import ConvexHull

# import of functions
import classes as cl
import gui_functions as gf
import TWOd_operations as TWOd
import interpolation_functions as inter_f
import vari as va
import coordiante_check as CC
import f_fafb
import window0 as w0




def check_CRS(self, notify=False):
    """function to check if entered text has corresponding Coordinate Reference System"""
    iCRS_text = self.txtB_iCRS.text()
    oCRS_text = self.txtB_oCRS.text()
    if iCRS_text != '':
        try:
            iCRS = pyproj.CRS.from_epsg(iCRS_text)
            self.iCRS = iCRS
        except:
            self.iCRS = ''
            self.crs_checked = False
            gf.messageBox(self, 'Error!', 'No matching CRS found!')
            print('error!, could not find corresponding CRS to:', iCRS_text)
            return
    else:
        # gf.messageBox(self, 'Error!', 'Please enter an input CRS!')
        pass

    if oCRS_text != '':
        try:
            oCRS = pyproj.CRS.from_epsg(oCRS_text)
            if oCRS.axis_info[0].unit_name == 'metre' and oCRS.axis_info[1].unit_name == 'metre':
                self.uom = 'm'
            else:
                msg = 'Unsupported unit(s): ' + oCRS.axis_info[0].unit_name + ' and ' + oCRS.axis_info[1].unit_name
                gf.messageBox(self, 'Error', msg)
                return 
            crs_4326 = pyproj.CRS.from_epsg(4326)
            x_min4326, y_min4326, x_max4326, y_max4326 = oCRS.area_of_use.bounds
            self.x_min, self.y_min = pyproj.transform(crs_4326, oCRS, x_min4326, y_min4326, always_xy=True)
            self.x_max, self.y_max = pyproj.transform(crs_4326, oCRS, x_max4326, y_max4326, always_xy=True)
            self.oCRS = oCRS
            self.crs_checked = True
        except:
            self.crs_checked = False
            gf.messageBox(self, 'Error!', 'No matching CRS found!')
            print('error!, could not find corresponding CRS to:', oCRS_text)
            return
    else:
        gf.messageBox(self, 'Error!', 'Please enter an output CRS!')
        return

    if notify:
        gf.messageBox(self,'Succes', 'Inputed CRS(s) are valid!')




def displaysetup(self):
    """preparing tbl_groundSurface in gui"""
    self.tbl_groundSurface.setColumnCount(2)
    self.tbl_groundSurface.setHorizontalHeaderLabels(['X coordinate', 'Y coordinate'])
    self.tbl_groundSurface.verticalHeader().hide()
    self.tbl_groundSurface.horizontalHeader().hide()
    self.tbl_groundSurface.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
    self.tbl_groundSurface.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)




def x_y_check(self, x_in, y_in, to_list=False, to_center=False):
    """to check if x and y can be transformed to floats and if they are within the bounds of the crs"""
    if self.crs_checked == False:
        check_CRS(self)
        if self.crs_checked == False:
            return False

    X = None
    Y = None

    if x_in != '':              # checking if entered x can be converted to float
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

    if y_in != '':              # checking if entered y can be converted to float
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
            iCRS = 'EPSG:' + self.txtB_iCRS.text()
            oCRS = 'EPSG:' + self.txtB_oCRS.text()
            x, y =  pyproj.transform(iCRS, oCRS, X, Y, always_xy=True)
        else:                   # coordinates don't need to be transformed
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
        
    # checking if points should be added to table
    if to_list == True:
        if [x, y] not in self.groundSurface_list:
            self.groundSurface_list.append([x, y])
            w0.point_to_table(self, [x, y])
            self.txtB_iCRS.setReadOnly(True)
            self.txtB_oCRS.setReadOnly(True)
        else:                   # not adding duplicates
            print('point', [x, y], 'already in groundSurface_list')


    # updating x and y center in case of transformation
    if to_center == True and (x != x_in or y != y_in):
        self.txtB_xCenter.setText(str(round(x, 3)))
        self.txtB_yCenter.setText(str(round(y, 3)))
        self.txtB_iCRS.setText('')
        self.iCRS = ''

    return True



def compute(self, value_dict, inter_dict):
    """function to start building calculation"""

    if value_dict["expoPath"] == None:
        gf.messageBox(self, 'error', 'Please select an export path first')
        return
    else:
        pass

    terrainIntersection = []

    if value_dict["cList"] != None:
        gS_list = value_dict["cList"].copy()

    # getting filenames of datapath
    if value_dict["dataPath"] == None:
        filenames = None
    else:
        filenames = (glob.glob(os.path.join(value_dict["dataPath"], '*.gml')) + glob.glob(os.path.join(value_dict["dataPath"], '*.xml')))

    # getting center of base plate
    x_center = value_dict["xCen"]
    y_center = value_dict["yCen"]

    # interpolating data if needed
    if sum(inter_dict.values()) > 0: # or i_SAG or i_SBG:
        if filenames == None:
            gf.messageBox(self, 'error', 'interpolation is needed; please select valid datasetpath')
            return
        else:
            if len(filenames) != 0:
                # interpolate missing data here
                if value_dict["sameAttrib"] == None:
                    # basically irrelevant
                    attribValue = ''
                elif value_dict["sameAttrib"] == 'roofType':
                    attribValue = value_dict["rType"]
                elif value_dict["sameAttrib"] == 'buildingFunction':
                    attribValue = value_dict["bFunction"]
                else:
                    print('error within same attrib! This should not be reachable')

                if inter_dict["terrainIntersection"]:
                    terrainRadius = float(value_dict["terrainIntersection"][:-1])
                else:
                    # just setting a default value (should not be used)
                    terrainRadius = 1000

                # getting coordinates for sel cor and so on here
                if value_dict["selectBy"] == 'all':
                    border_list = None
                    radius = None
                elif value_dict["selectBy"] == 'coordinates':
                    border_list = value_dict["bList"]
                    radius = None
                elif value_dict["selectBy"] == 'number of buildings':
                    border_list = f_fafb.fafnoB(filenames, [x_center, y_center], value_dict["noB"], value_dict["sameAttrib"], attribValue)
                    radius = None
                elif value_dict["selectBy"] == 'radius':
                    radius = value_dict["radius"]
                    x0 = x_center - radius
                    x1 = x_center + radius
                    y0 = y_center - radius
                    y1 = y_center + radius
                    border_list = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
                else:
                    print("this point should not be reachable (cbit_fucntions) getting border_list")

                gf.windowTitle(self, 'collecting data from dataset')
                df, df_area = inter_f.interpolation_start(filenames, value_dict["selectBy"], value_dict["sameAttrib"], attribValue, [x_center, y_center], border_list, radius, inter_dict, terrainRadius)

                # checking if there is data in dataframe
                if len(df.index) > 0 or (len(df_area.index) > 0 and inter_dict["area"] == True):
                    # found data for interpolation

                    # checking if data points provide ConvexHull for interpolation
                    centerDF = df[["X_center", "Y_center"]].copy()
                    hull = ConvexHull(centerDF.values)
                    hullCoor = np.array(centerDF.values)[hull.vertices]
                    hullBorder = mplP.Path(hullCoor)

                    if hullBorder.contains_point((x_center, y_center)):
                        # new center is within the collected data -> can continue
                        pass
                    else:           # new center is outside of the collected data -> can't interpolate
                        print("WARNING!\nCan't extrapolate data")
                        gf.messageBox(self, 'Error', 'Please increase the interpolation data.\nCollected data does not create ConvexHull\naround new center point.')
                        return

                else:
                    gf.messageBox(self, 'Error', 'Did not find any data for interpolation')
                    return
                

                # main interpolation part
                if inter_dict["groundSurface"]:
                    
                    # interpolating surface area
                    if inter_dict["area"]:
                        gf.windowTitle(self, 'interpolating ground area')
                        area = inter_f.interpolate_value(df_area, x_center, y_center, "area", value_dict["interMethod"])
                    else:
                        # surface area given by user and does not need to be interpolated
                        area = value_dict["area"]

                    # interpolating side to side ratio
                    if inter_dict["sideRatio"]:
                        gf.windowTitle(self, 'interpolating side ratio')
                        ratio = inter_f.interpolate_value(df, x_center, y_center, "side_ratio", value_dict["interMethod"])
                    else:
                        # ratio is given by user
                        ratio = value_dict["sideRatio"]

                    # calculating length of sides
                    long_side = math.sqrt(area * ratio)
                    short_side = math.sqrt(area / ratio)
                    long_side_h = long_side * 0.5
                    short_side_h = short_side * 0.5

                    # getting heading of the building
                    if inter_dict["bHeading"]:
                        gf.windowTitle(self, 'interpolating building heading')
                        long_dxN = inter_f.interpolate_value(df, x_center, y_center, "long_dxN", value_dict["interMethod"])
                        long_dyN = inter_f.interpolate_value(df, x_center, y_center, "long_dyN", value_dict["interMethod"])
                        angle =  TWOd.angle((0,0), (long_dxN, long_dyN))
                        print("calculated angle:\t", angle)
                    else:
                        # heading of building is given by user
                        angle = value_dict["bHeading"]

                    # calculating corner points for new rectangle and creating array of them
                    p0 = [x_center - math.sin(math.radians(angle)) * long_side_h - math.sin(math.radians(angle + 90)) * short_side_h, y_center - math.cos(math.radians(angle)) * long_side_h - math.cos(math.radians(angle + 90)) * short_side_h]
                    p1 = [x_center - math.sin(math.radians(angle)) * long_side_h + math.sin(math.radians(angle + 90)) * short_side_h, y_center - math.cos(math.radians(angle)) * long_side_h + math.cos(math.radians(angle + 90)) * short_side_h]
                    p2 = [x_center + math.sin(math.radians(angle)) * long_side_h + math.sin(math.radians(angle + 90)) * short_side_h, y_center + math.cos(math.radians(angle)) * long_side_h + math.cos(math.radians(angle + 90)) * short_side_h]
                    p3 = [x_center + math.sin(math.radians(angle)) * long_side_h - math.sin(math.radians(angle + 90)) * short_side_h, y_center + math.cos(math.radians(angle)) * long_side_h - math.cos(math.radians(angle + 90)) * short_side_h]
                    gS_list = [p0, p1, p2, p3]

                else:
                    # groundSurface coordinates already given
                    pass


                if inter_dict["sHeight"]:
                    gf.windowTitle(self, 'interpolating height of base plate')
                    surfaceHeight = inter_f.interpolate_value(df, x_center, y_center, "min_elevation", value_dict["interMethod"])
                else:
                    # surfaceHeight/min_elevation already given and does not need to be interpolated by user
                    surfaceHeight = value_dict["sHeight"]

                if inter_dict["bHeight"]:
                    gf.windowTitle(self, 'interpolating building height')
                    buildingHeight = inter_f.interpolate_value(df, x_center, y_center, "buildingHeight", value_dict["interMethod"])
                else:
                    # buildingHeight already given
                    buildingHeight = value_dict["bHeight"]


                if inter_dict["rType"]:
                    gf.windowTitle(self, 'interpolating roof type')
                    if len(gS_list) != 4:
                        roofType = inter_f.interpolate_categroy(df, x_center, y_center, "roofType", value_dict["interMethod"], posRes= ['1000', '1070'])
                    else:
                        roofType = inter_f.interpolate_categroy(df, x_center, y_center, "roofType", value_dict["interMethod"], posRes= ['1000', '1010', '1020', '1030', '1040', '1070'])
                else:
                    # roofType already given
                    roofType = value_dict["rType"]


                if inter_dict["rHeight"]:
                    gf.windowTitle(self, 'interpolating roof height')
                    roofHeight = inter_f.interpolate_value(df, x_center, y_center, "roofHeight", value_dict["interMethod"])
                else:
                    # roofHeight not needed or already given
                    if value_dict["rHeight"] != None:
                        roofHeight = value_dict["rHeight"]
                    else:
                        roofHeight = 0
                    pass


                # interpolating terrain intersection
                if inter_dict["terrainIntersection"]:
                    terrain_raw = df["intersectionCoor"]
                    # creating one list from list of lists 
                    terrain_data = [item for sublist in terrain_raw for item in sublist]
                    # remvoing duplicates 
                    terrain_data = [list(t) for t in set(tuple(element) for element in terrain_data)]
                    print('\n\n\n', len(terrain_data), '\n\n')
                    df_terrain = pd.DataFrame(terrain_data, columns= ["x_coor", "y_coor", "intersectionHeight"])
                    x_values = [i[0]for i in gS_list]
                    y_values = [i[1]for i in gS_list]

                    gf.windowTitle(self, 'interpolating terrain intersection')
                    terrainHeights = griddata((df_terrain["x_coor"], df_terrain["y_coor"]), df_terrain["intersectionHeight"], (x_values, y_values), method=value_dict["interMethod"])

                    max_ele_dif = 10

                    terrainIntersection = []
                    # checking if building is above groundSurface
                    if all(surfaceHeight >= height for height in terrainHeights):
                        # building is entirely above or equal to terrain -> no terrain intersection exists
                        gf.messageBox(self, "Information", "Building is entirely above ground.\nSkipping terrain intersection.")
                        pass
                    elif all(surfaceHeight + buildingHeight - roofHeight <= height for height in terrainHeights):
                        # building walls are entirely below the terrain -> no terrain intersection exists
                        gf.messageBox(self, "Information", "Building walls are all below the terrain intersection.\nSkipping terrain intersection.")
                        pass
                    else:
                        # building and terrain collide
                        terrainIntersection = []
                        for i, point in enumerate(gS_list):
                            if surfaceHeight <= terrainHeights[i] <= surfaceHeight + buildingHeight - roofHeight:
                                terrainIntersection.append(point + [round(terrainHeights[i], 3)])
                            elif terrainHeights[i] < surfaceHeight:
                                if surfaceHeight - terrainHeights[i] > max_ele_dif:
                                    msg = "Terrain intersection for " + str(point) + " is " + str( surfaceHeight - terrainHeights[i]) + "m lower than the building.\nSetting terrain intersection to base plate height"
                                    gf.messageBox(self, "Warning!", msg)
                                terrainIntersection.append(point + [surfaceHeight])
                            elif terrainHeights[i] > surfaceHeight + buildingHeight - roofHeight:
                                if terrainHeights[i] - surfaceHeight + buildingHeight - roofHeight > max_ele_dif:
                                    msg = "Terrain intersection for " + str(point) + " is " + str(terrainHeights[i] - surfaceHeight + buildingHeight - roofHeight) + "m higher than the building walls.\nSetting terrain intersection to wall height"
                                terrainIntersection.append(point + [surfaceHeight + buildingHeight - roofHeight])
                                
                else:
                    # here terrainIntersection inforamtion from user input
                    # to be added in a future update
                    pass


                # interpolating roof heading
                if inter_dict["rHeading"] and roofType != '1000' and roofType != '1040' and roofType != '1070':
                    gf.windowTitle(self, 'interpolating roof heading')

                    print(x_center, y_center, "roof_X", value_dict["interMethod"])
                    roof_X = inter_f.interpolate_value(df, x_center, y_center, "roof_X", value_dict["interMethod"])
                    roof_Y = inter_f.interpolate_value(df, x_center, y_center, "roof_Y", value_dict["interMethod"])
                    roof_angle =  TWOd.angle((0,0), (roof_X, roof_Y))

                    if math.isnan(roof_angle):
                        heading_index = 0
                        print("roof angle is NaN -> heading_index set to 0")
                    
                    else:
                        # getting rotation direction
                        direction = TWOd.rotationDirection([x_center, y_center], gS_list[0], gS_list[1])
                        
                        # calculating angles of orthogonals on the wallsurfaces
                        # and taking wall surface which has the smallest diviation from the interpolated angle as heading_index
                        gS_list.append(gS_list[0])
                        min_dif = 360
                        for i in range(4):
                            new_angle = TWOd.angle(gS_list[i], gS_list[i+1])
                            corrected_angle = TWOd.correct_angle(new_angle, direction)
                            if abs(corrected_angle - roof_angle) < min_dif:
                                min_dif = abs(corrected_angle - roof_angle)
                                heading_index = i                        

                        print("calculated ROOFangle:\t", roof_angle)
                        print("heading index:\t\t", heading_index)

                else:
                    # heading_index not needed or given
                    pass


                if inter_dict["bFunction"]:
                    gf.windowTitle(self, 'interpolating building function')
                    # buildingFunction_value = inter_f.interpolate_categroy(df, x_center, y_center, "buildingFunction", value_dict["interMethod"])
                    # buildingFunction = list(va.buildingFunctions.keys())[list(va.buildingFunctions.values()).index(float(buildingFunction_value))]
                    buildingFunction = inter_f.interpolate_categroy(df, x_center, y_center, "buildingFunction", value_dict["interMethod"])
                else:
                    # buildingFunction given
                    buildingFunction = value_dict["bFunction"]


                if inter_dict["SAG"]:
                    gf.windowTitle(self, 'interpolating storeys above ground')
                    print('cant interpolate SAG yet')
                    # either get averade storage height and depending on that or just depending on the surrounding buildings
                    storeysAboveGround = False
                else:
                    # SAG not needed or given
                    storeysAboveGround = value_dict["SAG"]


                if inter_dict["SBG"]:
                    gf.windowTitle(self, 'interpolating storeys below ground')
                    print('cant interpolate SBG yet')
                    # either get averade storage height and depending on that or just depending on the surrounding buildings
                    storeysBelowGround = False
                else:
                    # SBG not needed or given
                    storeysBelowGround = value_dict["SBG"]


            else:
                gf.messageBox(self, 'error', 'directory does not contain any .xml or .gml files')
                return

        interpol_name = value_dict["interMethod"] + ' interpolation'

    else:
        # interpolation not needed
        interpol_name = 'user entered values'

        roofType = value_dict["rType"]

        buildingFunction = value_dict["bFunction"]

        if value_dict["rHeight"] != None:
            roofHeight = value_dict["rHeight"]
        else:
            roofHeight = 0

        surfaceHeight = value_dict["sHeight"]

        buildingHeight = value_dict["bHeight"]

        storeysAboveGround = value_dict["SAG"]

        storeysBelowGround = value_dict["SBG"]


    if not inter_dict["rHeading"]:
        if roofType != '1000' and roofType != '1040' and roofType != '1070':
            if inter_dict["groundSurface"]:
                pp = gS_list.copy()
                gS_copy = gS_list.copy()
                # calculate center
                cent = TWOd.calc_center(pp)
                # sort by polar angle
                # headings after sorting 0->1 south 1->2 east 2->3 north 3->4 west
                pp.sort(key=lambda p: math.atan2(p[1]-cent[1], p[0]-cent[0]))
                pp.append(pp[0])
                gS_copy.append(gS_copy[0])

                # index 0=north,  1=east, 2=south, 3=west
                index = value_dict["rHeading"] - 1
                
                if (value_dict["rHeading"] - 1) % 2 == 0:
                    pass
                else:
                    # getting north to south and south to north issue right
                    index = (index + 2) % 4
                
                # the pair of wall coordinates
                pair = [pp[index], pp[index + 1]]

                # now getting the right index of groundSurface list
                for i in range(4):
                    if pair == [gS_copy[i], gS_copy[i + 1]]:
                        heading_index = i
                    else:
                        pass

            else:
                heading_index = value_dict["rHeading"]

        else:
            heading_index = 1


    # checking if new coordinates collide with existing buildings within dataset
    if filenames != None and len(filenames) > 0:
        gf.windowTitle(self, 'testing for collison with existing buildings')
        collision_result, file_overlap, element_id = collision_check(gS_list, filenames)
        if collision_result:
            print('collision check failed')
            msg = 'New groundSurface collided with existing building ' + element_id + ' in file ' + file_overlap +'.'
            gf.messageBox(self, 'Error', msg)
            print('continuing despite collision')
            # return
        else:
            print('groundSurface of new building does not interfere with dataset')

    gf.windowTitle(self, 'creating building volume')


    """
    calculating polygons
    """

    # surfaceHeight_plusHouse
    sH_pHouse = round(surfaceHeight + buildingHeight, 3)
    # surfaceHeight_plusWall
    sH_pWall = sH_pHouse - roofHeight
    
    # getting data for envelope
    envelope_dict = {}
    x_coor = [i[0]for i in gS_list]
    x_min = min(x_coor)
    x_max = max(x_coor)

    y_coor = [i[1]for i in gS_list]
    y_min = min(y_coor)
    y_max = max(y_coor)

    envelope_dict['lowerCorner'] = [x_min, y_min, surfaceHeight]
    envelope_dict['upperCorner'] = [x_max, y_max, sH_pHouse]

    gS_list.append(gS_list[0])
    if terrainIntersection != []:
        terrainIntersection.append(terrainIntersection[0])

    # calculating  3d ground surface
    gS_3d = []
    for i in gS_list:
        y = i.copy()
        y.append(surfaceHeight)
        gS_3d.append(y)
    gS_dict = {'Base Surface': gS_3d}

    wall_dict = {}
    roof_dict = {}
    
    # calculating walls and roofs
    if roofType == '1000':
        # calculating wall surfaces
        for i in range(len(gS_list) - 1):
            name = 'Outer Wall ' + str(i+1)
            wall = [gS_list[i] + [surfaceHeight], gS_list[i+1] + [surfaceHeight], gS_list[i+1] + [sH_pHouse], gS_list[i] + [sH_pHouse]]
            wall.append(wall[0])
            wall_dict[name]= wall

        # calculating roof surface
        rS_3d = []
        for i in gS_list:
            y = i.copy()
            y.append(sH_pHouse)
            rS_3d.append(y)
        roof_dict = {'Roof 1': rS_3d}


    elif roofType == '1010':
        # calculating wall surfaces
        # assuming the heading equals the wall with the lower side of the roof
        highPoints = []
        for i in range(4):
            name = 'Outer Wall ' + str(i+1)
            if i == heading_index:
                # both low
                wall = [gS_list[i] + [surfaceHeight], gS_list[i+1] + [surfaceHeight], gS_list[i+1] + [sH_pWall], gS_list[i] + [sH_pWall]]
            elif i - heading_index == 2 or i - heading_index == -2:
                # both high
                wall = [gS_list[i] + [surfaceHeight], gS_list[i+1] + [surfaceHeight], gS_list[i+1] + [sH_pHouse], gS_list[i] + [sH_pHouse]]
                highPoints = [gS_list[i], gS_list[i+1]]
            elif (heading_index + 1) % 4 - (i + 1) == - 1:
                # i low     i+1 high
                wall = [gS_list[i] + [surfaceHeight], gS_list[i+1] + [surfaceHeight], gS_list[i+1] + [sH_pHouse], gS_list[i] + [sH_pWall]]
            else:
                # i high    i+1 low
                wall = [gS_list[i] + [surfaceHeight], gS_list[i+1] + [surfaceHeight], gS_list[i+1] + [sH_pWall], gS_list[i] + [sH_pHouse]]


            wall.append(wall[0])
            wall_dict[name]= wall

        # calculating roof surface
        rS_3d = []
        for i in gS_list:
            y = i.copy()
            if y in highPoints:
                y.append(sH_pHouse)
            else:
                y.append(sH_pWall)
            rS_3d.append(y)
        roof_dict = {'Roof 1': rS_3d}


    elif roofType == '1020':
        # calculating wall surfaces
        # assuming the heading equals the side with the higher roof
        sH_pHalfRoof = sH_pHouse - (roofHeight / 3)
        highPoints = []
        lowPoints = []
        for i in range(4):
            name = 'Outer Wall ' + str(i+1)
            if i == heading_index:
                # wall on which the higher roof is ending
                wall = [gS_list[i] + [surfaceHeight], gS_list[i+1] + [surfaceHeight], gS_list[i+1] + [sH_pWall], gS_list[i] + [sH_pWall]]
                highPoints = [gS_list[i], gS_list[i+1]]
            elif i - heading_index == 2 or i - heading_index == -2:
                # wall on which the lower roof is ending
                wall = [gS_list[i] + [surfaceHeight], gS_list[i+1] + [surfaceHeight], gS_list[i+1] + [sH_pWall], gS_list[i] + [sH_pWall]]
                lowPoints = [gS_list[i], gS_list[i+1]]
            elif (heading_index + 1) % 4 - (i + 1) == - 1:
                # first half height than full height
                center0 = TWOd.calc_center(gS_list[i:i+2])
                wall = [gS_list[i] + [surfaceHeight], gS_list[i+1] + [surfaceHeight], gS_list[i+1] + [sH_pWall], center0 + [sH_pHalfRoof], center0 + [sH_pHouse] ,gS_list[i] + [sH_pWall]]
            else:
                # first full height than half height
                center1 = TWOd.calc_center(gS_list[i:i+2])
                wall = [gS_list[i] + [surfaceHeight], gS_list[i+1] + [surfaceHeight], gS_list[i+1] + [sH_pWall], center1 + [sH_pHouse], center1 + [sH_pHalfRoof] ,gS_list[i] + [sH_pWall]]
            
            wall.append(wall[0])
            wall_dict[name]= wall

        # for the wall between the two roof surfaces
        wall = [center0 + [sH_pHalfRoof], center1 + [sH_pHalfRoof], center1 + [sH_pHouse], center0 + [sH_pHouse]]
        wall.append(wall[0])
        name = 'Outer Wall ' + str(len(wall_dict) + 1)
        wall_dict[name] = wall


        # calculating roof surfaces
        # for roof with higher points
        roof = [highPoints[0] + [sH_pWall], highPoints[1] + [sH_pWall], center0 + [sH_pHouse], center1 + [sH_pHouse]]
        roof.append(roof[0])
        name = 'Roof ' + str(len(roof_dict) + 1)
        roof_dict[name] = roof
        # for roof with lower points
        roof = [lowPoints[0] + [sH_pWall], lowPoints[1] + [sH_pWall], center1 + [sH_pHalfRoof], center0 + [sH_pHalfRoof]]
        roof.append(roof[0])
        name = 'Roof ' + str(len(roof_dict) + 1)
        roof_dict[name] = roof


    elif roofType == '1030':
        # calculating wall surfaces
        # assuming the heading equals one of the 4 sided walls
        for i in range(4):
            name = 'Outer Wall ' + str(i+1)
            if i == heading_index or i - heading_index == 2 or i - heading_index == -2:
                # square surfaces
                wall = [gS_list[i] + [surfaceHeight], gS_list[i+1] + [surfaceHeight], gS_list[i+1] + [sH_pWall], gS_list[i] + [sH_pWall]]
            else:
                # surfaces with "5th", higher point
                wall = [gS_list[i] + [surfaceHeight], gS_list[i+1] + [surfaceHeight], gS_list[i+1] + [sH_pWall], TWOd.calc_center(gS_list[i:i+2]) + [sH_pHouse], gS_list[i] + [sH_pWall]]

            wall.append(wall[0])
            wall_dict[name]= wall
        
        if heading_index % 2 == 0:
            # square first, 5th second
            C0 = TWOd.calc_center(gS_list[1:3])
            C1 = TWOd.calc_center(gS_list[3:5])
            roof_dict['Roof 1'] = [gS_list[0]+ [sH_pWall], gS_list[1]+ [sH_pWall], C0 + [sH_pHouse], C1 + [sH_pHouse], gS_list[0]+ [sH_pWall]]
            roof_dict['Roof 2'] = [gS_list[2]+ [sH_pWall], gS_list[3]+ [sH_pWall], C1 + [sH_pHouse], C0 + [sH_pHouse], gS_list[2]+ [sH_pWall]]
        else:
            # 5th first, square second
            C0 = TWOd.calc_center(gS_list[0:2])
            C1 = TWOd.calc_center(gS_list[2:4])
            roof_dict['Roof 1'] = [gS_list[1]+ [sH_pWall], gS_list[2]+ [sH_pWall], C1 + [sH_pHouse], C0 + [sH_pHouse], gS_list[1]+ [sH_pWall]]
            roof_dict['Roof 2'] = [gS_list[3]+ [sH_pWall], gS_list[0]+ [sH_pWall], C0 + [sH_pHouse], C1 + [sH_pHouse], gS_list[3]+ [sH_pWall]]


    elif roofType == '1040':
        # calculating wall surfaces
        for i in range(4):
            name = 'Outer Wall ' + str(i+1)
            wall = [gS_list[i] + [surfaceHeight], gS_list[i+1] + [surfaceHeight], gS_list[i+1] + [sH_pWall], gS_list[i] + [sH_pWall]]
            wall.append(wall[0])
            wall_dict[name]= wall

        # calculating the roof surfaces based the assumption that the gabel is colinear to the longer side of the roof
        help_array = []
        for i in range(2):
            help_array.append(TWOd.distance(gS_list[i], gS_list[i+1]))
        
        gabel_length = abs(help_array[0] - help_array[1])
        center_to_gabel = (max(help_array) - gabel_length) / 2

        # list of groundSurface coordinates but with (surfaceHeight + wallHeight) as 3d coordinate
        sH_pWall_list = [i + [sH_pWall] for i in gS_list.copy()]
        if help_array[0] > help_array[1]:
            # longside first
            # getting some info about the heading of the roof
            shortCenter = TWOd.calc_center(gS_list[1:3])
            gabel_vector = TWOd.normedDirectionVector(gS_list[2], gS_list[3])
            # corners of roof
            C0 = [shortCenter[0] + center_to_gabel * gabel_vector[0], shortCenter[1] + center_to_gabel * gabel_vector[1], sH_pHouse]
            C1 = [shortCenter[0] + (center_to_gabel + gabel_length) * gabel_vector[0], shortCenter[1] + (center_to_gabel + gabel_length) * gabel_vector[1], sH_pHouse]
            #  roof surfaces
            roof_dict['Roof 1'] = [sH_pWall_list[0], sH_pWall_list[1], C0, C1, sH_pWall_list[0]]
            roof_dict['Roof 2'] = [sH_pWall_list[1], sH_pWall_list[2], C0, sH_pWall_list[1]]
            roof_dict['Roof 3'] = [sH_pWall_list[2], sH_pWall_list[3], C1, C0, sH_pWall_list[2]]
            roof_dict['Roof 4'] = [sH_pWall_list[3], sH_pWall_list[0], C1, sH_pWall_list[3]]


        else:
            # short side first
            # getting some info about the heading of the roof
            shortCenter = TWOd.calc_center(gS_list[0:2])
            gabel_vector = TWOd.normedDirectionVector(gS_list[1], gS_list[2])
            # corners of roof
            C0 = [shortCenter[0] + center_to_gabel * gabel_vector[0], shortCenter[1] + center_to_gabel * gabel_vector[1], sH_pHouse]
            C1 = [shortCenter[0] + (center_to_gabel + gabel_length) * gabel_vector[0], shortCenter[1] + (center_to_gabel + gabel_length) * gabel_vector[1], sH_pHouse]
            # roof surfaces
            roof_dict['Roof 1'] = [sH_pWall_list[0], sH_pWall_list[1], C0, sH_pWall_list[0]]
            roof_dict['Roof 2'] = [sH_pWall_list[1], sH_pWall_list[2], C1, C0, sH_pWall_list[1]]
            roof_dict['Roof 3'] = [sH_pWall_list[2], sH_pWall_list[3], C1, sH_pWall_list[2]]
            roof_dict['Roof 4'] = [sH_pWall_list[3], sH_pWall_list[0], C0, C1, sH_pWall_list[3]]


    elif roofType == '1070':
        # calculating wall surfaces
        for i in range(len(gS_list) - 1):
            name = 'Outer Wall ' + str(i+1)
            wall = [gS_list[i] + [surfaceHeight], gS_list[i+1] + [surfaceHeight], gS_list[i+1] + [sH_pWall], gS_list[i] + [sH_pWall]]
            wall.append(wall[0])
            wall_dict[name]= wall
        
        # calculating roof surface
        roof_center = TWOd.calc_center(gS_list[0:-1])

        for i in range(len(gS_list)-1):
            name = 'Roof ' + str(i+1)
            roof = [gS_list[i] + [sH_pWall], gS_list[i+1] + [sH_pWall], roof_center + [sH_pHouse]]
            roof.append(roof[0])
            roof_dict[name]= roof


    else:
        print('got unexpected roofType code "' + roofType + '" for roof calculation.\nABORTING!')
        return

    
    gf.windowTitle(self, 'writing building file')
    newFile, newNSmap = building_writer(self, value_dict["u_GML_ID"], envelope_dict, gS_dict, gS_list, terrainIntersection, wall_dict, roof_dict, roofType, buildingHeight, buildingFunction, storeysAboveGround, storeysBelowGround, value_dict["expoPath"], interpol_name)
    gf.messageBox(self, 'Succes', 'New file was created')

    # check if new file should be combined with existing dataset
    if filenames != None and self.checkB_combine.isChecked():
        combine_withDataset(self, filenames, newFile, [x_center, y_center], newNSmap)







def building_writer(self, u_GML_id, envelope_dict, gS_dict, gS_list, terrainIntersection, wall_dict, roof_dict, roofType, buildingHeight, buildingFunction, storeysAboveGround, storeysBelowGround, exppath, interpol_method):
    """function to write new file containing building"""
    # getting info from search_info
    crs = "urn:adv:crs:ETRS89_UTM32*DE_DHHN2016_NH*GCG2016"
    print('crs:', crs)

    name = 'CityBIT_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    minimum = envelope_dict['lowerCorner']
    maximum = envelope_dict['upperCorner']

    # version of newly created file
    version = 0

    if version == 1:
        nsClass = cl.CGML1
    else:
        nsClass = cl.CGML2


    # creating new namespacemap
    newNSmap = {'core': nsClass.core, 'gen' : nsClass.gen, 'grp' : nsClass.grp, 'app': nsClass.app, 'bldg' : nsClass.bldg, 'gml': nsClass.gml,
                'xal' : nsClass.xal, 'xlink' : nsClass.xlink, 'xsi' : nsClass.xsi}

    # creating new root element
    nroot_E = ET.Element(ET.QName(nsClass.core, 'CityModel'), nsmap= newNSmap)
    
    # creating name element
    name_E = ET.SubElement(nroot_E, ET.QName(nsClass.gml, 'name'), nsmap={'gml': nsClass.gml})
    name_E.text = 'created using the e3D CityBIT'

    # creating gml enevelope
    if crs != '':
        bound_E = ET.SubElement(nroot_E, ET.QName(nsClass.gml, 'boundedBy'))
        envelope = ET.SubElement(bound_E, ET.QName(nsClass.gml, 'Envelope'), srsName= crs)
        try:
            lcorner = ET.SubElement(envelope, ET.QName(nsClass.gml, 'lowerCorner'), srsDimension= str(len(minimum)))
            lcorner.text = ' '.join(map(str, minimum))
            ucorner = ET.SubElement(envelope, ET.QName(nsClass.gml, 'upperCorner'), srsDimension= str(len(maximum)))
            ucorner.text = ' '.join(map(str, maximum))
        except:
            print('error creating bounding box')
    else:
        print('error finding crs')


    # setting gml:id
    if u_GML_id != None:
        gmlID = u_GML_id
    else:
        gmlID = "e3D_CityBIT_" + str(uuid.uuid1())

    """create new building here"""
    cityObjectMember_E = ET.SubElement(nroot_E, ET.QName(nsClass.core, 'cityObjectMember'))
    building_E = ET.SubElement(cityObjectMember_E, ET.QName(nsClass.bldg, 'Building'), attrib={ET.QName(nsClass.gml, 'id'): gmlID})
    
    ET.SubElement(building_E, ET.QName(nsClass.gml, 'description')).text = 'approximation created using the e3D CityBIT - ' + interpol_method

    # building attributes
    ET.SubElement(building_E, ET.QName(nsClass.gml, 'name')).text = gmlID
    
    ET.SubElement(building_E, ET.QName(nsClass.core, 'creationDate')).text = str(date.today())
    
    if terrainIntersection == {}:
        ET.SubElement(building_E, ET.QName(nsClass.core, 'relativeToTerrain')).text = 'entirelyAboveTerrain'
    
    measureAttribute_E = ET.SubElement(building_E, ET.QName(nsClass.gen, 'measureAttribute'), attrib={'name': 'GrossPlannedArea'})
    ET.SubElement(measureAttribute_E, ET.QName(nsClass.gen, 'value'), attrib={'uom': "m2"}).text = str(TWOd.AREA(gS_list))
    
    if buildingFunction != '':
        ET.SubElement(building_E, ET.QName(nsClass.bldg, 'buildingFunction')).text = str(buildingFunction)
        
    # bldg:yearOfConstruction
    
    ET.SubElement(building_E, ET.QName(nsClass.bldg, 'roofType'), attrib={'codeSpace':'http://www.sig3d.org/codelists/citygml/2.0/building/2.0/_AbstractBuilding_roofType.xml'}).text = str(roofType)
    
    ET.SubElement(building_E, ET.QName(nsClass.bldg, 'measuredHeight'), attrib={'uom': "m"}).text = str(buildingHeight)
    
    if storeysAboveGround != '' and storeysAboveGround != False:
        ET.SubElement(building_E, ET.QName(nsClass.bldg, 'storeysAboveGround')).text = str(storeysAboveGround)
        
    if storeysBelowGround != '' and storeysBelowGround != False:
        ET.SubElement(building_E, ET.QName(nsClass.bldg, 'storeysBelowGround')).text = str(storeysBelowGround)


    # declaring surfaces
    lodnSolid_E = ET.SubElement(building_E, ET.QName(nsClass.bldg, 'lod2Solid'))
    solid_E = ET.SubElement(lodnSolid_E, ET.QName(nsClass.gml, 'Solid'))
    exterior_E = ET.SubElement(solid_E, ET.QName(nsClass.gml, 'exterior'))
    compositeSurface_E = ET.SubElement(exterior_E, ET.QName(nsClass.gml, 'CompositeSurface'))
    
    exteriorSurfaces = [wall_dict, roof_dict, gS_dict]
    polyIDs = []
    n = 0
    UUID = uuid.uuid1()
    for dictionary in exteriorSurfaces:
        for key in dictionary:
            ID = "PolyID" + str(UUID) + '_' + str(n)
            polyIDs.append(ID)
            hashtagedID = '#' + ID
            ET.SubElement(compositeSurface_E, ET.QName(nsClass.gml, 'surfaceMember'), attrib={ET.QName(nsClass.xlink, 'href'): hashtagedID})
            n -=- 1


    # terrainIntersection
    if terrainIntersection != []:
        lod2TerrainIntersection_E = ET.SubElement(building_E, ET.QName(nsClass.bldg, 'lod2TerrainIntersection'))
        multiCurve_E = ET.SubElement(lod2TerrainIntersection_E, ET.QName(nsClass.gml, 'MultiCurve'))
        for i in range(len(terrainIntersection)-1):
            curveMember_E = ET.SubElement(multiCurve_E, ET.QName(nsClass.gml, 'curveMember'))
            lineString_E = ET.SubElement(curveMember_E, ET.QName(nsClass.gml, 'LineString'))
            for k in range(2):
                stringed = [str(j) for j in terrainIntersection[i+k]]
                ET.SubElement(lineString_E, ET.QName(nsClass.gml, 'pos')).text = ' '.join(stringed)#, attrib={"srsDimension": '"3"'})


    # for keeping track of used IDs
    m = 0
    for i in range(len(exteriorSurfaces)):
        if i == 0:
            surfaceType = 'WallSurface'
        elif i == 1:
            surfaceType = 'RoofSurface'
        elif i == 2:
            surfaceType = 'GroundSurface'

        for key in exteriorSurfaces[i]:
            # creating elements for surfaces
            boundedBy_E = ET.SubElement(building_E, ET.QName(nsClass.bldg, 'boundedBy'))
            wallSurfaceID = "GML_" + str(uuid.uuid1())
            wallRoofGround_E = ET.SubElement(boundedBy_E, ET.QName(nsClass.bldg, surfaceType), attrib={ET.QName(nsClass.gml, 'id'): wallSurfaceID})
            ET.SubElement(wallRoofGround_E, ET.QName(nsClass.gml, 'name')).text = key
            lodnMultisurface_E = ET.SubElement(wallRoofGround_E, ET.QName(nsClass.bldg, 'lod2MultiSurface'))
            multiSurface_E = ET.SubElement(lodnMultisurface_E, ET.QName(nsClass.gml, 'MultiSurface'))
            surfaceMember_E = ET.SubElement(multiSurface_E, ET.QName(nsClass.gml, 'surfaceMember'))
            polyID = polyIDs[m]
            m -=- 1
            polygon_E = ET.SubElement(surfaceMember_E, ET.QName(nsClass.gml, 'Polygon'), attrib={ET.QName(nsClass.gml, 'id'): polyID})
            exterior_E = ET.SubElement(polygon_E, ET.QName(nsClass.gml, 'exterior'))
            ring_id = polyID + '_0'
            linearRing_E = ET.SubElement(exterior_E, ET.QName(nsClass.gml, 'LinearRing'), attrib={ET.QName(nsClass.gml, 'id'): ring_id})
            for point in exteriorSurfaces[i][key]:
                # converting floats to string to join
                stringed = [str(j) for j in point]
                ET.SubElement(linearRing_E, ET.QName(nsClass.gml, 'pos')).text = ' '.join(stringed)

    tree = ET.ElementTree(nroot_E)    

    # writing file
    print('writing file')
    print(os.path.join(exppath, name + ".gml"))
    tree.write(os.path.join(exppath, name + ".gml"), pretty_print = True, xml_declaration=True, 
                encoding='utf-8', standalone='yes', method="xml")
    
    print('created new CityGML file')
    return os.path.join(exppath, name + ".gml"), newNSmap




def collision_check(coor, filenames):
    """checks if coor(dinates) collide with buildings in filenames"""
    border = mplP.Path(np.array(coor))
    
    collision = False
    element_id = ''         # ID of overlapped building
    element_file = ''       # filename of overlapped building
    
    for filename in filenames:
        tree = ET.parse(filename)
        root = tree.getroot()
        namespace = root.nsmap

        x1 = False                              
        y1 = False
        x2 = False
        y2 = False
        fcheck = True

        envelope_E = root.find('./gml:boundedBy/gml:Envelope', namespace)
        if envelope_E != None:
            try:
                # srs = envelope.attrib['srsName'] currently not needed
                lowerCorner = envelope_E.find('./gml:lowerCorner', namespace).text.split(' ')
                x1 = float(lowerCorner[0])
                y1 = float(lowerCorner[1])
                upperCorner = envelope_E.find('./gml:upperCorner', namespace).text.split(' ')
                x2 = float(upperCorner[0])
                y2 = float(upperCorner[1])
            except:
                print('error within gml:envelope in file: ', filename)
        if x1 and x2 and y1 and y2:                                         # checking if all coordinates are present
            fcoor = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
            fcheck = CC.border_check(border, coor, fcoor)

        if fcheck == True:
            buildings_in_file = root.findall('core:cityObjectMember/bldg:Building', namespace)      # gets buildings within file
            for building_E in buildings_in_file:
                collision = CC.check_element(building_E, namespace, border, coor)
                if collision == False:
                    BPs_in_bldg = building_E.findall('./bldg:consistsOfBuildingPart', namespace)
                    for BP_E in BPs_in_bldg:
                        collision = CC.check_element(BP_E, namespace, border, coor)
                        if collision == False:
                            # no collision yet
                            pass
                        else:
                            # breaking from buildingPart loop
                            element_id = BP_E.attrib['{http://www.opengis.net/gml}id']
                            element_file = filename
                            print('building collides with another buildingPart')        
                            break

                else:
                    # breaking from building loop
                    element_id = building_E.attrib['{http://www.opengis.net/gml}id']
                    element_file = filename
                    print('building collides with another building')
                    break

            if collision == True:
                # breaking from filename loop
                break
    
    return collision, element_file, element_id




def combine_withDataset(self, filenames, newfile, center, newNSmap):
    """func for writing new CityGML file from list of buildings and files"""
    print("trying to merge new building with existing file")

    if len(filenames) > 0:

        # suffix of new file
        suffix = '_e3D_CityBIT_combined'

        # buildings for new file
        listOfBuildings = []
        # crs and minimum and maximum coordinates of created file
        crs = ''
        minimum = [math.inf, math.inf, math.inf]
        maximum = [-math.inf, -math.inf, -math.inf]
        nsClass = cl.CGML2

        for i, filename in enumerate(filenames):
            # parsing file, getting root and namespace map
            tree = ET.parse(filename)
            root = tree.getroot()
            nss = root.nsmap

            # search CityGML envelope
            # check if envelope contains the center of the new building
            envelope_E = root.find('.//gml:Envelope', namespaces= nss)
            if envelope_E != None:

                # getting bounding coordinates
                minimum = [math.inf, math.inf, math.inf]
                maximum = [-math.inf, -math.inf, -math.inf]
                try:
                    lowerCorner = envelope_E.find('./gml:lowerCorner', nss).text.split(' ')
                    for i, coor in enumerate(lowerCorner):
                        if float(coor) < minimum[i]:
                            minimum[i] = float(coor)
                    upperCorner = envelope_E.find('./gml:upperCorner', nss).text.split(' ')
                    for i, coor in enumerate(upperCorner):
                        if float(coor) > maximum[i]:
                            maximum[i] = float(coor)
                except:
                    print('error within gml:envelope in file: ', filename, " can't get values of envelope")
                    continue

                if minimum[0] <= center[0] and center[0] <= maximum[0] and minimum[1] <= center[1] and center[1] <= maximum[1]:
                    print(filename, ' is suitable for merging files')
                    crs = envelope_E.attrib['srsName']
                    cityObjectMembers = root.findall('core:cityObjectMember', namespaces=nss)
                    for cityObjectMember_E in cityObjectMembers:
                        listOfBuildings.append(cityObjectMember_E)
                    newName = os.path.splitext(os.path.basename(filename))[0] + suffix
                    break
                else:
                    continue

                
            else:
                print('error finding envelope in file ', filename)

        # checking if suitable file has been found
        try:
            newName
        except:
            gf.messageBox(self, 'Error', 'No matching file found to insert new building')
            return

        # getting building from new file
        tree = ET.parse(newfile)
        root = tree.getroot()
        nss = root.nsmap
        cityObjectMembers = root.findall('core:cityObjectMember', namespaces=nss)
        for cityObjectMember_E in cityObjectMembers:
            listOfBuildings.append(cityObjectMember_E)


        # creating new root element
        nroot = ET.Element(ET.QName(nsClass.core, 'CityModel'), nsmap= newNSmap)
        
        # creating name element
        name_E = ET.SubElement(nroot, ET.QName(nsClass.gml, 'name'), nsmap={'gml': nsClass.gml})
        name_E.text = 'created by the CGML-ATB of the e3D'

        # creating gml enevelope
        if crs != '':
            bound = ET.SubElement(nroot, ET.QName(nsClass.gml, 'boundedBy'))
            envelope = ET.SubElement(bound, ET.QName(nsClass.gml, 'Envelope'), srsName= crs)
            if all([x != math.inf for x in minimum]) and all([x != -math.inf for x in maximum]):
                lcorner = ET.SubElement(envelope, ET.QName(nsClass.gml, 'lowerCorner'), srsDimension= str(len(minimum)))
                lcorner.text = ' '.join(map(str, minimum))
                ucorner = ET.SubElement(envelope, ET.QName(nsClass.gml, 'upperCorner'), srsDimension= str(len(maximum)))
                ucorner.text = ' '.join(map(str, maximum))
            else:
                print('error finding necessary coordinates for bounding box')
        else:
            print('error no SRS found for new file')
            return

        # appending buildings to new root
        for building in listOfBuildings:
            string = ET.tostring(building)
            elemento = ET.fromstring(string)
            nroot.insert(nroot.index(name_E)+2, elemento)
            building.tail = None

        # creating tree from elements
        tree = ET.ElementTree(nroot)
        
        # setting export path
        exp_path = os.path.dirname(newfile)

        # writing file
        print('writing combined file')
        tree.write(os.path.join(exp_path, newName + ".gml"), pretty_print = True, xml_declaration=True, 
                    encoding='utf-8', standalone='yes', method="xml")

        print('combining complete! combined file is: ', os.path.join(exp_path, newName + ".gml"))
        msg = 'Successfully merged ' + os.path.basename(filename) + ' with new building!'
        gf.messageBox(self, 'Success', msg)
        return
    else:
        print('Error! The dataset folder is empty')
        return 
