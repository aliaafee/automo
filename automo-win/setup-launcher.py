from distutils.core import setup
import py2exe


setup(
    name="mopresc-launcher",
    windows = [
        {
            "script": 'launcher.py',
            "icon_resources": [(1, "automo.ico")]
        }
    ],
    #windows=['__main__.py'],
    options={
        "py2exe": {
            'bundle_files': 1,
            'compressed' : False
            }
    },
    zipfile = None
)
