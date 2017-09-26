# coding:utf-8
# !/usr/bin/env python

import wx, sys


class App(wx.App):
    '''应用程序对象'''

    def __init__(self, redirect=True, filename=None):
        print 'App __init__'
        wx.App.__init__(self, redirect, filename)

    def OnInit(self):
        print 'App OnInit'
        self.frame = Frame()  # 创建框架
        self.frame.Show()
        self.SetTopWindow(self.frame)
        print>> sys.stderr, "An Error Msg!"
        return True

    def OnExit(self):
        print "App OnExit"


class Frame(wx.Frame):
    '''框架'''

    def __init__(self, parent=None, id=-1, title="测试"):
        print 'Frame __init__'
        wx.Frame.__init__(self, parent, id, title)
        panel = wx.Panel(self)  # 添加画板

        # 增加菜单栏
        menuBar = wx.MenuBar()
        menuBar.Append(wx.Menu(), "&File")
        menuBar.Append(wx.Menu(), "&Copy")
        self.SetMenuBar(menuBar)


def main():
    app = App(True, 'output')  # 文本重定向
    print "Before MainLoop"
    app.MainLoop()
    print "After MainLoop"


if __name__ == '__main__':
    main()
