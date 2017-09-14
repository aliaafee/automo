"""GUI Configuration"""
import wx
from .. import config

STARTUP_INTERFACE = ""


def load_config():
    """Load Configuration from file/registery"""
    global STARTUP_INTERFACE

    wx_config = wx.Config("AutoMo")

    config.DATE_FORMAT = wx_config.Read("date-format", config.DATE_FORMAT)
    config.DATETIME_FORMAT = wx_config.Read("datetime-format", config.DATETIME_FORMAT)

    STARTUP_INTERFACE = wx_config.Read("default-interface", STARTUP_INTERFACE)


def save_config():
    """Save Configuration to file/registery"""
    wx_config = wx.Config("AutoMo")

    wx_config.Write("date-format", config.DATE_FORMAT)
    wx_config.Write("datetime-format", config.DATETIME_FORMAT)

    wx_config.Write("default-interface", STARTUP_INTERFACE)
