from tkinter import *

from Utilities.Constants import *

class NumberedButton(Button):

    def __init__(self, *arg, number, **kwargs):
        Button.__init__(self, *arg, **kwargs)

        self.number_label = Label(self, font=(FONT_FAMILY, LABEL_FONT_SIZE), text=number)
        self.number_label.place(x=0, y=0)

        self.bind('<Enter>', self._on_release)
        self.bind('<Button-1>', self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind('<Leave>', self._on_release)


    def gui_set(self, text, command, bg):
        self.config(text=text, command=command, bg=bg)
        self.number_label.config(bg=bg)
        self.bg = bg


    def _on_release(self, _):
        for widget in (self, self.number_label):
            widget.config(bg=self.bg)


    def _on_press(self, _):
        for widget in (self, self.number_label):
            widget.config(bg=self.cget('highlightbackground'))