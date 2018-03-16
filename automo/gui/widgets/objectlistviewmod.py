"""ObjectListView modded to fire event when checkbox changed"""
import  wx.lib.newevent

from ObjectListView import ObjectListView


OvlCheckEvent, EVT_OVL_CHECK_EVENT = wx.lib.newevent.NewEvent()

class ObjectListViewMod(ObjectListView):
    """ObjectListView modded to fire event when checkbox changed"""
    def _HandleLeftDownOnImage(self, rowIndex, subItemIndex):
        column = self.columns[subItemIndex]
        if not column.HasCheckState():
            return

        self._PossibleFinishCellEdit()
        model_object = self.GetObjectAt(rowIndex)
        if model_object is not None:
            column.SetCheckState(model_object, not column.GetCheckState(model_object))

            # Just added the event here ===================================
            check_event = OvlCheckEvent(object=model_object,
                                        value=column.GetCheckState(model_object))
            wx.PostEvent(self, check_event)
            # =============================================================

            self.RefreshIndex(rowIndex, model_object)
