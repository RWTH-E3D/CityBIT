def get_2dPosList_from_str(text):
    """convert string to a 2D list of coordinates"""
    coor_list = [float(x) for x in text.split()]
    coor_list = [ list(x) for x in zip(coor_list[0::3], coor_list[1::3])]   # creating 2D coordinate array from 1D array
    return coor_list



def get_3dPosList_from_str(text):
    """convert string to a 3D list of coordinates"""
    coor_list = [float(x) for x in text.split()]
    coor_list = [list(x) for x in zip(coor_list[0::3], coor_list[1::3], coor_list[2::3])]  # creating 3D coordinate array from 1D array
    return coor_list