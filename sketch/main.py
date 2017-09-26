# coding:utf-8
"""
Created on 2017/9/26
@author:zongan
"""
import wx


class SketchWindow(wx.Window):
    def __init__(self,parent,ID):
        wx.Window.__init__(self,parent,ID)
        self.SetBackgroundColour('White')
        self.color = 'Black'  # 画笔颜色
        self.thickness = 1  # 画笔粗细
        self.pen = wx.Pen(self.color,self.thickness,wx.SOLID)  # 创建一只画笔

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
            pen = wx.Pen(colour,thickness,wx.SOLID)
            dc.SetPen(pen)
            for coords in line:
                dc.DrawLine(*coords)

    def OnLeftDown(self,event):
        self.curLine = []
        self.pos = wx.GetMousePosition()
        self.CaptureMouse()  # 开始捕捉鼠标

    def OnLeftUp(self,event):
        if self.HasCapture():
            self.lines.append((self.color,self.thickness,self.curLine))
            self.curLine = []
            self.ReleaseMouse()  # 释放鼠标

    def OnMotion(self,event):
        if event.Dragging() and event.LeftDown():
            dc = wx.BufferedDC(wx.ClientDC(self),self.buffer)
            self.drawMotion(dc,event)
        event.Skip()

    def drawMotion(self,dc,event):
        dc.SetPen(self.pen)
        newPos = wx.GetMousePosition()
        coords = self.pos + newPos
        self.curLine.append(coords)
        dc.DrawLine(*coords)
        self.pos = newPos

    def OnSize(self,event):
        self.reInitBuffer = True

    def OnIdle(self,event):
        if self.reInitBuffer:
            self.InitBuffer()
            self.Refresh(False)

    def OnPaint(self,event):
        dc = wx.BufferedPaintDC(self,self.buffer)

    def setColor(self,color):
        self.color = color
        self.pen = wx.Pen(self.color,self.thickness,wx.SOLID)

    def setThickness(self,num):
        self.thickness = num
        self.pen = wx.Pen(self.color,self.thickness,wx.SOLID)

class SketchFrame(wx.Frame):
    def __init__(self,parent):
        wx.Frame.__init__(self,parent,-1,'画板',size=(800,600))
        self.sketch = SketchWindow(self,-1)


if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = SketchFrame(None)
    frame.Show()
    app.MainLoop()
