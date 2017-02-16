from distutils.core import setup
import py2exe


setup(
    name="db-patch-for-rev15",
    console = [
        {
            "script": 'db-patch-for-rev15.py'
        }
    ],
    options={
        "py2exe": {
            'bundle_files': 1,
            'compressed' : False
            }
    },
    zipfile = None
)
