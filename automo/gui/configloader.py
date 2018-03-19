"""Loads and saves configurations"""
import wx

from .. import config
from . import guiconfig


APP_NAME = "AutoMO"
FILENAME = "config.ini"
STYLE = wx.CONFIG_USE_LOCAL_FILE | wx.CONFIG_USE_RELATIVE_PATH


CONFIG_FIELDS = {
    'default-interface':
        ("Startup Interface", guiconfig, 'STARTUP_INTERFACE'),
    'date-format':
        ("Date Format", config, 'DATE_FORMAT'),
    'datetime-format':
        ("Date Time Format", config, 'DATETIME_FORMAT'),
    'time-format':
        ("Time Format", config, 'TIME_FORMAT'),
    'report-head-title':
        ("Report Title", config, 'REPORT_HEAD_TITLE'),
    'report-head-subtitle1':
        ("Report Subtitle 1", config, 'REPORT_HEAD_SUBTITLE1'),
    'report-head-subtitle2':
        ("Report Subtitle 2", config, 'REPORT_HEAD_SUBTITLE2'),
    'report-head-subtitle3':
        ("Report Subtitle 3", config, 'REPORT_HEAD_SUBTITLE3'),
    'report-head-logo-right':
        ("Report Logo Right", config, 'REPORT_HEAD_LOGO_RIGHT'),
    'report-head-logo-left':
        ("Report Logo Left", config, 'REPORT_HEAD_LOGO_LEFT'),
    'batch-import-columns':
        ("Batch Import Columns", config, 'BATCH_IMPORT_COLUMNS'),
    'circum-chief-complaint':
        ("Circumcision Cheif Complaints", config, 'CIRCUM_CHIEF_COMPLAINT'),
    'circum-preop-orders':
        ("Circumcision Preop Orders", config, 'CIRCUM_PREOP_ORDERS'),
    'circum-discharge-advice':
        ("Circumcision Discharge Advice", config, 'CIRCUM_DISCHARGE_ADVICE'),
    'circum-follow-up':
        ("Circumcision Follow up", config, 'CIRCUM_FOLLOW_UP'),
    'circum-meds':
        ("Circumcision Discharge Meds", config, 'CIRCUM_MEDS')
}


def load_config():
    """Load Configuration from file/registery"""
    wx_config = wx.FileConfig(
        appName=APP_NAME,
        localFilename=FILENAME,
        style=STYLE
    )

    for field_name, (label, module, attr) in CONFIG_FIELDS.items():
        default_value = getattr(module, attr)

        value = wx_config.Read(field_name, default_value)

        setattr(module, attr, value)


def save_config():
    """Load Configuration from file/registery"""
    wx_config = wx.FileConfig(
        appName=APP_NAME,
        localFilename=FILENAME,
        style=STYLE
    )

    for field_name, (label, module, attr) in CONFIG_FIELDS.items():
        value = getattr(module, attr)

        wx_config.Write(field_name, value)

