
import wx
from mainframe import MainFrame
import multiprocessing
import configparser
CP = configparser.ConfigParser()
CP.read('bitmaps/userPositionConfig.ini')
pos = int(CP['POSITION']['positionX']), int(CP['POSITION']['positionY'])
if __name__ == '__main__':

    multiprocessing.freeze_support()
    app = wx.App()
    size = wx.Size(945, 685)
    pos = wx.Point(pos)
    frame = MainFrame(None, title='Graduate work', size=size, pos=pos, style=wx.DEFAULT_FRAME_STYLE          | wx.STAY_ON_TOP )
    frame.Show()
    app.MainLoop()
