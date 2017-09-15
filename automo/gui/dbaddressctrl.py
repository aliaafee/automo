"""Address Control"""
import wx

from .. import database as db


class DbAddressCtrl(wx.Panel):
    """Address Control"""
    def __init__(self, parent, **kwds):
        super(DbAddressCtrl, self).__init__(parent, **kwds)

        self.txt_line1 = wx.TextCtrl(self)
        self.txt_line2 = wx.TextCtrl(self)
        self.txt_line3 = wx.TextCtrl(self)
        self.txt_city = wx.TextCtrl(self)
        self.txt_region = wx.TextCtrl(self)
        self.txt_country = wx.TextCtrl(self)

        grid_sizer = wx.FlexGridSizer(8, 2, 0, 0)
        grid_sizer.AddMany([
            (wx.StaticText(self, label="Line 1"), 1, wx.ALIGN_CENTER_VERTICAL),
            (self.txt_line1, 1, wx.EXPAND),
            (wx.StaticText(self, label="Line 2"), 1, wx.ALIGN_CENTER_VERTICAL),
            (self.txt_line2, 1, wx.EXPAND),
            (wx.StaticText(self, label="Line 3"), 1, wx.ALIGN_CENTER_VERTICAL),
            (self.txt_line3, 1, wx.EXPAND),
            (wx.StaticText(self, label="City"), 1, wx.ALIGN_CENTER_VERTICAL),
            (self.txt_city, 1, wx.EXPAND),
            (wx.StaticText(self, label="Region"), 1, wx.ALIGN_CENTER_VERTICAL),
            (self.txt_region, 1, wx.EXPAND),
            (wx.StaticText(self, label="Country"), 1, wx.ALIGN_CENTER_VERTICAL),
            (self.txt_country, 1, wx.EXPAND)
        ])
        grid_sizer.AddGrowableCol(1)

        self.SetSizer(grid_sizer)


    def set(self, address):
        if address is None:
            self.txt_line1.SetValue("")
            self.txt_line2.SetValue("")
            self.txt_line3.SetValue("")
            self.txt_region.SetValue("")
            self.txt_country.SetValue("")
            return
            
        blank = lambda s: "" if s is None else s

        self.txt_line1.SetValue(blank(address.line_1))
        self.txt_line2.SetValue(blank(address.line_2))
        self.txt_line3.SetValue(blank(address.line_3))
        self.txt_city.SetValue(blank(address.city))
        self.txt_region.SetValue(blank(address.region))
        self.txt_country.SetValue(blank(address.country))


    def get(self):
        address = db.Address()
        address.line_1 = self.txt_line1.GetValue()
        address.line_2 = self.txt_line2.GetValue()
        address.line_3 = self.txt_line3.GetValue()
        address.city = self.txt_city.GetValue()
        address.region = self.txt_region.GetValue()
        address.country = self.txt_country.GetValue()

        return address
