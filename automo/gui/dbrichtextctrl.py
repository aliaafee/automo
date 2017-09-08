"""Db Rich Text Ctrl"""
from StringIO import StringIO

from bs4 import BeautifulSoup
import wx
import wx.richtext

import images
from .events import DbCtrlChangedEvent


class DbRichTextCtrl(wx.Panel):
    """Rich Text ctrl that automatically updates database entry, on text change.
      currently only supports bold, italic and underline formatting."""
    def __init__(self, parent, session, **kwds):
        super(DbRichTextCtrl, self).__init__(parent, **kwds)

        self.session = session

        self.db_object = None
        self.db_str_attr = None

        self.editable = True

        self.changed = False

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_NODIVIDER)

        self.toolbar.AddLabelTool(wx.ID_SAVE, "Save", images.get("save"), wx.NullBitmap, wx.ITEM_NORMAL, "Save changes", "")
        self.toolbar.EnableTool(wx.ID_SAVE, False)
        self.toolbar.AddSeparator()
        self.toolbar.AddLabelTool(wx.ID_CUT, "Cut", images.get("cut"), wx.NullBitmap, wx.ITEM_NORMAL, "Cut", "")
        self.toolbar.AddLabelTool(wx.ID_COPY, "Copy", images.get("copy"), wx.NullBitmap, wx.ITEM_NORMAL, "Copy", "")
        self.toolbar.AddLabelTool(wx.ID_PASTE, "Paste", images.get("paste"), wx.NullBitmap, wx.ITEM_NORMAL, "Paste", "")
        self.toolbar.AddSeparator()
        self.toolbar.AddLabelTool(wx.ID_UNDO, "Undo", images.get("undo"), wx.NullBitmap, wx.ITEM_NORMAL, "Undo", "")
        self.toolbar.AddLabelTool(wx.ID_REDO, "Redo", images.get("redo"), wx.NullBitmap, wx.ITEM_NORMAL, "Redo", "")
        self.toolbar.AddSeparator()
        self.toolbar.AddLabelTool(wx.ID_BOLD, "Bold", images.get("bold"), wx.NullBitmap, wx.ITEM_NORMAL, "Bold", "")
        self.toolbar.AddLabelTool(wx.ID_ITALIC, "Italic", images.get("italic"), wx.NullBitmap, wx.ITEM_NORMAL, "Italic", "")
        self.toolbar.AddLabelTool(wx.ID_UNDERLINE, "Underline", images.get("underline"), wx.NullBitmap, wx.ITEM_NORMAL, "Underline", "")

        self.toolbar.Bind(wx.EVT_TOOL, self._on_save, id=wx.ID_SAVE)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_cut, id=wx.ID_CUT)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_copy, id=wx.ID_COPY)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_paste, id=wx.ID_PASTE)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_undo, id=wx.ID_UNDO)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_redo, id=wx.ID_REDO)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_bold, id=wx.ID_BOLD)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_italic, id=wx.ID_ITALIC)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_underline, id=wx.ID_UNDERLINE)

        self.toolbar.Realize()
        sizer.Add(self.toolbar, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT,
                  border=5)

        self.text_ctrl = wx.richtext.RichTextCtrl(self)
        self.text_ctrl.Bind(wx.EVT_TEXT, self._on_change)
        sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, border=5)

        self.SetSizer(sizer)


    def _has_changed(self):
        self.changed = True
        self.toolbar.EnableTool(wx.ID_SAVE, True)


    def _on_save(self, event):
        self.save_changes()


    def _on_cut(self, event):
        self.text_ctrl.Cut()
        self._has_changed()


    def _on_copy(self, event):
        self.text_ctrl.Copy()
        self._has_changed()


    def _on_paste(self, event):
        self.text_ctrl.Paste()
        self._has_changed()


    def _on_undo(self, event):
        self.text_ctrl.Undo()
        self._has_changed()


    def _on_redo(self, event):
        self.text_ctrl.Redo()
        self._has_changed()


    def _on_bold(self, event):
        self.text_ctrl.ApplyBoldToSelection()
        self._has_changed()


    def _on_italic(self, event):
        self.text_ctrl.ApplyItalicToSelection()
        self._has_changed()


    def _on_underline(self, event):
        self.text_ctrl.ApplyUnderlineToSelection()
        self._has_changed()


    def set_dbobject_attr(self, db_object, str_attr):
        """Set which object needs to be updated"""
        self.db_object = db_object
        self.db_str_attr = str_attr

        if self.db_object is None or self.db_str_attr == "":
            self.text_ctrl.ChangeValue("")
        else:
            value = getattr(self.db_object, self.db_str_attr)
            if value is None:
                value = ""

            self._set_html(value)

        self.changed = False
        self.toolbar.EnableTool(wx.ID_SAVE, False)


    def _on_change(self, event):
        """Track changes"""
        self._has_changed()


    def _get_xml(self):
        """Get richtext xml."""
        out = StringIO()
        handler = wx.richtext.RichTextXMLHandler()
        buff = self.text_ctrl.GetBuffer()
        handler.SaveStream(buff, out)
        out.seek(0)
        content = out.read()
        return content


    def _get_html(self):
        """Get richtext html."""
        out = StringIO()
        handler = wx.richtext.RichTextHTMLHandler()
        buff = self.text_ctrl.GetBuffer()
        handler.SaveStream(buff, out)
        out.seek(0)
        content = out.read()
        #strip extra stuff
        content = content.replace('<font face="Tahoma" size="1" color="#000000" >', '')
        content = content.replace('</font>', '')
        content = content.replace(' align="left"', '')
        content = content.replace('<html>', '')
        content = content.replace('</html>', '')
        content = content.replace('<head></head>', '')
        content = content.replace('<body>', '')
        content = content.replace('</body>', '')
        return content


    def _parse_tag(self, tag):
        attributes = []
        strings = []
        if tag.name == 'b':
            attributes.append('fontweight="92"')
        elif tag.name == 'i':
            attributes.append('fontstyle="93"')
        elif tag.name == 'u':
            attributes.append('fontunderlined="1"')
        for child in tag.children:
            if child.__class__.__name__ == "NavigableString":
                strings.append(unicode(child))
            elif child.__class__.__name__ == "Tag":
                child_attributes, child_strings = self._parse_tag(child)
                attributes.extend(child_attributes)
                strings.extend(child_strings)
        return attributes, strings


    def _convert_html_to_xml(self, html_str):
        """Convert html to xml, accepts document without <body> and <html> tags
          Currently only supports <b> <i> and <u> tags."""
        html_str = "<html>{}</html>".format(html_str)
        soup = BeautifulSoup(html_str, "lxml-xml")

        paragraphs_xml = []
        paragraphs = soup.find_all("p")
        for paragraph in paragraphs:
            paragraph_xml = []
            was_bold = False
            for child in paragraph.children:
                if child.__class__.__name__ == "NavigableString":
                    if was_bold:
                        paragraph_xml.append('<text fontweight="90">"{}"</text>'.format(child))
                        was_bold = False
                    else:
                        paragraph_xml.append('<text>"{}"</text>'.format(child))
                elif child.__class__.__name__ == "Tag":
                    attributes, strings = self._parse_tag(child)
                    paragraph_xml.append(
                        '<text {0}>"{1}"</text>'.format(
                            " ".join(attributes),
                            "".join(strings)
                        )
                    )
                    if 'fontweight="92"' in attributes:
                        was_bold = True
            paragraphs_xml.append(
                "<paragraph>\n{}\n</paragraph>\n".format(
                    "\n".join(paragraph_xml)
                )
            )
        document = '<?xml version="1.0" encoding="UTF-8"?>\n<richtext version="1.0.0.0" xmlns="http://www.wxwidgets.org">\n<paragraphlayout textcolor="#000000" fontpointsize="8" fontfamily="70" fontstyle="90" fontweight="90" fontunderlined="0" fontface="Tahoma" alignment="1" parspacingafter="10" parspacingbefore="0" linespacing="10" margin-left="5,4098" margin-right="5,4098" margin-top="5,4098" margin-bottom="5,4098">\n{}</paragraphlayout>\n</richtext>'
        return document.format("".join(paragraphs_xml))


    def _set_html(self, html_str):
        """Set richtext html."""
        xml_str = self._convert_html_to_xml(html_str)
        self._set_xml(xml_str)


    def _set_xml(self, xml_str):
        """Set richtext xml."""
        self.text_ctrl.ChangeValue("")
        if xml_str == "":
            return        
        out = StringIO()
        handler = wx.richtext.RichTextXMLHandler()
        buff = self.text_ctrl.GetBuffer()
        buff.AddHandler(handler)
        out.write(str(xml_str))
        out.seek(0)
        handler.LoadStream(buff, out)
        self.text_ctrl.Refresh()


    def set_editable(self, editable):
        """Set control to editable or not"""
        if editable:
            self.toolbar.Show()
            self.text_ctrl.SetEditable(True)
        else:
            self.toolbar.Hide()
            self.text_ctrl.SetEditable(False)

        if self.editable != editable:
            self.Layout()

        self.editable = editable


    def is_unsaved(self):
        """Check to see if any changes have been saved, must do before closing"""
        if self.db_object is None or self.db_str_attr == "":
            return False

        if self.changed:
            return True
        return False


    def save_changes(self):
        """Save changes"""
        if self.db_object is None or self.db_str_attr == "":
            return

        value = self._get_html()

        setattr(self.db_object, self.db_str_attr, value)

        self.session.commit()

        self.changed = False
        self.toolbar.EnableTool(wx.ID_SAVE, False)

        event = DbCtrlChangedEvent(object=self.db_object)
        wx.PostEvent(self, event)
