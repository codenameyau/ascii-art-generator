#!/usr/bin/env python
import wx
import PIL
import Image
import random
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
    
        # Menu Bar
        self.ascii_menu = wx.MenuBar()
        ascii_Menu = wx.Menu()
        ascii_Menu.Append(wx.NewId(), "Open", "", wx.ITEM_NORMAL)
        ascii_Menu.Append(wx.NewId(), "Save", "", wx.ITEM_NORMAL)
        ascii_Menu.AppendSeparator()
        ascii_Menu.Append(wx.NewId(), "Close", "", wx.ITEM_NORMAL)
        ascii_Menu.Append(wx.NewId(), "Exit", "", wx.ITEM_NORMAL)
        self.ascii_menu.Append(ascii_Menu, "File")
        ascii_Menu = wx.Menu()
        ascii_Menu.Append(wx.NewId(), "Start", "", wx.ITEM_NORMAL)
        self.ascii_menu.Append(ascii_Menu, "Run")
        ascii_Menu = wx.Menu()
        ascii_Menu.Append(wx.NewId(), "Full View", "", wx.ITEM_NORMAL)
        ascii_Menu.Append(wx.NewId(), "View Image", "", wx.ITEM_NORMAL)
        ascii_Menu.AppendSeparator()
        ascii_Menu.Append(wx.NewId(), "Zoom In", "", wx.ITEM_NORMAL)
        ascii_Menu.Append(wx.NewId(), "Zoom Out", "", wx.ITEM_NORMAL)
        ascii_Menu.Append(wx.NewId(), "Zoom Reset", "", wx.ITEM_NORMAL)
        self.ascii_menu.Append(ascii_Menu, "View")
        ascii_Menu = wx.Menu()
        ascii_Menu.Append(wx.NewId(), "Custom Characters", "", wx.ITEM_NORMAL)
        self.ascii_menu.Append(ascii_Menu, "Settings")
        ascii_Menu = wx.Menu()
        ascii_Menu.Append(wx.NewId(), "Help", "", wx.ITEM_NORMAL)
        ascii_Menu.Append(wx.NewId(), "About", "", wx.ITEM_NORMAL)
        self.ascii_menu.Append(ascii_Menu, "Help")
        self.SetMenuBar(self.ascii_menu)
        # Widgets
        self.status = self.CreateStatusBar(1, 0)
        self.panel_1 = wx.Panel(self, -1)
        self.bitmap_button = wx.BitmapButton(self.panel_1, -1, self.ImagePreview)
        self.label_grayscale = wx.StaticText(self.panel_1, -1, "Grayscale Preview")
        self.tb_grayscale = wx.ToggleButton(self.panel_1, -1, "Off")
        self.label_custom = wx.StaticText(self.panel_1, -1, "Custom Characters")
        self.tb_custom = wx.ToggleButton(self.panel_1, -1, "Off")
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
        self.slider_zoom = wx.Slider(self.panel_1, -1, 3, 2, 8, size=(120,-1), style=wx.SL_HORIZONTAL)
        self.et_asciiArea = wx.TextCtrl(self, -1, "", style=wx.TE_PROCESS_ENTER | wx.TE_PROCESS_TAB |\
                                         wx.TE_MULTILINE | wx.HSCROLL | wx.TE_RICH | wx.TE_RICH2 | wx.TE_NOHIDESEL)
        
        # Begin Methods
        self.__set_properties()
        self.__do_layout()
        self.EnableHandlers()

    def __set_properties(self):
        
        self.SetTitle("Ascii Art Generator")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("icon.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
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
        self.tb_grayscale.SetToolTipString("Switches image color of preview to grayscale")
        self.label_custom.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Tahoma"))
        self.tb_custom.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Tahoma"))
        self.tb_custom.SetToolTipString("Enables custom characters for ascii generation")
        self.label_dimension.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Tahoma"))
        self.tb_dimension.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Tahoma"))
        self.tb_dimension.SetToolTipString("Generates ascii height and width based on best-fit proportions")
        self.label_height.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Tahoma"))
        self.et_height.SetToolTipString("Enter lines of height for ascii generation")
        self.label_width.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Tahoma"))
        self.et_width.SetToolTipString("Enter characters of width for ascii generation")
        self.b_start.SetMinSize((105, 50))
        self.b_start.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Tahoma"))
        self.b_start.SetToolTipString("Generates ascii art from the image loaded")
        self.label_scale.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Tahoma"))
        self.label_scale.SetToolTipString("Scroll slider to change the font of the ascii characters")
        self.et_asciiArea.SetFont(wx.Font(self.Ascii_Font, wx.MODERN, wx.NORMAL, wx.NORMAL))
        
    def __do_layout(self):
        
        # begin wxGlade: AsciiArtFrame.__do_layout
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        grid_settings = wx.GridSizer(6, 2, 0, 0)
        sizer_3.Add(self.bitmap_button, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 6)
        grid_settings.Add(self.label_grayscale, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        grid_settings.Add(self.tb_grayscale, 0, wx.Top | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_settings.Add(self.label_custom, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        grid_settings.Add(self.tb_custom, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
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
        sizer_2.Add(self.et_asciiArea, 1, wx.ALL | wx.EXPAND, 2)
        self.SetSizer(sizer_2)
        self.Layout()
        self.Centre()
    
    def EnableHandlers(self):
        
        self.Bind(wx.EVT_BUTTON, self.CreateAscii, self.b_start)
        self.Bind(wx.EVT_BUTTON, self.OpenFileBrowser, self.bitmap_button)
        self.Bind(wx.EVT_SCROLL, self.SliderZoom, self.slider_zoom)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.ToggleGrayscale, self.tb_grayscale)
    
    #### --- DIALOG BOXES --- ####
    
    # InvalidInputDialog()
    def InvalidInputDialog(self):
        
        InvalidDialog = wx.MessageDialog(None, "You must enter a valid height and width.", 
                                         "Invalid Start", wx.OK | wx.ICON_EXCLAMATION)
        InvalidDialog.ShowModal()
    
    def NoImageDialog(self):
        
        NoImageDialog = wx.MessageDialog(None, "You must open an image file first.", 
                                         "Invalid Start", wx.OK | wx.ICON_EXCLAMATION)
        NoImageDialog.ShowModal()
    
    def InvalidImageDialog(self):
        
        InvalidDialog = wx.MessageDialog(None, "The file you have selected is not an image file.", 
                                         "Invalid File", wx.OK | wx.ICON_EXCLAMATION)
        InvalidDialog.ShowModal()

    #### --- EVENT HANDLERS --- ####
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
            else:
                pass
                
        except Exception:
            self.InvalidImageDialog()
        finally:
            filedialog.Destroy()
        
    def CreateAscii(self, event):
        # Grayscale Tones
        grayscale = [
                    " ",
                    " ",
                    ".",
                    "'",
                    "`",
                    ":",
                    "~",
                    "=",
                    "+",
                    "l",
                    "C",
                    "E",
                    "H"
                    ]
        
        # Use bisect class for luminosity values
        zonebounds = [21,42,63,84,105,126,147,168,189,210,231,252]
        
        # Open image and resize
        try:
            if self.ImageIsLoaded == False:
                raise RuntimeError
            self.Ascii_Height = int(self.et_height.GetValue())
            self.Ascii_Width  = int(self.et_width.GetValue())
            im = Image.open(self.ImagePath)
            im = im.resize((self.Ascii_Width, self.Ascii_Height), Image.ANTIALIAS)
            im = im.convert("L") # convert to mono
            
            # working with pixels, build up string
            str = ""
            for y in range(0,im.size[1]):
                for x in range(0,im.size[0]):
                    lum = 255-im.getpixel((x,y))
                    row = bisect(zonebounds, lum)
                    possibles = grayscale[row]
                    str = str + possibles[random.randint(0,len(possibles)-1)]
                str = str + "\n"
            self.et_asciiArea.SetValue(str)
        except RuntimeError:
            self.NoImageDialog()
        except ValueError:
            self.InvalidInputDialog()
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
            try:
                self.tb_grayscale.SetLabel("Off")
                self.ImagePreview = wx.BitmapFromImage(self.ImageSource)
                self.bitmap_button.SetBitmapLabel(self.ImagePreview)
            except Exception:
                pass

# end of class AsciiArtFrame

if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame = AsciiArtFrame(None, -1, "")
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()
