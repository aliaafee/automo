"""ICD-10 Chapter Tree"""
import wx

from ... import database as db

class Icd10ChapterTree(wx.TreeCtrl):
    """Tree of Icd10 Chapters and blocks. Nodes expand lazily only when they are clicked."""
    def __init__(self, parent, session, **kwds):
        super(Icd10ChapterTree, self).__init__(
            parent, style=wx.TR_HAS_BUTTONS,
            **kwds
        )

        self.session = session

        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self._on_expand)

        self._initialized = False


    def initialize(self):
        if not self._initialized:
            self._build_tree()
            self._initialized = True


    def set_class(self, icd10_class):
        """Set Selected Icd10 Class and display it"""
        def get_class_crumbs(iclass):
            """Get path to chapter"""
            result = [iclass.code]
            if iclass.parent is not None:
                result.extend(get_class_crumbs(iclass.parent))
            return result

        crumbs = get_class_crumbs(icd10_class)

        current_parent_id = self.root_id
        current_item_id, cookie = self.GetFirstChild(current_parent_id)
        for crumb_code in reversed(crumbs):
            while current_item_id.IsOk():
                item_class, status = self.GetItemData(current_item_id)
                if item_class.code == crumb_code:
                    if crumb_code == crumbs[0]:
                        self.SelectItem(current_item_id)
                        break
                    else:
                        if status is False:
                            self.DeleteChildren(current_item_id)
                            self.SetItemData(current_item_id, (item_class, True))
                            self._extend_tree(current_item_id)
                        self.Expand(current_item_id)
                        current_parent_id = current_item_id
                        current_item_id, cookie = self.GetFirstChild(current_parent_id)
                        break
                else:
                    current_item_id, cookie = self.GetNextChild(current_parent_id, cookie)


    def get_selected_class(self):
        """Return the selected db.Icd10Class object"""
        item_id = self.GetSelection()
        if not item_id.IsOk():
            return None

        item_class = self.GetItemData(item_id)[0]
        return item_class


    def _build_tree(self):
        self.root_id = self.AddRoot("ICD-10")
        self.SetItemData(self.root_id, (None, True))
        self._extend_tree(self.root_id)
        self.Expand(self.root_id)


    def _extend_tree(self, parent_id):
        parent_class = self.GetItemData(parent_id)[0]

        if parent_class is None:
            parent_code = None
        else:
            parent_code = parent_class.code

        child_classes = self.session.query(db.Icd10Class).\
                            filter(db.Icd10Class.parent_code == parent_code).all()

        for child in child_classes:
            child_title = "{0} {1}".format(child.code, child.preferred_plain)
            child_id = self.AppendItem(parent_id, child_title)
            self.SetItemData(child_id, (child, False))

            grand_child_class_count = self.session.query(db.Icd10Class)\
                                        .filter(db.Icd10Class.parent_code == child.code).count()

            if grand_child_class_count > 0:
                self.AppendItem(child_id, "Loading...")


    def _on_expand(self, event):
        expanded_id = event.GetItem()
        if not expanded_id.IsOk():
            expanded_id = self.GetSelection()

        expanded_class, status = self.GetItemData(expanded_id)
        if status is False:
            self.DeleteChildren(expanded_id)
            self._extend_tree(expanded_id)
            self.SetItemData(expanded_id, (expanded_class, True))
