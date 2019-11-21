import wx
import sys
import time
import matplotlib.pyplot as plt
from canvas import Canvas, ResultCanvas
from calculateloop import Calculate_loop, x_y_arrays_creating
import os
import json
from datetime import datetime
import winsound
from wx.lib.pubsub import pub
import numpy as np
import wx.lib.scrolledpanel as scrolled

PLOT_SCREENSHOT_DIR = 'Plot_screenshot'
PLOT_JSON_DIR = 'Plot_data'

ID_ALWAYS_ON_TOP = 0
ID_SAVE_POSITION = 1
ID_SHOW_HIDE_CANVAS = 3

ID_SHOW_MAIN_PAGE = 5
ID_SHOW_SECONDARY_PAGE = 6

ID_CANVAS_QUARTER_1 = 10
ID_CANVAS_QUARTER_4 = 11
ID_CANVAS_MENU = 12

DEFAULT_MASS = 0
DEFAULT_RADIUS = 10
DEFAULT_GAMMA = 0
DEFAULT_DIMENSION = 30
DEFAULT_POTENTIAL = True
DEFAULT_EIGENVALUE = 'First order'
DEFAULT_METHOD = 'Main method'
DEFAULT_SIGMA = 'Positive'

class MainFrame(wx.Frame):

    def __init__(self, *args, **kw):
        super(MainFrame, self).__init__(*args, **kw)
        self.multiPanel = wx.Panel(self)

        self.panel = wx.Panel(self.multiPanel)
        self.resultPanel = wx.Panel(self.multiPanel)
        self.onPanel = True
        self.onResultPanel = False
        self.currentPage = 'Main'
        self.filePath = ''
        icon = wx.Icon('bitmaps/icon.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        self.panel.SetBackgroundColour('')
        self.menu_bar = wx.MenuBar()
        self.fig = plt.figure(figsize=(7, 6))
        self.canvas = Canvas(self.panel, -1, self.fig)
        self.canvasShown = True
        self.canvas_drawn = [False, False]
        self.calculate_running = False
        self.taking_data = False
        self.taking_data_successfull = False
        self.CreateStatusBar()
        self.SetStatusText(text='Waiting for arguments.')

        # Default values
        self.method_choices = ['Main method', 'Alternative method']
        self.sigma_choices = ['Positive', 'Negative']
        self.eigenvalue_choices = ['First order', 'Second order', 'Third order']
        self.potential_choices = ['True', 'False']
        self.METHOD = DEFAULT_METHOD
        self.SIGMA = DEFAULT_SIGMA
        self.MASS = DEFAULT_MASS
        self.RADIUS = DEFAULT_RADIUS
        self.GAMMA = DEFAULT_GAMMA
        self.N_DIMENSION = DEFAULT_DIMENSION
        self.M_DIMENSION = DEFAULT_DIMENSION
        self.POTENTIAL = DEFAULT_POTENTIAL
        self.EIGENVALUE = DEFAULT_EIGENVALUE
        self.VALUE = []
        self.VALUE_test = []
        self.VECTOR = []
        self.VECTOR_test = []
        self.quarterNumber = 1
        self.settingsPanel = scrolled.ScrolledPanel(self.panel, -1, style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER)
        self.settingsPanel.SetAutoLayout(1)
        self.settingsPanel.SetupScrolling()


        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_right_sizer = wx.BoxSizer(wx.VERTICAL)
        self.left_sizer = wx.BoxSizer(wx.VERTICAL)
        #self.right_sizer = wx.BoxSizer(wx.VERTICAL)
        self.settings_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Canvas
        self.canvas_box = wx.BoxSizer()
        self.canvas_box.Add(self.canvas,2,wx.EXPAND)

        # Settings
        self.settings_text = wx.StaticText(self.panel, label='Settings')
        self.settings_text.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))

        # Method
        self.method_box = wx.StaticBox(self.settingsPanel, label='Method:')
        self.method_sizer_hor = wx.StaticBoxSizer(self.method_box, wx.HORIZONTAL)
        self.method_sizer = wx.BoxSizer(wx.VERTICAL)
        self.method_sizer_hor.AddSpacer(4)
        self.method_sizer_hor.Add(self.method_sizer)
        self.method_choice_static_text = wx.StaticText(self.settingsPanel, label='Select method:')
        self.method_choice_box = wx.ComboBox(self.settingsPanel, size=(135, 22), value=str(self.METHOD),
                                                choices=self.method_choices)
        self.method_choice_box.SetEditable(False)
        self.method_choice_box.Bind(wx.EVT_COMBOBOX, self.onMethodComboBox)

        # Sigma
        self.sigma_box = wx.StaticBox(self.settingsPanel, label='Sigma:')
        self.sigma_sizer_hor = wx.StaticBoxSizer(self.sigma_box, wx.HORIZONTAL)
        self.sigma_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sigma_sizer_hor.AddSpacer(5)
        self.sigma_sizer_hor.Add(self.sigma_sizer)
        self.sigma_choice_static_text = wx.StaticText(self.settingsPanel, label='Select sigma:')
        self.sigma_choice_box = wx.ComboBox(self.settingsPanel, size=(105, 22), value=str(self.SIGMA),
                                             choices=self.sigma_choices)
        self.sigma_choice_box.SetEditable(False)
        self.sigma_choice_box.Bind(wx.EVT_COMBOBOX, self.onSigmaComboBox)

        # Mass
        self.mass_box = wx.StaticBox(self.settingsPanel, label='Magnetic Quantum Number: ')
        self.mass_sizer_hor = wx.StaticBoxSizer(self.mass_box, wx.HORIZONTAL)
        self.mass_sizer = wx.BoxSizer(wx.VERTICAL)
        self.mass_sizer_hor.AddSpacer(4)
        self.mass_sizer_hor.Add(self.mass_sizer)
        self.mass_choice_static_text_1 = wx.StaticText(self.settingsPanel, label='What MQN do you want to use?')
        self.mass_choice_static_text_2 = wx.StaticText(self.settingsPanel, label='Select MQN:')
        self.mass_choice_box = wx.TextCtrl(self.settingsPanel, size=(50, 18), style=wx.TE_PROCESS_ENTER)
        self.mass_choice_box.Bind(wx.EVT_TEXT, self.onMassChoice)
        self.mass_choice_box.SetLabel(str(self.MASS))

        # Radius
        self.radius_box = wx.StaticBox(self.settingsPanel, label='Radius: ')
        self.radius_sizer_hor = wx.StaticBoxSizer(self.radius_box, wx.HORIZONTAL)
        self.radius_sizer = wx.BoxSizer(wx.VERTICAL)
        self.radius_sizer_hor.AddSpacer(4)
        self.radius_sizer_hor.Add(self.radius_sizer)
        self.radius_static_text_1 = wx.StaticText(self.settingsPanel, label='What radius do you want\nto use?')
        self.radius_static_text_2 = wx.StaticText(self.settingsPanel, label='Select radius:')
        self.radius_text_box = wx.TextCtrl(self.settingsPanel, size=(50, 18))
        self.radius_text_box.SetLabel(str(self.RADIUS))

        # Gamma
        self.gamma_box = wx.StaticBox(self.settingsPanel, label='Gamma: ')
        self.gamma_sizer_hor = wx.StaticBoxSizer(self.gamma_box, wx.HORIZONTAL)
        self.gamma_sizer = wx.BoxSizer(wx.VERTICAL)
        self.gamma_sizer_hor.AddSpacer(4)
        self.gamma_sizer_hor.Add(self.gamma_sizer)
        self.gamma_static_text_1 = wx.StaticText(self.settingsPanel, label='What gamma do you want\nto use?')
        self.gamma_static_text_2 = wx.StaticText(self.settingsPanel, label='Select Gamma: ')
        self.gamma_text_box = wx.TextCtrl(self.settingsPanel, size=(50, 18))
        self.gamma_text_box.SetLabel(str(self.GAMMA))

        # Dimension
        self.dimension_box = wx.StaticBox(self.settingsPanel, label='Dimension: ')
        self.dimension_sizer_hor = wx.StaticBoxSizer(self.dimension_box, wx.HORIZONTAL)
        self.dimension_sizer = wx.BoxSizer(wx.VERTICAL)
        self.dimension_sizer_hor.AddSpacer(4)
        self.dimension_sizer_hor.Add(self.dimension_sizer)
        self.dimension_static_text_1 = wx.StaticText(self.settingsPanel, label='What dimension do you\nwant to use?')
        self.dimension_static_text_2 = wx.StaticText(self.settingsPanel, label='Select dimension: ')
        self.dimension_text_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.dimension_x_text = wx.StaticText(self.settingsPanel, label='N = ')
        self.dimension_x_text_box = wx.TextCtrl(self.settingsPanel, size=(50, 18))
        self.dimension_x_text_box.SetLabel(str(self.N_DIMENSION))
        self.dimension_y_text = wx.StaticText(self.settingsPanel, label='M = ')
        self.dimension_y_text_box = wx.TextCtrl(self.settingsPanel, size=(50, 18))
        self.dimension_y_text_box.SetLabel(str(self.M_DIMENSION))

        # Potential
        self.potential_box = wx.StaticBox(self.settingsPanel, label='Potential: ')
        self.potential_sizer_hor = wx.StaticBoxSizer(self.potential_box, wx.HORIZONTAL)
        self.potential_sizer = wx.BoxSizer(wx.VERTICAL)
        self.potential_sizer_hor.AddSpacer(4)
        self.potential_sizer_hor.Add(self.potential_sizer)
        self.potential_choice_static_text_1 = wx.StaticText(self.settingsPanel, label='Using potential?')
        self.potential_choice_static_text_2 = wx.StaticText(self.settingsPanel, label='Select potential:')
        self.potential_choice_box = wx.ComboBox(self.settingsPanel, size=(60, 20), value=str(self.POTENTIAL),
                                                choices=self.potential_choices)
        self.potential_choice_box.SetEditable(False)

        # Eigenvalue
        self.eigenvalue_box = wx.StaticBox(self.settingsPanel, label='Eigenvalue')
        self.eigenvalue_sizer_hor = wx.StaticBoxSizer(self.eigenvalue_box, wx.HORIZONTAL)
        self.eigenvalue_sizer = wx.BoxSizer(wx.VERTICAL)
        self.eigenvalue_sizer_hor.AddSpacer(4)
        self.eigenvalue_sizer_hor.Add(self.eigenvalue_sizer)
        self.eigenvalue_choice_text = wx.StaticText(self.settingsPanel, label='Select eigenvalue: ')
        self.eigenvalue_choice_box = wx.ComboBox(self.settingsPanel, size=(100, 20), value=self.EIGENVALUE,
                                                 choices=self.eigenvalue_choices)
        self.eigenvalue_choice_box.SetEditable(False)

        # Buttons
        self.calculate_button = wx.Button(self.panel, label='Calculate', size=(100, 30))
        self.calculate_button.Bind(wx.EVT_BUTTON, self.on_calculate_button)

        # Sizers
        self.main_sizer.Add(self.canvas_box, 3, wx.EXPAND)
        self.main_sizer.Add(self.main_right_sizer,1, wx.EXPAND)
        self.main_right_sizer.AddSpacer(5)
        self.main_right_sizer.Add(self.settings_text,0, wx.ALIGN_CENTER_HORIZONTAL)
        self.main_right_sizer.AddSpacer(5)
        self.main_right_sizer.Add(self.settingsPanel,1, wx.EXPAND)
        self.main_right_sizer.AddSpacer(4)
        self.main_right_sizer.Add(self.calculate_button, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.main_right_sizer.AddSpacer(4)
        self.settings_sizer.AddSpacer(8)
        self.settings_sizer.Add(self.left_sizer, 1, wx.EXPAND)
        #self.settings_sizer.Add(self.right_sizer, 0, wx.ALL, 10)

        self.left_sizer.AddSpacer(10)
        self.left_sizer.Add(self.method_sizer_hor, 0, wx.EXPAND)
        self.left_sizer.AddSpacer(5)
        self.left_sizer.Add(self.sigma_sizer_hor, 0, wx.EXPAND)
        self.left_sizer.AddSpacer(5)
        self.left_sizer.Add(self.mass_sizer_hor, 0, wx.EXPAND)
        self.left_sizer.AddSpacer(5)
        self.left_sizer.Add(self.radius_sizer_hor, 0, wx.EXPAND)
        self.left_sizer.AddSpacer(5)
        self.left_sizer.Add(self.gamma_sizer_hor, 0, wx.EXPAND)
        self.left_sizer.AddSpacer(5)
        self.left_sizer.Add(self.dimension_sizer_hor, 0, wx.EXPAND)
        self.left_sizer.AddSpacer(5)
        self.left_sizer.Add(self.potential_sizer_hor, 0, wx.EXPAND)
        self.left_sizer.AddSpacer(5)
        self.left_sizer.Add(self.eigenvalue_sizer_hor, 0, wx.EXPAND)

        self.method_sizer.Add(self.method_choice_static_text)
        self.method_sizer.AddSpacer(5)
        self.method_sizer.Add(self.method_choice_box)

        self.sigma_sizer.Add(self.sigma_choice_static_text)
        self.sigma_sizer.AddSpacer(5)
        self.sigma_sizer.Add(self.sigma_choice_box)

        self.mass_sizer.Add(self.mass_choice_static_text_1)
        self.mass_sizer.AddSpacer(5)
        self.mass_sizer.Add(self.mass_choice_static_text_2)
        self.mass_sizer.AddSpacer(5)
        self.mass_sizer.Add(self.mass_choice_box)

        self.radius_sizer.Add(self.radius_static_text_1)
        self.radius_sizer.AddSpacer(7)
        self.radius_sizer.Add(self.radius_static_text_2)
        self.radius_sizer.AddSpacer(5)
        self.radius_sizer.Add(self.radius_text_box)

        self.dimension_sizer.Add(self.dimension_static_text_1)
        self.dimension_sizer.AddSpacer(5)
        self.dimension_sizer.Add(self.dimension_static_text_2)
        self.dimension_sizer.AddSpacer(5)
        self.dimension_sizer.Add(self.dimension_text_sizer)
        self.dimension_text_sizer.Add(self.dimension_x_text)
        self.dimension_text_sizer.Add(self.dimension_x_text_box)
        self.dimension_text_sizer.AddSpacer(10)
        self.dimension_text_sizer.Add(self.dimension_y_text)
        self.dimension_text_sizer.Add(self.dimension_y_text_box)

        self.gamma_sizer.Add(self.gamma_static_text_1)
        self.gamma_sizer.AddSpacer(5)
        self.gamma_sizer.Add(self.gamma_static_text_2)
        self.gamma_sizer.AddSpacer(5)
        self.gamma_sizer.Add(self.gamma_text_box)

        self.potential_sizer.Add(self.potential_choice_static_text_1)
        self.potential_sizer.AddSpacer(5)
        self.potential_sizer.Add(self.potential_choice_static_text_2)
        self.potential_sizer.AddSpacer(5)
        self.potential_sizer.Add(self.potential_choice_box)

        self.eigenvalue_sizer.Add(self.eigenvalue_choice_text)
        self.eigenvalue_sizer.AddSpacer(5)
        self.eigenvalue_sizer.Add(self.eigenvalue_choice_box)

        self.settingsPanel.SetSizerAndFit(self.settings_sizer)
        # self.settingsPanel.Fit()
        self.panel.SetSizer(self.main_sizer)



        # Result Panel
        self.resultSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Canvas
        self.resultFigure = plt.figure(figsize=(6, 5), facecolor='#d2d2d2')
        self.resultCanvas = ResultCanvas(self.resultPanel, -1, self.resultFigure)

        # Setting Text
        self.settings_text1 = wx.StaticText(self.resultPanel, label='Settings')
        self.settings_text1.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))

        # Settings Panel
        self.settingsResultPanel = scrolled.ScrolledPanel(self.resultPanel, -1, style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER)
        self.settingsResultPanel.SetAutoLayout(1)
        self.settingsResultPanel.SetupScrolling()
        self.settingsResultPanelSizer = wx.BoxSizer(wx.VERTICAL)

        self.dependenceRightSizer = wx.BoxSizer(wx.VERTICAL)

        # Settings
        self.dependenceGraphChoices = ['Energy from the radius', 'Energy from gamma', 'Energy from dimension']
        self.dependenceGraphBox = wx.StaticBox(self.settingsResultPanel, label='Dependence Graph:')
        self.dependenceGraphSizer_hor = wx.StaticBoxSizer(self.dependenceGraphBox, wx.HORIZONTAL)
        self.dependenceGraphSizer = wx.BoxSizer(wx.VERTICAL)
        self.dependenceGraphSizer_hor.AddSpacer(4)
        self.dependenceGraphSizer_hor.Add(self.dependenceGraphSizer)
        self.dependenceGraphText = wx.StaticText(self.settingsResultPanel, label='Select dependence graph:')
        self.dependenceGraphChoiceBox = wx.ComboBox(self.settingsResultPanel,value=str(self.dependenceGraphChoices[0]), choices=self.dependenceGraphChoices)
        self.dependenceGraphChoiceBox.SetEditable(False)
        self.dependenceGraphChoiceBox.Bind(wx.EVT_COMBOBOX, self.onDependenceGraphChoiceBox)

        self.dependenceGraphSizer.Add(self.dependenceGraphText)
        self.dependenceGraphSizer.Add(self.dependenceGraphChoiceBox)

        # Button
        self.calculateResultsButton = wx.Button(self.resultPanel, label='Calculate', size=(100, 30))
        self.calculateResultsButton.Bind(wx.EVT_BUTTON, self.onCalculateResultsButton)

        self.resultSizer.Add(self.resultCanvas,4 , wx.EXPAND)
        self.resultSizer.Add(self.dependenceRightSizer, 2, wx.EXPAND)

        self.dependenceRightSizer.AddSpacer(10)
        self.dependenceRightSizer.Add(self.settings_text1, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.dependenceRightSizer.Add(self.settingsResultPanel, 1, wx.EXPAND)
        self.dependenceRightSizer.Add(self.calculateResultsButton, 0 , wx.ALIGN_CENTER_HORIZONTAL)


        # Energy from the radius
        self.energyFrom_hor = wx.BoxSizer(wx.HORIZONTAL)
        self.energyFrom = wx.BoxSizer(wx.VERTICAL)

        # Method
        self.methodResultSizerBox = wx.StaticBox(self.settingsResultPanel, label='Method:')
        self.methodResultSizer_hor = wx.StaticBoxSizer(self.methodResultSizerBox, wx.HORIZONTAL)
        self.methodResultSizer = wx.BoxSizer(wx.VERTICAL)
        self.methodResultSizer_hor.AddSpacer(4)
        self.methodResultSizer_hor.Add(self.methodResultSizer)
        self.methodResultChoiceStaticText = wx.StaticText(self.settingsResultPanel, label='Select method:')
        self.methodResultChoiceBox = wx.ComboBox(self.settingsResultPanel, size=(135, 22), value=self.method_choices[0],
                                             choices=self.method_choices)
        self.methodResultChoiceBox.SetEditable(False)

        self.methodResultSizer.Add(self.methodResultChoiceStaticText)
        self.methodResultSizer.AddSpacer(4)
        self.methodResultSizer.Add(self.methodResultChoiceBox)

        # Sigma
        self.sigmaResultBox = wx.StaticBox(self.settingsResultPanel, label='Sigma:')
        self.sigmaResultSizer_hor = wx.StaticBoxSizer(self.sigmaResultBox, wx.HORIZONTAL)
        self.sigmaResultSizer = wx.BoxSizer(wx.VERTICAL)
        self.sigmaResultSizer_hor.AddSpacer(5)
        self.sigmaResultSizer_hor.Add(self.sigmaResultSizer)
        self.sigmaResultChoiceCtaticText = wx.StaticText(self.settingsResultPanel, label='Select sigma:')
        self.sigmaResultChoiceBox = wx.ComboBox(self.settingsResultPanel, size=(105, 22), value=self.sigma_choices[0],
                                            choices=self.sigma_choices)
        self.sigmaResultChoiceBox.SetEditable(False)

        self.sigmaResultSizer.Add(self.sigmaResultChoiceCtaticText)
        self.sigmaResultSizer.AddSpacer(5)
        self.sigmaResultSizer.Add(self.sigmaResultChoiceBox)

        # Mass
        self.massResultBox = wx.StaticBox(self.settingsResultPanel, label='Magnetic Quantum Number: ')
        self.massResultSizer_hor = wx.StaticBoxSizer(self.massResultBox, wx.HORIZONTAL)
        self.massResultSizer = wx.BoxSizer(wx.VERTICAL)
        self.massResultSizer_hor.AddSpacer(4)
        self.massResultSizer_hor.Add(self.massResultSizer)
        self.massResultChoiceStaticText = wx.StaticText(self.settingsResultPanel, label='Select MQN:')
        self.massResultChoiceBox = wx.TextCtrl(self.settingsResultPanel, size=(50, 18), style=wx.TE_PROCESS_ENTER)
        self.massResultChoiceBox.Bind(wx.EVT_TEXT, self.onMassResultChoice)
        self.massResultChoiceBox.SetLabel(str(self.MASS))

        self.massResultSizer.Add(self.massResultChoiceStaticText)
        self.massResultSizer.AddSpacer(5)
        self.massResultSizer.Add(self.massResultChoiceBox)

        # Gamma
        self.gammaResultSizerBox = wx.StaticBox(self.settingsResultPanel, label='Gamma:')
        self.gammaResultSizer_hor = wx.StaticBoxSizer(self.gammaResultSizerBox, wx.HORIZONTAL)
        self.gammaResultSizer = wx.BoxSizer(wx.VERTICAL)
        self.gammaResultSizer_hor.AddSpacer(4)
        self.gammaResultSizer_hor.Add(self.gammaResultSizer)
        self.gammaResultStaticText = wx.StaticText(self.settingsResultPanel, label='Select gamma range:')
        self.gammaResultRangeBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.gammaResultRangeBox1 = wx.TextCtrl(self.settingsResultPanel, size=(50, 18))
        self.gammaResultRangeBoxSeparator = wx.StaticText(self.settingsResultPanel, label=' - ')
        self.gammaResultRangeBox2 = wx.TextCtrl(self.settingsResultPanel, size=(50,18))
        self.gammaResultRangeBox1.SetLabel('0')
        self.gammaResultRangeBox2.SetLabel('0')
        self.gammaResultRangeBoxSizer.Add(self.gammaResultRangeBox1)
        self.gammaResultRangeBoxSizer.Add(self.gammaResultRangeBoxSeparator)
        self.gammaResultRangeBoxSizer.Add(self.gammaResultRangeBox2)

        self.gammaResultSizer.Add(self.gammaResultStaticText)
        self.gammaResultSizer.AddSpacer(4)
        self.gammaResultSizer.Add(self.gammaResultRangeBoxSizer)

        # Radius
        self.radiusResultSizerBox = wx.StaticBox(self.settingsResultPanel, label='Radius:')
        self.radiusResultSizer_hor = wx.StaticBoxSizer(self.radiusResultSizerBox, wx.HORIZONTAL)
        self.radiusResultSizer = wx.BoxSizer(wx.VERTICAL)
        self.radiusResultSizer_hor.AddSpacer(4)
        self.radiusResultSizer_hor.Add(self.radiusResultSizer)
        self.radiusResultStaticText = wx.StaticText(self.settingsResultPanel, label='Select radius range:')
        self.radiusResultRangeBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.radiusResultRangeBox1 = wx.TextCtrl(self.settingsResultPanel, size=(50, 18))
        self.radiusResultRangeBoxSeparator = wx.StaticText(self.settingsResultPanel, label=' - ')
        self.radiusResultRangeBox2 = wx.TextCtrl(self.settingsResultPanel, size=(50, 18))
        self.radiusResultRangeBox1.SetLabel('0')
        self.radiusResultRangeBox2.SetLabel('0')
        self.radiusResultRangeBoxSizer.Add(self.radiusResultRangeBox1)
        self.radiusResultRangeBoxSizer.Add(self.radiusResultRangeBoxSeparator)
        self.radiusResultRangeBoxSizer.Add(self.radiusResultRangeBox2)

        self.radiusResultSizer.Add(self.radiusResultStaticText)
        self.radiusResultSizer.AddSpacer(4)
        self.radiusResultSizer.Add(self.radiusResultRangeBoxSizer)

        # Eignevalue
        self.eigenvalueResultBox = wx.StaticBox(self.settingsResultPanel, label='Eigenvalue')
        self.eigenvalueResultSizer_hor = wx.StaticBoxSizer(self.eigenvalueResultBox, wx.HORIZONTAL)
        self.eigenvalueResultSizer = wx.BoxSizer(wx.VERTICAL)
        self.eigenvalueResultSizer_hor.AddSpacer(4)
        self.eigenvalueResultSizer_hor.Add(self.eigenvalueResultSizer)
        self.eigenvalueResultChoiceText = wx.StaticText(self.settingsResultPanel, label='Select eigenvalue: ')
        self.eigenvalueResultChoiceBox = wx.ComboBox(self.settingsResultPanel, size=(100, 20), value=self.eigenvalue_choices[0],
                                                 choices=self.eigenvalue_choices)
        self.eigenvalueResultChoiceBox.SetEditable(False)

        self.eigenvalueResultSizer.Add(self.eigenvalueResultChoiceText)
        self.eigenvalueResultSizer.AddSpacer(4)
        self.eigenvalueResultSizer.Add(self.eigenvalueResultChoiceBox)

        # Potential
        self.potentialResultBox = wx.StaticBox(self.settingsResultPanel, label='Potential: ')
        self.potentialResultSizer_hor = wx.StaticBoxSizer(self.potentialResultBox, wx.HORIZONTAL)
        self.potentialResultSizer = wx.BoxSizer(wx.VERTICAL)
        self.potentialResultSizer_hor.AddSpacer(4)
        self.potentialResultSizer_hor.Add(self.potentialResultSizer)
        self.potentialResultChoiceText = wx.StaticText(self.settingsResultPanel, label='Select potential:')
        self.potentialResultChoiceBox = wx.ComboBox(self.settingsResultPanel, size=(60, 20), value=self.potential_choices[0],
                                                choices=self.potential_choices)
        self.potentialResultChoiceBox.SetEditable(False)

        self.potentialResultSizer.Add(self.potentialResultChoiceText)
        self.potentialResultSizer.AddSpacer(4)
        self.potentialResultSizer.Add(self.potentialResultChoiceBox)

        # Dimension Coeff
        self.dimensionCoeffResultBox = wx.StaticBox(self.settingsResultPanel, label='Dimension Coefficient:')
        self.dimensionCoeffResultSizer_hor = wx.StaticBoxSizer(self.dimensionCoeffResultBox, wx.HORIZONTAL)
        self.dimensionCoeffResultSizer = wx.BoxSizer(wx.VERTICAL)
        self.dimensionCoeffResultSizer_hor.AddSpacer(4)
        self.dimensionCoeffResultSizer_hor.Add(self.dimensionCoeffResultSizer)
        self.dimensionCoeffResultChoiceText = wx.StaticText(self.settingsResultPanel, label='Select coefficient:')
        coeffChoices = ['N', '1/N', '1/N\u00B2']
        self.dimensionCoeffResultChoiceBox = wx.ComboBox(self.settingsResultPanel, size=(60,20), value = coeffChoices[0], choices=coeffChoices)
        self.dimensionCoeffResultChoiceBox.SetEditable(False)

        self.dimensionCoeffResultSizer.Add(self.dimensionCoeffResultChoiceText)
        self.dimensionCoeffResultSizer.AddSpacer(4)
        self.dimensionCoeffResultSizer.Add(self.dimensionCoeffResultChoiceBox)


        self.energyFrom.Add(self.eigenvalueResultSizer_hor, 0,wx.EXPAND)
        self.energyFrom.AddSpacer(5)
        self.energyFrom.Add(self.potentialResultSizer_hor, 0, wx.EXPAND)
        self.energyFrom.AddSpacer(5)
        self.energyFrom.Add(self.methodResultSizer_hor, 0, wx.EXPAND)
        self.energyFrom.AddSpacer(5)
        self.energyFrom.Add(self.sigmaResultSizer_hor, 0, wx.EXPAND)
        self.energyFrom.AddSpacer(5)
        self.energyFrom.Add(self.massResultSizer_hor, 0, wx.EXPAND)
        self.energyFrom.AddSpacer(5)
        self.energyFrom.Add(self.gammaResultSizer_hor, 0, wx.EXPAND)
        self.energyFrom.AddSpacer(5)
        self.energyFrom.Add(self.radiusResultSizer_hor, 0, wx.EXPAND)
        self.energyFrom.AddSpacer(5)
        self.energyFrom.Add(self.dimensionCoeffResultSizer_hor, 0, wx.EXPAND)

        self.energyFrom.Hide(self.dimensionCoeffResultSizer_hor, recursive=True)
        self.energyFrom.Hide(self.gammaResultSizer_hor, recursive=True)
        self.energyFrom.Hide(self.radiusResultSizer_hor, recursive=True)

        self.energyFrom_hor.AddSpacer(5)
        self.energyFrom_hor.Add(self.energyFrom)
        # self.energyFrom.Hide(self.gammaResultSizer_hor, recursive=True)
        self.settingsResultPanelSizer.AddSpacer(4)
        self.settingsResultPanelSizer.Add(self.dependenceGraphSizer_hor,0,wx.EXPAND)
        self.settingsResultPanelSizer.AddSpacer(5)
        self.settingsResultPanelSizer.Add(self.energyFrom_hor, 0, wx.EXPAND)

        self.settingsResultPanel.SetSizer(self.settingsResultPanelSizer)

        self.resultPanel.SetSizer(self.resultSizer)

        self.multiSizer = wx.BoxSizer(wx.VERTICAL)
        self.multiSizer.Add(self.panel)
        self.multiSizer.Add(self.resultPanel)
        self.multiPanel.SetSizer(self.multiSizer)

        self.resultPanel.Hide()

        size = wx.Size(945, 685)
        self.SetMinSize(size)
        self.SetSize(size)
        self.make_menu_bar()

    def make_menu_bar(self):

        # File
        file_menu = wx.Menu()

        screenshot_button = wx.MenuItem(file_menu, wx.ID_SAVEAS, '&Screenshot\tCtrl+S')
        screenshot_button.SetBitmap(wx.Bitmap('bitmaps/screenshot.png'))
        save_button = wx.MenuItem(file_menu, wx.ID_SAVE, '&Save')
        save_button.SetBitmap(wx.Bitmap('bitmaps/save.png'))
        open_button = wx.MenuItem(file_menu, wx.ID_OPEN, '&Open')
        open_button.SetBitmap(wx.Bitmap('bitmaps/open.png'))
        quit_button = wx.MenuItem(file_menu, wx.ID_EXIT, '&Quit\tCtrl+Q')
        quit_button.SetBitmap(wx.Bitmap('bitmaps/exit.png'))

        file_menu.Append(screenshot_button)
        file_menu.AppendSeparator()
        file_menu.Append(save_button)
        file_menu.Append(open_button)
        file_menu.AppendSeparator()
        file_menu.Append(quit_button)

        self.Bind(wx.EVT_MENU, self.on_screenshot, screenshot_button)
        self.Bind(wx.EVT_MENU, self.on_save, save_button)
        self.Bind(wx.EVT_MENU, self.on_open, open_button)
        self.Bind(wx.EVT_MENU, self.on_exit, quit_button)

        # View
        self.view_menu = wx.Menu()

        # self.view_menu.AppendSeparator()
        self.view_menu.AppendCheckItem(ID_ALWAYS_ON_TOP, '&Always on top')
        self.view_menu.Check(ID_ALWAYS_ON_TOP, True)
        self.view_menu.AppendSeparator()

        savePosition = self.view_menu.Append(ID_SAVE_POSITION, '&Save Position')

        self.Bind(wx.EVT_MENU, self.onAlwaysOnTop, id=ID_ALWAYS_ON_TOP)
        self.Bind(wx.EVT_MENU, self.onSavePosition, savePosition)

        # Canvas

        self.canvas_menu = wx.Menu()
        self.canvas_sub_menu = wx.Menu()


        self.canvas_sub_menu.AppendCheckItem(ID_CANVAS_QUARTER_1, '1 quarter')
        self.canvas_sub_menu.Check(ID_CANVAS_QUARTER_1,True)
        self.canvas_sub_menu.Enable(ID_CANVAS_QUARTER_1,False)

        self.canvas_sub_menu.AppendCheckItem(ID_CANVAS_QUARTER_4, '4 quarters')
        showHideCanvas = self.canvas_menu.Append(ID_SHOW_HIDE_CANVAS, '&Hide Canvas')
        self.canvas_menu.AppendSeparator()
        self.canvas_menu.Append(ID_CANVAS_MENU, 'Quarters count', self.canvas_sub_menu)

        self.Bind(wx.EVT_MENU, self.onShowHideCanvas, showHideCanvas)
        self.Bind(wx.EVT_MENU, self.onQuarter_1, id=ID_CANVAS_QUARTER_1)
        self.Bind(wx.EVT_MENU, self.onQuarter_4, id=ID_CANVAS_QUARTER_4)

        # Page
        self.page_menu = wx.Menu()
        self.page_menu.AppendCheckItem(ID_SHOW_MAIN_PAGE, '&1) Schemas Page')
        self.page_menu.Enable(ID_SHOW_MAIN_PAGE, False)
        self.page_menu.Check(ID_SHOW_MAIN_PAGE, True)
        self.page_menu.AppendCheckItem(ID_SHOW_SECONDARY_PAGE, '&2) Result Page')

        self.Bind(wx.EVT_MENU, self.onMainPage, id=ID_SHOW_MAIN_PAGE)
        self.Bind(wx.EVT_MENU, self.onSecondaryPage, id=ID_SHOW_SECONDARY_PAGE)

        # Help
        help_menu = wx.Menu()

        about_button = wx.MenuItem(help_menu, wx.ID_ABOUT, '&About')
        about_button.SetBitmap(wx.Bitmap('bitmaps/about.png'))

        help_menu.Append(about_button)
        help_menu.AppendSeparator()

        self.Bind(wx.EVT_MENU, self.on_about_button, about_button)

        # Filling menu
        self.menu_bar.Append(file_menu, 'File')
        self.menu_bar.Append(self.view_menu, '&View')
        self.menu_bar.Append(self.page_menu, '&Page')
        self.menu_bar.Append(self.canvas_menu, '&Canvas')
        self.menu_bar.Append(help_menu, 'Help')


        self.SetMenuBar(self.menu_bar)
        self.Bind(wx.EVT_CLOSE, self.on_exit)

    def on_screenshot(self, event):
        if self.currentPage == 'Main':
            if not self.canvas_drawn[0]:
                message = 'No plot drawn.'
                wx.MessageBox(message, 'Error', wx.OK | wx.ICON_ERROR)
                return
        else:
            if not self.canvas_drawn[1]:
                message = 'No plot drawn.'
                wx.MessageBox(message, 'Error', wx.OK | wx.ICON_ERROR)
                return
        path = os.path.join(os.getcwd(), PLOT_SCREENSHOT_DIR)
        if not os.path.exists(path):
            os.makedirs(path)
        if self.method_choice_box == 'Main method':
            method = 'Main'
        else:
            method = 'Alternative'
        with wx.FileDialog(self, "Screenshot", defaultDir=path,
                           defaultFile='plot_screenshot_(%s,%s)-%s-M%s_R%s_G%s_P%s_%s' %
                                       (self.N_DIMENSION, self.M_DIMENSION, method, self.MASS, self.RADIUS,
                                        self.GAMMA, self.POTENTIAL, self.EIGENVALUE),
                           wildcard="png files (*.png)|*.png",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            if self.currentPage == 'Main':
                self.canvas.axis.set_facecolor(color='white')
                self.canvas.figure.savefig(pathname)
                self.canvas.axis.set_facecolor(color='#d2d2d2')
                self.canvas.Refresh()
            else:
                self.resultCanvas.figure.savefig(pathname)
            self.SetStatusText('Screenshot saved successfully. Path: %s' % pathname)

    def on_save(self, event):
        if not self.canvas_drawn[0]:
            message = 'No data to save.'
            wx.MessageBox(message, 'Error', wx.OK | wx.ICON_ERROR)
            return
        path = os.path.join(os.getcwd(), PLOT_JSON_DIR)
        if not os.path.exists(path):
            os.makedirs(path)
        if self.METHOD == 'Main method':
            method = 'Main'
        else:
            method = 'Alternative'
        if self.SIGMA == 'Positive':
            sigma = 'Pos'
        else:
            sigma = 'Neg'
        path = os.path.join(path, method+'Method')
        path = os.path.join(path, sigma+'Sigma')
        with wx.FileDialog(self, "Save plot data", defaultDir=path,
                           defaultFile='plot_data_(%s,%s)-%s-%sS-M%s_R%s_G%s_P%s.txt' % (self.N_DIMENSION, self.M_DIMENSION, method, sigma, self.MASS, self.RADIUS,self.GAMMA, self.POTENTIAL),
                           wildcard="txt files (*.txt)|*.txt",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT, ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            self.creating_json(pathname)
            self.SetStatusText('Data saved successfully. Path: %s' % pathname)

    def on_open(self, event):
        if os.path.exists(os.path.join(os.getcwd(), PLOT_JSON_DIR)):
            path = os.path.join(os.getcwd(), PLOT_JSON_DIR)
        else:
            path = os.getcwd()
        with wx.FileDialog(self, "Open plot from data", defaultDir=path, wildcard="txt files (*.txt)|*.txt",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            self.taking_data = False
            self.reading_json(pathname)

    def on_exit(self, event):
        sys.exit()

    def onAlwaysOnTop(self, event):
        if self.view_menu.IsChecked(event.GetId()):
            self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        else:
            self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE)

    def onShowHideCanvas(self, event):
        if self.canvasShown:
            self.canvasShown = False
            self.canvas_menu.SetLabel(id=ID_SHOW_HIDE_CANVAS, label='Show Canvas')
            self.main_sizer.Hide(self.canvas_box, recursive=True)
            self.settingsPanel.SetMinSize((250, 350))
            size = wx.Size(260, 500)
            self.SetMinSize(size)
            self.SetSize(size)
        else:
            self.canvasShown = True
            self.canvas_menu.SetLabel(id=ID_SHOW_HIDE_CANVAS, label='Hide Canvas')
            self.canvas.Show()
            size = wx.Size(945, 685)
            self.SetMinSize(size)
            self.SetSize(size)

    def onQuarter_1(self, event):
        self.quarterNumber = 1
        self.canvas_menu.Enable(ID_CANVAS_QUARTER_1, False)
        self.canvas_menu.Enable(ID_CANVAS_QUARTER_4, True)
        self.canvas_menu.Check(ID_CANVAS_QUARTER_4, False)

    def onQuarter_4(self, event):
        self.quarterNumber = 4
        self.canvas_menu.Enable(ID_CANVAS_QUARTER_4, False)
        self.canvas_menu.Enable(ID_CANVAS_QUARTER_1, True)
        self.canvas_menu.Check(ID_CANVAS_QUARTER_1, False)

    def onSavePosition(self, event):
        pos = self.GetPosition()
        import configparser
        CP = configparser.RawConfigParser()
        CP.read('bitmaps/userPositionConfig.ini')
        CP.set('POSITION', 'positionX', str(pos[0]))
        CP.set('POSITION', 'positionY', str(pos[1]))
        with open('bitmaps/userPositionConfig.ini', 'w') as configfile:
            CP.write(configfile)

    def onMainPage(self, event):
        self.currentPage = 'Main'
        self.canvas_menu.Enable(ID_SHOW_HIDE_CANVAS, True)
        self.page_menu.Enable(ID_SHOW_MAIN_PAGE, False)
        self.page_menu.Enable(ID_SHOW_SECONDARY_PAGE, True)
        self.page_menu.Check(ID_SHOW_SECONDARY_PAGE, False)
        self.panel.Show()
        self.resultPanel.Hide()

        self.settingsPanel.SetupScrolling()
        self.panel.Fit()
        if self.canvasShown:
            size = wx.Size(945, 685)
        else:
            size = wx.Size(260,500)
        self.SetMinSize(size)
        self.SetSize(size)

    def onSecondaryPage(self, event):
        self.currentPage = 'Second'
        self.canvas_menu.Enable(ID_SHOW_HIDE_CANVAS, False)
        self.page_menu.Enable(ID_SHOW_SECONDARY_PAGE, False)
        self.page_menu.Enable(ID_SHOW_MAIN_PAGE, True)
        self.page_menu.Check(ID_SHOW_MAIN_PAGE, False)
        self.resultPanel.Show()
        self.panel.Hide()
        self.settingsResultPanel.SetupScrolling()
        self.resultPanel.Fit()
        size = wx.Size(820, 585)
        self.SetMinSize(size)
        self.SetSize(size)

    def on_about_button(self, event):
        message = 'Program for a graduate work.\nBy Andrew Vasilevskii.'
        wx.MessageBox(message, 'About', wx.OK | wx.ICON_ASTERISK)

    def onDependenceGraphChoiceBox(self, event):
        graph = event.GetEventObject().GetValue()
        if 'radius' in graph:
            self.settingsResultPanelSizer.Show(self.energyFrom, recursive=True)
            self.energyFrom.Hide(self.gammaResultSizer_hor, recursive=True)
            self.energyFrom.Hide(self.radiusResultSizer_hor, recursive=True)
            self.energyFrom.Hide(self.dimensionCoeffResultSizer_hor, recursive=True)
            self.settingsResultPanel.SetupScrolling(scroll_x=False)
            self.settingsResultPanel.Layout()
        elif 'gamma' in graph:
            self.settingsResultPanelSizer.Show(self.energyFrom, recursive=True)
            self.energyFrom.Hide(self.gammaResultSizer_hor, recursive=True)
            self.energyFrom.Hide(self.radiusResultSizer_hor, recursive=True)
            self.energyFrom.Hide(self.dimensionCoeffResultSizer_hor, recursive=True)
            self.settingsResultPanel.SetupScrolling(scroll_x=False)
            self.settingsResultPanel.Layout()
        else:
            self.settingsResultPanelSizer.Hide(self.energyFrom, recursive=True)
            self.energyFrom.Show(self.eigenvalueResultSizer_hor, recursive=True)
            self.energyFrom.Show(self.potentialResultSizer_hor, recursive=True)
            self.energyFrom.Show(self.dimensionCoeffResultSizer_hor, recursive=True)
            self.settingsResultPanel.SetupScrolling(scroll_x=False)
            self.settingsResultPanel.Layout()

    def onCalculateResultsButton(self, event):
        if self.canvas_drawn[1]:
            self.SetStatusText(text='Clearing area.')
            self.calculateResultsButton.SetLabel('Calculate')
            self.canvas_drawn[1] = False
            self.resultCanvas.Remove_Result()
            self.SetStatusText(text='Waiting for arguments.')
        else:
            # self.Layout()
            self.SetStatusText(text='Calculating. Please wait.')
            self.calculateResultsButton.SetLabel('Clear area')
            list = {}
            self.METHOD = str(self.methodResultChoiceBox.GetValue())
            if self.METHOD == 'Main method':
                method = 'Main'
            else:
                method = 'Alternative'
            self.SIGMA = str(self.sigmaResultChoiceBox.GetValue())
            if self.SIGMA == 'Positive':
                sigma = 'Pos'
            else:
                sigma = 'Neg'
            self.MASS = str(self.massResultChoiceBox.GetValue())
            print(self.MASS)
            self.POTENTIAL = self.potentialResultChoiceBox.GetValue()
            self.EIGENVALUE = self.eigenvalueResultChoiceBox.GetValue()
            self.N_DIMENSION = 40
            self.M_DIMENSION = 40
            if 'radius' in self.dependenceGraphChoiceBox.GetValue():
                # self.GAMMA = 0
                # for energyy in self.eigenvalue_choices:
                #     energy = {}
                #     self.EIGENVALUE = energyy
                #     for r in range(1,8):
                #         path = os.path.join(os.getcwd(), PLOT_JSON_DIR)
                #         path = os.path.join(path, method+'Method')
                #         path = os.path.join(path, sigma+'Sigma')
                #         if os.path.exists(path):
                #             path = os.path.join(path, 'plot_data_(%s,%s)-%s-%sS-M%s_R%s_G%s_P%s.txt' %(self.N_DIMENSION, self.M_DIMENSION, method, sigma, self.MASS, r, self.GAMMA, self.POTENTIAL))
                #             self.reading_json(path)
                #             if self.EIGENVALUE == 'First order':
                #                 energy[r] = self.VALUE[0]
                #             elif self.EIGENVALUE == 'Second order':
                #                 energy[r] = self.VALUE[1]
                #             else:
                #                 energy[r] = self.VALUE[2]
                #
                #         list[energyy] = energy
                # self.resultCanvas.Draw_Result(list, 'radius')
                for g in range(5):
                    energy = {}
                    for r in range(1, 11):
                        self.MASS = str(self.massResultChoiceBox.GetValue())
                        path = os.path.join(os.getcwd(), PLOT_JSON_DIR)
                        path = os.path.join(path, method+'Method')
                        path = os.path.join(path, sigma+'Sigma')
                        if os.path.exists(path):
                            path = os.path.join(path, 'plot_data_(%s,%s)-%s-%sS-M%s_R%s_G%s_P%s.txt' %
                                                (self.N_DIMENSION, self.M_DIMENSION, method, sigma, self.MASS, r,
                                                 g, self.POTENTIAL))
                        self.reading_json(path)
                        if self.EIGENVALUE == 'First order':
                            energy[r] = self.VALUE[0]
                        elif self.EIGENVALUE == 'Second order':
                            energy[r] = self.VALUE[1]
                        else:
                            energy[r] = self.VALUE[2]
                        path = os.path.join(os.getcwd(), PLOT_JSON_DIR)
                        path = os.path.join(path, method + 'Method')
                        path = os.path.join(path, sigma + 'Sigma')
                        if os.path.exists(path):
                            path = os.path.join(path, 'plot_data_(%s,%s)-%s-%sS-M%s_R%s_G%s_P%s.txt' %
                                                (self.N_DIMENSION, self.M_DIMENSION, method, sigma, 0, r,
                                                 g, self.POTENTIAL))
                        self.reading_json(path)
                        # energy[r] -= self.VALUE[0]
                        # print(energy[r], self.VALUE[0])
                    list[g] = energy
                self.resultCanvas.Draw_Result(list, 'radius', self.EIGENVALUE)
            if 'gamma' in self.dependenceGraphChoiceBox.GetValue():
                # for r in range(1, 5):
                #     energy = {}
                #     for g in range(0, 11):
                #         path = os.path.join(os.getcwd(), PLOT_JSON_DIR)
                #         path = os.path.join(path, method+'Method')
                #         path = os.path.join(path, sigma+'Sigma')
                #         if os.path.exists(path):
                #             path = os.path.join(path, 'plot_data_(%s,%s)-%s-%sS-M%s_R%s_G%s_P%s.txt' %
                #                                 (self.N_DIMENSION, self.M_DIMENSION, method, sigma, self.MASS, r,
                #                                  g, self.POTENTIAL))
                #         self.reading_json(path)
                #         if self.EIGENVALUE == 'First order':
                #             energy[g] = self.VALUE[0]
                #         elif self.EIGENVALUE == 'Second order':
                #             energy[g] = self.VALUE[1]
                #         else:
                #             energy[g] = self.VALUE[2]
                #
                #         list[r] = energy
                # self.resultCanvas.Draw_Result(list, 'gamma', self.EIGENVALUE)
                self.RADIUS = 10
                for m in [0,1, -1]:
                    self.MASS = m
                    mass = {}
                    for energyy in self.eigenvalue_choices:
                        if m == 1 or m == -1:
                            print(m)
                            if energyy != 'First order':
                                print(energyy)
                                continue
                        energy = {}
                        self.EIGENVALUE = energyy
                        for gamma in range(6):
                            self.GAMMA = gamma
                            path = os.path.join(os.getcwd(), PLOT_JSON_DIR)
                            path = os.path.join(path, method+'Method')
                            path = os.path.join(path, sigma+'Sigma')
                            if os.path.exists(path):
                                path = os.path.join(path, 'plot_data_(%s,%s)-%s-%sS-M%s_R%s_G%s_P%s.txt' %(self.N_DIMENSION, self.M_DIMENSION, method, sigma, self.MASS, self.RADIUS, self.GAMMA, self.POTENTIAL))
                                self.reading_json(path)
                                if self.EIGENVALUE == 'First order':
                                    energy[gamma] = self.VALUE[0]
                                elif self.EIGENVALUE == 'Second order':
                                    energy[gamma] = self.VALUE[1]
                                else:
                                    energy[gamma] = self.VALUE[2]

                            mass[energyy] = energy
                        print(self.MASS,energyy, mass[energyy])
                        list[m] = mass
                self.resultCanvas.Draw_Result(list, 'gamma')
                # for r in (1,3,5, 10):
                #     energy = {}
                #     for g in range(0, 11):
                #         path = os.path.join(os.getcwd(), PLOT_JSON_DIR)
                #         path = os.path.join(path, method+'Method')
                #         path = os.path.join(path, sigma+'Sigma')
                #         if os.path.exists(path):
                #             path = os.path.join(path, 'plot_data_(%s,%s)-%s-%sS-M%s_R%s_G%s_P%s.txt' %
                #                                 (self.N_DIMENSION, self.M_DIMENSION, method, sigma, self.MASS, r,
                #                                  g, self.POTENTIAL))
                #         self.reading_json(path)
                #         if self.EIGENVALUE == 'First order':
                #             energy[g] = self.VALUE[0]
                #         elif self.EIGENVALUE == 'Second order':
                #             energy[g] = self.VALUE[1]
                #         else:
                #             energy[g] = self.VALUE[2]
                #
                #         list[r] = energy
                # self.resultCanvas.Draw_Result(list, 'gamma', self.EIGENVALUE)
            if 'dimension' in self.dependenceGraphChoiceBox.GetValue():
                for i in range(2):
                    energy = {}
                    if i == 1:
                        method = 'Main'
                    else:
                        method = 'Alternative'
                    for index in range(2,15):
                        path = os.path.join(os.getcwd(), PLOT_JSON_DIR)
                        path = os.path.join(path, method+'Method')
                        path = os.path.join(path, sigma+'Sigma')
                        if os.path.exists(path):
                            path = os.path.join(path, 'plot_data_(%s,%s)-%s-%sS-M%s_R%s_G%s_P%s.txt' %
                                                (5*index, 5*index, method, 'Pos', 0, 10,
                                                 0, self.POTENTIAL))
                        self.reading_json(path)

                        if self.EIGENVALUE == 'First order':
                            energy[index] = self.VALUE[0]
                        elif self.EIGENVALUE == 'Second order':
                            energy[index] = self.VALUE[1]
                        else:
                            energy[index] = self.VALUE[2]
                    list[i] = energy
                dimensionCoeff = self.dimensionCoeffResultChoiceBox.GetValue()
                self.resultCanvas.Draw_Result(list, 'method', self.EIGENVALUE, dimensionCoeff=dimensionCoeff)
            self.canvas_drawn[1] = True

    def on_calculate_button(self, event):
        # tree = os.walk('Plot_data')
        # for d, dirs, files in tree:
        #     for f in files:
        #         filePath = os.path.join(os.getcwd(), os.path.join(d,f))
        #         print(filePath)
        #         self.reading_json(filePath)
        #         vectorLen = len(self.VECTOR[0])
        #         import numpy
        #         dimension = int(numpy.sqrt(vectorLen))
        #         print(dimension)
        #         string = ('(%s,%s)' % (dimension, dimension))
        #         if self.N_DIMENSION == dimension:
        #             if string in f:
        #                 print('ye')
        #                 continue
        #             else:
        #                 self.M_DIMENSION = dimension
        #                 self.N_DIMENSION = dimension
        #                 splitedD = d.split('\\')
        #                 string1 = ''
        #                 string2 = ''
        #                 string3 = ''
        #                 for i, val in enumerate(splitedD):
        #                     if i == 0:
        #                         string1 = val + '_new'
        #                     elif i == 1:
        #                         string2 = val
        #                     elif i == 2:
        #                         string3 = val
        #
        #                 newFilePath = os.path.join(os.getcwd(),os.path.join(string1, os.path.join(string2, string3)))
        #                 splitedFile = f.replace('(', ')').split(')')
        #                 newFilePath = os.path.join(newFilePath, splitedFile[0] + string + splitedFile[-1])
        #                 if not os.path.exists(newFilePath):
        #                     self.creating_json(newFilePath)
        #         else:
        #             self.M_DIMENSION = dimension
        #             self.N_DIMENSION = dimension
        #             splitedD = d.split('\\')
        #             string1 = ''
        #             string2 = ''
        #             string3 = ''
        #             for i,val in enumerate(splitedD):
        #                 if i == 0:
        #                     string1 = val+'_new'
        #                 elif i == 1:
        #                     string2 = val
        #                 elif i == 2:
        #                     string3 = val
        #
        #             newFilePath = os.path.join(os.getcwd(),os.path.join(string1, os.path.join(string2, string3)))
        #             splitedFile = f.replace('(', ')').split(')')
        #             newFilePath = os.path.join(newFilePath, splitedFile[0] + string + splitedFile[-1])
        #             if not os.path.exists(newFilePath):
        #                 self.creating_json(newFilePath)
        del self.VALUE[:]
        del self.VECTOR[:]
        if self.canvas_drawn[0]:
            self.SetStatusText(text='Clearing area.')
            self.calculate_button.SetLabel('Calculate')
            self.canvas_drawn[0] = False
            self.canvas.Remove_canvas()
            self.SetStatusText(text='Waiting for arguments.')
        else:
            self.Layout()
            self.SetStatusText(text='Calculating. Please wait.')
            inst = {'sizer': self.main_sizer, 'method': self.method_choice_box, 'sigma': self.sigma_choice_box, 'mass': self.mass_choice_box,
                    'radius': self.radius_text_box, 'dimension_N': self.dimension_x_text_box,
                    'dimension_M': self.dimension_y_text_box, 'gamma': self.gamma_text_box, 'potential': self.potential_choice_box,
                    'eigenvalue': self.eigenvalue_choice_box}
            select_method_ctrl = inst['method']
            select_sigma_ctrl = inst['sigma']
            select_mass_ctrl = inst['mass']
            select_radius_ctrl = inst['radius']
            select_dimension_n_ctrl = inst['dimension_N']
            select_dimension_m_ctrl = inst['dimension_M']
            select_gamma_ctrl = inst['gamma']
            select_potential_ctrl = inst['potential']
            select_eigenvalue_ctrl = inst['eigenvalue']

            self.METHOD = str(select_method_ctrl.GetValue())
            self.SIGMA = str(select_sigma_ctrl.GetValue())
            self.MASS = int(select_mass_ctrl.GetValue())
            self.RADIUS = int(select_radius_ctrl.GetValue())
            self.N_DIMENSION = int(select_dimension_n_ctrl.GetValue())
            self.M_DIMENSION = int(select_dimension_m_ctrl.GetValue())
            self.GAMMA = int(select_gamma_ctrl.GetValue())
            self.POTENTIAL = select_potential_ctrl.GetValue()
            self.EIGENVALUE = str(select_eigenvalue_ctrl.GetValue())
            if self.METHOD == 'Main method':
                method = 'Main'
            else:
                method = 'Alternative'
            if self.SIGMA == 'Positive':
                sigma = 'Pos'
            else:
                sigma = 'Neg'
        #
        # self.M_DIMENSION = 40
        # self.N_DIMENSION = 40
        # self.POTENTIAL = True
        # for method in ['Main', 'Alternative']:
        #     if method == 'Main':
        #         self.METHOD = 'Main method'
        #     else:
        #         self.METHOD = 'Alternative method'
        #     for m in [-1]:
        #         self.MASS = m
        #         for sigma in ['Pos', 'Neg']:
        #             if sigma == 'Pos':
        #                 self.SIGMA = 'Positive'
        #             else:
        #                 self.SIGMA = 'Negative'
        #             if m == 0 and sigma != 'Pos':
        #                 continue
        #             for gamma in range(0,11):
        #                 self.GAMMA = gamma
        #                 for radius in range(1,11):
        #                     self.RADIUS = radius
        #                     path = os.path.join(os.getcwd(), PLOT_JSON_DIR)
        #                     path = os.path.join(path, method + 'Method')
        #                     path = os.path.join(path, sigma + 'Sigma')
        #                     if os.path.exists(path):
        #                         path = os.path.join(path, 'plot_data_(%s,%s)-%s-%sS-M%s_R%s_G%s_P%s.txt' % (
        #                         40, 40, method, sigma, self.MASS, self.RADIUS, self.GAMMA,
        #                         self.POTENTIAL))
        #                         if os.path.exists(path):
        #                             continue
        #                     self.filePath = path
        #                     pub.subscribe(self.calculateListener, 'calculatedTransfer')
        #                     Calculate_loop(self.METHOD, self.MASS, self.RADIUS, self.N_DIMENSION,self.M_DIMENSION, self.GAMMA, self.POTENTIAL, self.SIGMA, 00)

        # import numpy, time
        #
        # self.SIGMA = 'Positive'
        # sigma = 'Pos'
        # self.MASS = 0
        # self.GAMMA = 0
        # self.RADIUS = 10
        # for method in ['Main', 'Alternative']:
        #     if method == 'Main':
        #         self.METHOD = 'Main method'
        #     else:
        #         self.METHOD = 'Alternative method'
        #     for potential in [True, False]:
        #         self.POTENTIAL = potential
        #         start_time = time.time()
        #         for dimension in range(5,75,5):
        #             self.M_DIMENSION = dimension
        #             self.N_DIMENSION = dimension
        #             path = os.path.join(os.getcwd(), PLOT_JSON_DIR)
        #             path = os.path.join(path, method + 'Method')
        #             path = os.path.join(path, sigma + 'Sigma')
        #             if os.path.exists(path):
        #                 path = os.path.join(path, 'plot_data_(%s,%s)-%s-%sS-M%s_R%s_G%s_P%s.txt' % (
        #                     dimension, dimension, method, sigma, self.MASS, self.RADIUS, self.GAMMA,
        #                     potential))
        #                 if os.path.exists(path):
        #                     continue
        #             self.filePath = path
        #             pub.subscribe(self.calculateListener, 'calculatedTransfer')
        #             Calculate_loop(self.METHOD, self.MASS, self.RADIUS, dimension, dimension, self.GAMMA, potential, sigma, 00)
        #         print('Time: %s', time.time() - start_time)
        #
        #
            path = os.path.join(os.getcwd(), PLOT_JSON_DIR)
            path = os.path.join(path, method+'Method')
            path = os.path.join(path, sigma+'Sigma')
            if os.path.exists(path):
                path = os.path.join(path, 'plot_data_(%s,%s)-%s-%sS-M%s_R%s_G%s_P%s.txt' %
                                    (self.N_DIMENSION, self.M_DIMENSION, method, sigma, self.MASS, self.RADIUS,
                                     self.GAMMA, self.POTENTIAL))
            if os.path.exists(path):
                self.taking_data = True
                self.reading_json(path)
            if not self.taking_data_successfull:
                start_time = time.time()
                self.SetStatusText(text='Calculating. Please wait. Start time: %s' %
                                        datetime.fromtimestamp(start_time).strftime('%H:%M:%S'))
                self.calculate_button.SetLabel('Clear area')
                pub.subscribe(self.calculateListener, 'calculatedTransfer')
                import threading
                thrd = threading.Thread(target=Calculate_loop, args=(self.METHOD, self.MASS, self.RADIUS, self.N_DIMENSION,
                                                                     self.M_DIMENSION, self.GAMMA, self.POTENTIAL, self.SIGMA,
                                                                     start_time,))
                thrd.daemon = True
                thrd.start()
                self.filePath = path

            self.taking_data_successfull = False

    def calcEnd(self, start):
        start_time = start
                # self.VALUE, self.VECTOR = readTempFile()
        x, y = x_y_arrays_creating(self.RADIUS, self.N_DIMENSION, self.M_DIMENSION)
        self.canvas_drawn[0] = True
        if self.EIGENVALUE == 'First order':
            eigh_value = self.VALUE[0]
            eigh_vector = self.VECTOR[0]
        elif self.EIGENVALUE == 'Second order':
            eigh_value = self.VALUE[1]
            eigh_vector = self.VECTOR[1]
        else:
            eigh_value = self.VALUE[2]
            eigh_vector = self.VECTOR[2]

        self.canvas.Draw_canvas(x, y, np.array(eigh_vector), self.N_DIMENSION, self.M_DIMENSION, '#ffa500', self.quarterNumber)
        self.SetStatusText(text='Calculate successfully. Eigenvalue = %.8f. Start time: %s. Plot drawn in: %.3f sec.' %
                                                (eigh_value, datetime.fromtimestamp(start_time).strftime('%H:%M:%S'),
                                                 time.time() - start_time))
        self.taking_data_successfull = False
        winsound.Beep(1100, 1000)

    def creating_json(self, filename):
        data = {'plot_data': []}
        data['plot_data'].append({
            'method': self.METHOD,
            'sigma': self.SIGMA,
            'n_dimension': self.N_DIMENSION,
            'm_dimension': self.M_DIMENSION,
            'mass': self.MASS,
            'radius': self.RADIUS,
            'gamma': self.GAMMA,
            'potential': self.POTENTIAL,
            'eig_val': {
                'first order': self.VALUE[0],
                'second order': self.VALUE[1],
                'third order': self.VALUE[2]
            },
            'eig_vector': {
                'first order': [self.VECTOR[0][i] for i in range(self.N_DIMENSION*self.M_DIMENSION)],
                'second order': [self.VECTOR[1][i] for i in range(self.N_DIMENSION*self.M_DIMENSION)],
                'third order': [self.VECTOR[2][i] for i in range(self.N_DIMENSION*self.M_DIMENSION)]
            }
        })
        with open(filename, 'w') as outfile:
            json.dump(data, outfile)

    def reading_json(self, filename):
        del self.VALUE[:]
        del self.VECTOR[:]
        with open(filename, 'r') as outfile:
            if self.taking_data:
                try:
                    data = json.load(outfile)
                except:
                    self.taking_data_successfull = False
                    return
            else:
                try:
                    data = json.load(outfile)
                except:
                    message = 'No JSON object in file, no data to draw.'
                    wx.MessageBox(message, 'Error', wx.OK | wx.ICON_ERROR)
                    return
        self.METHOD = str(data['plot_data'][0]['method'])
        self.SIGMA = str(data['plot_data'][0]['sigma'])
        self.N_DIMENSION = int(data['plot_data'][0]['n_dimension'])
        self.M_DIMENSION = int(data['plot_data'][0]['m_dimension'])
        self.MASS = int(data['plot_data'][0]['mass'])
        self.RADIUS = int(data['plot_data'][0]['radius'])
        self.GAMMA = int(data['plot_data'][0]['gamma'])
        self.POTENTIAL = data['plot_data'][0]['potential']
        if self.currentPage == 'Main':
            self.EIGENVALUE = self.eigenvalue_choice_box.GetValue()
        self.VALUE.append(data['plot_data'][0]['eig_val']['first order'])
        self.VECTOR.append(data['plot_data'][0]['eig_vector']['first order'])
        self.VALUE.append(data['plot_data'][0]['eig_val']['second order'])
        self.VECTOR.append(data['plot_data'][0]['eig_vector']['second order'])
        self.VALUE.append(data['plot_data'][0]['eig_val']['third order'])
        self.VECTOR.append(data['plot_data'][0]['eig_vector']['third order'])

        if self.currentPage == 'Main':
            self.method_choice_box.SetLabel(str(self.METHOD))
            self.sigma_choice_box.SetLabel(str(self.SIGMA))
            self.mass_choice_box.SetLabel(str(self.MASS))
            self.radius_text_box.SetLabel(str(self.RADIUS))
            self.gamma_text_box.SetLabel(str(self.GAMMA))
            self.dimension_x_text_box.SetLabel(str(self.N_DIMENSION))
            self.dimension_y_text_box.SetLabel(str(self.M_DIMENSION))
            self.potential_choice_box.SetValue(str(self.POTENTIAL))
            if self.canvas_drawn[0]:
                self.canvas.Remove_canvas()
            x, y = x_y_arrays_creating(self.RADIUS, self.N_DIMENSION, self.M_DIMENSION,4)
            self.calculate_button.SetLabel('Clear area')
            self.canvas_drawn[0] = True
            if self.EIGENVALUE == 'First order':
                eigh_value = self.VALUE[0]
                eigh_vector = self.VECTOR[0]
            elif self.EIGENVALUE == 'Second order':
                eigh_value = self.VALUE[1]
                eigh_vector = self.VECTOR[1]
            else:
                eigh_value = self.VALUE[2]
                eigh_vector = self.VECTOR[2]


            self.canvas.Draw_canvas(x, y, eigh_vector, self.N_DIMENSION, self.M_DIMENSION, '#ffa500', self.quarterNumber)
            self.SetStatusText(text='Data successfully loaded from file. Eigenvalue = %.8f. File path: %s' %
                                    (eigh_value, filename))
            self.taking_data_successfull = True
        return

    def onMethodComboBox(self, event):
        return

    def onSigmaComboBox(self, event):
        return

    def onMassChoice(self, event):
        if not event.GetEventObject().GetValue() == str(0):
            self.sigma_choice_box.Enable(True)
            # self.sigma_choice_box.SetValue(self.SIGMA)
        else:
            self.sigma_choice_box.Enable(False)
            self.sigma_choice_box.SetValue('Positive')

    def onMassResultChoice(self, event):
        if not event.GetEventObject().GetValue() == str(0):
            self.sigmaResultChoiceBox.Enable(True)
            # self.sigma_choice_box.SetValue(self.SIGMA)
        else:
            self.sigmaResultChoiceBox.Enable(False)
            self.sigmaResultChoiceBox.SetValue('Positive')

    def calculateListener(self, val, vector, time):
        self.VECTOR = vector
        self.VALUE = val
        self.creating_json(self.filePath)
        self.calcEnd(time)