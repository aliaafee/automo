"""Condition Panel"""
import wx

from events import *
import images
from icd10coder import Icd10Coder
from database import Condition
from dbqueryresultbox import DbQueryResultBox


class ConditionPanel(wx.Panel):
    """Condition Panel"""
    def __init__(self, parent, session, **kwds):
        super(ConditionPanel, self).__init__(parent, **kwds)

        self.session = session
        self.admission = None

        self.editable = True

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.toolbar = wx.ToolBar(self, style=wx.TB_NODIVIDER)

        tb_add = self.toolbar.AddLabelTool(
            wx.ID_ANY,
            label="Add",
            bitmap=images.get("add_condition"),
            shortHelp="Add Condition"
        )
        self.Bind(wx.EVT_TOOL, self.on_add_condition, tb_add)

        tb_add_quick = self.toolbar.AddLabelTool(
            wx.ID_ANY,
            label="Add Quick Search",
            bitmap=images.get("add_condition_quick"),
            shortHelp="Add Condition from Quick Search"
        )
        self.Bind(wx.EVT_TOOL, self.on_add_quick, tb_add_quick)

        tb_add_favourite = self.toolbar.AddLabelTool(
            wx.ID_ANY,
            label="Add Favourite",
            bitmap=images.get("add_condition_favourite"),
            shortHelp="Add Condition from Favourites"
        )
        self.Bind(wx.EVT_TOOL, self.on_add_favourite, tb_add_favourite)

        self.toolbar.Realize()
        sizer.Add(self.toolbar, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT,
                  border=5)

        self.conditions_list = DbQueryResultBox(self, self._conditions_decorator)
        sizer.Add(self.conditions_list, 1, wx.EXPAND | wx.ALL, border=5)

        self.SetSizer(sizer)

        self.icd10_coder = Icd10Coder(self, self.session)


    def _conditions_decorator(self, condition_object, query_string):
        comment = "" if condition_object.comment is None\
                  else "<tr><td></td><td></td><td>({0})</td></tr>".format(condition_object.comment)
        modifer_cls_strs = []
        for modifer_cls in [condition_object.icd10modifier_class,
                            condition_object.icd10modifier_extra_class]:
            if modifer_cls is not None:
                modifer_cls_strs.append(
                    '<tr><td></td><td></td><td>{0}: {1} - {2}</td></tr>'.format(
                        modifer_cls.modifier.name,
                        modifer_cls.code_short,
                        modifer_cls.preferred
                    )
                )
        modifer_str = "".join(modifer_cls_strs)

        html = u'<table width="100%">'\
                    '<tr>'\
                        '<td valign="top" width="80">{0}</td>'\
                        '<td valign="top" width="50"><b>{1}</b></td>'\
                        '<td valign="top"><b>{2}</b></td>'\
                        '{4}'\
                        '{3}'\
                    '</tr>'\
                '</table>'

        return html.format(
            condition_object.date,
            condition_object.icd10class_code,
            condition_object.icd10class.preferred_plain,
            comment,
            modifer_str
        )


    def on_add_condition(self, event):
        """Add Condition with Full Icd10 Coder"""
        #with Icd10Coder(self, self.session) as dlg:
        self.icd10_coder.CenterOnScreen()
        if self.icd10_coder.ShowModal() == wx.ID_OK:
            new_condition = self.icd10_coder.get_condition()
            new_condition.admission_id = self.admission.id
            self.session.add(new_condition)
            self.session.commit()
            self.set_admission(self.admission)
            event = ConditionChangedEvent(object=new_condition)
            wx.PostEvent(self, event)


    def on_add_quick(self, event):
        """Add Condition with Full Icd10 Coder"""
        pass


    def on_add_favourite(self, event):
        """Add Condition with Full Icd10 Coder"""
        pass

    def set_editable(self, editable):
        """Set control to editable or not"""
        self.editable = editable

        if self.editable:
            self.toolbar.Show()
        else:
            self.toolbar.Hide()

        self.Layout()

    def is_unsaved(self):
        """Check to see if any changes have been saved, must do before closing.
          Always false in this panel as all changes are autosaved"""
        return False


    def save_changes(self):
        """Save changes. Everything is auto saved."""
        pass


    def set_admission(self, admission, editable=True):
        """Set the current admission"""
        self.admission = admission

        self.set_editable(editable)

        self.conditions_list.set_result(
            self.session.query(Condition)\
                .filter(Condition.admission_id == self.admission.id)
        )
