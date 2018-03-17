"""Icd10 Category List"""
import wx
from sqlalchemy import and_

from ... import database as db


class Icd10CategoryList(wx.html.SimpleHtmlListBox):
    """List of Icd10 Categories in a block"""
    def __init__(self, parent, session, style=wx.BORDER_THEME, **kwds):
        super(Icd10CategoryList, self).__init__(
            parent, style=style, **kwds)

        self.session = session

        self.selected_category = None
        self.categories = []

        if wx.Platform == "__WXMSW__":
            self.SetSelectionBackground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENUHILIGHT))
        else:
            self.SetSelectionBackground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))


    def get_selected_category(self):
        """Return selected Icd10Category object"""
        try:
            self.selected_category = self.categories[self.GetSelection()]
        except IndexError:
            self.selected_category = None
        return self.selected_category


    def _goto_selected(self):
        list_index = 0
        for category in self.categories:
            if category.code == self.selected_category.code:
                self.SetSelection(list_index)
            list_index += 1


    def set_code(self, code):
        """Set the category that is selected, search by code"""
        self.selected_category = self.session.query(db.Icd10Class)\
                                    .filter(db.Icd10Class.code == code)\
                                    .one()
        if self.selected_category is None:
            return

        self.set_block(self.selected_category.parent_block_code)
        self._goto_selected()


    def set_category(self, category):
        """Set the category that is selected"""
        if category is None:
            self.categories = []
            self.Clear()
            self.selected_category = None
            return

        self.get_selected_category()

        if self.selected_category is not None:
            if category.code == self.selected_category.code:
                return

            if category.parent_block_code == self.selected_category.parent_block_code:
                self.selected_category = category
                self._goto_selected()
                return

        self.selected_category = category
        self.set_block(self.selected_category.parent_block_code)
        self._goto_selected()


    def set_block(self, block_code):
        """Set the currently displayed block"""
        self.categories = []
        self.Clear()
        categories = self.session.query(db.Icd10Class)\
                        .filter(
                            and_(
                                db.Icd10Class.kind == "category",
                                db.Icd10Class.parent_block_code == block_code
                            )
                        )

        htmls = []
        for category in categories:
            self.categories.append(category)
            main_cat = u'<font size="2"><table width="100%" cellspacing="0" border="0">'\
                        '<tr height="2" bgcolor="black">'\
                            '<td cellpadding="0" colspan="2"></td>'\
                        '</tr>'\
                        '<tr>'\
                            '<td width="50" bgcolor="black">'\
                                '<font color="white"><b>{0}</b></font>'\
                            '</td>'\
                            '<td><b>{1}</b></td>'\
                        '</tr>'\
                        '<tr>'\
                            '<td></td>'\
                            '<td>{2}</td>'\
                        '</tr>'\
                    '</table></font>'

            sub_cat = u'<font size="2"><table width="100%" cellspacing="0" border="0">'\
                        '<tr>'\
                            '<td width="50"><b>{0}</b></td>'\
                            '<td><b>{1}</b></td>'\
                        '</tr>'\
                        '<tr>'\
                            '<td></td>'\
                            '<td>{2}</td>'\
                        '</tr>'\
                    '</table></font>'

            html = sub_cat
            if len(category.code) <= 3:
                html = main_cat

            content = ""

            if category.preferred_long is not None:
                content += u"{0}".format(category.preferred_long)

            if category.text is not None:
                content += u"{0}".format(category.text)

            if category.inclusion is not None:
                content += u'<table width="100%">'\
                            '<tr>'\
                                '<td valign="top" width="40"><b><i>Incl.:</i></b></td>'\
                                '<td>{0}</td>'\
                            '<tr>'\
                        '</table>'.format(category.inclusion)

            if category.exclusion is not None:
                content += u'<table width="100%">'\
                            '<tr>'\
                                '<td valign="top" width="40"><b><i>Excl.:</i></b></td>'\
                                '<td>{0}</td>'\
                            '<tr>'\
                        '</table>'.format(category.exclusion)

            if category.note is not None:
                content += u'<table width="100%">'\
                            '<tr>'\
                                '<td valign="top" width="40"><b><i>Note:</i></b></td>'\
                                '<td>{0}</td>'\
                            '<tr>'\
                        '</table>'.format(category.note)

            if category.coding_hint is not None:
                content += u'<div><b><i>Coding Hint:</i></b> {0}</div>'.format(category.coding_hint)

            html = html.format(category.code, category.preferred, content)

            htmls.append(html)

        self.SetItems(htmls)
