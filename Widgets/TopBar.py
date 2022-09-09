import i18n
import PIL.Image, PIL.ImageTk
from tkinter import *

from Utilities.Constants import *
from Utilities.OpenFile import open_file

class TopBar(Frame):

    def __init__(self, *arg, **kwargs):
        Frame.__init__(self, *arg, **kwargs)

        self.logo_image = PIL.Image.open(open_file(f"{IMAGE_FILES_LOCATION}Logo.png")).resize((TOP_BAR_HEIGHT, TOP_BAR_HEIGHT), PIL.Image.ANTIALIAS)
        self.logo_image = PIL.ImageTk.PhotoImage(self.logo_image)
        self.logo_label = Label(self, image=self.logo_image)

        self.title_label = Label(self, font=(FONT_FAMILY, TITLE_FONT_SIZE), fg='black', bg=THEME_COLOR_BLUE)

        self.gui_set()


    def change_title(self, title):
        if title == i18n.t('t.home'):
            self.title_label.config(text="")
            self.logo_label.place_forget()
        else:
            self.title_label.config(text=title)
            self.logo_label.place(width=TOP_BAR_HEIGHT, height=TOP_BAR_HEIGHT)


    # GUI Methods

    def gui_set(self):
        self.title_label.place(relx=0.5, rely=0.5, anchor=CENTER)