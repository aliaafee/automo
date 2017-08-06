"""Condition Panel"""
import wx

import config
import events
import images
from icd10coder import Icd10Coder
#from database import Condition
from dbqueryresultbox import DbQueryResultBox


class ConditionPanel(wx.Panel):
    """Condition Panel"""
    def __init__(self, parent, session, **kwds):
        super(ConditionPanel, self).__init__(parent, **kwds)

        self.session = session
        self.admission = None

        self.editable = True

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_NODIVIDER)

        tb_add = self.toolbar.AddLabelTool(
            wx.ID_ADD,
            label="Add",
            bitmap=images.get("add_condition"),
            shortHelp="Add Condition"
        )
        self.Bind(wx.EVT_TOOL, self._on_add_condition, tb_add)

        """
        tb_add_quick = self.toolbar.AddLabelTool(
            wx.ID_ANY,
            label="Add Quick Search",
            bitmap=images.get("add_condition_quick"),
            shortHelp="Add Condition from Quick Search"
        )
        self.Bind(wx.EVT_TOOL, self._on_add_quick, tb_add_quick)

        tb_add_favourite = self.toolbar.AddLabelTool(
            wx.ID_ANY,
            label="Add Favourite",
            bitmap=images.get("add_condition_favourite"),
            shortHelp="Add Condition from Favourites"
        )
        self.Bind(wx.EVT_TOOL, self._on_add_favourite, tb_add_favourite)
        """

        self.toolbar.Realize()
        sizer.Add(self.toolbar, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT,
                  border=5)

        self.conditions_list = DbQueryResultBox(self, self._conditions_decorator, style=wx.LB_MULTIPLE)
        self.conditions_list.Bind(wx.EVT_RIGHT_DOWN, self._on_conditions_context)
        sizer.Add(self.conditions_list, 1, wx.EXPAND | wx.ALL, border=5)

        self.SetSizer(sizer)

        self.icd10_coder = Icd10Coder(self, self.session)

        self.conditions_menu = wx.Menu()
        self.conditions_menu.Append(wx.ID_REMOVE, "Remove", "Remove Selected Conditions.")
        self.conditions_menu.Bind(wx.EVT_MENU, self._on_remove_conditions, id=wx.ID_REMOVE)



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

        html = u'<font size="2"><table width="100%">'\
                    '<tr>'\
                        '<td valign="top" width="50">{0}</td>'\
                        '<td valign="top" width="40"><b>{1}</b></td>'\
                        '<td valign="top"><b>{2}</b></td>'\
                        '{4}'\
                        '{3}'\
                    '</tr>'\
                '</table></font>'

        return html.format(
            config.format_date(condition_object.date),
            condition_object.icd10class_code,
            condition_object.icd10class.preferred_plain,
            comment,
            modifer_str
        )


    def _on_add_condition(self, event):
        """Add Condition with Full Icd10 Coder"""
        self.icd10_coder.CenterOnScreen()
        new_condition = Condition(
            date=self.admission.admitted_date,
            admission_id=self.admission.id
        )
        if self.icd10_coder.ShowModal(new_condition) == wx.ID_OK:
            new_condition = self.icd10_coder.get_condition()
            #new_condition.admission_id = self.admission.id
            self.session.add(new_condition)
            self.session.commit()
            self.set_admission(self.admission)
            event = events.ConditionChangedEvent(object=new_condition)
            wx.PostEvent(self, event)


    def _on_add_quick(self, event):
        """Add Condition with Full Icd10 Coder"""
        pass


    def _on_add_favourite(self, event):
        """Add Condition with Full Icd10 Coder"""
        pass

    def _on_conditions_context(self, event):
        if not self.editable:
            return

        self.PopupMenu(self.conditions_menu)


    def _on_remove_conditions(self, event):
        with wx.MessageDialog(self, 'Remove selected conditions?', 'Remove Conditions',
                              wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION) as dlg:
            dlg.CenterOnParent()
            result = dlg.ShowModal()

            if result != wx.ID_YES:
                return

            selected = self.conditions_list.get_all_selected_object()
            for item in selected:
                self.session.delete(item)

            self.session.commit()

            event = events.ConditionChangedEvent(object=None)
            wx.PostEvent(self, event)

            self.conditions_list.set_result(
                self.session.query(Condition)\
                    .filter(Condition.admission_id == self.admission.id)
            )


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
