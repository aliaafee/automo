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
    'six'
]

setup(
    name="mopresc",
    windows = [
        {
            "script": '__main__.py',
            "icon_resources": [(1, "automo.ico")]
        }
    ],
    #windows=['__main__.py'],
    options={
        "py2exe": {
            'bundle_files': 3,
            'compressed' : False,
            "packages": packages
            }
    }#,
    #zipfile = None
)
