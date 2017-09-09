from distutils.core import setup
import py2exe

packages=[
    'reportlab',
    #'reportlab.graphics.charts',
    #'reportlab.graphics.samples',
    #'reportlab.graphics.widgets',
    #'reportlab.graphics.barcode',
    #'reportlab.graphics',
    'reportlab.lib',
    'reportlab.pdfbase',
    'reportlab.pdfgen',
    'reportlab.platypus',
    'sqlalchemy',
    'six',
    'lxml'
]

setup(
    name="automo",
    windows = [
        {
            "script": 'automo-gui.py',
            "icon_resources": [(1, "automo.ico")]
        }
    ],
    console = ["automo-cli.py"],
    options={
        "py2exe": {
            'bundle_files': 3,
            'compressed' : False,
            "packages": packages
            }
    }
)
