"""Default report stylesheet"""
from reportlab.lib.styles import ParagraphStyle, ListStyle
from reportlab.platypus import TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import black


def get_stylesheet():
    styles = {}

    styles['default'] = ParagraphStyle(
        'default',
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        leftIndent=0,
        rightIndent=0,
        firstLineIndent=0,
        alignment=TA_LEFT,
        spaceBefore=0,
        spaceAfter=0,
        bulletFontName='Helvetica',
        bulletFontSize=8,
        bulletIndent=0,
        textColor=black,
        backColor=None,
        wordWrap=None,
        borderWidth=0,
        borderPadding=0,
        borderColor=None,
        borderRadius=None,
        allowWidows=1,
        allowOrphans=0,
        textTransform=None,  # 'uppercase' | 'lowercase' | None
        endDots=None,
        splitLongWords=1,
    )

    styles['text'] = ParagraphStyle(
        'text',
        parent=styles['default'],
        spaceBefore=2,
        spaceAfter=4
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
        fontSize=9,
        leading=11,
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
        ('FONT', (0, 0), (-1, -1), styles['default'].fontName),
        ('FONTSIZE', (0, 0), (-1, -1), styles['default'].fontSize),
        ('LEADING', (0, 0), (-1, -1), styles['default'].leading),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ])

    styles['list-default'] = ListStyle(
        name='list-style',
        bulletFontName=styles['default'].fontName,
        bulletFontSize=styles['default'].fontSize
    )

    styles['prescription-item'] = ParagraphStyle(
        'prescription-item',
        parent=styles['default'],
        spaceAfter=4
    )

    styles['list-big'] = ListStyle(
        name='list-style',
        bulletFontName=styles['default'].fontName,
        bulletFontSize=10
    )

    styles['prescription-item-big'] = ParagraphStyle(
        'prescription-item',
        parent=styles['default'],
        fontSize=10,
        leading=12,
        spaceAfter=4
    )

    return styles
