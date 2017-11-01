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

    config.REPORT_HEAD_TITLE = wx_config.Read("report-head-title", config.REPORT_HEAD_TITLE)
    config.REPORT_HEAD_SUBTITLE1 = wx_config.Read("report-head-subtitle1", config.REPORT_HEAD_SUBTITLE1)
    config.REPORT_HEAD_SUBTITLE2 = wx_config.Read("report-head-subtitle2", config.REPORT_HEAD_SUBTITLE2)
    config.REPORT_HEAD_LOGO_RIGHT = wx_config.Read("report-head-logo-right", config.REPORT_HEAD_LOGO_RIGHT)
    config.REPORT_HEAD_LOGO_LEFT = wx_config.Read("report-head-logo-left", config.REPORT_HEAD_LOGO_LEFT)

    config.BATCH_IMPORT_COLUMNS = wx_config.Read("batch-import-columns", config.BATCH_IMPORT_COLUMNS)


def save_config():
    """Save Configuration to file/registery"""
    wx_config = wx.Config("AutoMo")

    wx_config.Write("date-format", config.DATE_FORMAT)
    wx_config.Write("datetime-format", config.DATETIME_FORMAT)

    wx_config.Write("default-interface", STARTUP_INTERFACE)

    wx_config.Write("report-head-title", config.REPORT_HEAD_TITLE)
    wx_config.Write("report-head-subtitle1", config.REPORT_HEAD_SUBTITLE1)
    wx_config.Write("report-head-subtitle2", config.REPORT_HEAD_SUBTITLE2)
    wx_config.Write("report-head-logo-right", config.REPORT_HEAD_LOGO_RIGHT)
    wx_config.Write("report-head-logo-left", config.REPORT_HEAD_LOGO_LEFT)

    wx_config.Write("batch-import-columns", config.BATCH_IMPORT_COLUMNS)
