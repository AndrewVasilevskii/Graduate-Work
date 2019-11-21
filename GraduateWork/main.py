# -*- encoding: utf-8 -*-
import wx
# from mainframe import MainFrame
# import multiprocessing
# import configparser
# CP = configparser.ConfigParser()
# CP.read('bitmaps/userPositionConfig.ini')
# pos = int(CP['POSITION']['positionX']), int(CP['POSITION']['positionY'])
# if __name__ == '__main__':
#
#     multiprocessing.freeze_support()
#     app = wx.App()
#     size = wx.Size(945, 685)
#     pos = wx.Point(pos)
#     frame = MainFrame(None, title='Graduate work', size=size, pos=pos, style=wx.DEFAULT_FRAME_STYLE          | wx.STAY_ON_TOP )
#     frame.Show()
#     app.MainLoop()

import itertools

# k, k1 = [1, "fjh"],[-1, 1]
# k1, k = [1, "fjh"],[-1, 1]

def number_transform(num):
    typ = type(num)
    if typ == str:
        if num.isdigit():
            return int(num)
        elif num[:2] == "0x":
            return (int(num, 16))
        elif num[:2] == "0b":
            return (int(num, 2))
        elif num[:2] == "0o":
            return (int(num, 8))
        else:
            raise ValueError
    return num

def scalar_product(iter1, iter2):
    try:
        return sum(itertools.starmap(lambda x, y: x * y, zip(map(number_transform, iter1),
                                                             map(number_transform, iter2))))
    except ValueError:
        return None

print(scalar_product([1, "2"], [-1, 1]))
print(scalar_product([1, "xyz"], [-1, 1]))


def kq(k):
    for i in list(map(fff, k)):
        print(i)
        if i is 'NoneType':
            print('a')
        return None

def scalar(k, k1):
    print(kq(k))
    print(kq(k1))
    if kq(k) is None and kq(k1) is None:
        print(sum(itertools.starmap(lambda x, y: x * y, zip(map(fff, k), map(fff, k1)))))

# print(fff("1"))
# print(kq([1, "1"]))


# import math
# main_no_donor_first_abs = abs(math.pi**2/100 - 0.0986668353140353)
# main_no_donor_first_rel = main_no_don or_first_abs/ 0.0986668353140353
# alternative_no_donor_first_abs = abs(math.pi**2/100 - 0.0987817688903076)
# alternative_no_donor_first_rel = alternative_no_donor_first_abs/0.0987817688903076
#
# main_with_donor_first_abs = 1 - 0.9950877006473412
# main_with_donor_first_rel =main_with_donor_first_abs/0.9950877006473412
# alternative_with_donor_first_abs = 1 - 0.9921402513759334
# alternative_with_donor_first_rel = alternative_with_donor_first_abs/0.9921402513759334
#
# main_with_donor_second_abs = 1/4 - 0.2252128075248813
# main_with_donor_second_rel = main_with_donor_second_abs/0.2252128075248813
# alternative_with_donor_second_abs = 1/4 - 0.22422674010320923
# alternative_with_donor_second_rel = alternative_with_donor_second_abs/0.22422674010320923
#
# main_with_donor_third_abs = 1/9 - 0.014391897807740675
# main_with_donor_third_rel = main_with_donor_third_abs/0.014391897807740675
# alternative_with_donor_third_abs = 1/9 - 0.014072376993313842
# alternative_with_donor_third_rel = alternative_with_donor_third_abs/0.014072376993313842
#
# with open('results.txt', 'w') as file:
#     file.write('\n{0}{1}\n'.format(''.ljust(25),'==== No Donor ===='))
#     file.write('\n{0}{1}\n'.format(''.ljust(25), '=== First Order ==='))
#     file.write('\t{0}\t{1}\n'.format('== Main =='.ljust(36) , '== Alternative =='.ljust(40) ))
#     file.write('{0}{1}\n'.format(('Abs = %s' % main_no_donor_first_abs).ljust(40) , ('Abs = %s' % alternative_no_donor_first_abs).ljust(20) ))
#     file.write('{0}{1}\n'.format(('Rel = %s' % main_no_donor_first_rel).ljust(40), ('Rel = %s' % alternative_no_donor_first_rel).ljust(40)))
#     file.write('\n\n{0}{1}\n'.format(''.ljust(25),'==== With Donor ===='))
#     file.write('\n{0}{1}\n'.format(''.ljust(25),'=== First Order ==='))
#     file.write('\t{0}\t{1}\n'.format('== Main =='.ljust(36) , '== Alternative =='.ljust(30) ))
#     file.write('{0}{1}\n'.format(('Abs = %s' % main_with_donor_first_abs).ljust(40) , ('Abs = %s' % alternative_with_donor_first_abs).ljust(20) ))
#     file.write('{0}{1}\n'.format(('Rel = %s' % main_with_donor_first_rel).ljust(40), ('Rel = %s' % alternative_with_donor_first_rel).ljust(40)))
#     file.write('\n{0}{1}\n'.format(''.ljust(25),'=== Second Order ==='))
#     file.write('\t{0}\t{1}\n'.format('== Main =='.ljust(36) , '== Alternative =='.ljust(15) ))
#     file.write('{0}{1}\n'.format(('Abs = %s' % main_with_donor_second_abs).ljust(40) , ('Abs = %s' % alternative_with_donor_second_abs).ljust(20) ))
#     file.write('{0}{1}\n'.format(('Rel = %s' % main_with_donor_second_rel).ljust(40), ('Rel = %s' % alternative_with_donor_second_rel).ljust(40)))
#     file.write('\n{0}{1}\n'.format(''.ljust(25),'=== Third Order ==='))
#     file.write('\t{0}\t{1}\n'.format('== Main =='.ljust(36) , '== Alternative =='.ljust(15) ))
#     file.write('{0}{1}\n'.format(('Abs = %s' % main_with_donor_third_abs).ljust(40) , ('Abs = %s' % alternative_with_donor_third_abs).ljust(20) ))
#     file.write('{0}{1}\n'.format(('Rel = %s' % main_with_donor_third_rel).ljust(40), ('Rel = %s' % alternative_with_donor_third_rel).ljust(40)))

# import numpy as np
# arr = np.array([[1,2],[3,4]]).transpose()
# arr2 = np.append(arr,arr)
# # for i in range(4):
# arnew = np.append(arr,arr)
# arrr = np.append(arr2,arnew)
# TArr = arr.transpose()
# arnew = np.append(TArr,TArr)
# print(arrr)
# import os
# import datetime
# tree = os.walk('Plot_data')
# for d, dirs, files in tree:
#     for f in files:
#          it = 40
#          string = ('(%s,%s)' % (it,it))
#          if string in f:    print('ye')
        # print(d)
        # splitedD= d.split('\\')
        # string1 = ''
        # string2 = ''
        # string3 = ''
        # for i,val in enumerate(splitedD):
        #     if i == 0:
        #         string1 = val+'_new'
        #     elif i == 1:
        #         string2 = val
        #     elif i == 2:
        #         string3 = val
        #
        # print(os.path.join(string1,os.path.join(string2,string3)))
        # splitedFile = f.replace('(', ')').split(')')
        # if '30' in f:
#             if os.path.getmtime(os.path.join(os.getcwd(), os.path.join(d, f))) > datetime.datetime(2018, 5, 22, 21,00,00).timestamp():
#
#                 old = os.path.join(d, f)
#                 # print(old)
#                 # print(splitedFile)
#                 new = os.path.join(d,splitedFile[0]+'(40,40)'+splitedFile[-1])
#                 # print(new)
#                 os.rename(old, new)
                # print(datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(os.getcwd(), os.path.join(d, f)))).strftime('%Y-%m-%d %H:%M:%S'))
# DATE = datetime.datetime(2018, 5, 22, 21,00,00)
# print(DATE.timestamp())
# print(datetime.datetime.fromtimestamp(DATE.timestamp()))
# os.rename(os.path.join(os.getcwd(), 'Plot_data/222.txt'), os.path.join(os.getcwd(), 'Plot_data/111.txt'))
        # print(os.path.getatime(f))
        # item = f.split('-')
        # method = item[1]
        # if len(item) == 5: # m = - 1
        #     sigma = item[-3].split('S')[0]
        #     magneticNumber = item[-2].split('_')[0]
        # else: # m >=0
        #     sigma = item[-2].split('S')[0]
        #     magneticNumber = item[-1].split('_')[0]
        # path = 'Plot_data'
        # path = os.path.join(path, method + 'Method')
        # path = os.path.join(path, sigma+'Sigma')
        # import shutil
#         shutil.move(os.path.join(d,f), path)
# import shutil
# shutil.move('Plot_data/111.txt', 'Plot_data/MainMethod/PosSigma')


# import wx
# from wx.lib.stattext import GenStaticText
# import webbrowser
#
#
# class Link(GenStaticText):
#
#     def __init__(self, *args, **kw):
#         super(Link, self).__init__(*args, **kw)
#
#         self.font1 = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD, True, 'Verdana')
#         self.font2 = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD, False, 'Verdana')
#
#         self.SetFont(self.font2)
#         self.SetForegroundColour('#0000ff')
#
#         self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvent)
#         self.Bind(wx.EVT_MOTION, self.OnMouseEvent)
#
#     def SetUrl(self, url):
#
#         self.url = url
#
#     def OnMouseEvent(self, e):
#
#         if e.Moving():
#
#             self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
#             self.SetFont(self.font1)
#
#         elif e.LeftUp():
#
#             webbrowser.open_new(self.url)
#
#         else:
#             self.SetCursor(wx.NullCursor)
#             self.SetFont(self.font2)
#
#         e.Skip()
#
#
# class Example(wx.Frame):
#
#     def __init__(self, *args, **kw):
#         super(Example, self).__init__(*args, **kw)
#
#         self.InitUI()
#
#     def InitUI(self):
#         panel = wx.Panel(self)
#         lnk = Link(panel, label='ZetCode', pos=(10, 60))
#         lnk.SetUrl('http://www.zetcode.com')
#
#         motto = GenStaticText(panel, label='Knowledge only matters', pos=(10, 30))
#         motto.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD, False, 'Verdana'))
#
#         self.SetSize((220, 150))
#         self.SetTitle('A Hyperlink')
#         self.Centre()
#         self.Show(True)
#
#
# def main():
#     ex = wx.App()
#     Example(None)
#     ex.MainLoop()
#
#
# if __name__ == '__main__':
#     main()

#
# import wx
#
# class Page(wx.Panel):
#     def __init__(self, parent):
#         wx.Panel.__init__(self, parent)
#         t = wx.StaticText(self, -1, "THIS IS A PAGE OBJECT", (20,20))
#
# class MainFrame(wx.Frame):
#     def __init__(self):
#         wx.Frame.__init__(self, None, title="Notebook Remove Pages Example")
#
#         pannel  = wx.Panel(self)
#         vbox    = wx.BoxSizer(wx.VERTICAL)
#         hbox    = wx.BoxSizer(wx.HORIZONTAL)
#
#         self.buttonRemove = wx.Button(pannel, id=wx.ID_ANY, label="DELETE", size=(80, 25))
#         self.buttonRemove.Bind(wx.EVT_BUTTON, self.onButtonRemove)
#         hbox.Add(self.buttonRemove)
#
#         self.buttonInsert = wx.Button(pannel, id=wx.ID_ANY, label="CREATE", size=(80, 25))
#         self.buttonInsert.Bind(wx.EVT_BUTTON, self.onButtonInsert)
#         hbox.Add(self.buttonInsert)
#
#         self.printButton = wx.Button(pannel, label='Count', size=(80,25))
#         self.printButton.Bind(wx.EVT_BUTTON, self.printCount)
#         hbox.Add(self.printButton)
#         vbox.Add(hbox)
#
#         self.Notebook3 = wx.Notebook(pannel)
#         vbox.Add(self.Notebook3, 2, flag=wx.EXPAND)
#
#         pannel.SetSizer(vbox)
#
#         self.pageCounter = 0
#         self.addPage()
#
#     def addPage(self):
#         self.pageCounter += 1
#         page      = Page(self.Notebook3)
#         pageTitle = "Page: {0}".format(str(self.pageCounter))
#         self.Notebook3.AddPage(page, pageTitle)
#
#     def onButtonRemove(self, event):
#         self.Notebook3.DeletePage(self.Notebook3.GetSelection())
#
#     def onButtonInsert(self, event):
#         self.addPage()
#
#     def printCount(self, event):
#         print(self.pageCounter)
# if __name__ == "__main__":
#     app = wx.App()
#     MainFrame().Show()
#     app.MainLoop()