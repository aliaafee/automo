"""DB Query Result Grid"""
import math
import wx.grid
import wx

from .. import config
from . import events


class StringRenderer(wx.grid.GridCellRenderer):
    def __init__(self):
        wx.grid.GridCellRenderer.__init__(self)


    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        value = grid.GetCellValue(row, col)

        dc.SetBackgroundMode(wx.SOLID)
        if not isSelected:
            if value == 0:
                dc.SetBrush(wx.Brush(wx.Colour(255,230,240) , wx.SOLID))
            else:
                dc.SetBrush(wx.Brush(grid.GetCellBackgroundColour(row, col) , wx.SOLID))
        else:
            dc.SetBrush(wx.Brush(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT), wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangle(rect)
        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetFont(attr.GetFont())

        self.Draw2(grid, attr, dc, rect, row, col, isSelected)


    def OverFlow(self, width, dc, rect):
        rectw = rect.right - rect.x
        if width > rectw:
            x = rect.x + 1
            y = rect.y + 1
            cw, ch = dc.GetTextExtent('#')
            while x <= rect.right-cw:
                dc.DrawText('#',x, y)
                x += cw
            return True
        else:
            return False


    def Draw2(self, grid, attr, dc, rect, row, col, isSelected):
        value = grid.GetCellValue(row, col)
        if value is not None:
            text = unicode(value)
        else:
            text = "-"

        rect_width = rect.right - rect.x
        x = rect.x + 1
        y = rect.y + 1
        text_width, h = dc.GetTextExtent(text)
        if text_width < rect_width:
            #No overflow just draw
            dc.DrawText(text, x, y)
        else:
            #if overflow, create shortened string
            short_text = ""
            short_text_width, h = dc.GetTextExtent("...")
            for char in text:
                char_width, char_height = dc.GetTextExtent(char)
                if short_text_width + char_width > rect_width:
                    short_text += "..."
                    break
                else:
                    short_text_width += char_width
                    short_text += char
            dc.DrawText(short_text, x, y)


    def GetBestSize(self, grid, attr, dc, row, col):
        text = grid.GetCellValue(row, col)
        dc.SetFont(attr.GetFont())
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)


class NumberRenderer(StringRenderer):
    def Draw2(self, grid, attr, dc, rect, row, col, isSelected):
        value = grid.GetCellValue(row, col)
        if value is not None:
            text = unicode(value)
        else:
            text = "-"

        w, h = dc.GetTextExtent(text)

        if not self.OverFlow(w, dc, rect):
            x = rect.right - w #rect.x + 1
            y = rect.y + 1

            dc.DrawText(text, x, y)


class FloatRenderer(StringRenderer):
    def __init__(self, precision=None):
        super(FloatRenderer, self).__init__()
        self.precision = precision
    
    def Draw2(self, grid, attr, dc, rect, row, col, isSelected):
        value = grid.GetCellValue(row, col)
        if value is not None:
            if self.precision is not None: 
                text = unicode(round(value, self.precision))
            else:
                text = unicode(value)
        else:
            text = "-"

        w, h = dc.GetTextExtent(text)

        if not self.OverFlow(w, dc, rect):
            x = rect.right - w #rect.x + 1
            y = rect.y + 1

            dc.DrawText(text, x, y)



class DateRenderer(StringRenderer):
    def Draw2(self, grid, attr, dc, rect, row, col, isSelected):
        value = grid.GetCellValue(row, col)
        if value is not None:
            text = config.format_date(value)
        else:
            text = "-"

        w, h = dc.GetTextExtent(text)

        if not self.OverFlow(w, dc, rect):
            x = rect.right - w #rect.x + 1
            y = rect.y + 1

            dc.DrawText(text, x, y)


class DateTimeRenderer(StringRenderer):
    def Draw2(self, grid, attr, dc, rect, row, col, isSelected):
        value = grid.GetCellValue(row, col)
        if value is not None:
            text = config.format_datetime(value)
        else:
            text = "-"

        w, h = dc.GetTextExtent(text)

        if not self.OverFlow(w, dc, rect):
            x = rect.right - w #rect.x + 1
            y = rect.y + 1

            dc.DrawText(text, x, y)




class GridColumnDefn(object):
    def __init__(self, title, str_attr, editable=True, width=100):
        self.title = title
        self.str_attr = str_attr
        self.editable = editable
        self.width = width


    def get_renderer(self):
        return StringRenderer()


    def strfvalue(self, value):
        return unicode(value)


    def strpvalue(self, value_str):
        return value_str


class GridColumnString(GridColumnDefn):
    def __init__(self, title, str_attr, editable=True, width=100):
        super(GridColumnString, self).__init__(
            title, str_attr, editable, width
        )


class GridColumnFloat(GridColumnDefn):
    def __init__(self, title, str_attr, precision=None, editable=True, width=100):
        super(GridColumnFloat, self).__init__(
            title, str_attr, editable, width
        )
        self.precision = precision


    def get_renderer(self):
        return FloatRenderer(precision=self.precision)


    def strfvalue(self, value):
        if value is None:
            return ""
        return unicode(value)


    def strpvalue(self, value_str):
        return float(value_str)


class GridColumnInt(GridColumnDefn):
    def __init__(self, title, str_attr, editable=True, width=100):
        super(GridColumnInt, self).__init__(
            title, str_attr, editable, width, NumberRenderer
        )


    def get_renderer(self):
        return NumberRenderer()


    def strfvalue(self, value):
        if value is None:
            return ""
        return unicode(value)


    def strpvalue(self, value_str):
        return int(value_str)



class GridColumnDate(GridColumnDefn):
    def __init__(self, title, str_attr, editable=True, width=100):
        super(GridColumnDate, self).__init__(
            title, str_attr, editable, width
        )

    def get_renderer(self):
        return DateRenderer()


    def strfvalue(self, value):
        return config.format_date(value)


    def strpvalue(self, value_str):
        return config.parse_date(value_str)


class GridColumnDateTime(GridColumnDefn):
    def __init__(self, title, str_attr, editable=True, width=100):
        super(GridColumnDateTime, self).__init__(
            title, str_attr, editable, width
        )


    def get_renderer(self):
        return DateTimeRenderer()


    def strfvalue(self, value):
        return config.format_datetime(value)


    def strpvalue(self, value_str):
        return config.parse_datetime(value_str)




class DbQueryResultGrid(wx.grid.Grid):
    """DB Query Result as editable grid, supports very large query results without
      much slowdown. Cells can be edited in place and changes are auto saved."""
    def __init__(self, parent, session, minimum_fetch=50):
        super(DbQueryResultGrid, self).__init__(parent, style=wx.BORDER_SIMPLE)
        self.parent = parent
        self.session = session
        self.minimum_fetch = minimum_fetch
        self.query_result = None
        self.query_result_count = 0

        self.items_cache = {}

        self._columns = []

        self.CreateGrid(0, 0)
        self.SetRowLabelSize(1)

        self.Bind(wx.grid.EVT_GRID_EDITOR_SHOWN, self._on_editor_shown)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self._on_cell_change)


    def add_column(self, column_defn):
        """Add Column To Grid, using GridColumnDefn Object, Available types are
          GridColumnString, GridColumnFloat, GridColumnInt, GridColumnDate,
          GridColumnDateTime"""
        self._columns.append(column_defn)
        new_index = len(self._columns) - 1
        self.AppendCols(1)
        self.SetColLabelValue(new_index, column_defn.title)
        attr = wx.grid.GridCellAttr()
        attr.SetRenderer(column_defn.get_renderer())
        if not column_defn.editable:
            attr.SetReadOnly()
        self.SetColSize(new_index, column_defn.width)
        self.SetColAttr(new_index, attr)


    def set_result(self, query_result):
        """Set the query result"""
        self.query_result = query_result
        self.items_cache = {}

        new_count = self.query_result.count()
        if new_count != self.query_result_count:
            if self.query_result_count > 0:
                self.DeleteRows(0, self.query_result_count)
            self.AppendRows(new_count)
        self.query_result_count = new_count
        self.Refresh()


    def GetCellValue(self, row, col):
        """Return the value of the cell."""
        item = self.get_object(row)
        return getattr(item, self._columns[col].str_attr)


    def SetCellValue(self, row, col, value):
        """Set the value of the cell. Commits the session also."""
        item = self.get_object(row)
        setattr(item, self._columns[col].str_attr, value)
        self.session.commit()


    def _on_editor_shown(self, event):
        row, col = event.GetRow(), event.GetCol()
        value = self.GetCellValue(row, col)
        value_str = self._columns[col].strfvalue(value)
        super(DbQueryResultGrid, self).SetCellValue(row, col, value_str)


    def _on_cell_change(self, event):
        row, col = event.GetRow(), event.GetCol()
        value_str = super(DbQueryResultGrid, self).GetCellValue(row, col)
        try:
            value = self._columns[col].strpvalue(value_str)
            self.SetCellValue(row, col, value)
            event = events.DbGridCellChangedEvent(object=self.get_object(row))
            wx.PostEvent(self, event)
        except ValueError:
            print "Invalid Value"
            return


    def _fetch_items(self, page):
        start = page * self.minimum_fetch
        items = self.query_result.offset(start).limit(self.minimum_fetch).all()
        for index, item in enumerate(items):
            self.items_cache[start+index] = item


    def get_object(self, index):
        """Return the object at the given index"""
        if index < 0 or index > self.query_result_count - 1:
            return None

        try:
            return self.items_cache[index]
        except KeyError:
            page = int(index / float(self.minimum_fetch))
            self._fetch_items(page)
            return self.items_cache[index]
