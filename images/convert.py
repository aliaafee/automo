"""Convert images to b64 and generates images.py module"""
import os
import os.path
import base64


result = \
'''
"""Images used in the app, all images encoded in base 64"""
import cStringIO
import base64
import wx

_APP_ICON = None
_IMAGE_CACHE = {}

def get(image_name):
    """Converts a base64 bitmap into a wx.Bitmap"""
    global _IMAGE_CACHE
    if not _IMAGE_CACHE.has_key(image_name):
        image = base64.b64decode(_IMAGE[image_name])
        stream = cStringIO.StringIO(image)
        _IMAGE_CACHE[image_name] = wx.Bitmap(wx.Image(stream))
    return _IMAGE_CACHE[image_name]


def get_app_icon():
    global _APP_ICON
    if _APP_ICON is None:
        _APP_ICON = wx.Icon()
        _APP_ICON.CopyFromBitmap(get("icon_16"))
    return _APP_ICON

_IMAGE = {}

'''

files = os.listdir("src")

for filename in files:
    if filename[0] != ".":
        with open(os.path.join("src",filename), "rb") as image_file:
            b64 = base64.b64encode(image_file.read())
            var_name = "{0}".format(os.path.splitext(filename)[0])
            result += "_IMAGE['{0}'] = \"{1}\"\n\n".format(var_name, b64)

print result



