"""
The City-BuildingInterpolationTool (CityBIT) was developed as part of the bachelor thesis of Simon Raming at the "Institute of Energy Efficiency and Sustainable Building (e3D), RWTH Aachen University" under the supervision of Avichal Malhotra. 
This tool was developed for Python 3.5+ using PySide2. A detailed list of the required libraries can be found in the readme.

Contact:
Simon Raming:           simon.raming@rwth-aachen.de
M.Sc. Avichal Malhotra: malhotra@e3d.rwth-aachen.de
"""


# import of libraries
import os
import sys
import PySide2
from PySide2 import QtWidgets, QtGui, QtCore

# import of functions
import gui_functions as gf
import cbit_functions as cbit_f
import vari as va
import window0 as w0
import window1 as w1
import window2 as w2


# setting system environment variable
dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path



# positions and dimensions of window
posx = 275
posy = 100
width = 800
height = 800
sizefactor = 0
sizer = True

# path of script
pypath = os.path.dirname(os.path.realpath(__file__))

# global variables
value_dict = {"iCRS": None, "oCRS": None, "cList": None, "xCen": None, "yCen": None, "xCenOrig": None, "yCenOrig": None, "groundSurface": None, "area": None, "sideRatio": None, "bHeading": None, "sHeight": None, "bHeight": None, "rHeight": None, "rType": None, "rHeading": None, "bFunction": None, "terrainIntersection": None, "SAG": None, "SBG": None, "u_GML_ID": None, "dataPath": None, "interMethod": None, "sameAttrib": None, "selectBy": None, "expoPath": None, "bList": None, "noB": None, "radius": None}
inter_dict = {"groundSurface": True, "area": True, "sideRatio": True, "bHeading": True, "sHeight": True, "bHeight": True, "rHeight": True, "rType": True, "rHeading": True, "bFunction": True, "terrainIntersection": True, "SAG": True, "SBG": True}

# border of selected CRS
x_min = 0
x_max = 0
y_min = 0
y_max = 0




class mainWindow(QtWidgets.QWidget):
    """mainWindow class"""
    def __init__(self):
        #initiate the parent
        super(mainWindow,self).__init__()
        self.initUI()


    def initUI(self):
        global posx, posy, width, height, sizefactor, sizer, value_dict

        # setup of gui / layout
        if sizer:
            posx, posy, width, height, sizefactor = gf.screenSizer(self, posx, posy, width, height, app)
            sizer = False
        gf.windowSetup(self, posx, posy, width, height, pypath, 'CityBIT - CityGML Building Interpolation Tool')

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        gf.load_banner(self, os.path.join(pypath, r'pictures\e3dHeader.png'), sizefactor)

        self.uGrid = QtWidgets.QGridLayout()

        self.lbl_iCRS = QtWidgets.QLabel('Input CRS:')
        self.uGrid.addWidget(self.lbl_iCRS, 0, 0, 1, 1)

        self.txtB_iCRS = QtWidgets.QLineEdit()
        self.txtB_iCRS.setPlaceholderText('EPSG code')
        self.txtB_iCRS.setToolTip('Coordinate reference system in which the coordinates are entered\ncan be left empty if input CRS = output CRS')
        self.uGrid.addWidget(self.txtB_iCRS, 0, 1, 1, 1)

        self.lbl_oCRS = QtWidgets.QLabel('Output CRS:')
        self.uGrid.addWidget(self.lbl_oCRS, 0, 2, 1, 1)

        self.txtB_oCRS = QtWidgets.QLineEdit()
        self.txtB_oCRS.setPlaceholderText('EPSG code')
        self.txtB_oCRS.setToolTip('Coordiante reference system in which the CityGML file should be created')
        self.uGrid.addWidget(self.txtB_oCRS, 0, 3, 1, 1)

        self.txtB_checCRS = QtWidgets.QLineEdit('')
        self.uGrid.addWidget(self.txtB_checCRS, 0, 4, 1, 1)

        self.btn_checkCRS = QtWidgets.QPushButton('Check CRS')
        self.btn_checkCRS.setToolTip('Checks if the entered CRSs are present in the database')
        self.uGrid.addWidget(self.btn_checkCRS, 0, 4, 1, 1)

        self.vbox.addLayout(self.uGrid)


        self.gB_groundSurface = QtWidgets.QGroupBox('Ground surface')
        self.vbox.addWidget(self.gB_groundSurface)

        self.gS_grid = QtWidgets.QGridLayout()
        self.gB_groundSurface.setLayout(self.gS_grid)

        self.rB_center = QtWidgets.QRadioButton('Enter center of area')
        self.rB_center.setToolTip('Base plate will be an interpolated rectangle with the entered center point')
        self.gS_grid.addWidget(self.rB_center, 0, 0, 1, 1)
        self.rB_center.setChecked(True)

        self.rB_list = QtWidgets.QRadioButton('Enter list of corner points')
        self.rB_list.setToolTip('Base plate will be created with the entered corner points')
        self.gS_grid.addWidget(self.rB_list, 0, 1, 1, 1)

        self.btn_loadCSV = QtWidgets.QPushButton('Load .csv')
        self.btn_loadCSV.setToolTip('Load coordinates from .csv file\nSee example.csv for syntax')
        self.gS_grid.addWidget(self.btn_loadCSV, 0, 3, 1, 1)

        self.btn_sqrRec = QtWidgets.QPushButton('Square/Rectangle')
        self.btn_sqrRec.setToolTip('Creates a square if two points are entered\nCreates a rectangle if three points are entered')
        self.gS_grid.addWidget(self.btn_sqrRec, 0, 4, 1, 1)
        self.btn_sqrRec.setEnabled(False)
        
        self.lbl_xCenter = QtWidgets.QLabel('Center longitude:')
        self.gS_grid.addWidget(self.lbl_xCenter, 1, 0, 1, 1)

        self.txtB_xCenter = QtWidgets.QLineEdit('')
        self.txtB_xCenter.setPlaceholderText('Center longitude')
        self.gS_grid.addWidget(self.txtB_xCenter, 1, 1, 1, 1)

        self.lbl_yCenter = QtWidgets.QLabel('Center latitude:')
        self.gS_grid.addWidget(self.lbl_yCenter, 1, 2, 1, 1)

        self.txtB_yCenter = QtWidgets.QLineEdit('')
        self.txtB_yCenter.setPlaceholderText('Center latitude')
        self.gS_grid.addWidget(self.txtB_yCenter, 1, 3, 1, 1)

        self.txtB_addPoint = QtWidgets.QLineEdit('')
        self.gS_grid.addWidget(self.txtB_addPoint, 1, 4, 1, 1)

        self.btn_addPoint = QtWidgets.QPushButton('Add point')
        self.btn_addPoint.setToolTip('Add entered coordinates to list of base plate points')
        self.gS_grid.addWidget(self.btn_addPoint, 1, 4, 1, 1)

        self.btn_delPoint = QtWidgets.QPushButton('Delete point')
        self.btn_delPoint.setToolTip('Delted last point from list')
        self.gS_grid.addWidget(self.btn_delPoint, 2, 4, 1, 1)
        self.btn_delPoint.setEnabled(False)

        self.tbl_groundSurface = QtWidgets.QTableWidget(self)
        self.tbl_groundSurface.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.gS_grid.addWidget(self.tbl_groundSurface, 3, 0, 1, 5)

        self.gB_additional = QtWidgets.QGroupBox('Additional information')
        self.vbox.addWidget(self.gB_additional)

        self.add_grid = QtWidgets.QGridLayout()
        self.gB_additional.setLayout(self.add_grid)

        self.lbl_surfaceHeight = QtWidgets.QLabel('Height of base plate:')
        self.add_grid.addWidget(self.lbl_surfaceHeight, 0, 0, 1, 1)

        self.txtB_surfaceHeight = QtWidgets.QLineEdit('')
        self.txtB_surfaceHeight.setPlaceholderText('Height of base plate in m')
        self.txtB_surfaceHeight.setToolTip('Height of base plate in m above sea level')
        self.add_grid.addWidget(self.txtB_surfaceHeight, 0, 1, 1, 1)

        self.lbl_surfaceArea = QtWidgets.QLabel('Ground area:')
        self.add_grid.addWidget(self.lbl_surfaceArea, 0, 2, 1, 1)

        self.txtB_area = QtWidgets.QLineEdit('')
        self.txtB_area.setPlaceholderText('Area of base plate in sqrm')
        self.txtB_area.setToolTip('Area of base plate in sqrm')
        self.add_grid.addWidget(self.txtB_area, 0, 3, 1, 1)

        self.lbl_ratio = QtWidgets.QLabel('Side ratio:')
        self.add_grid.addWidget(self.lbl_ratio, 1, 0, 1, 1)

        self.txtB_ratio = QtWidgets.QLineEdit('')
        self.txtB_ratio.setPlaceholderText('long side / short side (as decimal number)')
        self.txtB_ratio.setToolTip('Aspect ratio of rectangle as a decimal number\nneeds to be greater or equal to 1')
        self.add_grid.addWidget(self.txtB_ratio, 1, 1 ,1 ,1)

        self.lbl_heading = QtWidgets.QLabel('Building heading:')
        self.add_grid.addWidget(self.lbl_heading, 1, 2, 1, 1)

        self.txtB_heading = QtWidgets.QLineEdit('')
        self.txtB_heading.setPlaceholderText('[0, 360) heading of longest side in degrees')
        self.txtB_heading.setToolTip('Heading of the longest side of the base plate\nneeds to be an element of [0, 360) in degrees')
        self.add_grid.addWidget(self.txtB_heading, 1, 3 , 1, 1)

        self.l_grid = QtWidgets.QGridLayout()
        self.vbox.addLayout(self.l_grid)

        self.btn_about = QtWidgets.QPushButton('About')
        self.btn_about.setToolTip('Information about CityBIT')
        self.l_grid.addWidget(self.btn_about, 2, 0, 1, 1)

        self.btn_reset = QtWidgets.QPushButton('Reset window')
        self.btn_reset.setToolTip('Resets all options of this window to their defaults')
        self.l_grid.addWidget(self.btn_reset, 2, 1, 1, 1)

        self.btn_next = QtWidgets.QPushButton('Next')
        self.btn_next.setToolTip('Move to the next window')
        self.l_grid.addWidget(self.btn_next, 2, 4, 1, 1)


        # assigning functions to buttons
        self.btn_checkCRS.clicked.connect(self.func_checkCRS)
        self.btn_loadCSV.clicked.connect(self.func_loadCSV)
        self.btn_addPoint.clicked.connect(self.func_addPoint)
        self.btn_delPoint.clicked.connect(self.func_delPoint)
        self.btn_sqrRec.clicked.connect(self.func_sqrRec)
        self.btn_about.clicked.connect(self.func_about)
        self.btn_reset.clicked.connect(self.func_reset)
        self.btn_next.clicked.connect(self.func_next)

        # toggeling radio button
        self.rB_center.toggled.connect(self.func_center)

        # variables
        self.iCRS = ''
        self.oCRS = ''
        self.crs_checked = False
        self.groundSurface_list = []

        # setting up table
        cbit_f.displaysetup(self)


        w0.updateWindow0(self, value_dict)
        w0.center_of_list(self)



    def func_center(self):
        w0.center_of_list(self)

    
    def func_checkCRS(self):
        cbit_f.check_CRS(self, True)


    def func_loadCSV(self):
        w0.load_csv(self)


    def func_addPoint(self):
        w0.add_point(self)


    def func_delPoint(self):
        w0.del_point(self)


    def func_sqrRec(self):
        w0.square_rectangle(self)

    def func_about(self):
        global posx, posy
        posx, posy = gf.dimensions(self)
        gf.next_window(self, about(), False)


    def func_reset(self):
        global value_dict, inter_dict, posx, posy
        values = ["iCRS", "oCRS", "cList", "xCen", "yCen", "groundSurface", "area", "sideRatio", "bHeading", "sHeight"]
        inters = ["groundSurface", "area", "sideRatio", "bHeading", "sHeight"]
        value_dict, inter_dict = gf.reset_dicts(values, inters, value_dict, inter_dict)
        posx, posy = gf.dimensions(self)
        gf.next_window(self, mainWindow())


    def func_next(self):
        global value_dict, inter_dict, posx, posy, x_min, x_max, y_min, y_max
        res, value_dict, inter_dict = w0.gatherInfo0(self, value_dict, inter_dict)
        if res:
            # setting results for CRS border 
            x_min = self.x_min
            x_max = self.x_max
            y_min = self.y_min
            y_max = self.y_max
        
            posx, posy = gf.dimensions(self)
            gf.next_window(self, buildingInfo())
        else:
            pass



class buildingInfo(QtWidgets.QWidget):
    """window for entering information realated to roof type, building function etc."""
    def __init__(self):
        super(buildingInfo, self).__init__()
        self.initUI()

    def initUI(self):
        global posx, posy, width, height, sizefactor, value_dict

        self.pictures = ["roofInfo.png", "flat.png", "monopitch.png", "dualpent.png", "gabled.png", "hipped.png", "pavilion.png"]

        gf.windowSetup(self, posx, posy, width, height, pypath, 'CityBIT - General Building Information')

        # creating main layout
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        gf.load_banner(self, os.path.join(pypath, r'pictures\e3dHeader.png'), sizefactor)


        self.gB_roof = QtWidgets.QGroupBox('Roof information')
        self.vbox.addWidget(self.gB_roof)
        
        self.r_grid = QtWidgets.QGridLayout()
        self.gB_roof.setLayout(self.r_grid)

        self.lbl_buildingHeight = QtWidgets.QLabel('Building height')
        self.r_grid.addWidget(self.lbl_buildingHeight, 0, 0, 1, 1)

        self.txtB_buildingHeight = QtWidgets.QLineEdit('')
        self.txtB_buildingHeight.setPlaceholderText('Building height in m')
        self.txtB_buildingHeight.setToolTip('Difference in height from base plate to the highest point of the roof')
        self.r_grid.addWidget(self.txtB_buildingHeight, 0, 1, 1, 1)

        self.lbl_roofHeight = QtWidgets.QLabel('Roof height')
        self.r_grid.addWidget(self.lbl_roofHeight, 0, 2, 1, 1)

        self.txtB_roofHeight = QtWidgets.QLineEdit('')
        self.txtB_roofHeight.setPlaceholderText('Roof height in m')
        self.txtB_roofHeight.setToolTip('Difference in height from lowest to highest point of the roof')
        self.r_grid.addWidget(self.txtB_roofHeight, 0, 3, 1, 1)

        self.lbl_roofType = QtWidgets.QLabel('Roof type:')
        self.r_grid.addWidget(self.lbl_roofType, 1, 0, 1, 1)

        self.cB_roofType = QtWidgets.QComboBox()
        self.cB_roofType.setFont(QtGui.QFont("Consolas"))
        self.cB_roofType.setToolTip('List of available roof types in CityBIT')
        self.cB_roofType.addItems(['', 'flat roof :      1000'])
        if value_dict["cList"] == None or (value_dict["cList"] != None and len(value_dict["cList"]) == 4):
            self.cB_roofType.addItems(w1.createListForComboBox({"monopitch roof": 1010, "dual pent roof": 1020, "gabled roof": 1030, "hipped roof": 1040}, 14))
        self.cB_roofType.addItem('pavilion roof :  1070')
        self.r_grid.addWidget(self.cB_roofType, 1, 1, 1, 1)

        self.lbl_roofHeading = QtWidgets.QLabel('Roof heading:')
        self.r_grid.addWidget(self.lbl_roofHeading, 1, 2, 1, 1)

        self.cB_heading = QtWidgets.QComboBox()
        self.cB_heading.setToolTip('Orientation of the roof ridge')
        self.r_grid.addWidget(self.cB_heading, 1, 3, 1, 1)


        w1.addRoofPictures(self, pypath, sizefactor)


        self.gB_info = QtWidgets.QGroupBox('General information')
        self.vbox.addWidget(self.gB_info)
        
        self.info_grid = QtWidgets.QGridLayout()
        self.gB_info.setLayout(self.info_grid)

        self.lbl_buildingFunction = QtWidgets.QLabel('Building function:')
        self.info_grid.addWidget(self.lbl_buildingFunction, 0, 0, 1, 1)

        self.cB_buildingFunction = QtWidgets.QComboBox()
        self.cB_buildingFunction.setFont(QtGui.QFont("Consolas"))
        self.cB_buildingFunction.setToolTip('List of available building functions in CityBIT')
        self.cB_buildingFunction.addItems(w1.createListForComboBox(va.buildingFunctions, 40))
        self.info_grid.addWidget(self.cB_buildingFunction, 0, 1, 1, 1)

        self.lbl_terrainIntersection = QtWidgets.QLabel('Terrain intersection interpolation radius:')
        self.info_grid.addWidget(self.lbl_terrainIntersection, 0, 2, 1, 1)

        self.cB_terrainIntersection = QtWidgets.QComboBox()
        self.info_grid.addWidget(self.cB_terrainIntersection, 0, 3, 1, 1)
        self.cB_terrainIntersection.setToolTip('Interpolates a terrain intersection for the base plate\nwith data points within the selected radius')
        self.cB_terrainIntersection.addItems([ 'off', '100m', '200m', '500m'])

        self.lbl_SAG = QtWidgets.QLabel('Storeys above ground:')
        self.info_grid.addWidget(self.lbl_SAG, 1, 0, 1, 1)

        self.txtB_SAG = QtWidgets.QLineEdit('')
        self.txtB_SAG.setToolTip('Sets the value for the storeysAboveGround CityGML attribute')
        self.info_grid.addWidget(self.txtB_SAG, 1, 1, 1, 1)

        self.lbl_SBG = QtWidgets.QLabel('Storeys below ground:')
        self.info_grid.addWidget(self.lbl_SBG, 1, 2, 1, 1)
        
        self.txtB_SBG = QtWidgets.QLineEdit('')
        self.txtB_SBG.setToolTip('Sets the value for the storeysBelowGround CityGML attribute')
        self.info_grid.addWidget(self.txtB_SBG, 1, 3, 1, 1)


        self.l_grid = QtWidgets.QGridLayout()
        self.vbox.addLayout(self.l_grid)

        self.btn_back = QtWidgets.QPushButton('Back')
        self.btn_back.setToolTip('Move to the previous window')
        self.l_grid.addWidget(self.btn_back, 0, 0, 1, 1)

        self.btn_reset = QtWidgets.QPushButton('Reset window')
        self.btn_reset.setToolTip('Resets all options of this window to their defaults')
        self.l_grid.addWidget(self.btn_reset, 0, 1, 1, 1)

        self.btn_next = QtWidgets.QPushButton('Next')
        self.btn_next.setToolTip('Move to the next window')
        self.l_grid.addWidget(self.btn_next, 0, 3, 1, 1)

        # assigning functions to buttons
        self.btn_back.clicked.connect(self.func_back)
        self.btn_reset.clicked.connect(self.func_reset)
        self.btn_next.clicked.connect(self.func_next)

        self.cB_roofType.currentIndexChanged.connect(self.func_updateRoof)

        w1.updateWindow1(self, value_dict)
        w1.changeRoof(self, pypath)


    def func_updateRoof(self):
        w1.changeRoof(self, pypath)    


    def func_back(self):
        global value_dict, inter_dict, posx, posy
        res, value_dict, inter_dict = w1.gatherInfo1(self, value_dict, inter_dict)
        if res:
            posx, posy = gf.dimensions(self)
            gf.next_window(self, mainWindow())
        else:
            pass

    def func_reset(self):
        global value_dict, inter_dict, posx, posy
        values = ["bHeight", "rHeight", "rType", "rHeading", "bFunction", "SAG", "SBG"]
        # inters (inter_dict keys) would be identical to values
        value_dict, inter_dict = gf.reset_dicts(values, values, value_dict, inter_dict)
        posx, posy = gf.dimensions(self)
        gf.next_window(self, buildingInfo())


    def func_next(self):
        global value_dict, inter_dict, posx, posy
        res, value_dict, inter_dict = w1.gatherInfo1(self, value_dict, inter_dict)
        if res:
            posx, posy = gf.dimensions(self)
            gf.next_window(self, datasetInfo())
        else:
            pass




class datasetInfo(QtWidgets.QWidget):
    """window for entering export location and selecting dataset"""
    def __init__(self):
        super(datasetInfo, self).__init__()
        self.initUI()

    def initUI(self):
        global posx, posy, width, height, sizefactor

        gf.windowSetup(self, posx, posy, width, height, pypath, 'CityBIT - Export Options')

        # creating main layout
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        gf.load_banner(self, os.path.join(pypath, r'pictures\e3dHeader.png'), sizefactor)

        self.uGrid = QtWidgets.QGridLayout()
        self.lbl_gml_ID = QtWidgets.QLabel('gml:id :')
        self.uGrid.addWidget(self.lbl_gml_ID, 0, 0, 1, 1)

        self.txtB_u_GML_ID = QtWidgets.QLineEdit()
        self.txtB_u_GML_ID.setPlaceholderText('gml:id of created building')
        self.txtB_u_GML_ID.setToolTip('uuid is used if left empty')
        self.uGrid.addWidget(self.txtB_u_GML_ID, 0, 1, 1, 3)

        self.checkB_combine = QtWidgets.QCheckBox('Combine with existing dataset')
        self.uGrid.addWidget(self.checkB_combine, 0, 4, 1, 1)

        self.vbox.addLayout(self.uGrid)

        self.gB_interpol = QtWidgets.QGroupBox('Interpolation')
        self.vbox.addWidget(self.gB_interpol)
        
        self.iGrid = QtWidgets.QGridLayout()
        self.gB_interpol.setLayout(self.iGrid)

        self.btn_dataFolder = QtWidgets.QPushButton('Select input directory')
        self.btn_dataFolder.setToolTip('Path to dataset for interpolation and collision check')
        self.iGrid.addWidget(self.btn_dataFolder, 1, 0, 1, 1)
        
        self.txtB_dataFolder = QtWidgets.QLineEdit()
        self.txtB_dataFolder.setPlaceholderText('Data set for interpolation')
        self.txtB_dataFolder.setReadOnly(True)
        self.iGrid.addWidget(self.txtB_dataFolder, 1, 1, 1, 1)

        self.btn_exportPath = QtWidgets.QPushButton('Output directory')
        self.btn_exportPath.setToolTip('Path to which new file should be written')
        self.iGrid.addWidget(self.btn_exportPath, 2, 0, 1, 1)

        self.txtB_exportPath = QtWidgets.QLineEdit()
        self.txtB_exportPath.setPlaceholderText('Output directory')
        self.txtB_exportPath.setReadOnly(True)
        self.iGrid.addWidget(self.txtB_exportPath, 2, 1, 1, 1)

        self.lbl_interMethod = QtWidgets.QLabel('Interpolation method:')
        self.iGrid.addWidget(self.lbl_interMethod, 3, 0, 1, 1)

        self.cB_interMethod = QtWidgets.QComboBox()
        self.cB_interMethod.setToolTip('Interpolation algorithm with which\nmissing values are interpolated')
        self.cB_interMethod.addItems(['linear', 'nearest', 'cubic'])
        self.iGrid.addWidget(self.cB_interMethod, 3, 1, 1, 1)

        self.lbl_sameAttrib = QtWidgets.QLabel('Buildings with identical:')
        self.iGrid.addWidget(self.lbl_sameAttrib, 4, 0, 1, 1)

        self.cB_sameAttrib = QtWidgets.QComboBox()
        self.cB_sameAttrib.addItem('')
        if value_dict["bFunction"] != None:
            self.cB_sameAttrib.addItem('buildingFunction')
        if value_dict["rType"] != None:
            self.cB_sameAttrib.addItem('roofType')
        if self.cB_sameAttrib.count() < 2:
            self.cB_sameAttrib.setEnabled(False)
            self.cB_sameAttrib.setToolTip('Choose a building function or roof type in the previous window')
        else:
            self.cB_sameAttrib.setToolTip('Restrict interpolation to only consider\nbuildings with the same attribute')
        self.iGrid.addWidget(self.cB_sameAttrib, 4, 1, 1, 1)


        # number of buildings
        self.gB_noB = QtWidgets.QGroupBox('Number of buildings used for interpolation')
        self.vbox.addWidget(self.gB_noB)
        self.gB_noB.setCheckable(True)
        self.gB_noB.setChecked(False)
        self.gB_noB.setToolTip('Restrict interpolation to only consider\nthe closest *number* of buildings')

        self.noB_grid = QtWidgets.QGridLayout()
        self.gB_noB.setLayout(self.noB_grid)

        self.lbl_noB = QtWidgets.QLabel('Number of buildings')
        self.noB_grid.addWidget(self.lbl_noB, 5, 0, 1, 1)

        self.sB_noB = QtWidgets.QSpinBox()
        self.sB_noB.setRange(1, 9999)
        self.sB_noB.setValue(10)
        self.noB_grid.addWidget(self.sB_noB, 5, 1, 1, 1)


        # radius
        self.gB_radius = QtWidgets.QGroupBox('Buildings within radius')
        self.vbox.addWidget(self.gB_radius)
        self.gB_radius.setCheckable(True)
        self.gB_radius.setChecked(False)
        self.gB_radius.setToolTip('Restrict interpolation to only consider\nbuildings within the radius')

        self.radius_grid = QtWidgets.QGridLayout()
        self.gB_radius.setLayout(self.radius_grid)

        self.lbl_radius = QtWidgets.QLabel('Buildings within a radius of:')
        self.radius_grid.addWidget(self.lbl_radius, 6, 0, 1, 1)

        self.sB_radius = QtWidgets.QSpinBox()
        self.sB_radius.setValue(50)
        self.sB_radius.setRange(10, 10000)
        self.sB_radius.setSingleStep(50)
        self.sB_radius.setSuffix('m')
        self.radius_grid.addWidget(self.sB_radius, 6, 1, 1, 1)


        # coordinates
        self.gB_coor = QtWidgets.QGroupBox('Coordinate border')
        self.vbox.addWidget(self.gB_coor)
        self.gB_coor.setCheckable(True)
        self.gB_coor.setChecked(False)
        self.gB_coor.setToolTip('Restrict interpolation to only consider\n buildings within the entered coordiante border')

        self.coor_grid = QtWidgets.QGridLayout()
        self.gB_coor.setLayout(self.coor_grid)

        self.lbl_iCRS = QtWidgets.QLabel('Input CRS:')
        self.coor_grid.addWidget(self.lbl_iCRS, 0, 0, 1, 1)

        self.txtB_iCRS = QtWidgets.QLineEdit()
        self.coor_grid.addWidget(self.txtB_iCRS, 0, 1, 1, 1)
        self.txtB_iCRS.setEnabled(False)

        self.lbl_oCRS = QtWidgets.QLabel('Output CRS:')
        self.coor_grid.addWidget(self.lbl_oCRS, 0, 2, 1, 1)

        self.txtB_oCRS = QtWidgets.QLineEdit()
        self.coor_grid.addWidget(self.txtB_oCRS, 0, 3, 1, 1)
        self.txtB_oCRS.setEnabled(False)

        self.lbl_xCoor = QtWidgets.QLabel('Longitude:')
        self.coor_grid.addWidget(self.lbl_xCoor, 1, 0, 1, 1)

        self.txtB_xCoor = QtWidgets.QLineEdit('')
        self.txtB_xCoor.setPlaceholderText('Longitude')
        self.coor_grid.addWidget(self.txtB_xCoor, 1, 1, 1, 1)

        self.lbl_yCoor = QtWidgets.QLabel('Latitude:')
        self.coor_grid.addWidget(self.lbl_yCoor, 1, 2, 1, 1)
        
        self.txtB_yCoor = QtWidgets.QLineEdit('')
        self.txtB_yCoor.setPlaceholderText('Latitude')
        self.coor_grid.addWidget(self.txtB_yCoor, 1, 3, 1, 1)

        self.txtB_addPoint = QtWidgets.QLineEdit('')
        self.coor_grid.addWidget(self.txtB_addPoint, 1, 4, 1, 1)

        self.btn_addPoint = QtWidgets.QPushButton('Add point')
        self.btn_addPoint.setToolTip('Add entered coordinates to list of border points')
        self.coor_grid.addWidget(self.btn_addPoint, 1, 4, 1, 1)

        self.btn_loadCSV = QtWidgets.QPushButton('Load .csv')
        self.btn_loadCSV.setToolTip('Load coordinates from .csv file\nSee example.csv for syntax')
        self.coor_grid.addWidget(self.btn_loadCSV, 2, 3, 1, 1)

        self.btn_delPoint = QtWidgets.QPushButton('Delete point')
        self.btn_delPoint.setToolTip('Delted last point from list')
        self.coor_grid.addWidget(self.btn_delPoint, 2, 4, 1, 1)

        self.tbl_groundSurface = QtWidgets.QTableWidget(self)
        self.tbl_groundSurface.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.coor_grid.addWidget(self.tbl_groundSurface, 3, 0, 1, 5)

        self.l_grid = QtWidgets.QGridLayout()
        self.vbox.addLayout(self.l_grid)


        self.btn_back  = QtWidgets.QPushButton('Back')
        self.btn_back.setToolTip('Move to the previous window')
        self.l_grid.addWidget(self.btn_back, 1, 0, 1, 1)

        self.btn_reset = QtWidgets.QPushButton('Reset window')
        self.btn_reset.setToolTip('Resets all options of this window to their defaults')
        self.l_grid.addWidget(self.btn_reset, 1, 1, 1, 1)

        self.btn_compute = QtWidgets.QPushButton('Compute')
        self.btn_compute.setToolTip('Start building creation')
        self.l_grid.addWidget(self.btn_compute, 1, 3, 1, 1)

        # assigning functions to buttons
        self.btn_dataFolder.clicked.connect(self.func_dataset)
        self.btn_exportPath.clicked.connect(self.func_exportPath)
        self.btn_back.clicked.connect(self.func_back)
        self.btn_reset.clicked.connect(self.func_reset)
        self.btn_compute.clicked.connect(self.func_compute)

        self.gB_noB.toggled.connect(self.func_noB)
        self.gB_radius.toggled.connect(self.func_radius)
        self.gB_coor.toggled.connect(self.func_coor)

        # variable for coordinate border of interpolation input
        self.border_list = []

        w2.updateWindow2(self, value_dict)

        # checking if interpolation overview needs to be displayed
        if sum(inter_dict.values()) == 0:
            # interpolation not needed
            gf.messageBox(self, 'Information', 'Interpolation not needed.\nSelect input folder for collsion check with existing buildings.')
            self.cB_interMethod.setEnabled(False)
            self.cB_sameAttrib.setEnabled(False)
            self.gB_noB.setEnabled(False)
            self.gB_radius.setEnabled(False)
            self.gB_coor.setEnabled(False)
        else:
            gf.next_window(self, summary(inter_dict), False)



    def func_noB(self):
        # changing GUI for number of building selection
        if self.gB_noB.isChecked():
            # disable others
            self.gB_radius.setChecked(False)
            self.gB_coor.setChecked(False)
        else:
            # skip
            pass


    def func_radius(self):
        # changing GUI for radius selection
        if self.gB_radius.isChecked():
            # disable others
            self.gB_noB.setChecked(False)
            self.gB_coor.setChecked(False)
        else:
            # skip
            pass


    def func_coor(self):
        # changing GUI for coordiante selection
        if self.gB_coor.isChecked():
            self.gB_noB.setChecked(False)
            self.gB_radius.setChecked(False)
        else:
            # skip
            pass



    def func_dataset(self):
        # getting dataset path
        global value_dict
        value_dict["dataPath"] = gf.select_folder(self, self.txtB_dataFolder, 'Select folder containing dataset for interpolation')


    def func_exportPath(self):
        # getting export path
        global value_dict
        value_dict["expoPath"] = gf.select_folder(self, self.txtB_exportPath, 'Select directory to save to')


    def func_back(self):
        global posx, posy, value_dict
        value_dict = w2.gatherInfo2(self, value_dict)
        posx, posy = gf.dimensions(self)
        gf.next_window(self, buildingInfo())

    def func_reset(self):
        global value_dict, inter_dict, posx, posy
        values = ["dataPath", "interMethod", "sameAttrib", "selectBy", "expoPath", "bList", "noB", "radius"]
        # inters (inter_dict keys) is empty
        value_dict, inter_dict = gf.reset_dicts(values, [], value_dict, inter_dict)
        posx, posy = gf.dimensions(self)
        gf.next_window(self, datasetInfo())

    def func_compute(self):
        # start interpolation, building creation, collison check
        global value_dict, inter_dict
        value_dict = w2.gatherInfo2(self, value_dict)
        import time
        start = time.time()
        cbit_f.compute(self, value_dict, inter_dict)
        gf.windowTitle(self, 'export options')
        end = time.time()
        if False:
            print(end - start)




class about(QtWidgets.QWidget):
    def __init__(self):
        super(about, self).__init__()
        self.initUI()

    def initUI(self):
        global posx, posy, width, height, sizefactor

        gf.windowSetup(self, posx + 10, posy + 10, width, height, pypath, 'CityBIT - About')

        # creating main layout
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        gf.load_banner(self, os.path.join(pypath, r'pictures\e3dHeader.png'), sizefactor)

        self.textwidget = QtWidgets.QTextBrowser()
        self.vbox.addWidget(self.textwidget)
        self.textwidget.setFontPointSize(14)
        with open(os.path.join(pypath, 'about/about.txt'), 'r') as file:
            text = file.read()
        self.textwidget.setText(text)

        self.lGrid = QtWidgets.QGridLayout()

        self.btn_repo = QtWidgets.QPushButton('Open repository')
        self.lGrid.addWidget(self.btn_repo, 0, 0, 1, 1)

        self.btn_close = QtWidgets.QPushButton('Close')
        self.lGrid.addWidget(self.btn_close, 0, 1, 1, 1)

        self.vbox.addLayout(self.lGrid)

        self.btn_repo.clicked.connect(self.open_repo)
        self.btn_close.clicked.connect(self.close_about)


    def open_repo(self):
        os.startfile('https://gitlab.e3d.rwth-aachen.de/e3d-software-tools/citybit/citybit')

    def close_about(self):
        self.hide()




class summary(QtWidgets.QWidget):
    def __init__(self, inter_dict):
        super(summary, self).__init__()
        self.initUI(inter_dict)

    def initUI(self, inter_dict):
        global posx, posy, width, height, sizefactor

        gf.windowSetup(self, posx + 20, posy + 20, width / 3, height / 3, pypath, 'CityBIT - List of values that need to be interpolated')

        # creating main layout
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.lbl_list = QtWidgets.QLabel('Value(s) which are going to be interpolated:')
        self.vbox.addWidget(self.lbl_list)

        self.lst_inter = QtWidgets.QListWidget()
        self.vbox.addWidget(self.lst_inter)
        self.lst_inter.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        for key in inter_dict:
            if inter_dict[key]:
                self.lst_inter.addItem(va.intDict_toDispName[key])

        self.btn_close = QtWidgets.QPushButton('Close')
        self.vbox.addWidget(self.btn_close)

        self.btn_close.clicked.connect(self.close_about)


    def close_about(self):
        self.hide()


class CustomDialog(QtWidgets.QDialog):
    def __init__(self):
        super(CustomDialog, self).__init__()
        
        global posx, posy, width, height, sizefactor, pypath

        gf.windowSetup(self, posx + 20, posy + 20, width, height / 5, pypath, 'CityBIT - Reference Coordinate System')

        # creating main layout
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.lbl_list = QtWidgets.QLabel('Please enter a coordinate reference system:')
        self.vbox.addWidget(self.lbl_list)

        self.btn_openReference = QtWidgets.QPushButton("Open modeling guide")
        self.vbox.addWidget(self.btn_openReference)
        self.btn_openReference.clicked.connect(self.openGuide)

        self.txtB_crs = QtWidgets.QLineEdit("")
        self.txtB_crs.setPlaceholderText("recommendation for germany: 'urn:adv:crs:ETRS89_UTM32*DE_DHHN92_NH'")
        self.vbox.addWidget(self.txtB_crs)

        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, self)
        self.vbox.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.xyz)

    def openGuide(self):
        os.startfile(r"https://en.wiki.quality.sig3d.org/index.php/Modeling_Guide_for_3D_Objects_-_Part_2:_Modeling_of_Buildings_(LoD1,_LoD2,_LoD3)#Reference_Coordinate_System:~:text=as%20semantic%20objects.-,Reference%20Coordinate%20System,-CityGML%202.0%20strongly")

    def xyz(self):
        gf.messageBox(self, "Error", "The CRS is required!")

    def getResults(self):
        if self.exec_() == QtWidgets.QDialog.Accepted:
            return self.txtB_crs.text()
        else:
            print("error")
            return None






if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    widget = mainWindow()
    widget.show()
    sys.exit(app.exec_())