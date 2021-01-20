# import of libraries
import glob
import os
import lxml.etree as ET
import math
import numpy as np
import pandas as pd
import matplotlib.path as mplP


import vari as va
import TWOd_operations as TWOd
import coordiante_check as CC
import string_manipulation as sm

# possible selection methods
# all
# by coordinate
# by number of buildings
# by radius




def check_building(building_E, namespace, selCor_path, selCor_list):
    """func checking if building needs to be considered for interpolation"""
    if CC.check_element(building_E, namespace, selCor_path, selCor_list):
        # groundSurface of builiding is within the selected coordinates
        return True
    else:
        # checking if buildingParts are within selected coordinates
        bps_in_bldg = building_E.findall('./bldg:consistsOfBuildingPart', namespace)
        for co_bp_E in bps_in_bldg:
            bp_E = co_bp_E.find('bldg:BuildingPart', namespace)
            if CC.check_element(bp_E, namespace, selCor_path, selCor_list):
                # groundSurface of builidingPart is within the selected coordinates
                return True
            else:
                pass
    
    return False



def roof_min_max(building_E, namespace):
    """function returning the highest and lowest point of a roof"""
    maximum_R = 0
    minimum_R = math.inf
    all_polygons = []
    
    roofSurfaces = building_E.findall('bldg:boundedBy/bldg:RoofSurface', namespace)
    
    for roofSurface_E in roofSurfaces:
        polygon_E = roofSurface_E.find('.//gml:Polygon',namespace)
        posList_E = polygon_E.find('.//gml:posList', namespace)
        if posList_E != None:
            polyStr = posList_E.text
            polygon = polyStr.split(' ')
        else:
            pos_Es = polygon_E.findall('.//gml:pos', namespace)
            polygon = []
            for pos_E in pos_Es:
                polygon.extend(pos_E.text.split(' '))
        all_polygons.append(polygon)
        z_coorSTR = polygon[2::3]
        z_coorFLT = [float(z) for z in z_coorSTR]
        maximum_R = max(maximum_R, max(z_coorFLT))
        minimum_R = min(minimum_R, min(z_coorFLT))
    
    # if valid maximum and miniumum has been found
    if maximum_R != 0 and minimum_R != math.inf:
        return maximum_R, minimum_R, all_polygons
    else:
        # values are not valid, returning None
        return None, None, all_polygons




def get_info_from_building(building_E, namespace, center_oI, radius, inter_dict, terrainRadius, parent= None, ALKIS= False):
    """function collecting needed interpolation data from building_E or bp_E"""
    # getting coordinates of groundSurface of the building
    groundSurface_coor = get_groundSurface_coor(building_E, namespace)
    if groundSurface_coor == '':
        # no geometry found -> skipping building
        return []
    else:
        pass
    data = [groundSurface_coor]

    # calculate center
    center = TWOd.calc_center(groundSurface_coor)

    # checking if selection radius is present
    if radius != None:
        if TWOd.distance(center, center_oI) <= radius:
            # building center is within radius
            pass
        else:
            # building radius is outside of radius
            return []

    data.append(center[0])
    data.append(center[1])
    # calculate area
    area = TWOd.AREA(groundSurface_coor)
    data.append(area)
    # getting minimum elevation of building
    minimum_B = min([i[2] for i in data[0]])
    data.append(minimum_B)




    # creating an surrounding rectangle from which we take the side to side ratio to

    coor_2d = [[i[0], i[1]] for i in groundSurface_coor]
    mbr_info = minBoundingRect(coor_2d)
    long_side = max(mbr_info[2], mbr_info[3])
    short_side = min(mbr_info[2], mbr_info[3])
    data.append(long_side / short_side)

    pp = mbr_info[5]

    # calculate center
    cent = mbr_info[4]
    # sort by polar angle
    pp.sort(key=lambda p: math.atan2(p[1]-cent[1], p[0]-cent[0]))

    maximum_d = 0

    for i in range(2):
        distance = TWOd.distance(pp[i], pp[i+1])
        if distance > maximum_d:
            dx = (pp[i+1][0] - pp[i][0]) / distance
            dy = (pp[i+1][1] - pp[i][1]) / distance


    # heading of longest side
    data.append(dx)
    data.append(dy)


    # getting bldg:lod2TerrainIntersection here
    if inter_dict["terrainIntersection"]:
        # calculating distance between centers of buildings to check if terrain intersection of this building is to be considered
        if TWOd.distance(center, center_oI) < terrainRadius:
            data.append(get_terrain_intersection(building_E, namespace))
        else:
            # building is to far away, not considering it's terrainIntersection
            data.append([])
    else:
        # building intersection not needed
        pass


    # default values for roof
    maximum_R = None
    minimum_R = None
    roof_surfaces = []



    # getting buildingHeight
    if inter_dict["bHeight"]:
        measuredHeight_E = building_E.find('bldg:measuredHeight', namespace)
        if measuredHeight_E != None:
            data.append(float(measuredHeight_E.text))
        else:
            # need to get measuredHeight from coordinates
            maximum_R, minimum_R, roof_surfaces = roof_min_max(building_E, namespace)
            if maximum_R != None and minimum_B != None:
                data.append(float(maximum_R - minimum_B))
            else:
                data.append('buildingH_ND')

    else:
        # buildingHeight not needed
        pass

    
    # getting roofHeight
    if inter_dict["rHeight"]:
        # getting minimum and maximum height of building
        if maximum_R == None or minimum_R == None:
            maximum_R, minimum_R, roof_surfaces = roof_min_max(building_E, namespace)
        else:
            # minimum and maximum height are already present
            pass
        if maximum_R != None and minimum_R != None:
            data.append(round(maximum_R - minimum_R, 3))
        else:
            data.append('roofH_N/D')
    else:
        # roofHeight not needed
        pass


    # getting roofType
    roofType_value = 0
    if inter_dict["rType"] or inter_dict["rHeading"]:
        roofType_E = building_E.find('bldg:roofType', namespace)
        if roofType_E != None:
            roofType_value = roofType_E.text
            if ALKIS:
                # transfering ALKIS roofType to CityGML roofType
                roofType_value = va.roofType_ALKIS_to_CityGML[roofType_value]
            else:
                # taking roofType as it is
                pass
        else:
            pass
    else:
        # roofType not needed
        pass
    
    # passing roofType to dataFrame
    if inter_dict["rType"]:
        if roofType_value:
            data.append(roofType_value)
        else:
            data.append('errorWithRoofType')


    # getting roof Heading
    if inter_dict["rHeading"]:
        if roofType_value:
            if roofType_value == '1000':
                # data.append('fR')
                # data.append('fR')
                data.append('rH_N/D')
                data.append('rH_N/D')
            elif roofType_value == '1040':
                # data.append('hR')
                # data.append('hR')
                data.append('rH_N/D')
                data.append('rH_N/D')
            elif roofType_value == '1070':
                # data.append('pR')
                # data.append('pR')
                data.append('rH_N/D')
                data.append('rH_N/D')
            elif roofType_value == '1010' or roofType_value == '1020' or roofType_value == '1030':
                if roof_surfaces == []:
                    maximum_R, minimum_R, roof_surfaces = roof_min_max(building_E, namespace)
                else:
                    # already got coordinates of roof surface
                    pass
                
                # heading is roofline from highest point to lowest point (steepest angle)

                for roof_surface in roof_surfaces:
                    string = ' '.join(roof_surface)
                    points = sm.get_3dPosList_from_str(string)

                    max_slope = -999

                    for i in range(len(points) - 1):
                        # getting the length of line
                        length = TWOd.distance(points[i][0:2], points[i+1][0:2])
                        slope = abs((points[i][2] - points[i+1][2]) / length)

                        if slope > max_slope:
                            max_slope = slope

                            if points[i][2] > points[i+1][2]:
                                # slope goes from first point to second one
                                rx = (points[i+1][0] - points[i][0]) / length
                                ry = (points[i+1][1] - points[i][1]) / length
                            else:
                                # slope goes from second point to first (or heights are equal)
                                rx = (points[i][0] - points[i+1][0]) / length
                                ry = (points[i][1] - points[i+1][1]) / length

                data.append(rx)
                data.append(ry)



                # old idea
                # # for the first choice
                # max_length = 0
                # heading = 'head_N/D'
                # direction = 'N/D'
                # # for the second choice
                # max_length2 = 0
                # heading2 = 'head_N/D'
                # direction_2 = 'N/D'
                # max_avg_height = 0
                # for roof_surface in roof_surfaces:
                #     string = ' '.join(roof_surface)
                #     points = sm.get_3dPosList_from_str(string)
                #     # getting roation direction
                #     center = TWOd.calc_center(points)
                #     new_direction = TWOd.rotationDirection(center, points[0], points[1])
                #     for i in range(len(points) - 1):
                #         # taking heading from longest roof line
                #         length = TWOd.distance(points[i][0:2], points[i+1][0:2])
                #         if points[i][2] == maximum_R and points[i+1][2] == maximum_R:
                #             # roof line with max height
                #             if length > max_length:
                #                 max_length = length
                #                 heading = TWOd.angle(points[i], points[i+1])
                #                 direction = new_direction
                #         else:
                #             # is not the highest roof line, so only for second choice
                #             avg_height = (points[i][2] + points[i+1][2]) / 2
                #             if avg_height > max_avg_height:
                #                 max_avg_height = avg_height
                #                 max_length2 = length
                #                 heading2 = TWOd.angle(points[i], points[i+1])
                #                 direction_2 = new_direction
                #             elif avg_height == max_avg_height:
                #                 if length > max_length2:
                #                     max_length2 = length
                #                     heading2 = TWOd.angle(points[i], points[i+1])
                #                     direction_2 = new_direction
                #             else:
                #                 # below previous avg roof line -> not considered
                #                 pass

                # if heading == 'head_N/D' and heading2 != 'head_N/D':
                #     heading = heading2
                #     direction = direction_2
                # if heading != 'head_N/D':
                #     if roofType_value == '1010' or roofType_value == '1020':
                #         # need to correct angle
                #         heading = TWOd.correct_angle(heading, direction)
                #     else:
                #         # no need to correct angle
                #         pass
                # data.append(heading)


            else:
                # unsupported roofTypes for heading
                # data.append('uR')
                # data.append('uR')
                data.append('rH_N/D')
                data.append('rH_N/D')
        else:
            data.append('rH_N/D')
            data.append('rH_N/D')
    else:
        # roofHeading is not needed
        pass


    # getting buildingFunction
    if inter_dict["bFunction"]:
        buildingFunction_E = building_E.find('bldg:function', namespace)
        if buildingFunction_E != None:
            buildingFunction_value = buildingFunction_E.text
            if ALKIS:
                # transfering ALKIS buildingFunction to CityGML buildingFuncction
                buildingFunction_value = va.buildingFunction_ALKIS_to_CityGML[buildingFunction_value]
            else:
                # taking buildingFunction as it is
                pass
            data.append(buildingFunction_value)
        else:
            if parent != None:
                # here getting building function of parrent
                buildingFunction_E = parent.find('bldg:function', namespace)
                if buildingFunction_E != None:
                    buildingFunction_value = buildingFunction_E.text
                    if ALKIS:
                        # transfering ALKIS buildingFunction to CityGML buildingFuncction
                        buildingFunction_value = va.buildingFunction_ALKIS_to_CityGML[buildingFunction_value]
                    else:
                        # taking buildingFunction as it is
                        pass
                    data.append(buildingFunction_value)
                else:
                    data.append('bF_N/D')    
            else:
                data.append('bF_N/D')
    else:
        # buildingFunction not needed
        pass


    # getting storeysAboveGround
    if inter_dict["SAG"]:
        SAG_E = building_E.find('bldg:storeysAboveGround', namespace)
        if SAG_E != None:
            data.append(SAG_E.text)
        else:
            data.append('SAG_N/D')
    else:
        # storeysAboveGround not needed
        pass


    # getting storeysBelowGround
    if inter_dict["SBG"]:
        SBG_E = building_E.find('storeysBelowGround', namespace)
        if SBG_E != None:
            data.append(SBG_E.text)
        else:
            data.append('SBG_N/D')
    else:
        # storeysBelowGround not needed
        pass
    

    # returning collected data
    return data



def interpolation_start(filenames, selection, sameAttrib, attribValue, center_oI, selCor_list, radius, inter_dict, terrainRadius):
    """func collecting necessary info for interpolation"""

    # variables
    if selCor_list != None:
        selCor_path = mplP.Path(np.array(selCor_list))



    # creating header for the collected data
    header = ['filename', 'building_id', 'buildingPart_id', 'groundSurface_coordinates', 'X_center', 'Y_center', 'area', 'min_elevation', 'side_ratio', 'long_dxN', 'long_dyN']
    if inter_dict["terrainIntersection"]:
        header.append('intersectionCoor')
    if inter_dict["bHeight"]:
        header.append('buildingHeight')
    if inter_dict["rHeight"]:
        header.append('roofHeight')
    if inter_dict["rType"]:
        header.append('roofType')
    if inter_dict["rHeading"]:
        header.extend(['roof_X', 'roof_Y'])
    if inter_dict["bFunction"]:
        header.append('buildingFunction')
    if inter_dict["SAG"]:
        header.append('storeysAboveGround')
    if inter_dict["SBG"]:
        header.append('storeysBelowGround')

    big_data = []       # holding all information
    small_data = []     # holding weighted area info


    # collecting data from buildings

    for filename in filenames:
        tree = ET.parse(filename)
        root = tree.getroot()
        namespace = root.nsmap
        
        fcheck = True

        # getting envelope
        if selection != 'all':
            # bounding coordinates
            x1 = False                              
            y1 = False
            x2 = False
            y2 = False
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
                fcheck = CC.border_check(selCor_path, selCor_list, fcoor)
        
        else:
            # all files need to be checkded if selection is all
            pass

        # if file should be checked
        if fcheck == True:
            # getting all buildings
            buildings_in_file = root.findall('core:cityObjectMember/bldg:Building', namespace)

            for building_E in buildings_in_file:
                area_info = []
                ALKIS = False

                if selection != 'all':
                    # need to check if building is within selected area
                    success = check_building(building_E, namespace, selCor_path, selCor_list)
                    if success:
                        # going to consider building
                        pass
                    else:
                        # skipping building because building is not within the selected area
                        continue
                else:
                    # selection is all, so building needs to be checked
                    pass


                # here ALKIS check
                externalReference_E = building_E.find('core:externalReference', namespace)
                if externalReference_E != None:
                    informationSystem_E = externalReference_E.find('core:informationSystem', namespace)
                    if informationSystem_E != None:
                        if informationSystem_E.text == 'http://repository.gdi-de.org/schemas/adv/citygml/fdv/art.htm#_9100':
                            # alkis code list is used for this building
                            ALKIS = True


                consider = False
                if sameAttrib == 'buildingFunction':
                    buildingFunc_Es = building_E.findall('.//bldg:function', namespace)
                    if buildingFunc_Es == []:
                        # checking building because of unknown buildingFunction
                        consider = True
                        pass
                    else:
                        for buildingFunc_E in buildingFunc_Es:
                            if ALKIS:
                                if str(attribValue) == str(va.buildingFunction_ALKIS_to_CityGML[buildingFunc_E.text]):
                                    # is the same -> consider building
                                    consider = True
                                    break
                                else:
                                    # is different value -> check other values
                                    continue
                            else:
                                if str(attribValue) == buildingFunc_E.text:
                                    # is the same -> consider building
                                    consider = True
                                    break
                                else:
                                    # is different value -> check other values
                                    continue
                
                elif sameAttrib == 'roofType':
                    roofType_Es = building_E.findall('.//bldg:roofType', namespace)
                    if roofType_Es == []:
                        # checking building because of unkown roofType
                        consider = True
                        pass
                    else:
                        for roofType_E in roofType_Es:
                            if ALKIS:
                                if str(va.roofTypes[attribValue]) == str(va.roofType_ALKIS_to_CityGML[roofType_E.text]):
                                    # is the same -> consider building
                                    consider = True
                                    break
                                else:
                                    # is different value -> check other values
                                    continue
                            else:
                                if str(va.roofTypes[attribValue]) == roofType_E.text:
                                    # is the same -> consider building
                                    consider = True
                                    break
                                else:
                                    # is different value -> check other values
                                    continue
                                    
                else:
                    # no attribute given -> consider
                    consider = True
                
                # checking if building needs to be consideres
                if consider == True:
                    # checking building
                    pass
                else:
                    # skipping building
                    continue


                # list to collect data
                data = [os.path.basename(filename)]

                building_id = building_E.attrib['{http://www.opengis.net/gml}id']
                data.append(building_id)
                data.append('mainBuilding')
                
                # functioncall to get needed info from building
                new_data = get_info_from_building(building_E, namespace, center_oI, radius, inter_dict, terrainRadius, ALKIS=ALKIS)
                
                if new_data != []:
                    data += new_data

                    # add data to dataframe
                    big_data.append(data)

                    if inter_dict["area"]:
                        area_info.append(new_data[1:4])
                else:
                    # skipping building because of missing geometry
                    pass


                # getting groundSurface coordiantes of buildingParts
                bps_in_bldg = building_E.findall('./bldg:consistsOfBuildingPart', namespace)
                for co_bp_E in bps_in_bldg:
                    bp_E = co_bp_E.find('bldg:BuildingPart', namespace)
                    # samestuff what has been for building now for buildingPart
                    data = [os.path.basename(filename)]
                    data.append(building_id)
                    data.append(bp_E.attrib['{http://www.opengis.net/gml}id'])
                    
                    # function call to get needed info from buildingPart
                    new_data = get_info_from_building(bp_E, namespace, center_oI, radius, inter_dict, terrainRadius, parent=building_E, ALKIS=ALKIS)
                    
                    if new_data != []:
                        data += new_data

                        # add data to dataframe
                        big_data.append(data)
                        
                        if inter_dict["area"]:
                            area_info.append(new_data[1:4])
                    else:
                        # skipping buildingPart because of missing geometry
                        pass

                # calculate cumulated area here and new x and y center
                if area_info != []:
                    area_sum = 0
                    x_sum = 0
                    y_sum = 0
                    for i in area_info:
                        area_sum += i[2]
                        x_sum += i[0] * i[2]
                        y_sum += i[1] * i[2]
                    small_data.append([os.path.basename(filename), building_id, x_sum/area_sum, y_sum/area_sum, area_sum])
        
        else:
            # file doesnot need to be checked because of selection criteria (envelope)
            pass

    # interpolating info

    df = pd.DataFrame(big_data, columns= header)

    if inter_dict["area"]:
        df_area = pd.DataFrame(small_data, columns= ['filename', 'building_id', 'X_center', 'Y_center', 'area'])
    else:
        df_area = None

    exp_name = r'dataframe.csv'
    df.to_csv(exp_name, sep='\t', encoding='utf-8', index=False)
    return df, df_area



def get_groundSurface_coor(element, namespace):
    """function for getting coordinates from groundsurface; positions and height"""
    groundSurface_E = element.find('bldg:boundedBy/bldg:GroundSurface', namespace)
    if groundSurface_E != None:
        posList_E = groundSurface_E.find('.//gml:posList', namespace)       # searching for list of coordinates

        if posList_E != None:           # case aachen lod2
            return sm.get_3dPosList_from_str(posList_E.text)
            
        else:                           # case hamburg lod2 2020
            pos_Es = groundSurface_E.findall('.//gml:pos', namespace)
            polygon = []
            for pos_E in pos_Es:
                polygon.append(pos_E.text)
            polyStr = ' '.join(polygon)
            return sm.get_3dPosList_from_str(polyStr)

    
    #  checking if no groundSurface element has been found
    else:               # case for lod1 files
        geometry = element.find('bldg:lod1Solid', namespace)
        if geometry != None:
            poly_Es = geometry.findall('.//gml:Polygon', namespace)
            all_poylgons = []
            for poly_E in poly_Es:
                polygon = []
                posList_E = element.find('.//gml:posList', namespace)       # searching for list of coordinates
                if posList_E != None:
                    polyStr = posList_E.text
                else:
                    pos_Es = poly_E.findall('.//gml:pos', namespace)        # searching for individual coordinates in polygon
                    for pos_E in pos_Es:
                        polygon.append(pos_E.text)
                    polyStr = ' '.join(polygon)
                coor_list = sm.get_3dPosList_from_str(polyStr)
                all_poylgons.append(coor_list)
            
            # to get the groundSurface polygon, the average height of each polygon is calculated and the polygon with the lowest average height is considered the groundsurface
            averages = []
            for polygon in all_poylgons:
                # need to get polygon with lowest z coordinate here
                average = 0
                for i in range(len(polygon)-1):
                    average -=- polygon[i][2]
                averages.append(average/len(polygon)-1)

            return all_poylgons[averages.index(min(averages))]
        else:
            return ''
        


def get_terrain_intersection(element, namespace):
    """function for getting bldg:lod2TerrainIntersection points"""
    coordinates = []

    relativeToTerrain_E = element.find('core:relativeToTerrain', namespace)
    if relativeToTerrain_E != None:
        if relativeToTerrain_E.text == 'entirelyAboveTerrain':
            return 'entirelyAboveTerrain'

        elif relativeToTerrain_E.text == 'entirelyBelowTerrain':
            return 'entirelyBelowTerrain'

        else:
            # still need to check for intersection data
            pass
    else:
        # still need to check for intersection data
        pass

    intersection_E = element.find('bldg:lod2TerrainIntersection', namespace)
    if intersection_E != None:
        # case of gml:posList (e.g. Aachen)
        posList_Es = intersection_E.findall('.//gml:posList', namespace)
        for posList_E in posList_Es:
            # getting the string of coordinates and appending individual points to list of all coordinates
            coordinates.extend(sm.get_3dPosList_from_str(posList_E.text))

        # case of list of gml:pos
        pos_Es = intersection_E.findall('.//gml:pos', namespace)
        for pos_E in pos_Es:
            # get string of element and split it for spaces resulting in a list of strings
            coor_list = pos_E.text.split(' ')
            # looping through list to get list of floats
            coor_list = [float(i) for i in coor_list]
            coordinates.append(coor_list)
        coordinates = [list(t) for t in set(tuple(element) for element in coordinates)]
        return coordinates


    else:
        # could not find TerrainIntersection
        return 'noIntersection'



def interpolate_value(dataframe, X_coor, Y_coor, wanted_value, interpolation_method, cout=True):
    """function to call griddata interpolation and return wanted value for given X_coor and Y_coor"""
    from scipy.interpolate import griddata
    value = float(griddata((dataframe["X_center"], dataframe["Y_center"]), dataframe[wanted_value], (X_coor, Y_coor), method=interpolation_method))
    if cout:
        print(wanted_value)
        print(value)
    return round(value, 2)



def minBoundingRect(hull_points_2d):
    """calculates a minimum surrounding rectangle of a 2d shape"""

    # calculating vectors of each side
    edges = []
    for i in range(len(hull_points_2d) - 1):
        edge_x = hull_points_2d[i+1][0] - hull_points_2d[i][0]
        edge_y = hull_points_2d[i+1][1] - hull_points_2d[i][1]
        edges.append([edge_x,edge_y])


    # calculating angles of each side unsing arctan in radian
    edge_angles = []
    for i in range( len(edges) ):
        edge_angles.append(math.atan2( edges[i][1], edges[i][0] ))


    # getting angles in to the 1st quadrant (0 to 90 deg or 0 to pi/2)
    for i in range( len(edge_angles) ):
        edge_angles[i] = abs( edge_angles[i] % (math.pi/2) )


    # removing duplicates of angles
    edge_angles = np.unique(edge_angles)


    # setting default values
    min_bbox = (0, float("inf"), 0, 0, 0, 0, 0, 0) # rot_angle, area, width, height, min_x, max_x, min_y, max_y


    for i in range( len(edge_angles) ):

        # Create rotation matrix to shift points to baseline
        # theta = edge_angles[i]
        # R = [ cos(theta)      , cos(theta-PI/2)
        #       cos(theta+PI/2) , cos(theta)     ]
        R = np.array([ [ math.cos(edge_angles[i]), math.cos(edge_angles[i]-(math.pi/2)) ], [ math.cos(edge_angles[i]+(math.pi/2)), math.cos(edge_angles[i]) ] ])


        # Apply this rotation to convex hull points
        rot_points = np.dot(R, np.transpose(hull_points_2d) ) # 2x2 * 2xn


        # Find min/max x,y points
        x_min = np.nanmin(rot_points[0], axis=0)
        x_max = np.nanmax(rot_points[0], axis=0)
        y_min = np.nanmin(rot_points[1], axis=0)
        y_max = np.nanmax(rot_points[1], axis=0)


        # calculating min
        width = x_max - x_min
        height = y_max - y_min
        area = width * height


        # Store the smallest rect found first (a simple convex hull might have 2 answers with same area)
        if (area < min_bbox[1]):
            min_bbox = ( edge_angles[i], area, width, height, x_min, x_max, y_min, y_max )
            R_small = R


    # min/max x,y points are against baseline
    x_min = min_bbox[4]
    x_max = min_bbox[5]
    y_min = min_bbox[6]
    y_max = min_bbox[7]


    # Calculate center point and project onto rotated frame
    center_x = (x_min + x_max)/2
    center_y = (y_min + y_max)/2
    center_point = np.dot( [ center_x, center_y ], R_small ).tolist()


    # Calculate corner points and project onto rotated frame
    corner_points = [] 
    corner_points.append(np.dot( [ x_max, y_min ], R_small ).tolist())
    corner_points.append(np.dot( [ x_min, y_min ], R_small ).tolist())
    corner_points.append(np.dot( [ x_min, y_max ], R_small ).tolist())
    corner_points.append(np.dot( [ x_max, y_max ], R_small ).tolist())


    return (min_bbox[0], min_bbox[1], min_bbox[2], min_bbox[3], center_point, corner_points) # rot_angle, area, width, height, center_point, corner_points



def interpolate_categroy(df, category, x_center, y_center, interpol_method, posRes=[]):
    """used for interpolating categories like roofType or building function"""
    unsorted = df[category].tolist()
    sorted_list = list(set(unsorted))
    sorted_list.sort()  # list of additional categories

    # creating truthmatrix for present values of categories
    new_header = ['filename', 'building_id', 'buildingPart_id', 'X_center', 'Y_center'] + sorted_list
    new_list = []
    for index, row in df.iterrows():
        new_row = [row["filename"], row["building_id"], row["buildingPart_id"], row["X_center"], row["Y_center"]]
        for i in sorted_list:
            new_row.append(int(row[category] == i))
        new_list.append(new_row)

    # creating new dataframe
    df_cate = pd.DataFrame(new_list, columns= new_header)
    df_cate.to_csv('category.csv', sep='\t', encoding='utf-8', index=False)

    
    highest = 0 
    index = -1
    for i, value in enumerate(sorted_list):
        # checking if the possible results are limited
        if posRes != []:
            # checking if value is in possible results
            if value in posRes:
                pass
            else:
                # skipping value because it is not in the possible results
                continue
        prob = interpolate_value(df_cate, x_center, y_center, value, interpol_method)
        if prob > highest:
            highest = prob
            index = i
    if index != -1:
        print('interpolated:\t', sorted_list[index])
        return sorted_list[index]
    else:
        print('ERROR interpolating', category,'\nreturning 1000')
        return '1000'