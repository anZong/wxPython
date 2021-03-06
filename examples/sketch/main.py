# coding:utf-8
"""
Created on 2017/9/26
@author:zongan
"""
import wx,os


class SketchWindow(wx.Window):
    '''画板窗口'''
    def __init__(self,parent,id):
        wx.Window.__init__(self,parent,id)
        self.SetBackgroundColour('White')
        self.color = (0,0,0,1)  # 画笔颜色
        self.thickness = 5  # 画笔粗细
        self.pen = wx.Pen(self.color,self.thickness,wx.PENSTYLE_SOLID)  # 创建一只画笔

        self.lines = []
        self.curLine = []
        self.pos = (0,0)

        #   初始化画布
        self.InitBuffer()

        #  绑定事件处理函数
        self.Bind(wx.EVT_LEFT_DOWN,self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP,self.OnLeftUp)
        self.Bind(wx.EVT_MOTION,self.OnMotion)
        self.Bind(wx.EVT_SIZE,self.OnSize)
        self.Bind(wx.EVT_IDLE,self.OnIdle)
        self.Bind(wx.EVT_PAINT,self.OnPaint)

    def InitBuffer(self):
        '''初始化画布'''
        size = self.GetClientSize()
        self.buffer = wx.EmptyBitmap(size.width,size.height)
        dc = wx.BufferedDC(None,self.buffer)  # 设备上下文
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))  # 设置画布背景
        dc.Clear()  # 清除画布
        self.DrawLines(dc)
        self.reInitBuffer = False

    def GetLinesData(self):
        return self.lines[:]

    def SetLinesData(self,lines):
        self.lines = lines[:]
        self.InitBuffer()
        self.Refresh()

    def DrawLines(self,dc):
        for colour,thickness,line in self.lines:
            pen = wx.Pen(colour,thickness,wx.PENSTYLE_SOLID)  # 根据线条的颜色，粗细重新设置画笔
            dc.SetPen(pen)
            for coords in line:
                dc.DrawLine(*coords)

    def OnLeftDown(self,event):
        self.LeftDown = True
        self.curLine = []
        self.pos = event.GetPosition()
        self.CaptureMouse()  # 开始捕捉鼠标

    def OnLeftUp(self,event):
        self.LeftDown = False
        if self.HasCapture():
            self.lines.append((self.color,self.thickness,self.curLine))
            self.curLine = []
            self.ReleaseMouse()  # 释放鼠标

    def OnMotion(self,event):
        if event.Dragging() and self.LeftDown:
            dc = wx.BufferedDC(wx.ClientDC(self),self.buffer)
            self.drawMotion(dc,event)
        event.Skip()

    def drawMotion(self,dc,event):
        dc.SetPen(self.pen)
        newPos = event.GetPosition()
        coords = tuple(self.pos) + tuple(newPos)
        dc.DrawLine(*coords)
        self.curLine.append(coords)
        self.pos = newPos

    def OnSize(self,event):
        self.reInitBuffer = True

    def OnIdle(self,event):
        if self.reInitBuffer:
            self.InitBuffer()
            self.Refresh(False)

    def OnPaint(self,event):
        dc = wx.BufferedPaintDC(self,self.buffer)

    def SetColor(self,color):
        self.color = color
        self.pen = wx.Pen(color,self.thickness,wx.PENSTYLE_SOLID)

    def SetThickness(self,num):
        self.thickness = num
        self.pen = wx.Pen(self.color,num,wx.PENSTYLE_SOLID)


class SketchFrame(wx.Frame):
    def __init__(self,parent):
        wx.Frame.__init__(self,parent,-1,'画板',size=(800,600))
        self.sketch = SketchWindow(self,-1)
        self.sketch.Bind(wx.EVT_MOTION,self.OnSketchMotion)
        self.initStatusBar()
        self.createMenuBar()
        self.createToolBar()

        self.title = self.Label
        self.filename = ""
        self.wildcard = "Sketch files(*.sketch)|*.sketch|All files (*.*)|*.*"

    def initStatusBar(self):
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(3)
        self.statusbar.SetStatusWidths([-1,-2,-3])

    def createMenuBar(self):
        menubar = wx.MenuBar()
        for menu in self.menuData():
            menuLabel = menu[0]
            menuItems = menu[1]
            menubar.Append(self.createMenu(menuItems),menuLabel)
        self.SetMenuBar(menubar)

    def createMenu(self,menuData):
        menu = wx.Menu()
        for item in menuData:
            if len(item) == 2:
                label = item[0]
                subMenu = self.createMenu(item[1])
                menu.AppendMenu(-1,label,subMenu)
            else:
                self.createMenuItem(menu,*item)
        return menu

    def createMenuItem(self,menu,label,status,handler,kind=wx.ITEM_NORMAL):
        if not label:
            menu.AppendSeparator()
            return
        menuItem = menu.Append(-1,label,status,kind)
        self.Bind(wx.EVT_MENU,handler,menuItem)

    def menuData(self):
        return [
            ("文件",(
                ("新建","新建一个文件",self.OnNew),
                ("打开","打开一个已有的文件",self.OnOpen),
                ("保存","保存文件",self.OnSave),
                ("","",""),
                ("颜色",(
                    ("Black","",self.OnColor,wx.ITEM_RADIO),
                    ("Red","",self.OnColor,wx.ITEM_RADIO),
                    ("Green","",self.OnColor,wx.ITEM_RADIO),
                    ("Blue","",self.OnColor,wx.ITEM_RADIO),
                    ("其他","",self.OnOtherColor,wx.ITEM_RADIO),
                )),
                ("","",""),
                ("退出","Quit",self.OnCloseWindow)
            )),
            ("编辑",()),
            ("关于",()),
        ]

    def createToolBar(self):
        pass

    def OnSketchMotion(self,event):
        self.statusbar.SetStatusText("Pos:%s" % str(event.GetPosition()),0)
        self.statusbar.SetStatusText("Current Pts:%s" % len(self.sketch.curLine),1)
        self.statusbar.SetStatusText("Line Count:%s" % len(self.sketch.lines),2)
        event.Skip()

    def OnNew(self,event):
        self.filename = ""
        self.sketch.SetLinesData([])
        self.SetTitle(self.title)

    def OnOpen(self,event):
        dlg = wx.FileDialog(self,"打开文件...",os.getcwd(),style=wx.FD_DEFAULT_STYLE,wildcard=self.wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetPath()
            self.ReadFile()
            self.SetTitle(self.title + "--" + self.filename)
        dlg.Destroy()

    def OnSave(self,event):
        if not self.filename:
            self.OnSaveAs(event)
        else:
            self.SaveFile()

    def OnColor(self,event):
        menubar = self.GetMenuBar()
        itemId = event.GetId()
        item = menubar.FindItemById(itemId)
        color = item.GetLabel()
        self.sketch.SetColor(color)

    def OnOtherColor(self,event):
        pass

    def OnCloseWindow(self,event):
        self.Destroy()

    def SaveFile(self):
        import cPickle
        if self.filename:
            data = self.sketch.GetLinesData()
            f = open(self.filename,'w')
            cPickle.dump(data,f)
            f.close()

    def OnSaveAs(self,event):
        dlg = wx.FileDialog(self,"另存为",os.getcwd(),style=wx.FD_SAVE,wildcard=self.wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if not os.path.splitext(filename)[1]:
                filename = filename + '.sketch'
            self.filename = filename
            self.SaveFile()
            self.SetTitle(self.title + '--' + self.filename)
        dlg.Destroy()

    def ReadFile(self):
        import cPickle
        if self.filename:
            try:
                f = open(self.filename,'r')
                data = cPickle.load(f)
                f.close()
                self.sketch.SetLinesData(data)
            except cPickle.UnpicklingError:
                wx.MessageBox("该文件不是sketch文件","oops!",style=wx.OK|wx.ICON_EXCLAMATION)



if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = SketchFrame(None)
    frame.Show()
    app.MainLoop()
