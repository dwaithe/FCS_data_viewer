import struct
import numpy as np
#import scipy.weave as weave
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import sys, csv, os

from PyQt5 import QtGui, QtCore, QtWidgets
#import matplotlib
#matplotlib.use('Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.transforms import ScaledTranslation
import random
import errno
import os.path

from scipy.special import _ufuncs_cxx
import pickle
from correlation_objects import *
import tifffile as tif_fn
import json

"""FCS Bulk Correlation Software

    Copyright (C) 2015  Dominic Waithe

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
class folderOutput(QtWidgets.QMainWindow):
    
    def __init__(self,parent):
        super(folderOutput, self).__init__()
       
        self.initUI()
        self.parent = parent
        self.parent.config ={}
        
        try:
            self.parent.config = pickle.load(open(os.path.expanduser('~')+'/FCS_Analysis/config.p', "rb" ));
            self.filepath = self.parent.config['output_corr_filepath']
        except:
            self.filepath = os.path.expanduser('~')+'/FCS_Analysis/output/'
            try:
                os.makedirs(self.filepath)
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise
        
        
    def initUI(self):      

        self.textEdit = QtWidgets.QTextEdit()
        self.setCentralWidget(self.textEdit)
        self.statusBar()

        openFile = QtWidgets.QAction(QtGui.QIcon('open.png'), 'Open', self)
        openFile.triggered.connect(self.showDialog)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)       
        
        self.setGeometry(300, 300, 350, 500)
        self.setWindowTitle('Select a Folder')
        #self.show()
        
    def showDialog(self):

        if self.type == 'output_corr_dir':
            #folderSelect = QtGui.QFileDialog()
            #folderSelect.setDirectory(self.filepath);
            tfilepath = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory",self.filepath))
            
            if tfilepath !='':
                self.filepath = tfilepath
            #Save to the config file.
                self.parent.config['output_corr_filepath'] = str(tfilepath)
                pickle.dump(self.parent.config, open(str(os.path.expanduser('~')+'/FCS_Analysis/config.p'), "wb" ))
            

class Annotate():
    def __init__(self,win_obj,par_obj,scrollBox):
        self.ax = plt.gca()
        
        self.x0 = []
        self.par_obj = par_obj
        self.win_obj = win_obj
        self.scrollBox = scrollBox
        
        self.pickerSelect = False;
        self.ax.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.ax.figure.canvas.mpl_connect('button_release_event', self.on_release)
        

    def on_press(self, event):
        self.ax.figure.canvas.draw()
        self.x0 = event.xdata
        

    def on_release(self, event):
        #self.rect.remove()
        self.x1 = event.xdata
        
        if(self.x0 <0): self.x0 =0
        if(self.x1 <0): self.x1 =0
        if(self.x0 >self.x1): self.x1b =self.x0;self.x0=self.x1;self.x0=self.x1b
       

        self.scrollBox.rect.append(plt.axvspan(self.x0, self.x1, facecolor=self.par_obj.colors[self.scrollBox.rect.__len__() % len(self.par_obj.colors)], alpha=0.5,picker=True))
        self.ax.figure.canvas.draw()
        #Saves regions to series of arrays. Opted not to make class for this. Not sure why :-)
        self.scrollBox.x0.append(self.x0)
        self.scrollBox.x1.append(self.x1)
        self.scrollBox.color = self.par_obj.colors[self.scrollBox.rect.__len__()]
        self.scrollBox.TGid.append(self.par_obj.TGnumOfRgn)
        self.scrollBox.facecolor.append(self.par_obj.colors[self.par_obj.TGnumOfRgn])
        self.par_obj.TGnumOfRgn = self.par_obj.TGnumOfRgn + 1
        self.scrollBox.generateList()
        #refreshTable()
    def freshDraw(self):
            self.scrollBox.rect =[]
            for i in range(0,self.scrollBox.x0.__len__()):
                
                self.scrollBox.rect.append(plt.axvspan(self.scrollBox.x0[i], self.scrollBox.x1[i], facecolor=self.par_obj.colors[i % len(self.par_obj.colors)], alpha=0.5,picker=True))
            self.win_obj.canvas5.draw() 
    def redraw(self):
            
            for i in range(0,self.scrollBox.rect.__len__()):
                self.scrollBox.rect[i].remove()
            self.scrollBox.rect =[]
            for i in range(0,self.scrollBox.x0.__len__()):
                
                self.scrollBox.rect.append(plt.axvspan(self.scrollBox.x0[i], self.scrollBox.x1[i], facecolor=self.par_obj.colors[i % len(self.par_obj.colors)], alpha=0.5,picker=True))
            self.win_obj.canvas5.draw() 

    
class baseList(QtWidgets.QLabel):
    def __init__(self):
        super(baseList, self).__init__()
        self.listId=0
    def mousePressEvent(self,ev):
        print(self.listId)

class FileDialog(QtWidgets.QMainWindow):
    
    def __init__(self, win_obj, par_obj, fit_obj):
        super(FileDialog, self).__init__()
       
        
        self.initUI()
        self.par_obj = par_obj
        self.fit_obj = fit_obj
        self.win_obj = win_obj

        
        
    def initUI(self):      

        self.textEdit = QtWidgets.QTextEdit()
        self.setCentralWidget(self.textEdit)
        self.statusBar()

        openFile = QtWidgets.QAction(QtGui.QIcon('open.png'), 'Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.showDialog)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)       
        
        self.setGeometry(300, 300, 350, 500)
        self.setWindowTitle('File dialog')
    def count(self):
        print('workes')
        #self.show()
        
    def showDialog(self):
        #Intialise Dialog.
        fileInt = QtWidgets.QFileDialog()
        try:
            #Try and read the default location for a file.
            f = open(os.path.expanduser('~')+'/FCS_Analysis/configLoad', 'r')
            self.loadpath =f.readline()
            f.close() 
        except:
            #If not default will do.
            self.loadpath = os.path.expanduser('~')+'/FCS_Analysis/'

        
        #Create loop which opens dialog box and allows selection of files.

        self.win_obj.update_correlation_parameters()
        file_imports = fileInt.getOpenFileNames(self, 'Open a data file',self.loadpath, 'pt3 files (*.pt3);ptU files (*.ptU);asc files (*.asc);spc files (*.spc);All Files (*.*)')
        bt = QtWidgets.QPushButton("cancel")
        
        for c,filename in enumerate(file_imports[0]):
            self.win_obj.image_status_text.setStyleSheet("QStatusBar{padding-left:8px;color:green;font-weight:regular;}")
            self.win_obj.image_status_text.showMessage("Processing file "+str(c+1)+" of "+str(file_imports.__len__()))
            self.fit_obj.app.processEvents()
            pic = picoObject(filename,self.par_obj,self.fit_obj);
            if pic.exit == True:
                self.win_obj.image_status_text.setStyleSheet("QStatusBar{padding-left:8px;color:red;font-weight:bold;}")
                self.win_obj.image_status_text.showMessage("Your data-file is not a supported format.")
                self.fit_obj.app.processEvents()
                return
            self.loadpath = str(QtCore.QFileInfo(filename).absolutePath())
            self.par_obj.numOfLoaded = self.par_obj.numOfLoaded+1
            self.win_obj.label.generateList()
            self.win_obj.TGScrollBoxObj.generateList()
            self.win_obj.updateCombo()
            self.win_obj.cbx.setCurrentIndex(self.par_obj.numOfLoaded-1)
            self.win_obj.plot_PhotonCount(self.par_obj.numOfLoaded-1)
        self.win_obj.plotDataQueueFn()
        self.win_obj.image_status_text.setStyleSheet("QStatusBar{padding-left:8px;color:green;font-weight:regular;}")
        self.win_obj.image_status_text.showMessage("Processing finished")
        try:
            
            f = open(os.path.expanduser('~')+'/FCS_Analysis/configLoad', 'w')

            f.write(self.loadpath)
            f.close()
            
        except:
            print('nofile')



        #Update listing:
        #main.label.remakeList()

    
class Window(QtWidgets.QWidget):
    def __init__(self, par_obj, fit_obj):
        super(Window, self).__init__()
        self.fit_obj = fit_obj
        self.par_obj = par_obj
        self.generateWindow()
    def on_resize1(self,event): 
        self.figure1.subplots_adjust(wspace=0.73, hspace=0.24,top=0.96, bottom =0.14,left=0.09, right=0.98)
        self.figure1.tight_layout()
    
    def on_resize4(self,event): 
        self.figure4.tight_layout(pad=1.08)
    def on_resize5(self,event): 
        self.figure5.tight_layout(pad=1.08)
    def generateWindow(self):
        # a figure instance to plot on
        self.figure1 = plt.figure()
        self.figure1.set_size_inches(5.0,5.4)
        self.figure1.subplots_adjust(wspace=0.73, hspace=0.24,top=0.96, bottom =0.14,left=0.09, right=0.98)


        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        #self.canvas1 = FigureCanvas(self.figure1)
        self.canvas1 = FigureCanvas(self.figure1)
        self.figure1.patch.set_facecolor('white')
        

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar1 = NavigationToolbar(self.canvas1, self)


        #self.figure2 = plt.figure()
        #self.canvas2 = FigureCanvas(self.figure2)
        
        #self.toolbar2 = NavigationToolbar(self.canvas2, self)

        #self.figure3 = plt.figure()
        #self.canvas3 = FigureCanvas(self.figure3)
        #self.toolbar3 = NavigationToolbar(self.canvas3, self)

        self.figure4 = plt.figure(figsize=(5.4,2.1))
        self.figure4.subplots_adjust(left=0.15,bottom=0.25)

        self.canvas4 = FigureCanvas(self.figure4)
        self.figure4.patch.set_facecolor('white')
        #self.toolbar4 = NavigationToolbar(self.canvas4, self)

        self.figure5 = plt.figure(figsize=(5.4,2.1))
        self.figure5.subplots_adjust(left=0.15,bottom=0.25)

        # this is the Navigation widget
        self.canvas5 = FigureCanvas(self.figure5)
        self.figure5.patch.set_facecolor('white')
        #Tself.toolbar5 = NavigationToolbar(self.canvas5, self)
        self.canvas1.mpl_connect('resize_event',self.on_resize1)
        #self.canvas2.mpl_connect('resize_event',self.on_resize2)
        #self.canvas3.mpl_connect('resize_event',self.on_resize3)
        self.canvas4.mpl_connect('resize_event',self.on_resize4)
        self.canvas5.mpl_connect('resize_event',self.on_resize5)
        
        self.ex = FileDialog(self, self.par_obj, self.fit_obj)

        self.folderOutput = folderOutput(self.par_obj)
        self.folderOutput.type = 'output_corr_dir'

        # Just some button connected to `plot` method
        self.openFile = QtWidgets.QPushButton('Open File')
        self.openFile.setFixedWidth(120)
        self.openFile.clicked.connect(self.ex.showDialog)
        self.replot_btn = QtWidgets.QPushButton('Replot Data')
        self.replot_btn.clicked.connect(self.plotDataQueueFn)
        self.replot_btn2 = QtWidgets.QPushButton('Replot Data')
        self.replot_btn2.clicked.connect(self.plotDataQueueFn)
        self.saveAll_btn = QtWidgets.QPushButton('Save all as corr. files (.csv)')
        self.saveAll_btn.clicked.connect(self.saveDataQueue)

        self.normPlot = QtWidgets.QCheckBox('Normalise')
        self.normPlot.setChecked(False)
        #self.figure.canvas.mpl_connect('button_press_event', self.on_press)
        #self.figure.canvas.mpl_connect('button_release_event', self.on_release)
        # set the layout
        self.spacer = QtWidgets.QLabel()
        main_layout = QtWidgets.QHBoxLayout()
        self.globalText = QtWidgets.QLabel()
        self.globalText.setText('Correlation Para:')
        self.reprocess_btn = QtWidgets.QPushButton('reprocess data')
        self.reprocess_btn.clicked.connect(self.reprocessDataFn)
        self.reprocess_btn.setFixedWidth(120)
        self.reprocess_btn2 = QtWidgets.QPushButton('reprocess data')
        self.reprocess_btn2.clicked.connect(self.reprocessDataFn)
        self.reprocess_btn2.setFixedWidth(120)
        self.reprocess_btn3 = QtWidgets.QPushButton('reprocess data')
        self.reprocess_btn3.clicked.connect(self.reprocessDataFn)
        self.reprocess_btn3.setFixedWidth(120)
        self.NsubText = QtWidgets.QLabel('Nsub:')
        self.NsubText.resize(50,40)
        
        self.NsubEdit =lineEditSp('6',self)
        self.NsubEdit.setFixedWidth(60)
        self.NsubEdit.type ='nsub'
        
        self.NcascStartText = QtWidgets.QLabel('Ncasc Start:')
        self.NcascStartEdit = lineEditSp('0',self)
        self.NcascStartEdit.setFixedWidth(60)
        self.NcascStartEdit.parentId = self
        self.NcascStartEdit.type = 'ncasc'
        self.NcascEndText = QtWidgets.QLabel('Ncasc End:')
        self.NcascEndEdit = lineEditSp('25',self)
        self.NcascEndEdit.setFixedWidth(60)
        self.NcascEndEdit.type = 'ncascEnd'
        self.NcascEndEdit.parentId = self
        
        self.winIntText = QtWidgets.QLabel('Bin Size (CH):')

        self.winIntEdit = lineEditSp('10',self)
        self.winIntEdit.setMaxLength(5)
        self.winIntEdit.setFixedWidth(40)
        self.winIntEdit.type = 'winInt'
        self.winIntEdit.parObj = self
        self.folderSelect_btn = QtWidgets.QPushButton('Output Folder')
        self.folderSelect_btn.clicked.connect(self.folderOutput.showDialog)

        
        #Adds an all option to the combobox.lfkk

        

        
        
        #grid1.addWidget(self.folderSelect_btn,11,0)
       
        
        #grid1.addWidget(self.spacer,12,0,20,0)
        
        

        self.label =scrollBox(self,self.par_obj)
        self.TGScrollBoxObj =TGscrollBox(self,self.par_obj)

        #The table which shows the details of the time-gating.
        self.modelTab = QtWidgets.QTableWidget(self)
        self.modelTab.setRowCount(0)
        self.modelTab.setColumnCount(7)
        
        
        self.modelTab.setColumnWidth(0,20);
        self.modelTab.setColumnWidth(1,40);
        self.modelTab.setColumnWidth(2,20);
        self.modelTab.setColumnWidth(3,40);
        self.modelTab.setColumnWidth(4,85);
        self.modelTab.setColumnWidth(5,70);
        self.modelTab.setColumnWidth(6,20);
        #self.modelTab.horizontalHeader().setStretchLastSection(True)
        self.modelTab.resize(350,200)
        self.modelTab.setMinimumSize(310,200)
        self.modelTab.setMaximumSize(310,200)
        self.modelTab.setHorizontalHeaderLabels(["","From:","","To:","Apply to:", "", "", "", ""])

        #The table which shows the details of each correlated file. 
        self.modelTab2 = QtWidgets.QTableWidget(self)
        self.modelTab2.setRowCount(0)
        self.modelTab2.setColumnCount(5)
        self.modelTab2.setColumnWidth(0,80);
        self.modelTab2.setColumnWidth(1,140);
        self.modelTab2.setColumnWidth(2,30);
        self.modelTab2.setColumnWidth(3,150);
        self.modelTab2.setColumnWidth(4,100);
        self.modelTab2.setColumnWidth(5,100);
        self.modelTab2.horizontalHeader().setStretchLastSection(True)
        self.modelTab2.resize(800,400)
        

        self.modelTab2.setHorizontalHeaderLabels(["","data name","plot","save","file name"])

        tableAndBtns =  QtWidgets.QVBoxLayout()
        correlationBtns =  QtWidgets.QHBoxLayout()
        #self.label.setText('<HTML><H3>DATA file: </H3><P>'+str(6)+' Click here to load in this sample and what happens if I make it too long.</P></HTML>')
        #self.label.listId = 6
        self.fileDialog = QtWidgets.QFileDialog()
        self.centre_panel = QtWidgets.QVBoxLayout()
        
        
        
    
        self.right_panel = QtWidgets.QVBoxLayout()
        #Adds the main graph components to the top panel
       

        #LEFT PANEL
        self.left_panel = QtWidgets.QVBoxLayout()
        self.left_panel_top = QtWidgets.QHBoxLayout()
        self.left_panel.addLayout(self.left_panel_top)
        self.left_panel_top.addWidget(self.canvas4)
        self.left_panel_top.addStretch()
        
        #LEFT PANEL TOP
        self.left_panel_top_btns= QtWidgets.QHBoxLayout()
        self.plotText =QtWidgets.QLabel()
        self.plotText.setText('Plot: ')
        self.left_panel_top_btns.addWidget(self.plotText)

        self.left_panel_second_row_btns = QtWidgets.QHBoxLayout()

        self.photonCountText = QtWidgets.QLabel()
        self.photonCountText.setText('Bin Duration (ms): ')
        self.photonCountEdit = lineEditSp('25',self)
        self.photonCountEdit.type ='int_bin'
        self.photonCountEdit.setMaxLength(5)
        self.photonCountEdit.setFixedWidth(40)
        self.photonCountEdit.parObj = self
        self.photonCountEdit.resize(40,50)
        self.photonCountExport_label = QtWidgets.QLabel("Export Individual Timeseries as: ")
        self.photonIntensityTraceExportCSV = QtWidgets.QPushButton('.csv')
        self.photonIntensityTraceExportTIF = QtWidgets.QPushButton('.tiff')

        self.left_panel_third_row_btns = QtWidgets.QHBoxLayout()
        self.save_int_timeSeries_csv = QtWidgets.QPushButton('Export all Timeseries as .csv')
        self.save_int_timeSeries_tif = QtWidgets.QPushButton('Export all Timeseries as .tiff')


        self.left_panel_third_row_btns.addWidget(self.save_int_timeSeries_csv)
        self.left_panel_third_row_btns.addWidget(self.save_int_timeSeries_tif)
        self.left_panel_third_row_btns.addStretch()

        self.save_int_timeSeries_csv.clicked.connect(self.save_all_PhotonBinFnCSV)
        self.save_int_timeSeries_tif.clicked.connect(self.save_all_PhotonBinFnTIF)
    

        self.cbx = comboBoxSp(self)
        self.cbx.type ='PhotonCount'
        self.updateCombo()

        self.left_panel_top_btns.addWidget(self.cbx)
        self.left_panel_top_btns.addStretch()

        self.left_panel_export_fns = QtWidgets.QGroupBox('Export Binned Intensities')
        self.left_panel_second_row_btns.addWidget(self.photonCountText)
        self.left_panel_second_row_btns.addWidget(self.photonCountEdit)
        self.left_panel_second_row_btns.addWidget(self.photonCountExport_label)
        self.left_panel_second_row_btns.addWidget(self.photonIntensityTraceExportCSV)
        self.left_panel_second_row_btns.addWidget(self.photonIntensityTraceExportTIF)
        self.left_panel_second_row_btns.addStretch()

        self.photonIntensityTraceExportCSV.clicked.connect(self.reprocessPhotonBinFnCSV)
        self.photonIntensityTraceExportTIF.clicked.connect(self.reprocessPhotonBinFnTIF)

        self.left_panel.addLayout(self.left_panel_top_btns)
        
        self.left_panel_vertical_export = QtWidgets.QVBoxLayout()

        self.left_panel_export_fns.setLayout(self.left_panel_vertical_export)
        self.left_panel_vertical_export.addLayout(self.left_panel_second_row_btns)
        self.left_panel_vertical_export.addLayout(self.left_panel_third_row_btns)
        



        self.left_panel.addWidget(self.left_panel_export_fns)

        


        #LEFT PANEL centre
        self.left_panel_centre = QtWidgets.QHBoxLayout()

        #LEFT PANEL centre right
        self.left_panel_centre_right = QtWidgets.QVBoxLayout()
        
        self.left_panel.addLayout(self.left_panel_centre)
        
        self.left_panel_centre.addWidget(self.modelTab)
        self.left_panel_centre.addLayout(self.left_panel_centre_right)
        self.left_panel_centre.addStretch()
        
        #LEFT PANEL bottom
        self.left_panel_bottom = QtWidgets.QVBoxLayout()
        self.left_panel_bottom_fig = QtWidgets.QHBoxLayout()
        self.left_panel_bottom.addLayout(self.left_panel_bottom_fig)
        self.left_panel_bottom_fig.addWidget(self.canvas5)
        self.left_panel_bottom_fig.addStretch()
        
        self.left_panel.addLayout(self.left_panel_bottom)
        #LEFT PANEL bottom buttons
        self.left_panel_bottom_btns = QtWidgets.QHBoxLayout()
        self.left_panel_bottom.addLayout(self.left_panel_bottom_btns)
        self.left_panel_bottom_btns.addWidget(self.normPlot)
        self.left_panel_bottom_btns.addWidget(self.replot_btn2)
        self.left_panel_bottom_btns.addWidget(self.winIntText)

        self.left_panel_bottom_btns.addWidget(self.winIntEdit)
        self.left_panel_bottom_btns.addWidget(self.reprocess_btn2)
        #

        self.left_panel_bottom_btns.addStretch()


        self.left_panel_centre_right.setSpacing(2)
        self.left_panel_centre_right.addWidget(self.openFile)
        
        self.left_panel_centre_right.addWidget(self.globalText)
        
        self.left_panel_centre_right.addWidget(self.NsubText)
        self.left_panel_centre_right.addWidget(self.NsubEdit)
        self.left_panel_centre_right.addWidget(self.NcascStartText)
        self.left_panel_centre_right.addWidget(self.NcascStartEdit)
        self.left_panel_centre_right.addWidget(self.NcascEndText)
        self.left_panel_centre_right.addWidget(self.NcascEndEdit)
        self.left_panel_centre_right.addWidget(self.reprocess_btn)

        self.left_panel_bottom_bottom = QtWidgets.QHBoxLayout()
        self.image_status_text = QtWidgets.QStatusBar()
        self.left_panel_bottom_bottom.addWidget(self.image_status_text)
        self.left_panel.addLayout(self.left_panel_bottom_bottom)

        
        self.left_panel_centre_right.setAlignment(QtCore.Qt.AlignTop)
        self.right_panel.addWidget(self.canvas1)
        self.right_panel.addLayout(correlationBtns)
        self.right_panel.addWidget(self.modelTab2)
        self.right_panel.addStrut(800)

        
        
        correlationBtns.addWidget(self.replot_btn)
        correlationBtns.addWidget(self.folderSelect_btn)
        correlationBtns.addWidget(self.saveAll_btn)
        correlationBtns.addWidget(self.toolbar1)
        correlationBtns.setAlignment(QtCore.Qt.AlignLeft)
        self.left_panel.addStretch()
        tableAndBtns.addWidget(self.modelTab2)
        
        self.setLayout(main_layout)
        main_layout.addLayout(self.left_panel)
        main_layout.addStretch()
        #main_layout.addLayout(self.centre_panel)
        main_layout.addLayout(self.right_panel)
        #main_layout.addLayout(self.right_panel)


        

        self.plt1= self.figure1.add_subplot(311)
        self.plt2= self.figure1.add_subplot(312)
        self.plt3= self.figure1.add_subplot(313)
        self.plt4= self.figure4.add_subplot(111)
        self.plt5= self.figure5.add_subplot(111)

        

        self.plt1.format_coord = lambda x, y: ''
        self.plt2.format_coord = lambda x, y: ''
        self.plt3.format_coord = lambda x, y: ''

        
   

        self.plt1.set_title('Correlation', fontsize=12)
        self.plt1.set_ylabel('Auto-correlation CH0 (tau)', fontsize=8)
        self.plt2.set_ylabel('Auto-correlation CH1 (tau)', fontsize=8)
        self.plt3.set_ylabel('Cross-correlation CH01 (tau)', fontsize=8)
        self.figure4.suptitle('Photon Count', fontsize=12)
        self.figure5.suptitle('Photon Decay Curve', fontsize=12)
        self.plt5.a = Annotate(self,self.par_obj,self.TGScrollBoxObj)
    def update_correlation_parameters(self):
        self.par_obj.NcascStart = int(self.NcascStartEdit.text())
        self.par_obj.NcascEnd = int(self.NcascEndEdit.text())
        self.par_obj.Nsub = int(self.NsubEdit.text())
        self.par_obj.winInt = float(self.winIntEdit.text())
        self.par_obj.photonCountBin = float(self.photonCountEdit.text())
        
    def plotDataQueueFn(self):
        self.plt1.cla()
        self.plt2.cla()
        self.plt3.cla()
        
        
        self.plt5.clear()
        self.canvas1.draw()
        
        self.canvas5.draw()
        for x in range(0, self.par_obj.numOfLoaded):
            if(self.label.objCheck[x].isChecked() == True):
                
                self.plot(self.par_obj.objectRef[x])
        for y in range(0, self.par_obj.subNum):

            if(self.label.objCheck[y+x+1].isChecked() == True):
                
                self.plot(self.par_obj.subObjectRef[y])
        self.plt5.ax = plt.gca()
        self.plt5.a.freshDraw()
    def save_all_PhotonBinFnCSV(self):
        """Reprocess all images and export .csv images."""
        for x in range(0, self.par_obj.numOfLoaded):
            self.reprocessPhotonBinFn('CSV',x)           
        for y in range(0, self.par_obj.subNum):
            self.reprocessPhotonBinFn('CSV',x+y+1)
        
    def save_all_PhotonBinFnTIF(self):
        """Reprocess all images and export .tiff images."""
        for x in range(0, self.par_obj.numOfLoaded):
            self.reprocessPhotonBinFn('TIFF',x)           
        for y in range(0, self.par_obj.subNum):
            self.reprocessPhotonBinFn('TIFF',x+y+1)

    def reprocessPhotonBinFnCSV(self):
        self.reprocessPhotonBinFn('CSV',index)
    def reprocessPhotonBinFnTIF(self):
        self.reprocessPhotonBinFn('TIFF',index)

    def reprocessPhotonBinFn(self,type_ex,index):
        #Time series of photon counts. For visualisation.
        
        
        objId = None


        if index < self.par_obj.numOfLoaded:
            objId = self.par_obj.objectRef[index]
            objId.timeSeries1,objId.timeSeriesScale1 = delayTime2bin(np.array(objId.trueTimeArr)/1000000,np.array(objId.subChanArr),objId.ch_present[0],self.par_obj.photonCountBin)
            if objId.numOfCH == 2:
                objId.timeSeries2,objId.timeSeriesScale2 = delayTime2bin(np.array(objId.trueTimeArr)/1000000,np.array(objId.subChanArr),objId.ch_present[1],self.par_obj.photonCountBin)
        else:
            objId = self.par_obj.subObjectRef[index-self.par_obj.numOfLoaded]
            objId.timeSeries1,objId.timeSeriesScale1 = delayTime2bin(np.array(objId.trueTimeArr)/1000000,np.array(objId.subChanArr),objId.ch_present[0],self.par_obj.photonCountBin)
            if objId.numOfCH == 2:
                objId.timeSeries2,objId.timeSeriesScale2 = delayTime2bin(np.array(objId.trueTimeArr)/1000000,np.array(objId.subChanArr),objId.ch_present[1],self.par_obj.photonCountBin)
        
        
        
        if type_ex == 'CSV':
            f = open(self.folderOutput.filepath+'/'+objId.name+'_intensity.csv', 'w')
            f.write('version,'+str(2)+'\n')
            f.write('numOfCH,'+str(objId.numOfCH)+'\n')
            f.write('time(ms), intensityCH0, intensityCH1\n')

            if objId == None:
                return

            
            if objId.numOfCH == 1:
                
                for x in range(0,objId.timeSeries1.__len__()):
                    f.write(str(objId.timeSeriesScale1[x])+','+str(objId.timeSeries1[x])+ '\n')
            if objId.numOfCH == 2:
                for x in range(0,objId.timeSeries1.__len__()):
                    f.write(str(objId.timeSeriesScale2[x])+','+str(objId.timeSeries1[x])+','+str(objId.timeSeries2[x])+ '\n')

            
        
        if type_ex == 'TIFF':
            height = objId.timeSeries1.__len__()
            if objId.numOfCH ==1:
                
                    export_im =np.zeros((height,1))
                    export_im[:,0] = np.array(objId.timeSeries1).astype(np.float32)
                    metadata = dict(microscope='', shape=[height,1], dtype=export_im.dtype.str)
                    metadata = json.dumps(metadata)
                    tif_fn.imsave(self.folderOutput.filepath+'/'+objId.name+'_raw.tiff', export_im.astype(np.float32), description=metadata)
       

            if objId.numOfCH ==2:
                
                    export_im =np.zeros((height,1))
                    export_im[:,0] =  np.array(objId.timeSeries1).astype(np.float32)
                    metadata = dict(microscope='', shape=[height,1], dtype=export_im.dtype.str)
                    metadata = json.dumps(metadata)
                    tif_fn.imsave(self.folderOutput.filepath+'/'+objId.name+'_CH0_raw.tiff', export_im.astype(np.float32), description=metadata)
                    export_im =np.zeros((height,1))
                    export_im[:,0] =  np.array(objId.timeSeries2).astype(np.float32)
                    tif_fn.imsave(self.folderOutput.filepath+'/'+objId.name+'_CH1_raw.tiff', export_im.astype(np.float32), description=metadata)
       
                    

        
        
        
    def save_raw_carpet_fn(self):
        """Saves the carpet raw data to an image file"""
        
                     
    def reprocessDataFn(self):

        for i in range(0, self.par_obj.numOfLoaded):
                    self.par_obj.objectRef[i].processData()
        for i in range(0, self.par_obj.subNum):
                    self.par_obj.subObjectRef[i].processData()

        self.plotDataQueueFn();
        self.plot_PhotonCount(self.par_obj.numOfLoaded-1)
        self.updateCombo()
    def updateCombo(self):
        """Updates photon counting combox box"""
        self.cbx.clear()
        #Populates comboBox with datafiles to which to apply the time-gating.
        for b in range(0,self.par_obj.numOfLoaded):
                self.cbx.addItem("Data: "+str(b), b)
        for i in range(0, self.par_obj.subNum):
                self.cbx.addItem("subData: "+str(b+i+1), b+i+1)
    def plot_PhotonCount(self,index):
        """Plots the photon counting"""

        if index < self.par_obj.numOfLoaded:
            object = self.par_obj.objectRef[index]
        else:
            object = self.par_obj.subObjectRef[index-self.par_obj.numOfLoaded]
        self.plt4.clear()
        self.canvas4.draw()
        
        self.plt4.bar(np.array(object.timeSeriesScale1),np.array(object.timeSeries1), float(object.photonCountBin), color=object.color,linewidth=0)
        if object.numOfCH ==  2:
            self.plt4.bar(np.array(object.timeSeriesScale2),-1*np.array(object.timeSeries2).astype(np.float32),float(object.photonCountBin),color="grey",linewidth=0,edgecolor = None)
       
        self.figure4.subplots_adjust(left=0.15,bottom=0.25)
        self.plt4.set_xlim(0,object.timeSeriesScale1[-1])
        self.plt4.set_xlabel('Time (ms)', fontsize=12)
        self.plt4.set_ylabel('Photon counts', fontsize=12)
        self.plt4.xaxis.grid(True,'minor')
        self.plt4.xaxis.grid(True,'major')
        self.plt4.yaxis.grid(True,'minor')
        self.plt4.yaxis.grid(True,'major')
        self.canvas4.draw()

            
    def plot(self,object):
        ''' plot some random stuff '''

        autotime = object.autotime
        
        auto = object.autoNorm
        corrText = 'Auto-correlation'
        
        
        subDTimeMax = object.subDTimeMax
        subDTimeMin = object.subDTimeMin
        
        
        self.plt1.plot(autotime,auto[:,0,0],object.color)
        self.plt1.set_xscale('log')
        self.plt1.set_xlim([0, np.max(autotime)])
       
        self.plt1.set_xlabel('Tau (ms)', fontsize=12)
        self.plt1.set_ylabel('Auto-correlation CH0 (tau)', fontsize=8)
        self.plt1.xaxis.grid(True,'minor')
        self.plt1.xaxis.grid(True,'major')
        self.plt1.yaxis.grid(True,'minor')
        self.plt1.yaxis.grid(True,'major')
        self.plt2.set_ylabel('Auto-correlation CH1 (tau)', fontsize=8)
        self.plt2.xaxis.grid(True,'minor')
        self.plt3.set_ylabel('Cross-correlation CH01 (tau)', fontsize=8)
        self.plt3.xaxis.grid(True,'minor')
        if object.numOfCH ==  2:
            self.plt2.plot(autotime,auto[:,1,1],object.color)
            self.plt2.set_xscale('log')
            self.plt2.set_xlim([0, np.max(autotime)])
            
            self.plt2.set_xlabel('Tau (ms)', fontsize=12)
            self.plt2.xaxis.grid(True,'minor')
            self.plt2.xaxis.grid(True,'major')
            self.plt2.yaxis.grid(True,'minor')
            self.plt2.yaxis.grid(True,'major')
            
            self.plt3.plot(autotime,auto[:,0,1],object.color)
            self.plt3.set_xscale('log')
            self.plt3.set_xlim([0, np.max(autotime)])
         
            self.plt3.set_xlabel('Tau (ms)', fontsize=12)
            
            self.plt3.xaxis.grid(True,'minor')
            self.plt3.xaxis.grid(True,'major')
            self.plt3.yaxis.grid(True,'minor')
            self.plt3.yaxis.grid(True,'major')
            
            

        if object.type == 'mainObject':
            decayScale1 = object.decayScale1
            if object.numOfCH ==  2:
                decayScale2 = object.decayScale2
            if self.normPlot.isChecked() == True:
                photonDecayCh1 = object.photonDecayCh1Norm
                if object.numOfCH ==  2:
                    photonDecayCh2 = object.photonDecayCh2Norm
                axisText = 'No. of photons (Norm)'
            else:
                photonDecayCh1 = object.photonDecayCh1
                if object.numOfCH ==  2:
                    photonDecayCh2 = object.photonDecayCh2
                axisText = 'No. of photons '
            self.plt5.plot(decayScale1, photonDecayCh1,object.color)
            if object.numOfCH ==  2:
                self.plt5.plot(decayScale2, photonDecayCh2,object.color,linestyle='dashed')
            self.figure5.subplots_adjust(left=0.1,right=0.95, bottom=0.20,top=0.90)
            if object.resolution != None:
                self.plt5.set_xlabel('Time channels (1 ='+str(np.round(object.resolution,4))+' ns)', fontsize=12)
            else:
                self.plt5.set_xlabel('Time channels (No micro time in file))', fontsize=12)
            self.plt5.set_ylabel(axisText, fontsize=12)
            self.plt5.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
            self.plt5.xaxis.grid(True,'minor')
            self.plt5.xaxis.grid(True,'major')
            self.plt5.yaxis.grid(True,'minor')
            self.plt5.yaxis.grid(True,'major')
            self.canvas5.draw()
        # refresh canvas
        self.canvas1.draw()
        
        
    def saveDataQueue(self):
       
        
        for obj in self.par_obj.objectRef:
            self.saveFile(obj)
        for obj in self.par_obj.subObjectRef:
            self.saveFile(obj)
    def saveFile(self,objId):
        """Save files as .csv"""
        
            
            
                
            
        f = open(self.folderOutput.filepath+'/'+objId.name+'_correlation.csv', 'w')
        f.write('version,'+str(2)+'\n')
        f.write('numOfCH,'+str(objId.numOfCH)+'\n')
        f.write('type, point\n')
        
        if objId.numOfCH == 1:
            f.write('ch_type,'+str(0)+'\n')
            f.write('kcount,'+str(objId.kcount_CH1)+'\n')
            f.write('numberNandB,'+str(objId.numberNandBCH0)+'\n')
            f.write('brightnessNandB,'+str(objId.brightnessNandBCH0)+'\n')
            f.write('carpet pos, 0 \n')
            f.write('pc, 0\n');
            f.write('Time (ms), CH0 Auto-Correlation\n')
            for x in range(0,objId.autotime.shape[0]):
                f.write(str(objId.autotime[x][0])+','+str(objId.autoNorm[x,0,0])+ '\n')
            f.write('end\n')
        if objId.numOfCH == 2:
            f.write('ch_type, 0 ,1, 2\n')
            f.write('kcount,'+str(objId.kcount_CH1)+','+str(objId.kcount_CH2)+'\n')
            f.write('numberNandB,'+str(objId.numberNandBCH0)+','+str(objId.numberNandBCH1)+'\n')
            f.write('brightnessNandB,'+str(objId.brightnessNandBCH0)+','+str(objId.brightnessNandBCH1)+'\n')
            f.write('CV,'+str(objId.CV)+','+str(objId.CV)+','+str(objId.CV)+'\n')
            f.write('carpet pos, 0 \n')
            
            f.write('pc, 0\n');
            f.write('Time (ms), CH0 Auto-Correlation, CH1 Auto-Correlation, CH01 Cross-Correlation\n')
            for x in range(0,objId.autotime.shape[0]):
                f.write(str(objId.autotime[x][0])+','+str(objId.autoNorm[x,0,0])+','+str(objId.autoNorm[x,1,1])+','+str(objId.autoNorm[x,0,1])+'\n')
            f.write('end\n')
                





        

        
        

        
class checkBoxSp(QtWidgets.QCheckBox):
    def __init__(self):
        QtWidgets.QCheckBox.__init__(self)
        self.obj = []
        self.type = []
        self.name =[]
    def updateChecked(self):
            
                self.obj.plotOn = self.isChecked()
class checkBoxSp2(QtWidgets.QCheckBox):
    def __init__(self, win_obj, par_obj):
        QtWidgets.QCheckBox.__init__(self, parent)
        self.obj = []
        self.type = []
        self.name =[]
        self.stateChanged.connect(self.__changed)
    def __changed(self,state):
        
        if state == 2:
            if self.obj.carpetDisplay == 0:
                self.obj.CH0AutoFn()
            if self.obj.carpetDisplay == 1:
                self.obj.CH1AutoFn()
            if self.obj.carpetDisplay == 2:
                self.obj.CH01CrossFn()
        if state == 0:
            if self.obj.carpetDisplay == 3:
                self.obj.CH0AutoFn()
            if self.obj.carpetDisplay == 4:
                self.obj.CH1AutoFn()
            if self.obj.carpetDisplay == 5:
                self.obj.CH01CrossFn()
            


            #plotDataQueueFn()
class lineEditSp(QtWidgets.QLineEdit):
    def __init__(self, txt, win_obj):
        QtWidgets.QLineEdit.__init__(self, txt)
        self.editingFinished.connect(self.__handleEditingFinished)
        self.textChanged.connect(self.__handleTextChanged)
        self.obj = []
        self.type = []
        self.TGid =[]
        self.win_obj = win_obj
        
    def __handleEditingFinished(self):
        
        if(self.type == 'tgt0' ):
            self.win_obj.TGScrollBoxObj.x0[self.TGid] = float(self.text())
            self.win_obj.plt5.a.redraw()
            #plotDataQueueFn()
        if(self.type == 'tgt1' ):
            self.win_obj.TGScrollBoxObj.x1[self.TGid] = float(self.text())
            self.win_obj.plt5.a.redraw()
        if(self.type == 'name' ):
            self.obj.name = str(self.text())
        if(self.type == 'ncasc' or self.type =='ncascEnd' or self.type =='nsub' or self.type =='int_bin'):
            self.win_obj.update_correlation_parameters()
    def __handleTextChanged(self):
        if self.type == 'int_bin':
            self.win_obj.update_correlation_parameters()


           
            
      


            
class comboBoxSp(QtWidgets.QComboBox):
    def __init__(self,win_obj):
        QtWidgets.QComboBox.__init__(self,parent=None)
        self.activated[str].connect(self.__activated) 
        self.obj = []
        self.TGid =[]
        self.type = []
        self.win_obj = win_obj
    def __activated(self,selected):
        
        if self.type == 'AUG':
            if self.currentIndex() == 1:
                self.obj.aug = 'PIE'
                self.obj.PIE = self.currentIndex();
                self.obj.processData()
                self.win_obj.plotDataQueueFn()
            if self.currentIndex() == 2:
                self.obj.aug = 'PIE'
                self.obj.PIE = self.currentIndex();
                self.obj.processData()
                self.win_obj.plotDataQueueFn()
            if self.currentIndex() == 3:
                self.obj.aug = 'rmAP'
                self.obj.processData()
                self.win_obj.plotDataQueueFn()
        if self.type == 'PhotonCount':
            self.win_obj.plot_PhotonCount(self.currentIndex());

class pushButtonSp(QtWidgets.QPushButton):
    def __init__(self, win_obj, par_obj):
        QtWidgets.QPushButton.__init__(self)
        self.clicked.connect(self.__activated)
        self.par_obj = par_obj;
        self.win_obj = win_obj;
        #Which list is should look at.
        self.objList = []
        self.xmin = []
        self.xmax =[]
        self.TGid = []
    def __activated(self):
        if self.type =='photoCrr':
            self.par_obj.clickedS1 = self.xmin
            self.par_obj.clickedS2 = self.xmax
            self.win_obj.bleachInt.create_main_frame()
        if self.type =='remove':
            self.par_obj.TGnumOfRgn -= 1
            self.win_obj.TGScrollBoxObj.rect.pop(self.TGid)
            self.win_obj.TGScrollBoxObj.x0.pop(self.TGid)
            self.win_obj.TGScrollBoxObj.x1.pop(self.TGid)
            self.win_obj.TGScrollBoxObj.facecolor.pop(self.TGid)
            self.win_obj.modelTab.clear()
            self.win_obj.TGScrollBoxObj.generateList()
            self.win_obj.plotDataQueueFn()
        if self.type =='create':
            self.xmin =  self.win_obj.TGScrollBoxObj.x0[self.TGid]
            self.xmax =  self.win_obj.TGScrollBoxObj.x1[self.TGid]

            if (self.objList.currentIndex() == self.par_obj.objectRef.__len__()):
                for i in range(0,self.par_obj.objectRef.__len__()):
                    picoSub = subPicoObject(self.par_obj.objectRef[i],self.xmin,self.xmax,self.TGid,self.par_obj)
                    self.win_obj.updateCombo()
                    self.par_obj.subNum = self.par_obj.subNum+1
            else:
                picoSub = subPicoObject(self.par_obj.objectRef[self.objList.currentIndex()],self.xmin,self.xmax,self.TGid,self.par_obj)          
                self.win_obj.updateCombo()
                self.par_obj.subNum = self.par_obj.subNum+1
            self.win_obj.label.generateList()
            self.win_obj.plotDataQueueFn()
            self.win_obj.updateCombo()
class pushButtonSp2(QtWidgets.QPushButton):
    """Save button"""
    def __init__(self, txt, win_obj, par_obj):
        QtWidgets.QPushButton.__init__(self,txt)
        self.clicked.connect(self.__clicked)
        self.win_obj = win_obj;
        self.par_obj = par_obj;
        self.corr_obj =[]
    def __clicked(self):
        self.win_obj.saveFile(self.corr_obj)





class scrollBox():
    def __init__(self, win_obj, par_obj):
        self.win_obj = win_obj
        self.par_obj = par_obj
        self.par_obj.numOfLoaded = 0
        self.par_obj.subNum =0
        self.generateList()
    def generateList(self):
        
        self.obj =[];
        self.objCheck =[];

        
        
        for i in range(0, self.par_obj.numOfLoaded):
            self.win_obj.modelTab2.setRowCount(i+1)
            #Represents each y
            self._l=QtWidgets.QHBoxLayout()
            self.obj.append(self._l)

            
            #HTML text
            a =baseList()
            a.listId = i
            a.setText('<HTML><p style="color:'+str(self.par_obj.colors[i % len(self.par_obj.colors)])+';margin-top:0">Data '+str(i)+': </p></HTML>')
            

            self.win_obj.modelTab2.setCellWidget(i, 0, a)

            #Line edit for each entry in the file list
            lb = lineEditSp(self.win_obj, self.par_obj)
            
            lb.type ='name'
            lb.obj = self.par_obj.objectRef[i]
            lb.setText(self.par_obj.objectRef[i].name);
            self.win_obj.modelTab2.setCellWidget(i, 1, lb)

            
            

            cb = checkBoxSp()
            cb.setChecked(self.par_obj.objectRef[i].plotOn)
            cb.obj = self.par_obj.objectRef[i]
            cb.stateChanged.connect(cb.updateChecked)
            self.win_obj.modelTab2.setCellWidget(i, 2, cb)


            #cbx = comboBoxSp(self.win_obj)
            #Populates comboBox with datafiles to which to apply the time-gating.
            
            #cbx.addItem("norm", 0)
            #cbx.addItem("PIE-CH-0", 1)
            #cbx.addItem("PIE-CH-1", 2)
            #cbx.addItem("rm AfterPulse", 3)
            #cbx.obj = self.par_obj.objectRef[i]
            #cbx.type = 'AUG'
            #Adds an all option to the combobox.lfkk
            
            #cbx.TGid = i
            #self.win_obj.modelTab2.setCellWidget(i, 3, cbx)

            
            #Adds save button to the file.
            sb = pushButtonSp2('save corr. file (.csv)', self.win_obj, self.par_obj)
            sb.corr_obj = self.par_obj.objectRef[i]
            self.win_obj.modelTab2.setCellWidget(i, 3, sb)

            b = baseList()
            b.setText('<HTML><p style="margin-top:0">'+str(self.par_obj.objectRef[i].ext)+' file :'+str(self.par_obj.data[i])+' </p></HTML>')
            self.win_obj.modelTab2.setCellWidget(i, 4, b)
            
            
            self.objCheck.append(cb)
            j = i+1
        for i in range(0,self.par_obj.subNum):
            self.win_obj.modelTab2.setRowCount(j+i+1)
            
            a =baseList()
            a.listId = i
            a.setText('<HTML><p style="color:'+str(self.par_obj.subObjectRef[i].color)+';margin-top:0">TG-'+str(self.par_obj.subObjectRef[i].TGid)+': Data:'+str(self.par_obj.subObjectRef[i].parentUnqID)+'-xmin:'+str(round(self.par_obj.subObjectRef[i].xmin,1))+'-xmax:'+str(round(self.par_obj.subObjectRef[i].xmax,1))+' </p></HTML>')
            self.win_obj.modelTab2.setCellWidget(i+j, 0, a)
            
            #Line edit for each entry in the file list
            lb =lineEditSp(self.win_obj, self.par_obj)
            lb.type ='name'
            lb.obj = self.par_obj.subObjectRef[i]
            lb.setText(self.par_obj.subObjectRef[i].name);
            self.win_obj.modelTab2.setCellWidget(i+j, 1, lb)
            #Main text for file menu.


            #Adds the plot checkBox:
            cb = checkBoxSp()
            cb.setChecked(self.par_obj.subObjectRef[i].plotOn)
            cb.obj = self.par_obj.subObjectRef[i]
            cb.stateChanged.connect(cb.updateChecked)
            self.win_obj.modelTab2.setCellWidget(i+j, 2, cb)

            
            #Adds save button to the file.
            sb = pushButtonSp2('save corr. file (.csv)', self.win_obj, self.par_obj)
            sb.corr_obj = self.par_obj.subObjectRef[i]
            
            self.win_obj.modelTab2.setCellWidget(i+j, 3, sb)

            b = baseList()
            b.setText('<HTML><p style="margin-top:0">'+str(self.par_obj.subObjectRef[i].ext)+' file :'+str(self.par_obj.subObjectRef[i].filepath)+' </p></HTML>')
            self.win_obj.modelTab2.setCellWidget(i+j, 4, b)

            #Adds the checkBox to a list.
            self.objCheck.append(cb)
        

class TGscrollBox():
    #Generates scroll box for time-gating data.
    def __init__(self, win_obj, par_obj):
        
        self.win_obj = win_obj
        self.par_obj = par_obj
        self.par_obj.TGnumOfRgn = 0
        self.x0 =[]
        self.x1 =[]
        self.facecolor =[]
        self.TGid = []
        self.rect =[]

    def generateList(self):
        
        for i in range(0, self.par_obj.TGnumOfRgn):
            self.win_obj.modelTab.setRowCount(i+1)
            
            
            txt2 = QtWidgets.QLabel()
            txt2.setText('<HTML><p style="color:'+str(self.par_obj.colors[i % len(self.par_obj.colors)])+';margin-top:0">tg1:</p></HTML>')
            self.win_obj.modelTab.setCellWidget(i, 0, txt2)


            lb1 = lineEditSp('', self.win_obj)
            lb1.setMaxLength(5)
            lb1.setFixedWidth(40)
            lb1.setText(str(self.win_obj.TGScrollBoxObj.x0[i]))
            lb1.type = 'tgt0'
            lb1.TGid = i
            self.win_obj.modelTab.setCellWidget(i, 1, lb1)

            txt3 = QtWidgets.QLabel()
            txt3.setText('<HTML><p style="color:'+str(self.par_obj.colors[i % len(self.par_obj.colors)])+';margin-top:0">tg2:</p></HTML>')
            self.win_obj.modelTab.setCellWidget(i, 2, txt3)
            
            

            lb2 = lineEditSp('', self.win_obj)
            lb2.setMaxLength(5)
            lb2.setFixedWidth(40)
            lb2.setText(str(self.win_obj.TGScrollBoxObj.x1[i]))
            lb2.type = 'tgt1'
            lb2.TGid = i
            self.win_obj.modelTab.setCellWidget(i, 3, lb2)
            

            cbx = comboBoxSp(self.win_obj)
            #Populates comboBox with datafiles to which to apply the time-gating.
            for b in range(0,self.par_obj.numOfLoaded):
                cbx.addItem("Data: "+str(b), b)
            #Adds an all option to the combobox.lfkk
            cbx.addItem("All",b+1)
            cbx.TGid = i
            self.win_obj.modelTab.setCellWidget(i, 4, cbx)
            
            cbtn = pushButtonSp(self.win_obj, self.par_obj)
            cbtn.setText('Create')
            cbtn.type ='create'
            cbtn.TGid = i
            cbtn.xmin = self.win_obj.TGScrollBoxObj.x0[i]
            cbtn.xmax = self.win_obj.TGScrollBoxObj.x1[i]
            self.win_obj.modelTab.setCellWidget(i, 5, cbtn)
            #Make sure the btn knows which list it is connected to.
            cbtn.objList = cbx

            rmbtn = pushButtonSp(self.win_obj, self.par_obj)
            rmbtn.setText('X')
            rmbtn.TGid = i
            rmbtn.type = 'remove'
            self.win_obj.modelTab.setCellWidget(i, 6, rmbtn)

class ParameterClass():
    def __init__(self):
        
        #Where the data is stored.
        self.data = []
        self.objectRef =[]
        self.subObjectRef =[]
        self.colors = ['blue','green','red','cyan','magenta','yellow','black']