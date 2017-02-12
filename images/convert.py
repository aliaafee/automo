import os
import os.path
import base64 


result = """
import wx
import cStringIO
import base64


def BitmapFromBase64(str_base64):
    image = base64.b64decode(str_base64)
    stream = cStringIO.StringIO(image)

    return wx.BitmapFromImage(wx.ImageFromStream(stream))


"""

files = os.listdir("src")

for filename in files:
    with open(os.path.join("src",filename), "rb") as image_file:
        b64 = base64.b64encode(image_file.read())
        var_name = "{0}_b64".format(os.path.splitext(filename)[0])
        result += "{0} = \"{1}\"\n\n".format(var_name, b64)

print result



