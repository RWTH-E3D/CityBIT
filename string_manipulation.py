def get_2dPosList_from_str(text):
    """function to convert string to a list of coordinates"""
    coor_list = [float(x) for x in text.split()]
    # del coor_list[2::3]                                                     # deleting height from list of coordinates
    coor_list = [ list(x) for x in zip(coor_list[0::3], coor_list[1::3])]   # creating 2d coordinate array from 1d array
    return coor_list



def get_3dPosList_from_str(text):
    coor_list = [float(x) for x in text.split()]
    coor_list = [list(x) for x in zip(coor_list[0::3], coor_list[1::3], coor_list[2::3])]  # creating 2d coordinate array from 1d array
    return coor_list