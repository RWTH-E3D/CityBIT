# import of libraries
import matplotlib.path as mplP
import numpy as np
import lxml.etree as ET



import string_manipulation as sm



def border_check(border, list_of_border, list_of_coordinates):
    """ checks for area vice verca"""
    for point in list_of_coordinates:
        if border.contains_point(point):
            return True
    n_border = mplP.Path(np.array(list_of_coordinates))
    for point in list_of_border:
        if n_border.contains_point(point):
            return True
    return False



def check_element(element, namespace, selCor_path, selCor_list):
    """function checking groundSurface if building/buildingPart needs to be checked for interpolation"""

    groundSurface_E = element.find('./bldg:boundedBy/bldg:GroundSurface', namespace)
    if groundSurface_E != None:
        posList_E = groundSurface_E.find('.//gml:posList', namespace)       # searching for list of coordinates
        
        if posList_E != None:           # case aachen lod2
            coor_list = sm.get_2dPosList_from_str(posList_E.text)
            result = border_check(selCor_path, selCor_list, coor_list)
            
        else:           # case hamburg lod2 2020
            pos_Es = groundSurface_E.findall('.//gml:pos', namespace)
            polygon = []
            for pos_E in pos_Es:
                polygon.append(pos_E.text)
            polyStr = ' '.join(polygon)
            coor_list = sm.get_2dPosList_from_str(polyStr)
            result = border_check(selCor_path, selCor_list, coor_list)

        if result:
            # groundSurface of building is in the selected area -> building is considered
            return True
        else:
            # groundSurface of building is not in the selected area -> checking if there are buildingParts
            pass
    
    #  checking if no groundSurface element has been found
    else:               # case for lod1 files 
        poly_Es = element.findall('.//gml:Polygon', namespace)
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
            coor_list = sm.get_2dPosList_from_str(polyStr)
            all_poylgons.append(coor_list)
        for polygon in all_poylgons:
            result = border_check(selCor_path, selCor_list, polygon)
            if result:
                return True
    
    return False