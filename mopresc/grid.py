import  wx
import  wx.grid as  gridlib
from datetime import datetime
import locale


class NumberRenderer(gridlib.PyGridCellRenderer):
    def __init__(self):
        gridlib.PyGridCellRenderer.__init__(self)


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
        dc.DrawRectangleRect(rect)
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
        
        if value == None:
            return

        text = '%g' % grid.GetCellValue(row, col)

        w, h = dc.GetTextExtent(text)
        if not self.OverFlow(w, dc, rect):
            x = rect.right - w #rect.x + 1
            y = rect.y + 1

            dc.DrawText(text, x, y)
    

    def GetBestSize(self, grid, attr, dc, row, col):
        text = grid.GetCellValue(row, col)
        dc.SetFont(attr.GetFont())
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)


    def Clone(self):
        return NumberRenderer()




class PercentRenderer(NumberRenderer):
    def Draw2(self, grid, attr, dc, rect, row, col, isSelected):

        text = '%g' % grid.GetCellValue(row, col) + " %"
        w, h = dc.GetTextExtent(text)

        if not self.OverFlow(w, dc, rect):
            x = rect.right - w #rect.x + 1
            y = rect.y + 1

            dc.DrawText(text, x, y)


    def Clone(self):
        return PercentRenderer()



class DateRenderer(NumberRenderer):
    def Draw2(self, grid, attr, dc, rect, row, col, isSelected):

        value = grid.GetCellValue(row, col)
        text = "{0}/{1}/{2}".format(value.day, value.month, value.year)

        w, h = dc.GetTextExtent(text)

        if not self.OverFlow(w, dc, rect):
            x = rect.right - w #rect.x + 1
            y = rect.y + 1

            dc.DrawText(text, x, y)


    def Clone(self):
        return DateRenderer()



class VGridColumn(object):
    #def __init__(self, Label, Type=COL_TYPE_TEXT, EditDoneCallback=None):
    def __init__(self, Label, EditDoneCallback=None, ReadOnly=False, Hidden=False, Sum=False):
        self.Label = Label
        self.EditDoneCallback = EditDoneCallback
        self.ReadOnly = ReadOnly
        self.Renderer = None
        self.Editor = None
        self.Default = ''
        self.Hidden = Hidden
        self.Sum = Sum
        self.Sumable = False


    def StringToValue(self, text):
        return text
    def ValueToColType(self, value):
        return str(value)

VGridStringColumn = VGridColumn


class VGridBoolCol(VGridColumn):
    def __init__(self, Label, EditDoneCallback=None, ReadOnly=False, Hidden=False, Sum=False):
        VGridColumn.__init__(self, Label, EditDoneCallback, ReadOnly, Hidden, Sum)
        self.Renderer = gridlib.GridCellBoolRenderer()
        self.Editor = gridlib.GridCellBoolEditor()
        self.Default = True

    def ValueToColType(self, value):
        if bool(value) == True:
            return "1"
        else:
            return "0"


class VGridDateCol(VGridColumn):
    def __init__(self, Label, EditDoneCallback=None, ReadOnly=False, Hidden=False, Sum=False):
        VGridColumn.__init__(self, Label, EditDoneCallback, ReadOnly, Hidden, Sum)
        self.Renderer = DateRenderer()
        self.Default = datetime.now()

    def StringToValue(self, datestr):
        date = datestr.split('/')
        if len(date) != 3:
            raise ValueError
        else:
            try:
                value = datetime(int(date[2]), int(date[1]), int(date[0]), 0, 0, 0)
            except:
                raise ValueError
        return value

    def ValueToColType(self, value):
        return "{0}/{1}/{2}".format(value.day, value.month, value.year)




class VGridIntCol(VGridColumn):
    def __init__(self, Label, EditDoneCallback=None, ReadOnly=False, Hidden=False, Sum=False):
        VGridColumn.__init__(self, Label, EditDoneCallback, ReadOnly, Hidden, Sum)
        self.Renderer = NumberRenderer()
        self.Default = 0
        self.Sumable = True

    def StringToValue(self, value):
        return int(value)




class VGridNumberCol(VGridColumn):
    def __init__(self, Label, EditDoneCallback=None, ReadOnly=False, Hidden=False, Sum=False):
        VGridColumn.__init__(self, Label, EditDoneCallback, ReadOnly, Hidden, Sum)
        self.Renderer = NumberRenderer()
        self.Default = 0.0
        self.Sumable = True

    def StringToValue(self, value):
        return float(value)
    



class VGridPercentCol(VGridNumberCol):
    def __init__(self, Label, EditDoneCallback=None, ReadOnly=False, Hidden=False, Sum=False):
        VGridNumberCol.__init__(self, Label, EditDoneCallback, ReadOnly, Hidden, Sum)
        self.Renderer = PercentRenderer()
        self.Sumable = True




class VGrid(gridlib.Grid):
    def __init__(self, parent, columns):
        gridlib.Grid.__init__(self, parent)
        self._CellData = []
        self._Columns = columns
        self._SetupColumns()
        self.SetRowLabelSize(0)
        self._BottomOffset = 0
        self._SetupSumRow()
        self.Bind(gridlib.EVT_GRID_CMD_CELL_CHANGE, self._OnCellChange)
        self._ResizeCol = None
        self.Bind(wx.EVT_SIZE, self._OnResize)
        self.Bind(gridlib.EVT_GRID_COL_SIZE, self._OnResize)


    def _OnResize(self, event):
        if 'gtk2' in wx.PlatformInfo:
            wx.CallAfter(self._DoResize)
            self.Refresh()
        else:
            self._DoResize()
        event.Skip()
        

    def _DoResize(self):
        if self._ResizeCol != None:
            totColWidth = 0
            for col in range(self.NumberCols):
                if col != self._ResizeCol:
                    totColWidth += self.GetColSize(col)
            gridWidth = self.GetClientSize().width - self.GetRowLabelSize()
            resizeColMinWidth = 100
            newResizeColWidth = gridWidth - totColWidth
            if newResizeColWidth > resizeColMinWidth:
                self.SetColSize(self._ResizeCol, newResizeColWidth)
            else:
                self.SetColSize(self._ResizeCol, resizeColMinWidth)


    def _OnCellChange(self, event):
        print event.GetRow(), event.GetCol()
        row = event.GetRow()
        col = event.GetCol()
        valuestr = gridlib.Grid.GetCellValue(self, row, col)
        prev_value = self.GetCellValue(row, col)
        try:
            value = self._Columns[col].StringToValue(valuestr)
        except ValueError:
            gridlib.Grid.SetCellValue(self,
                    row, col,
                    self._Columns[col].ValueToColType(prev_value))
            event.Skip()
        else:
            self.SetCellValue(row, col, value)

            if self._Columns[col].EditDoneCallback != None:
                wx.CallAfter(self._Columns[col].EditDoneCallback,row, col, value, prev_value)


    def _SetupColumns(self):
        '''
        columns as dictionary with keys as integers
        '''
        self.CreateGrid(0, len(self._Columns))
        for key in sorted(self._Columns.iterkeys()):
            self.SetColLabelValue(key, self._Columns[key].Label)
            if self._Columns[key].Hidden:
                self.SetColMinimalWidth(key, 0)
                self.SetColMinimalAcceptableWidth(0)
                self.SetColSize(key, 0)


    def _SetupRow(self, row):
        for key in self._Columns.iterkeys():
            self._SetupCell(row, key)
        

    def _SetupCell(self, row, col):
        if self._Columns[col].Renderer != None:
            self.SetCellRenderer(row,col,self._Columns[col].Renderer.Clone())
        if self._Columns[col].Editor != None:
            self.SetCellEditor(row,col,self._Columns[col].Editor.Clone())
        self.SetCellValue(row, col, self._Columns[col].Default)
        if self._Columns[col].ReadOnly:
            self.SetReadOnly(row, col)
        else:
            self.SetReadOnly(row, col, False)


    def _SetupSumRow(self):
        self._SumCols = []

        for key in self._Columns.iterkeys():
            if self._Columns[key].Sum == True:
                self._SumCols.append(key)

        if len(self._SumCols) != 0:
            gridlib.Grid.AppendRows(self)
            self._CellData.append(['' for i in range(len(self._Columns))])
            self._BottomOffset = 1
            row = self.GetNumberRows() - 1
            for col in self._SumCols:
                self._SetupCell(row, col)
            for col in self._Columns.iterkeys():
                self.SetReadOnly(row, col)
                f = self.GetCellFont(row, col)
                f.SetWeight(wx.FONTWEIGHT_BOLD)
                self.SetCellFont(row, col, f)
            self._SumCols.sort()
            if self._SumCols[0] != 0:
                col = self._SumCols[0] - 1
                gridlib.Grid.SetCellValue(self, row, col, 'Total')
                gridlib.Grid.SetCellAlignment(self, row, col, wx.ALIGN_RIGHT, wx.ALIGN_TOP)


    def _Sum(self, col):
        if self._BottomOffset != 0:
            if col in self._SumCols:
                if self._Columns[col].Sumable:
                    rowcount = self.GetNumberRows()
                    sumvalue = self._Columns[col].Default
                    for row in range(rowcount - self._BottomOffset):
                        sumvalue += self.GetCellValue(row, col)
                    self._CellData[rowcount - 1][col] = sumvalue
                    gridlib.Grid.SetCellValue(self, rowcount - 1, col, self._Columns[col].ValueToColType(sumvalue))


    def GetColumnSum(self, col):
        sumvalue = self._Columns[col].Default
        for row in range(self.GetRowCount()):
            sumvalue += self.GetCellValue(row, col)
        return sumvalue


    def AppendRow(self, values=None):
        gridlib.Grid.InsertRows(self, self.GetNumberRows() - self._BottomOffset)
        if self._BottomOffset == 0:
            self._CellData.append([0 for i in range(len(self._Columns))])
        else:
            self._CellData.insert(self.GetNumberRows() - self._BottomOffset,
                                    [0 for i in range(len(self._Columns))])

        row = self.GetNumberRows() - 1 - self._BottomOffset
        self._SetupRow(row)

        if values != None:
            self.SetRow(row, values)

        return row


    def SetRow(self, row, values):
        for col in self._Columns.iterkeys():
            self.SetCellValue(row, col, values[col])


    def SetCellValue(self, row, col, value):
        self._CellData[row][col] = value
        gridlib.Grid.SetCellValue(self, row, col, self._Columns[col].ValueToColType(value))
        self._Sum(col)


    def GetCellValue(self, row, col):
        return self._CellData[row][col]


    def HasItems(self):
        if self.GetRowCount() > 0:
            return True
        return False


    def DeleteRow(self, row):
        self.DeleteRows(row, 1)
        del(self._CellData[row])


    def DeleteAllRows(self):
        rows = self.GetNumberRows()
        if rows > 0:
            self.DeleteRows(0, rows)
            self._CellData = []
        self._SetupSumRow()

    def GetRowCount(self):
        return self.NumberRows - self._BottomOffset

    def SetResizeCol(self, col):
        self._ResizeCol = col

    def GetAll(self, cols):
        result = []
        for row in range(self.GetRowCount()):
            result.append({})
            for col in cols:
                result[row][col] = self.GetCellValue(row, col)
        return result


    def SearchCol(self, col, value, skiprow=None):
        "Return first row with given value in given column"
        for row in range(self.GetRowCount()):
            if row != skiprow:
                if value == self.GetCellValue(row, col):
                    return row
        return None

    def HasItems(self):
        if self.GetRowCount > 0:
            return True
        return False





if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None, size=wx.Size(800,600))

    def datecallback(row,col,value,prev_value):
        print "edited {0} {1} to {2} from {3}".format(row, col, str(value), str(prev_value))

    g = VGrid(frame, columns=
        {
            0 : VGridColumn('h', None, ReadOnly=True),
            1 : VGridDateCol('w', datecallback),
            2 : VGridPercentCol('a', None),
            3 : VGridNumberCol('b', None),
            4 : VGridIntCol('c', None),
        })
    g.SetResizeCol(1)
    row = g.AppendRow()
    g.SetRow(row,[
            'ali',
            datetime.now(),
            100,
            45.131513,
            123,
            12452])
    row = g.AppendRow()
    g.SetRow(row,[
            'ali',
            datetime.now(),
            100,
            45.131513,
            321,
            12452])
    sz = wx.BoxSizer()

    sz.Add(g,1,wx.ALL|wx.EXPAND,10)

    frame.SetSizer(sz)
    frame.Show()
    app.MainLoop()


