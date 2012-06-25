# Program: Ascii Art Generator
# Author:  Jorge Yau
# Email:   exaccus0205@gmail.com
# File:    ascii.py

import wx
import PIL
import Image
import os
from bisect import bisect

class AsciiArtFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # AsciiArtFrame.__init__
        kwds["style"] = wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX |\
                wx.SYSTEM_MENU | wx.SIMPLE_BORDER | wx.RESIZE_BORDER | wx.CLIP_CHILDREN
        wx.Frame.__init__(self, *args, **kwds)
        self.SetMinSize((320,700))
        self.SetBackgroundStyle(wx.BG_STYLE_SYSTEM)
        
        # Blank Image
        self.blank_image = wx.EmptyBitmapRGBA(280,280,255,255,255)
        self.ImagePreview = self.blank_image
        self.ImageSource = self.blank_image
        self.ImageGrayscale = self.blank_image
        
        # Resources
        self.Ascii_Width  = 100
        self.Ascii_Height = 100
        self.ImageIsLoaded = False
        self.ImagePath = ""
        self.AutoProportion = False
        self.GrayscaleActive = False
        self.ProportionsActive = False

        # Menu Bar
        self.ascii_menu = wx.MenuBar()
        ascii_Menu = wx.Menu()
        menu_file_open = ascii_Menu.Append(wx.NewId(), "Open Image\tCtrl+O", "", wx.ITEM_NORMAL)
        menu_file_save = ascii_Menu.Append(wx.NewId(), "Save Text\tCtrl+S", "", wx.ITEM_NORMAL)
        ascii_Menu.AppendSeparator()
        menu_file_restart = ascii_Menu.Append(wx.NewId(), "Clear\tCtrl+C", "", wx.ITEM_NORMAL)
        menu_file_exit = ascii_Menu.Append(wx.NewId(), "Exit", "", wx.ITEM_NORMAL)
        self.ascii_menu.Append(ascii_Menu, "File")
        
        ascii_Menu = wx.Menu()
        menu_run_start = ascii_Menu.Append(wx.NewId(), "Start\tF2", "", wx.ITEM_NORMAL)
        self.ascii_menu.Append(ascii_Menu, "Run")
        
        ascii_Menu = wx.Menu()
        menu_view_image = ascii_Menu.Append(wx.NewId(), "View Image\tF5", "", wx.ITEM_NORMAL)
        ascii_Menu.AppendSeparator()
        menu_view_in = ascii_Menu.Append(wx.NewId(), "Zoom In\t+", "", wx.ITEM_NORMAL)
        menu_view_out = ascii_Menu.Append(wx.NewId(), "Zoom Out\t-", "", wx.ITEM_NORMAL)
        menu_view_reset = ascii_Menu.Append(wx.NewId(), "Zoom Reset", "", wx.ITEM_NORMAL)
        self.ascii_menu.Append(ascii_Menu, "View")
        
        ascii_Menu = wx.Menu()
        menu_tools_grayscale = ascii_Menu.Append(wx.NewId(), "Toggle Grayscale\tF3", "", wx.ITEM_NORMAL)
        menu_tools_proportions = ascii_Menu.Append(wx.NewId(), "Auto Proportions\tF4", "", wx.ITEM_NORMAL)
        self.ascii_menu.Append(ascii_Menu, "Tools")
        
        ascii_Menu = wx.Menu()
        menu_help_help = ascii_Menu.Append(wx.NewId(), "Help", "", wx.ITEM_NORMAL)
        menu_help_about = ascii_Menu.Append(wx.NewId(), "About", "", wx.ITEM_NORMAL)
        self.ascii_menu.Append(ascii_Menu, "Help")
        self.SetMenuBar(self.ascii_menu)
        
        # Bind Menu Items
        self.Bind(wx.EVT_MENU, self.MenuFileOpen, menu_file_open)
        self.Bind(wx.EVT_MENU, self.MenuFileSave, menu_file_save)
        self.Bind(wx.EVT_MENU, self.MenuFileRestart, menu_file_restart)
        self.Bind(wx.EVT_MENU, self.MenuFileExit, menu_file_exit)
        self.Bind(wx.EVT_MENU, self.MenuRunStart, menu_run_start)
        
        self.Bind(wx.EVT_MENU, self.MenuViewImage, menu_view_image)
        self.Bind(wx.EVT_MENU, self.MenuViewIn, menu_view_in)
        self.Bind(wx.EVT_MENU, self.MenuViewOut, menu_view_out)
        self.Bind(wx.EVT_MENU, self.MenuViewReset, menu_view_reset)
        
        self.Bind(wx.EVT_MENU, self.MenuToolsGrayscale, menu_tools_grayscale)
        self.Bind(wx.EVT_MENU, self.MenuToolsProportions, menu_tools_proportions)
        self.Bind(wx.EVT_MENU, self.MenuHelpHelp, menu_help_help)
        self.Bind(wx.EVT_MENU, self.MenuHelpAbout, menu_help_about)
        
        # Widgets
        self.status = self.CreateStatusBar(1, 0)
        self.panel_1 = wx.Panel(self, -1)
        self.bitmap_button = wx.BitmapButton(self.panel_1, -1, self.ImagePreview)
        self.label_grayscale = wx.StaticText(self.panel_1, -1, "Grayscale Preview")
        self.tb_grayscale = wx.ToggleButton(self.panel_1, -1, "Off")
        self.label_dimension = wx.StaticText(self.panel_1, -1, "Auto Proportions")
        self.tb_dimension = wx.ToggleButton(self.panel_1, -1, "Off")
        self.label_height = wx.StaticText(self.panel_1, -1, "Rows for Height")
        self.et_height = wx.TextCtrl(self.panel_1, -1, "")
        self.label_width = wx.StaticText(self.panel_1, -1, "Columns for Width")
        self.et_width = wx.TextCtrl(self.panel_1, -1, "")
        self.static_line_1 = wx.StaticLine(self.panel_1, -1)
        self.b_start = wx.Button(self.panel_1, wx.ID_OPEN, "Start")
        self.static_line_2 = wx.StaticLine(self.panel_1, -1)
        self.label_scale = wx.StaticText(self.panel_1, -1, "Zoom")
        self.slider_zoom = wx.Slider(self.panel_1, -1, 2, 2, 7, size=(120,-1), style=wx.SL_HORIZONTAL)
        self.et_asciiArea = wx.TextCtrl(self, -1, "", style=wx.TE_PROCESS_ENTER | wx.TE_PROCESS_TAB |\
                                         wx.TE_MULTILINE | wx.HSCROLL | wx.TE_RICH | wx.TE_RICH2 | wx.TE_NOHIDESEL)
        
        # Begin Methods
        self.SetProperties()
        self.MakeLayout()
        self.EnableHandlers()

    def SetProperties(self):
        
        self.SetTitle("Ascii Art Generator")
        self.SetSize((1100, 700))
        self.status.SetStatusWidths([-1])
        
        # statusbar fields
        status_fields = ["New"]
        for i in range(len(status_fields)):
            self.status.SetStatusText(status_fields[i], i)
        
        # Ascii Resources
        self.Ascii_Font = self.slider_zoom.GetValue()
        
        self.bitmap_button.SetToolTipString("Click to open a new image")
        self.bitmap_button.SetSize(self.bitmap_button.GetBestSize())
        self.bitmap_button.SetDefault()
        self.label_grayscale.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Tahoma"))
        self.tb_grayscale.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Tahoma"))
        self.tb_grayscale.SetToolTipString("Toggles preview image color between grayscale and RGB")
        self.label_dimension.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Tahoma"))
        self.tb_dimension.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Tahoma"))
        self.tb_dimension.SetToolTipString("Generates rows and columns to fill width of the text area")
        self.label_height.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Tahoma"))
        self.et_height.SetToolTipString("Enter number of lines for height")
        self.label_width.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Tahoma"))
        self.et_width.SetToolTipString("Enter number of columns for width")
        self.b_start.SetMinSize((105, 50))
        self.b_start.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Tahoma"))
        self.b_start.SetToolTipString("Generates ascii art from the image loaded")
        self.label_scale.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Tahoma"))
        self.label_scale.SetToolTipString("Scroll slider to change the font size of the ascii characters")
        self.et_asciiArea.SetFont(wx.Font(self.Ascii_Font, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.et_asciiArea.SetEditable(False)
        
    def MakeLayout(self):
        
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        
        grid_settings = wx.GridSizer(6, 2, 0, 0)
        sizer_3.Add(self.bitmap_button, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 6)
        grid_settings.Add(self.label_grayscale, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        grid_settings.Add(self.tb_grayscale, 0, wx.Top | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_settings.Add(self.label_dimension, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        grid_settings.Add(self.tb_dimension, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_settings.Add(self.label_height, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        grid_settings.Add(self.et_height, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_settings.Add(self.label_width, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        grid_settings.Add(self.et_width, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
        
        sizer_3.Add(grid_settings, 1, wx.EXPAND, 0)
        sizer_1.Add(self.static_line_1, 0, wx.EXPAND, 0)
        sizer_4.Add(self.b_start, 0, wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 15)
        sizer_4.Add(self.static_line_2, 0, wx.EXPAND, 0)
        sizer_5.Add(self.label_scale, 0, wx.TOP | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 10)
        sizer_5.Add(self.slider_zoom, 0, wx.TOP | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_4.Add(sizer_5, 1, wx.EXPAND, 0)
        sizer_1.Add(sizer_4, 1, wx.EXPAND, 0)
        sizer_3.Add(sizer_1, 1, wx.EXPAND, 0)
        self.panel_1.SetSizer(sizer_3)
        sizer_2.Add(self.panel_1, 0, wx.EXPAND, 0)
        sizer_2.Add(self.et_asciiArea, 1, wx.ALL | wx.EXPAND, 1)
        self.SetSizer(sizer_2)
        self.Layout()
        self.Centre()
        
    #### --- DIALOG BOXES --- ####
    def InvalidInputDialog(self):
        InvalidDialog = wx.MessageDialog(None, "You must enter a valid height and width.", 
                                         "Invalid Size", wx.OK | wx.CENTER | wx.ICON_EXCLAMATION)
        InvalidDialog.ShowModal()
        InvalidDialog.Destroy()
    
    def NoImageDialog(self):
        NoImageDialog = wx.MessageDialog(None, "You must open an image file first.", 
                                         "Invalid Image", wx.OK | wx.CENTER | wx.ICON_EXCLAMATION)
        NoImageDialog.ShowModal()
        NoImageDialog.Destroy()
    
    def InvalidImageDialog(self):
        InvalidImageDialog = wx.MessageDialog(None, "The image you have selected is an invalid file.", 
                                         "Invalid File", wx.OK | wx.CENTER | wx.ICON_ERROR)
        InvalidImageDialog.ShowModal()
        InvalidImageDialog.Destroy()
        
    def LargeSizeDialog(self):
        LargeSizeDialog = wx.MessageDialog(None, "The ascii image may take a while to generate.\nDo you want to continue?", 
                                           "Large Conversion Size", wx.YES_NO | wx.YES_DEFAULT | 
                                           wx.CENTER | wx.ICON_INFORMATION)
        result = LargeSizeDialog.ShowModal()
        LargeSizeDialog.Destroy()
        return result      
      
    def GiantSizeDialog(self):
        GiantSizeDialog = wx.MessageDialog(None, "The program may freeze or even crash.\nDo you want to continue?", 
                                           "Large Conversion Size", wx.YES_NO | wx.YES_DEFAULT | 
                                           wx.CENTER | wx.ICON_INFORMATION)
        result = GiantSizeDialog.ShowModal()
        GiantSizeDialog.Destroy()
        return result

    def ShowSaveDialog(self):
        ShowSaveDialog = wx.MessageDialog(None, "Your file has been successfully saved.", "File Saved", 
                                          wx.OK | wx.CENTER | wx.ICON_INFORMATION)
        ShowSaveDialog.ShowModal()
        ShowSaveDialog.Destroy()

    def EnableHandlers(self):
        
        self.Bind(wx.EVT_BUTTON, self.CreateAscii, self.b_start)
        self.Bind(wx.EVT_BUTTON, self.OpenFileBrowser, self.bitmap_button)
        self.Bind(wx.EVT_SCROLL, self.SliderZoom, self.slider_zoom)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.ToggleGrayscale, self.tb_grayscale)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.ToggleProportions, self.tb_dimension)
        
    def MenuFileOpen(self, event):
        self.OpenFileBrowser(event)
    
    def MenuFileSave(self, event):
        wildcard = "Text Files (*.txt)| *.txt"
        SaveDialog = wx.FileDialog(None, message="Save text as",
                                   wildcard=wildcard,style = wx.SAVE)
        try:
            if SaveDialog.ShowModal() == wx.ID_OK:
                savepath = SaveDialog.GetPath()
                savetext = self.et_asciiArea.GetValue()
                savefile = open(savepath, 'w')
                savefile.write(savetext)
                savefile.close()
                self.ShowSaveDialog()
        except Exception:
            pass
    
    def MenuFileRestart(self, event):
        self.ImageIsLoaded = False
        self.bitmap_button.SetBitmapLabel(self.blank_image)
        self.status.SetStatusText("New")
        self.et_asciiArea.Clear()
        self.et_height.Clear()
        self.et_width.Clear()
    
    def MenuFileExit(self, event):
        self.Close()
        
    def MenuViewImage(self, event):
        try:
            if self.ImageIsLoaded == True:
                os.startfile(self.ImagePath)
            else:
                self.NoImageDialog()
        except Exception:
            self.InvalidImageDialog()
        
    def MenuViewIn(self, event):
        self.slider_zoom.SetValue(self.slider_zoom.GetValue()+1)
        self.SliderZoom(event)
    
    def MenuViewOut(self, event):
        self.slider_zoom.SetValue(self.slider_zoom.GetValue()-1)
        self.SliderZoom(event)
        
    def MenuViewReset(self, event):
        self.slider_zoom.SetValue(1)
        self.SliderZoom(event)
        
    def MenuToolsGrayscale(self, event):
        if self.GrayscaleActive == False:
            self.GrayscaleActive = True
            self.tb_grayscale.SetValue(True)
            self.ToggleGrayscale(event)
        else:
            self.GrayscaleActive = False
            self.tb_grayscale.SetValue(False)
            self.ToggleGrayscale(event)
        
    def MenuToolsProportions(self, event):
        if self.ProportionsActive == False:
            self.ProportionsActive = True
            self.tb_dimension.SetValue(True)
            self.ToggleProportions(event)
        else:
            self.ProportionsActive = False
            self.tb_dimension.SetValue(False)
            self.ToggleProportions(event)
    
    def MenuHelpHelp(self, event):
        help1 = ("First Time Users:\nStep 1:  Click on the preview box to open an image." +
                "\nStep 2:  Click the Auto Proportion button or press (F4)." +
                "\nStep 3:  Press the Start button or Menu->Run->Start (F2)." +
                "\n\nTip:  Hover the mouse over something to read what it does."
                )
        Help = wx.MessageDialog(None, help1, "Help", wx.ICON_QUESTION)
        Help.ShowModal()
        
    def MenuHelpAbout(self, event):
        About = wx.AboutDialogInfo()
        About.SetName('Ascii Art Generator')
        About.SetVersion('0.5')
        About.SetCopyright('(C) 2012 \tJorge Yau')
        About.SetDescription('Contact: \tcodenameyau@gmail.com')
        wx.AboutBox(About)
        
    #### EVENT HANDLERS ####
    
    def MenuRunStart(self, event):
        self.CreateAscii(event)
    
    def OpenFileBrowser(self, event):
        
        wildcard = "Image Files |*.jpg;*.png;*.bmp|" \
                    "JPEG (*.jpg)|*.jpg|" \
                    "PNG (*.png)|*.png|" \
                    "BMP (*.bmp)|*.bmp"
        filedialog = wx.FileDialog (
                                    self, message="Choose a file",
                                    defaultFile="", wildcard=wildcard,
                                    style=wx.OPEN | wx.CHANGE_DIR
                                    )
        try:
            if filedialog.ShowModal() == wx.ID_OK:
                self.ImagePath = filedialog.GetPath()
                self.ImageIsLoaded = True
                img = wx.Image(self.ImagePath)
                
                # Preview Image Resizer 
                if img.GetHeight() > img.GetWidth():
                    baseheight = 280
                    h_percent = (baseheight / float(img.GetHeight()))
                    basewidth = img.GetWidth() * h_percent
                else:
                    basewidth = 280
                    w_percent = (basewidth / float(img.GetWidth()))
                    baseheight = img.GetHeight() * w_percent
                    
                img = img.Rescale(basewidth, baseheight, wx.IMAGE_QUALITY_HIGH)
                # Acquire original and grayscale version
                self.ImageSource = img
                self.ImageGrayscale = img.ConvertToGreyscale()
                if self.tb_grayscale.GetValue() == True:
                    self.ImagePreview = wx.BitmapFromImage(self.ImageGrayscale)
                else:
                    self.ImagePreview = wx.BitmapFromImage(self.ImageSource)
                self.bitmap_button.SetBitmapLabel(self.ImagePreview)
                self.status.SetStatusText(self.ImagePath)
            else:
                pass
                
        except Exception:
            self.InvalidImageDialog()
        finally:
            filedialog.Destroy()
        
    def CreateAscii(self, event):
        # Default characters for luminosity
        grayscale = [
                    " ",
                    " ",
                    ".",
                    "'",
                    "`",
                    ":",
                    ";",
                    "-",
                    "=",
                    "+",
                    "l",
                    "I",
                    "J",
                    "C",
                    "D",
                    "B",
                    "H",
                    "M"
                    ]
        # Use bisect class for luminosity values
        zonebounds = [15,30,45,60,75,90,105,120,135,150,165,180,195,210,225,240,255]
            
        # Open image, convert to grayscale, and resize
        try:
            if self.ImageIsLoaded == False:
                raise RuntimeError
            im = Image.open(self.ImagePath).convert("L")
            
            # Auto Proportion
            if self.AutoProportion == True:
                # Getting image text ratio to generate height and width 
                text_w, text_h = self.et_asciiArea.GetClientSize()
                img_w, img_h = im.size 
                img_ratio = float(img_h)/float(img_w)
                text_ratio = float(text_w)/float(text_h)
                
                text_h = int((text_h/3.0)*img_ratio*text_ratio)
                text_w = int((text_w/2.0))
                self.Ascii_Height = text_h
                self.Ascii_Width  = text_w
                
                self.et_height.SetValue(str(text_h))
                self.et_width.SetValue(str(text_w))
            # Take user's size input
            else:
                self.Ascii_Height = int(self.et_height.GetValue())
                self.Ascii_Width  = int(self.et_width.GetValue())
            
            
            size = self.Ascii_Height * self.Ascii_Width
            if size > 2000000:
                if self.GiantSizeDialog() == wx.ID_NO:
                    raise AssertionError
            elif size > 500000:
                if self.LargeSizeDialog() == wx.ID_NO:
                    raise AssertionError
                
            im = im.resize((self.Ascii_Width, self.Ascii_Height), Image.ANTIALIAS)
            
            # working with pixels, build up string
            asciiText = ""
            for y in range(0,im.size[1]):
                for x in range(0,im.size[0]):
                    lum = 255-im.getpixel((x,y))
                    row = bisect(zonebounds, lum)
                    possibles = grayscale[row]
                    asciiText = asciiText + possibles[0]
                asciiText = asciiText + "\n"
            self.et_asciiArea.SetValue(asciiText)
        except RuntimeError:
            self.NoImageDialog()
        except ValueError:
            self.InvalidInputDialog()
        except AssertionError:
            pass
        except MemoryError:
            pass
        except Exception:
            self.InvalidImageDialog()

    def SliderZoom(self, event):
        self.Ascii_Font = self.slider_zoom.GetValue()
        self.et_asciiArea.SetFont(wx.Font(self.Ascii_Font, wx.MODERN, wx.NORMAL, wx.NORMAL))
        
    def ToggleGrayscale(self, event):
        if self.tb_grayscale.GetValue() == True:
            self.tb_grayscale.SetLabel("On")
            try:
                self.ImageGrayscale = self.ImageGrayscale.ConvertToGreyscale()
                self.ImagePreview = wx.BitmapFromImage(self.ImageGrayscale)
                self.bitmap_button.SetBitmapLabel(self.ImagePreview)
            except Exception:
                pass
        elif self.tb_grayscale.GetValue() == False:
            self.tb_grayscale.SetLabel("Off")
            try:
                self.ImagePreview = wx.BitmapFromImage(self.ImageSource)
                self.bitmap_button.SetBitmapLabel(self.ImagePreview)
            except Exception:
                pass
    
    def ToggleProportions(self, event):
        if self.tb_dimension.GetValue() == True:
            self.tb_dimension.SetLabel("On")
            self.AutoProportion = True
            self.et_height.SetEditable(False)
            self.et_width.SetEditable(False)
            
        elif self.tb_dimension.GetValue() == False:
            self.tb_dimension.SetLabel("Off")
            self.AutoProportion = False
            self.et_height.SetEditable(True)
            self.et_width.SetEditable(True)

    def ToggleCustomCharacters(self, event):
        if self.tb_custom.GetValue() == True:
            self.tb_custom.SetLabel("On")
            self.CustomCharacters = True
        elif self.tb_custom.GetValue() == False:
            self.tb_custom.SetLabel("Off")
            self.CustomCharacters = False 
    
# end of class AsciiArtFrame

if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame = AsciiArtFrame(None, -1, "")
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()
