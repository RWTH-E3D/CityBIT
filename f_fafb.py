import numpy as np
import os
import matplotlib.path as mpl
import math
import lxml.etree as ET


import interpolation_functions as inter_f
import vari as va




def stretch_poly(oCoor, x, y, scale):
    """to stretch a polygon by given factor, x and y presenting center around which the poly is steched"""
    stretched = []
    [stretched.append(((scale * (p[0] - x)) + x, (scale * (p[1] - y)) + y)) for p in oCoor]
    return stretched


def AREA(oCoor):
    """calculates the area of polygon (input as 1D array of tuples)"""
    x = [i[0]for i in oCoor]
    y = [i[1]for i in oCoor]
    return 0.5*np.abs(np.dot(x, np.roll(y, 1))-np.dot(y, np.roll(x, 1)))




def noB_interpol(filenames, noB_shall, p_old, sameAttrib, attribValue):
    """interpolating new coordinates for new scaled area"""
    # calculating center of mass based on mode
    x_old = [i[0]for i in p_old]
    y_old = [i[1]for i in p_old]

    x_mid = sum(x_old) / len(x_old)
    y_mid = sum(y_old) / len(y_old)


    # setting lower bound for interpolation
    s_low = 0
    b_low = 0
    # setting upper bound for interpolation
    s_high = 1000
    b_high = math.inf

    b_cur = coordinates(filenames, p_old, sameAttrib, attribValue)
    print('buildings currently:\t', b_cur)

    if b_cur > noB_shall:
        s_high = 1
        b_high = b_cur
    elif b_cur < noB_shall:
        s_low = 1
        b_low = b_cur


    i = 0                                                           # counter
    max_runs = 1000                                                # max number of runs
    if b_cur != noB_shall:
        for i in range(max_runs):
            if b_low < noB_shall < b_high:                                # checking if areas are suitable for interpolation
                s_new = (s_high+s_low)*0.5                              # calculating new scale
                new_coor = stretch_poly(p_old, x_mid, y_mid, s_new)
                b_new = coordinates(filenames, new_coor, sameAttrib, attribValue)  # calculating new area
                if b_new == noB_shall:                                    # break condition for exact match
                    break
                elif b_new > noB_shall:                                   # setting new higher bound
                    b_high = b_new
                    s_high = s_new
                elif b_new < noB_shall:                                   # setting new lower bound
                    b_low = b_new
                    s_low = s_new
                else:
                    print('error with new area')
            else:
                print('error while searching for interpolation bounds')
                return ['error with interpolation bounds']
            i -=- 1
            if (i + 1) * 10  % max_runs == 0:
                print('number of interpolations:\t', i)
                print('buildings currently:\t', b_new)
                # print('scale\t', s_new)
                # print('nCoor\t', new_coor)
                print('\n\n')
        p_new = stretch_poly(p_old, x_mid, y_mid, s_new)
        print('buildings after loop:\t', b_new)
        print('after', i, 'runs')
        return p_new
    else:
        print('area is already fine')
        return p_old




def border_check(border, list_of_border, list_of_coordinates):
    """ checks for area vice verca"""
    for point in list_of_coordinates:
        if border.contains_point(point):
            return True
    n_border = mpl.Path(np.array(list_of_coordinates))
    for point in list_of_border:
        if n_border.contains_point(point):
            return True
    return False




def coordinates(filenames, list_pol, sameAttrib, attribValue):
    """searching for area of list_pol in fileNames"""
    border = mpl.Path(np.array(list_pol))


    numberOfBuildings = 0

    for filex in filenames:
        fcheck = True
        # bounding coordinates
        x1 = False                              
        y1 = False
        x2 = False
        y2 = False

        tree = ET.parse(filex)
        root = tree.getroot()
        namespace = root.nsmap
        # searching for envelope
        envelope_E = root.find('./gml:boundedBy/gml:Envelope', namespace)
        

        if envelope_E != None:
            try:
                lowerCorner = envelope_E.find('./gml:lowerCorner', namespace).text.split(' ')
                x1 = float(lowerCorner[0])
                y1 = float(lowerCorner[1])
                upperCorner = envelope_E.find('./gml:upperCorner', namespace).text.split(' ')
                x2 = float(upperCorner[0])
                y2 = float(upperCorner[1])
            except:
                print('error within gml:envelope in file: ', filex)
        if x1 and x2 and y1 and y2:                                         # checking if all coordinates are present
            fcoor = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
            fcheck = border_check(border, list_pol, fcoor)
        
        if fcheck:
            buildings_in_file = root.findall('core:cityObjectMember/bldg:Building', namespace)

            for building_E in buildings_in_file:
                
                # here ALKIS check
                ALKIS = False
                externalReference_E = building_E.find('core:externalReference', namespace)
                if externalReference_E != None:
                    informationSystem_E = externalReference_E.find('core:informationSystem', namespace)
                    if informationSystem_E != None:
                        if informationSystem_E.text == 'http://repository.gdi-de.org/schemas/adv/citygml/fdv/art.htm#_9100':
                            # alkis code list is used for this building
                            ALKIS = True

                attribCheck = False
                if sameAttrib != None:
                    if sameAttrib == 'roofType':
                        searched_Es = building_E.findall('.//bldg:roofType', namespace)
                        dicti = va.roofType_ALKIS_to_CityGML
                    elif sameAttrib == 'buildingFunction':
                        searched_Es = building_E.findall('.//bldg:function', namespace)
                        dicti = va.buildingFunction_ALKIS_to_CityGML
                    else:
                        print('unknown sameAttrib in f_fafby.py')

                    for searched_E in searched_Es:
                        if ALKIS:
                            if sameAttrib == 'roofType':
                                if dicti[searched_E.text] == str(va.roofTypes[attribValue]):
                                    attribCheck = True
                                    break
                            else:
                                if dicti[searched_E.text] == str(attribValue):
                                    attribCheck = True
                                    break
                        else:
                            if searched_E.text == attribValue:
                                attribCheck = True
                                break
                else:
                    attribCheck = True

                if attribCheck:
                    pass
                else:
                    # attribCheck failed -> not considering building
                    continue

                res = inter_f.check_building(building_E, namespace, border, list_pol)
                if res:
                    numberOfBuildings -=- 1
        
        
    return numberOfBuildings




def fafnoB(filenames, center, N, sameAttrib, attribValue):
    """function to find a circle like area containing N buildings"""
    radius = 1
    x1 = 0                              # default
    y1 = radius                         # default
    noC = 8                             # number of corner points of area - noC >= 3
    
    # getting corner points 
    corners = []
    for i in range(noC):
        a = (math.pi *2) / noC * i
        x = round(x1 * math.cos(a) - y1 * math.sin(a) + center [0], 5)
        y = round(x1 * math.sin(a) + y1 * math.cos(a) + center [1], 5)
        corners.append((x, y))

    return noB_interpol(filenames, N, corners, sameAttrib, attribValue)
