import glob
import os
import webbrowser
import wx
import kink
import io
import urllib.request
import wx.lib.scrolledpanel
from lxml import etree as et
import xml.dom.minidom as minidom
from sys import platform as _platform
import config

'''
    Here we define base string format
    Supported:
    {SET}
    {S_E_T}
    {S.E.T}
    {S-E-T}
    {SET-}
    {DATE}
    {D.A.T.E}
    {D_A_T_E}
    {D A T E}
    {DATE-}
    {NAME}
    {N_A_M_E}
    {N.A.M.E}
    {N-A-M-E}
    {NAME-}
    {ID}
'''


selectedItem = ''
detectedIds = []

print(glob.glob(os.path.dirname(__file__)))
cache_dir = glob.glob(os.path.dirname(__file__))[0]

cache_dir += '/cache'

if not os.path.isdir(cache_dir):
    os.makedirs(cache_dir)


class OptionsDialog(wx.Dialog):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Dialog.__init__(self, None, title="Options")

        radio1 = wx.RadioButton(self, -1, " Radio1 ", style=wx.RB_GROUP)
        radio2 = wx.RadioButton(self, -1, " Radio2 ")
        radio3 = wx.RadioButton(self, -1, " Radio3 ")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(radio1, 0, wx.ALL, 5)
        sizer.Add(radio2, 0, wx.ALL, 5)
        sizer.Add(radio3, 0, wx.ALL, 5)

        for i in range(3):
            chk = wx.CheckBox(self, label="Checkbox #%s" % (i+1))
            sizer.Add(chk, 0, wx.ALL, 5)
        self.SetSizer(sizer)


class SearchDlg(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, title="Search")

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.selected = ''

        self.pos = 0
        for detectedId in detectedIds:
            if self.pos == 0:
                self.radio = wx.RadioButton(self, -1, detectedId, style=wx.RB_GROUP)
                self.radio.Bind(wx.EVT_RADIOBUTTON, self.onSelect)
                self.selected = detectedId
            else:
                self.radio = wx.RadioButton(self, -1, detectedId)
                self.radio.Bind(wx.EVT_RADIOBUTTON, self.onSelect)
            self.sizer.Add(self.radio, 0, wx.ALL, 5)
        self.radio = wx.RadioButton(self, self.pos, label='Search string')
        self.sizer.Add(self.radio, 0, wx.ALL, 5)
        self.searchString = wx.TextCtrl(self, size=(300, -1))
        self.sizer.Add(self.searchString, 0, wx.ALL, 5)
        self.searchString.SetLabel(kink.generateSearchString(selectedItem))
        self.searchBtn = wx.Button(self, label="Search")
        self.sizer.Add(self.searchBtn, 0, wx.ALL, 5)
        self.sizer.Layout()
        self.sizer.Fit(self)
        self.SetSizer(self.sizer)

        self.searchBtn.Bind(wx.EVT_BUTTON, self.doSearchInSearch)

    def doSearchInSearch(self, event):
        search_string = self.searchString.GetValue()
        results = kink.search(search_string)
        self.inScrollBoxer = wx.GridBagSizer()
        self.searchResultScroll = wx.lib.scrolledpanel.ScrolledPanel(self, -1, size=(900, 500))
        self.searchResultScroll.SetAutoLayout(1)
        self.searchResultScroll.SetupScrolling()
        self.searchResultScroll.SetSizer(self.inScrollBoxer)
        self.sizer.Add(self.searchResultScroll, 0, wx.ALL, 5)
        self.sizer.Layout()
        self.sizer.Fit(self)
        row = 0
        col = 0
        for i in range(len(results['shoots'])):
            shoot_id = results['urls'][i].strip()
            shoot_id = shoot_id.split('/')
            shoot_id = shoot_id[2]
            if row == 0 and col == 0:
                self.shoot_id = wx.RadioButton(self.searchResultScroll, -1, label=shoot_id, style=wx.RB_GROUP)
                self.selected = shoot_id
            else:
                self.shoot_id = wx.RadioButton(self.searchResultScroll, -1, label=shoot_id)
            self.inScrollBoxer.Add(self.shoot_id, pos=(row, col), flag=wx.ALL, border=5)
            self.shoot_id.Bind(wx.EVT_RADIOBUTTON, self.onSelect)
            self.setName = wx.StaticText(self.searchResultScroll, label=results['studios'][i])
            self.inScrollBoxer.Add(self.setName, pos=(row + 1, col), flag=wx.ALL, border=5)
            self.shoot_name = wx.StaticText(self.searchResultScroll, label=results['shoots'][i].strip())
            self.inScrollBoxer.Add(self.shoot_name, pos=(row + 2, col), flag=wx.ALL, border=5)
            self.shoot_date = wx.StaticText(self.searchResultScroll, label=results['dates'][i].strip())
            self.inScrollBoxer.Add(self.shoot_date, pos=(row + 3, col), flag=wx.ALL, border=5)
            cached = results['images'][i].strip()
            cached = cached.replace('/', '_')
            cached = cached.replace(':', '_')
            if not os.path.isfile(cache_dir + '/' + cached):
                print('image not here')
                url = results['images'][i].strip()
                fp = urllib.request.urlopen(url)
                data = fp.read()
                fp.close()
                with open(cache_dir + '/' + cached, "wb") as code:
                    code.write(data)

            data = cache_dir + '/' + cached
            # img = wx.Image(io.BytesIO(data), type=wx.BITMAP_TYPE_ANY, index=-1)
            img = wx.Image(data, type=wx.BITMAP_TYPE_ANY, index=-1)

            self.imageCtrl = wx.StaticBitmap(self.searchResultScroll, wx.ID_ANY,
                                             wx.Bitmap(img))
            self.inScrollBoxer.Add(self.imageCtrl, pos=(row + 4, col), flag=wx.ALL, border=5)
            self.searchResultScroll.Layout()
            self.searchResultScroll.SetupScrolling()
            if col < 1:
                col += 1
            else:
                col = 0
                row += 5

    def onSelect(self, event):
        button = event.GetEventObject()
        self.selected = button.GetLabel()


class MainWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Scraper")

        self.OS = ''

        if _platform == "linux" or _platform == "linux2":
            self.OS = "linux"
        elif _platform == "darwin":
            self.OS = "linux"
        elif _platform == "win32":
            self.OS = "windows"

        self.selectedFolder = ''
        self.selectedItem = ''
        self.scrapeId = ''
        self.output = ''

        self.panel = wx.Panel(self, wx.ID_ANY)

        #Menu

        menuBar = wx.MenuBar()
        fileMenu = wx.Menu()
        optionsItem = fileMenu.Append(wx.NewId(), "Options",
                                      "Show an Options Dialog")
        self.Bind(wx.EVT_MENU, self.onOptionsMenu, optionsItem)

        exitMenuItem = fileMenu.Append(wx.NewId(), "Exit",
                                       "Exit the application")
        self.Bind(wx.EVT_MENU, self.onExit, exitMenuItem)

        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        #Window

        self.mainInfoScroll = wx.lib.scrolledpanel.ScrolledPanel(self.panel, -1)
        self.mainInfoScroll.SetAutoLayout(1)
        self.mainInfoScroll.SetupScrolling()

        # split Dir selector in sizer
        self.dirSelectorSizer = wx.BoxSizer(wx.VERTICAL)
        self.dirList = wx.ListCtrl(self.panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.dirList.InsertColumn(0, 'Filename', width=300)
        self.dirSelectorSizer.Add(self.dirList, -1, flag=wx.ALL | wx.EXPAND)
        self.openDirBtn = wx.Button(self.panel, label="Open Dir")
        self.dirSelectorSizer.Add(self.openDirBtn)

        #Main Info
        self.sizer = wx.GridBagSizer()
        self.labelFileName = wx.StaticText(self.mainInfoScroll, label="File Name")
        self.sizer.Add(self.labelFileName, pos=(0, 0), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.movieFileName = wx.TextCtrl(self.mainInfoScroll, size=(300, -1))
        self.sizer.Add(self.movieFileName, pos=(0, 1), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.labelMovieId = wx.StaticText(self.mainInfoScroll, label="Detected Movie ID")
        self.sizer.Add(self.labelMovieId, pos=(1, 0), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.movieId = wx.TextCtrl(self.mainInfoScroll, size=(300, -1))
        self.sizer.Add(self.movieId, pos=(1, 1), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.scrapeSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.searchBtn = wx.Button(self.mainInfoScroll, label="Search")
        self.sizer.Add(self.searchBtn, pos=(1, 2), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL,
                       border=5)
        self.laberNfoPresent = wx.StaticText(self.mainInfoScroll, label="NFO?")
        self.scrapeSizer.Add(self.laberNfoPresent, flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.nfoPresent = wx.StaticText(self.mainInfoScroll, label="n/a")
        self.scrapeSizer.Add(self.nfoPresent, flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.scrapeBtn = wx.Button(self.mainInfoScroll, label="Scrape")
        self.scrapeSizer.Add(self.scrapeBtn, flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL,
                       border=5)
        self.renameBtn = wx.Button(self.mainInfoScroll, label="Rename")
        self.scrapeSizer.Add(self.renameBtn, flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL,
                       border=5)
        self.renameBtn.Disable()
        self.sizer.Add(self.scrapeSizer, pos=(2, 0), span=(0, 2), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL,
                       border=5)
        self.labelMovieName = wx.StaticText(self.mainInfoScroll, label="Movie Name")
        self.sizer.Add(self.labelMovieName, pos=(3, 0), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.movieName = wx.TextCtrl(self.mainInfoScroll, size=(300, -1))
        self.sizer.Add(self.movieName, pos=(3, 1), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.labelOriginalTitle = wx.StaticText(self.mainInfoScroll, label="Original Title")
        self.sizer.Add(self.labelOriginalTitle, pos=(4, 0), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL,
                       border=5)
        self.originalTitle = wx.TextCtrl(self.mainInfoScroll, size=(300, -1))
        self.sizer.Add(self.originalTitle, pos=(4, 1), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.labelSortTitle = wx.StaticText(self.mainInfoScroll, label="Sort Title")
        self.sizer.Add(self.labelSortTitle, pos=(5, 0), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL,
                       border=5)
        self.sortTitle = wx.TextCtrl(self.mainInfoScroll, size=(300, -1))
        self.sizer.Add(self.sortTitle, pos=(5, 1), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.labelMovieSet = wx.StaticText(self.mainInfoScroll, label="Set")
        self.sizer.Add(self.labelMovieSet, pos=(6, 0), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL,
                       border=5)
        self.movieSet = wx.TextCtrl(self.mainInfoScroll, size=(300, -1))
        self.sizer.Add(self.movieSet, pos=(6, 1), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.labelYear = wx.StaticText(self.mainInfoScroll, label="Year")
        self.sizer.Add(self.labelYear, pos=(7, 0), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.movieYear = wx.TextCtrl(self.mainInfoScroll, size=(50, -1))
        self.sizer.Add(self.movieYear, pos=(7, 1), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.labelTop250 = wx.StaticText(self.mainInfoScroll, label="Top 250")
        self.sizer.Add(self.labelTop250, pos=(8, 0), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL,
                       border=5)
        self.Top250 = wx.TextCtrl(self.mainInfoScroll, size=(300, -1))
        self.sizer.Add(self.Top250, pos=(8, 1), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.labelTrailer = wx.StaticText(self.mainInfoScroll, label="Trailer")
        self.sizer.Add(self.labelTrailer, pos=(9, 0), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL,
                       border=5)
        self.Trailer = wx.TextCtrl(self.mainInfoScroll, size=(300, -1))
        self.sizer.Add(self.Trailer, pos=(9, 1), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.labelMovieVotes = wx.StaticText(self.mainInfoScroll, label="Votes")
        self.sizer.Add(self.labelMovieVotes, pos=(10, 0), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL,
                       border=5)
        self.movieVotes = wx.TextCtrl(self.mainInfoScroll, size=(300, -1))
        self.sizer.Add(self.movieVotes, pos=(10, 1), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.labelMovieRating = wx.StaticText(self.mainInfoScroll, label="Rating")
        self.sizer.Add(self.labelMovieRating, pos=(11, 0), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL,
                       border=5)
        self.movieRating = wx.TextCtrl(self.mainInfoScroll, size=(300, -1))
        self.sizer.Add(self.movieRating, pos=(11, 1), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.labelOutline = wx.StaticText(self.mainInfoScroll, label="Outline")
        self.sizer.Add(self.labelOutline, pos=(12, 0), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL,
                       border=5)
        self.Outline = wx.TextCtrl(self.mainInfoScroll, size=(300, -1))
        self.sizer.Add(self.Outline, pos=(12, 1), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.labelPlot = wx.StaticText(self.mainInfoScroll, label="Plot")
        self.sizer.Add(self.labelPlot, pos=(13, 0), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.moviePlot = wx.TextCtrl(self.mainInfoScroll, size=(300, 150), style=wx.TE_MULTILINE)
        self.sizer.Add(self.moviePlot, pos=(13, 1), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.labelTagLine = wx.StaticText(self.mainInfoScroll, label="Tag Line")
        self.sizer.Add(self.labelTagLine, pos=(14, 0), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.tagLine = wx.TextCtrl(self.mainInfoScroll, size=(300, -1))
        self.sizer.Add(self.tagLine, pos=(14, 1), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.labelRunTime = wx.StaticText(self.mainInfoScroll, label="Run Time")
        self.sizer.Add(self.labelRunTime, pos=(15, 0), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.runTime = wx.TextCtrl(self.mainInfoScroll, size=(150, -1))
        self.sizer.Add(self.runTime, pos=(15, 1), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.labelRealeseDate = wx.StaticText(self.mainInfoScroll, label="Release date")
        self.sizer.Add(self.labelRealeseDate, pos=(16, 0), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.releaseDate = wx.TextCtrl(self.mainInfoScroll, size=(150, -1))
        self.sizer.Add(self.releaseDate, pos=(16, 1), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.labelStudio = wx.StaticText(self.mainInfoScroll, label="Studio")
        self.sizer.Add(self.labelStudio, pos=(17, 0), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.Studio = wx.TextCtrl(self.mainInfoScroll, size=(300, -1))
        self.sizer.Add(self.Studio, pos=(17, 1), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.labelThumbs = wx.StaticText(self.mainInfoScroll, label="Thumbs")
        self.sizer.Add(self.labelThumbs, pos=(18, 0), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.listThumbs = wx.TextCtrl(self.mainInfoScroll, size=(380, 100), style=wx.TE_MULTILINE)
        self.sizer.Add(self.listThumbs, pos=(18, 1), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.labelFanart = wx.StaticText(self.mainInfoScroll, label="Fanart")
        self.sizer.Add(self.labelFanart, pos=(19, 0), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.listFanart = wx.GridBagSizer()
        self.listFanartlist = wx.lib.scrolledpanel.ScrolledPanel(self.mainInfoScroll, -1, size=(380, 100))
        self.listFanartlist.SetupScrolling()
        self.listFanartlist.SetSizer(self.listFanart)
        self.sizer.Add(self.listFanartlist, pos=(19, 1), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.labelGenres = wx.StaticText(self.mainInfoScroll, label="Genres")
        self.sizer.Add(self.labelGenres, pos=(20, 0), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.listGenres = wx.TextCtrl(self.mainInfoScroll, size=(300, 50), style=wx.TE_MULTILINE)
        self.sizer.Add(self.listGenres, pos=(20, 1), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.labelActors = wx.StaticText(self.mainInfoScroll, label="Actors")
        self.sizer.Add(self.labelActors, pos=(21, 0), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.listActors = wx.TextCtrl(self.mainInfoScroll, size=(300, 50), style=wx.TE_MULTILINE)
        self.sizer.Add(self.listActors, pos=(21, 1), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)

        self.btnSaveNFO = wx.Button(self.mainInfoScroll, label="Save NFO")
        self.sizer.Add(self.btnSaveNFO, pos=(22, 0), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)

        self.mainInfoScroll.SetSizer(self.sizer)

        self.main = wx.BoxSizer(wx.HORIZONTAL)
        self.main.Add(self.dirSelectorSizer, 1, wx.EXPAND)
        self.main.Add(self.mainInfoScroll, 2, wx.EXPAND)
        self.panel.SetSizer(self.main)

        # set Event Hanflers
        self.openDirBtn.Bind(wx.EVT_BUTTON, self.onOpenDirectory)
        self.scrapeBtn.Bind(wx.EVT_BUTTON, self.onScrape)
        self.btnSaveNFO.Bind(wx.EVT_BUTTON, self.saveNFO)
        self.searchBtn.Bind(wx.EVT_BUTTON, self.onOpenSearch)
        self.renameBtn.Bind(wx.EVT_BUTTON, self.doRename)

    def onOpenDirectory(self, e):
        """"""
        dlg = wx.DirDialog(self, "Choose a directory:")
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.updateDisplay(path)
        dlg.Destroy()

    def updateDisplay(self, folder_path):
        """
        Update the listctrl with the file names in the passed in folder
        """
        paths = glob.glob(folder_path + "/*")
        self.selectedFolder = glob.glob(folder_path)
        self.dirList.DeleteAllItems()
        for index, path in enumerate(paths):
            self.dirList.InsertItem(index, os.path.basename(path))
        self.dirList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.ListOnClick, self.dirList)

    def ListOnClick(self, event):
        #clear up what we have
        self.renameBtn.Disable()
        self.scrapeId = ''
        self.movieId.SetLabel('')
        self.movieName.SetLabel('')
        self.originalTitle.SetLabel('')
        self.sortTitle.SetLabel('')
        self.movieSet.SetLabel('')
        self.movieYear.SetLabel('')
        self.Top250.SetLabel('')
        self.Trailer.SetLabel('')
        self.movieVotes.SetLabel('')
        self.movieRating.SetLabel('')
        self.Outline.SetLabel('')
        self.moviePlot.SetLabel('')
        self.tagLine.SetLabel('')
        self.runTime.SetLabel('')
        self.releaseDate.SetLabel('')
        self.Studio.SetLabel('')
        self.listThumbs.SetLabel('')
        self.listGenres.SetLabel('')
        self.listActors.SetLabel('')
        cols = self.listFanart.GetCols()
        rows = self.listFanart.GetRows()
        if rows > 0:
            for row in range(rows):
                for col in range(cols):
                    itm = self.listFanart.FindItemAtPosition((row, col))
                    if itm:
                        obj = itm.GetWindow()
                        obj.Destroy()

            #Let's see if this is direcotry (if yes - do we have NFO)
        self.selectedItem = event.GetText()
        if os.path.isdir(self.selectedFolder[0] + "/" + event.GetText()):
            if os.path.isfile(self.selectedFolder[0] + "/" + event.GetText() + "/" + event.GetText() + ".nfo"):
                self.nfoPresent.SetLabel('yes')
                path = self.selectedFolder[0] + "/" + event.GetText() + "/" + event.GetText() + ".nfo"
                self.readNFO(path)
            else:
                self.nfoPresent.SetLabel('no')
                detectedIds = kink.detectId(self.selectedItem)
                print(detectedIds)
                if len(detectedIds) == 1:
                    self.movieId.SetLabel(detectedIds[0])
                    self.scrapeId = detectedIds[0]
                else:
                    selectedItem = self.selectedItem
                    detectedIds = detectedIds
        else:
            self.moveToFolderBtn = wx.Button(self.mainInfoScroll, label="Move to folder")
            self.sizer.Add(self.moveToFolderBtn, pos=(0, 2), flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL,
                               border=5)
            self.sizer.Layout()
            self.sizer.Ref(self)
            self.moveToFolderBtn.Bind(wx.EVT_BUTTON, self.moveToFolder)
            detectedIds = kink.detectId(self.selectedItem)
            print(detectedIds)
            if len(detectedIds) > 1 or len(detectedIds) == 0:
                selectedItem = self.selectedItem
                detectedIds = detectedIds

        self.movieFileName.SetLabel(event.GetText())

    def onScrape(self, e):
        self.scrapeId = self.movieId.GetValue()
        self.output = kink.scrape_movie(self.scrapeId)
        #Let's populate Descriptions fields
        self.movieName.SetLabel(self.output['name'])
        self.movieSet.SetLabel(self.output['set'])
        self.movieYear.SetLabel(self.output['year'])
        self.moviePlot.SetLabel(self.output['plot'])
        self.releaseDate.SetLabel(self.output['date'])
        self.Studio.SetLabel(self.output['studio'])
        row = 0
        col = 0
        for thumb in self.output['thumbs']:
            self.listThumbs.AppendText(thumb + '\n')
            #self.listFanart.AppendText(thumb + '\n')
            cached = thumb.replace('/', '_')
            cached = cached.replace(':', '_')
            if not os.path.isfile(cache_dir + '/' + cached):
                print('image not here')
                url = thumb
                fp = urllib.request.urlopen(url)
                data = fp.read()
                fp.close()
                with open(cache_dir + '/' + cached, "wb") as code:
                    code.write(data)

            data = cache_dir + '/' + cached
            #img = wx.Image(io.BytesIO(data), type=wx.BITMAP_TYPE_ANY, index=-1)
            img = wx.Image(data, type=wx.BITMAP_TYPE_ANY, index=-1)
            img.Rescale(75, 75)
            self.imageCtrl = wx.StaticBitmap(self.listFanartlist, wx.ID_ANY,
                                         wx.Bitmap(img))
            self.listFanart.Add(self.imageCtrl, pos=(row, col), flag=wx.ALL, border=5)
            self.listFanartlist.Layout()
            self.listFanartlist.SetupScrolling()
            if col < 3:
                col += 1
            else:
                col = 0
                row += 1

        for genre in self.output['genres']:
            self.listGenres.AppendText(genre + '\n')
        for actor in self.output['actors_names']:
            self.listActors.AppendText(actor + '\n')
        if self.generateBaseString() != self.selectedFolder[0] + '/' + self.selectedItem:
            self.renameBtn.Enable()

    def saveNFO(self, event):
        root = et.Element('movie')
        title = et.SubElement(root, 'title')
        title.text = self.movieName.GetValue()
        originaltitle = et.SubElement(root, 'originaltitle')
        originaltitle.text = self.originalTitle.GetValue()
        sorttitle = et.SubElement(root, 'sorttitle')
        sorttitle.text = self.sortTitle.GetValue()
        set = et.SubElement(root, 'set')
        set.text = self.movieSet.GetValue()
        year = et.SubElement(root, 'year')
        year.text = self.movieYear.GetValue()
        top250 = et.SubElement(root, 'top250')
        top250.text = self.movieSet.GetValue()
        trailer = et.SubElement(root, 'trailer')
        trailer.text = self.Trailer.GetValue()
        votes = et.SubElement(root, 'votes')
        votes.text = self.movieVotes.GetValue()
        rating = et.SubElement(root, 'rating')
        rating.text = self.movieRating.GetValue()
        outline = et.SubElement(root, 'outline')
        outline.text = self.Outline.GetValue()
        plot = et.SubElement(root, 'plot')
        plot.text = self.moviePlot.GetValue()
        tagline = et.SubElement(root, 'tagline')
        tagline.text = self.tagLine.GetValue()
        runtime = et.SubElement(root, 'runtime')
        runtime.text = self.runTime.GetValue()
        releasedate = et.SubElement(root, 'releasedate')
        releasedate.text = self.releaseDate.GetValue()
        studio = et.SubElement(root, 'studio')
        studio.text = self.Studio.GetValue()
        fanart = et.SubElement(root, 'fanart')
        thumbs = self.listThumbs.GetValue()
        thumbs = thumbs.split('\n')
        for thumb in thumbs:
            if thumb:
                thumb_tag = et.SubElement(root, 'thumb')
                thumb_tag.text = thumb
                fanart_tag = et.SubElement(fanart, 'thumb')
                fanart_tag.text = thumb

        movieid = et.SubElement(root, 'id')
        movieid.text = self.movieId.GetValue()
        actors = self.listActors.GetValue()
        actors = actors.split('\n')
        for actor in actors:
            if actor:
                actor_tag = et.SubElement(root, 'actor')
                actor_name = et.SubElement(actor_tag, 'name')
                actor_name.text = actor

        genres = self.listGenres.GetValue()
        genres = genres.split('\n')
        for genre in genres:
            if genre:
                genre_tag = et.SubElement(root, 'genre')
                genre_tag.text = genre

        parser = et.XMLParser(remove_blank_text=True)
        tree = et.ElementTree(root)
        fname = self.selectedFolder[0] + '/' + self.selectedItem + '/' + self.selectedItem + '.nfo'

        xmlstr = minidom.parseString(et.tostring(tree)).toprettyxml(indent="   ", encoding='utf-8', )

        with open(fname, 'wb') as f:
            f.write(xmlstr)

    def readNFO(self, path):
        tree = et.parse(path)
        root = tree.getroot()
        if root.find('title').text:
            self.movieName.SetLabel(root.find('title').text)
        if root.find('originaltitle').text:
            self.originalTitle.SetLabel(root.find('originaltitle').text)
        if root.find('sorttitle').text:
            self.sortTitle.SetLabel(root.find('sorttitle').text)
        if root.find('set').text:
            self.movieSet.SetLabel(root.find('set').text)
        if root.find('year').text:
            self.movieYear.SetLabel(root.find('year').text)
        if root.find('top250').text:
            self.Top250.SetLabel(root.find('top250').text)
        if root.find('trailer').text:
            self.Trailer.SetLabel(root.find('trailer').text)
        if root.find('votes').text:
            self.movieVotes.SetLabel(root.find('votes').text)
        if root.find('rating').text:
            self.movieRating.SetLabel(root.find('rating').text)
        if root.find('outline').text:
            self.Outline.SetLabel(root.find('outline').text)
        if root.find('plot').text:
            self.moviePlot.SetLabel(root.find('plot').text)
        if root.find('tagline').text:
            self.tagLine.SetLabel(root.find('tagline').text)
        if root.find('runtime').text:
            self.runTime.SetLabel(root.find('runtime').text)
        if root.find('releasedate').text:
            self.releaseDate.SetLabel(root.find('releasedate').text)
        if root.find('studio').text:
            self.Studio.SetLabel(root.find('studio').text)
        if root.findall('thumb'):
            row = 0
            col = 0
            for thumb in root.findall('thumb'):
                if thumb.text:
                    self.listThumbs.AppendText(thumb.text + '\n')
                    cached = thumb.text.replace('/', '_')
                    cached = cached.replace(':', '_')
                    if not os.path.isfile(cache_dir + '/' + cached):
                        print('image not here')
                        url = thumb.text
                        fp = urllib.request.urlopen(url)
                        data = fp.read()
                        fp.close()
                        with open(cache_dir + '/' + cached, "wb") as code:
                            code.write(data)

                    data = cache_dir + '/' + cached
                    # img = wx.Image(io.BytesIO(data), type=wx.BITMAP_TYPE_ANY, index=-1)
                    img = wx.Image(data, type=wx.BITMAP_TYPE_ANY, index=-1)
                    img.Rescale(75, 75)
                    self.imageCtrl = wx.StaticBitmap(self.listFanartlist, wx.ID_ANY,
                                                     wx.Bitmap(img))
                    self.listFanart.Add(self.imageCtrl, pos=(row, col), flag=wx.ALL, border=5)
                    self.listFanartlist.Layout()
                    self.listFanartlist.SetupScrolling()

                    if col < 3:
                        col += 1
                    else:
                        col = 0
                        row += 1
        if root.find('id').text:
            self.movieId.SetLabel(root.find('id').text)
            self.scrapeId = root.find('id').text
        if root.findall('genre'):
            for genre in root.findall('genre'):
                self.listGenres.AppendText(genre.text + '\n')
        if root.findall('actor'):
            for actor in root.findall('actor'):
                self.listActors.AppendText(actor.find('name').text + '\n')
        if self.generateBaseString() != self.selectedFolder[0] + '/' + self.selectedItem:
            self.renameBtn.Enable()


    # ----------------------------------------------------------------------

    def onExit(self, event):
        """"""
        self.Close()

    # ----------------------------------------------------------------------
    def onOptionsMenu(self, event):
        """"""
        dlg = OptionsDialog()
        dlg.ShowModal()
        dlg.Destroy()

    def onOpenSearch(self, event):
        """"""
        dlg = SearchDlg()
        dlg.ShowModal()
        seleceted = dlg.selected
        dlg.Destroy()
        self.movieId.SetLabel(seleceted)
        self.scrapeId = seleceted

    def moveToFolder(self, event):
        base = os.path.basename(self.selectedItem)
        base = os.path.splitext(base)[0]
        path = self.selectedFolder[0] + "/" + base
        os.makedirs(path)

        os.rename(self.selectedFolder[0] + "/" + self.selectedItem, path + "/" + selectedItem)

        self.updateDisplay(self.selectedFolder[0])

    def doRename(self, event):
        '''
        paths = glob.glob(folder_path + "/*")
        self.selectedFolder = glob.glob(folder_path)
        self.dirList.DeleteAllItems()
        for index, path in enumerate(paths):
            self.dirList.InsertItem(index, os.path.basename(path))
        self.dirList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.ListOnClick, self.dirList)
        Let's get folder content ... shall we?
        '''
        enum_path = glob.glob(self.selectedFolder[0] + "/" + self.selectedItem + "/*")
        ext_path = glob.glob(self.selectedFolder[0] + '/' + self.selectedItem)
        base = self.generateBaseString()
        tgt_path = glob.glob(self.selectedFolder[0] + "/")
        for index, path in enumerate(enum_path):
            file = os.path.basename(path)
            file_container = os.path.splitext(file)
            if kink.extensions.count(file_container[1][1:]) or file_container[1] == '.nfo':
                os.rename(path, ext_path[0] + '/' + base + file_container[1])
        os.rename(ext_path[0], tgt_path[0] + base)
        self.selectedItem = base
        self.updateDisplay(self.selectedFolder[0])

    def generateBaseString(self):
        """
            Here we define base string format
            Supported:
            {SET}
            {S_E_T}
            {S.E.T}
            {S-E-T}
            {SET-}
            {DATE}
            {D.A.T.E}
            {D_A_T_E}
            {DATE-}
            {NAME}
            {N_A_M_E}
            {N.A.M.E}
            {N-A-M-E}
            {NAME-}
            {ID}
        """
        ''' Let's build strings '''
        movieSet = self.movieSet.GetValue()
        releaseDate = self.releaseDate.GetValue()
        movieName = self.movieName.GetValue()
        id = self.movieId.GetValue()

        string = config.config['ALL']['base_string']
        string = string.replace('{SET}', movieSet)
        string = string.replace('{S_E_T}', movieSet.replace(' ', '_'))
        string = string.replace('{S.E.T}', movieSet.replace(' ', '.'))
        string = string.replace('{S-E-T}', movieSet.replace(' ', '-'))
        string = string.replace('{SET-}', movieSet.replace(' ', ''))
        string = string.replace('{DATE}', releaseDate)
        string = string.replace('{D_A_T_E}', releaseDate.replace(' ', '_'))
        string = string.replace('{D.A.T.E}', releaseDate.replace(' ', '.'))
        string = string.replace('{D-A-T-E}', releaseDate.replace(' ', '-'))
        string = string.replace('{DATE-}', releaseDate.replace(' ', ''))
        string = string.replace('{NAME}', movieName)
        string = string.replace('{N_A_M_E}', movieName.replace(' ', '_'))
        string = string.replace('{N.A.M.E}', movieName.replace(' ', '.'))
        string = string.replace('{N-A-M-E}', movieName.replace(' ', '-'))
        string = string.replace('{NAME-}', movieName.replace(' ', ''))
        string = string.replace('{ID}', id)

        return string


app = wx.App(False)
frame = MainWindow()
frame.Show()
frame.Maximize(True)
app.MainLoop()