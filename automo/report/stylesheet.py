"""Default report stylesheet"""
from reportlab.lib.styles import ParagraphStyle, ListStyle
from reportlab.platypus import TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import black


def get_stylesheet():
    styles = {}

    styles['default'] = ParagraphStyle(
        'default',
        fontName='Times-Roman',
        fontSize=10,
        leading=12,
        leftIndent=0,
        rightIndent=0,
        firstLineIndent=0,
        alignment=TA_LEFT,
        spaceBefore=0,
        spaceAfter=0,
        bulletFontName='Times-Roman',
        bulletFontSize=10,
        bulletIndent=0,
        textColor= black,
        backColor=None,
        wordWrap=None,
        borderWidth= 0,
        borderPadding= 0,
        borderColor= None,
        borderRadius= None,
        allowWidows= 1,
        allowOrphans= 0,
        textTransform=None,  # 'uppercase' | 'lowercase' | None
        endDots=None,         
        splitLongWords=1,
    )

    styles['text'] = ParagraphStyle(
        'text',
        parent=styles['default'],
        spaceBefore=10
    )

    styles['header'] = ParagraphStyle(
        'header',
        parent=styles['default'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        alignment=TA_CENTER
    )

    styles['header-subscript'] = ParagraphStyle(
        'header-subscript',
        parent=styles['default'],
        fontName='Helvetica',
        fontSize=8,
        leading=9,
        alignment=TA_CENTER
    )

    styles['title'] = ParagraphStyle(
        'title',
        parent=styles['default'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        spaceBefore=5,
        spaceAfter=10,
        alignment=TA_CENTER
    )

    styles['heading_1'] = ParagraphStyle(
        'heading_1',
        parent=styles['default'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        spaceBefore=10
    )

    styles['heading_2'] = ParagraphStyle(
        'heading_2',
        parent=styles['default'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        spaceBefore=10
    )

    styles['table-default'] = TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ])

    styles['list-default'] = ListStyle(
        name='list-style',
        bulletFontName='Times-Roman',
        bulletFontSize=10
    )

    w = TableStyle()

    return styles
