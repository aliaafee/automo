"""Base Document Template"""
from reportlab.platypus import SimpleDocTemplate, Image, Table
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus.flowables import Flowable

from .. import config


class DefaultHeader(Flowable):
    def __init__(self, title="HEADER", xoffset=0):
        self.xoffset = xoffset
        self.size = 17*mm
        self.width = 0
        self.height = 0

        self.logo_left = None
        if config.REPORT_HEAD_LOGO_LEFT != "":
            try:
                self.logo_left = canvas.ImageReader(config.REPORT_HEAD_LOGO_LEFT)
            except IOError:
                self.logo_left = None

        self.logo_right = None
        if config.REPORT_HEAD_LOGO_RIGHT != "":
            try:
                self.logo_right = canvas.ImageReader(config.REPORT_HEAD_LOGO_RIGHT)
            except IOError:
                self.logo_right = None

        self.title = title

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        return (self.xoffset, self.size)

    def draw(self):
        this_canvas = self.canv
        this_canvas.setFont('Helvetica-Bold', 12)
        this_canvas.drawCentredString(self.width / 2.0, 12*mm, config.REPORT_HEAD_TITLE)
        this_canvas.setFont('Helvetica', 7)
        this_canvas.drawCentredString(self.width / 2.0, 9.5*mm, config.REPORT_HEAD_SUBTITLE1)
        this_canvas.drawCentredString(self.width / 2.0, 6.5*mm, config.REPORT_HEAD_SUBTITLE2)
        this_canvas.setFont('Helvetica-Bold', 12)
        this_canvas.drawCentredString(self.width / 2.0, 0*mm, self.title)

        if self.logo_left is not None:
            this_canvas.drawImage(self.logo_left, 0, 1*mm, width=15*mm, height=15*mm)

        if self.logo_right is not None:
            this_canvas.drawImage(self.logo_right, ((self.width/mm) - 15)*mm, 1*mm, width=15*mm, height=15*mm)


class TableExpandable(Table):
    def __init__(self, data, colWidths, pagesize, rightMargin, leftMargin, *args, **kwargs):
        exp_columns_count = 0
        total_width = 0
        for colWidth in colWidths:
            if colWidth is None:
                exp_columns_count += 1
            else:
                total_width += colWidth

        if exp_columns_count > 0:
            w, h = pagesize
            exp_col_width = (w - rightMargin - leftMargin - total_width) / exp_columns_count
            newColWidths = []
            for colWidth in colWidths:
                if colWidth is None:
                    newColWidths.append(exp_col_width)
                else:
                    newColWidths.append(colWidth)
            Table.__init__(self, data, colWidths=newColWidths, *args, **kwargs)
            return

        Table.__init__(self, data, colWidths=colWidths, *args, **kwargs)
        


class PageNumberCanvasMaker(canvas.Canvas):
    """
    Page number code from:
    http://code.activestate.com/recipes/546511-page-x-of-y-with-reportlab/
    http://code.activestate.com/recipes/576832/
    """
    def __init__(self, *args, **kwargs):
        """Constructor"""
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        self.pagesize = kwargs['pagesize']

        w, h = self.pagesize
        self.page_number_position = (w - 20*mm, 22*mm)
        self.head_position = h - 20*mm


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

        self.line(20*mm, 25*mm, self.page_number_position[0], 25*mm)

        if page_count > 1:
            if self._pageNumber > 1:
                self.line(20*mm, self.head_position, self.page_number_position[0], self.head_position)

            page = "Page {0} of {1}".format(self._pageNumber, page_count)
            
            self.setFont('Helvetica', 7)
            self.drawRightString(self.page_number_position[0], self.page_number_position[1], page)

        self.restoreState()




class DocTemplate(SimpleDocTemplate):
    """Base Document Template"""
    def __init__(self, filename, page_footer, page_header, first_page_footer=None, pagesize=A4, **kwds):
        SimpleDocTemplate.__init__(self, filename, pagesize=pagesize, **kwds)

        self.page_footer = page_footer
        self.page_header = page_header
        self.first_page_footer = first_page_footer

        #if self.first_page_footer is None:
        self.first_page_footer = ""

        self.pagesize = pagesize
        self.header_position = pagesize[1] - 19*mm


    def onFirstPage(self, this_canvas, document):
        this_canvas.saveState()
        this_canvas.setFont('Helvetica', 7)
        this_canvas.drawString(20*mm, 22*mm, self.first_page_footer)
        this_canvas.restoreState()


    def onLaterPages(self, this_canvas, document):
        this_canvas.saveState()
        this_canvas.setFont('Helvetica', 7)
        this_canvas.drawString(20*mm, 22*mm, self.page_footer)
        this_canvas.drawString(20*mm, self.header_position, self.page_header)
        this_canvas.restoreState()

    
    def build(self, flowables):
        SimpleDocTemplate.build(self, flowables,
                                onFirstPage=self.onFirstPage,
                                onLaterPages=self.onLaterPages,
                                canvasmaker=PageNumberCanvasMaker)
