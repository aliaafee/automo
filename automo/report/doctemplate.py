"""Base Document Template"""
from reportlab.platypus import SimpleDocTemplate, Image
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus.flowables import Flowable

from .. import config


class DefaultHeader(Flowable):
    def __init__(self, title="HEADER", xoffset=0):
        self.xoffset = xoffset
        self.size = 16*mm
        self.width = 0
        self.height = 0
        self.logo1 = canvas.ImageReader("tmp/logo1.png")
        self.logo2 = canvas.ImageReader("tmp/logo2.png")
        self.title = title

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        return (self.xoffset, self.size)

    def draw(self):
        this_canvas = self.canv
        this_canvas.setFont('Helvetica-Bold', 12)
        this_canvas.drawCentredString(self.width / 2.0, 11*mm, config.REPORT_HEAD_TITLE)
        this_canvas.setFont('Helvetica', 8)
        this_canvas.drawCentredString(self.width / 2.0, 7*mm, config.REPORT_HEAD_SUBTITLE)
        this_canvas.setFont('Helvetica-Bold', 12)
        this_canvas.drawCentredString(self.width / 2.0, 0*mm, self.title)
        this_canvas.drawImage(self.logo1, 0, 1*mm, width=15*mm, height=15*mm)
        this_canvas.drawImage(self.logo2, ((self.width/mm) - 15)*mm, 1*mm, width=15*mm, height=15*mm)


class PageNumberCanvasMakerA4(canvas.Canvas):
    """
    Page number code from:
    http://code.activestate.com/recipes/546511-page-x-of-y-with-reportlab/
    http://code.activestate.com/recipes/576832/
    """
    def __init__(self, *args, **kwargs):
        """Constructor"""
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        self.page_number_position = (195*mm, 20*mm)


    def showPage(self):
        """On a page break, add information to the list"""
        self.pages.append(dict(self.__dict__))
        self._startPage()


    def save(self):
        """Add the page number to each page (page x of y)"""
        page_count = len(self.pages)

        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_number(page_count)
            canvas.Canvas.showPage(self)

        canvas.Canvas.save(self)


    def draw_page_number(self, page_count):
        """Add the page number, dont draw page number if only one page"""
        self.saveState()

        self.line(10*mm, 15*mm, self.page_number_position[0], 15*mm)

        if page_count > 1:
            page = "Page {0} of {1}".format(self._pageNumber, page_count)
            
            self.setFont('Times-Roman', 9)
            self.drawRightString(self.page_number_position[0], self.page_number_position[1], page)

        self.restoreState()



class PageNumberCanvasMakerA5(PageNumberCanvasMakerA4):
    def __init__(self, *args, **kwargs):
        PageNumberCanvasMakerA4.__init__(self, *args, **kwargs)
        self.page_number_position = (138*mm, 10*mm)



class DocTemplate(SimpleDocTemplate):
    """Base Document Template"""
    def __init__(self, filename, page_footer, first_page_footer=None, pagesize=A4, **kwds):
        SimpleDocTemplate.__init__(self, filename, pagesize=pagesize, **kwds)

        self.page_footer = page_footer
        self.first_page_footer = first_page_footer

        if self.first_page_footer is None:
            self.first_page_footer = page_footer

        self.pagesize = pagesize


    def onFirstPage(self, this_canvas, document):
        self.onLaterPages(this_canvas, document)


    def onLaterPages(self, this_canvas, document):
        this_canvas.saveState()
        this_canvas.setFont('Times-Roman', 9)
        this_canvas.drawString(10*mm, 10*mm, self.page_footer)
        this_canvas.restoreState()

    
    def build(self, flowables):
        canvas_maker = PageNumberCanvasMakerA5
        if self.pagesize == A4:
            canvas_maker = PageNumberCanvasMakerA4
    
        SimpleDocTemplate.build(self, flowables,
                                onFirstPage=self.onFirstPage,
                                onLaterPages=self.onLaterPages,
                                canvasmaker=canvas_maker)
