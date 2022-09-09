from tkinter import *
from Utilities.Constants import *
from Widgets.ControlBarButton import ControlBarButton
from Widgets.NumberedButton import NumberedButton

class ControlBar(Frame):

    def __init__(self, *arg, **kwargs):
        Frame.__init__(self, *arg, **kwargs)

        self.button0 = NumberedButton(self, number=0, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE))
        self.button1 = NumberedButton(self, number=1, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE))
        self.button2 = NumberedButton(self, number=2, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE))
        self.button3 = NumberedButton(self, number=3, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE))
        self.button4 = NumberedButton(self, number=4, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE))
        self.button5 = NumberedButton(self, number=5, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE))
        self.button6 = NumberedButton(self, number=6, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE))
        self.button7 = NumberedButton(self, number=7, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE))
        self.button8 = NumberedButton(self, number=8, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE))
        self.button9 = NumberedButton(self, number=9, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE))


    def invoke_button(self, button, is_reverse_keypad: bool):
        if not is_reverse_keypad:
            if button == '0' and self.button0['command'] != '':
                self.button0.invoke()
            if button == '9' and self.button1['command'] != '':
                self.button1.invoke()
            if button == '8' and self.button2['command'] != '':
                self.button2.invoke()
            if button == '7' and self.button3['command'] != '':
                self.button3.invoke()
            if button == '6' and self.button4['command'] != '':
                self.button4.invoke()
            if button == '5' and self.button5['command'] != '':
                self.button5.invoke()
            if button == '4' and self.button6['command'] != '':
                self.button6.invoke()
            if button == '3' and self.button7['command'] != '':
                self.button7.invoke()
            if button == '2' and self.button8['command'] != '':
                self.button8.invoke()
            if button == '1' and self.button9['command'] != '':
                self.button9.invoke()
        else:
            if button == '1' and self.button0['command'] != '':
                self.button0.invoke()
            if button == '2' and self.button1['command'] != '':
                self.button1.invoke()
            if button == '3' and self.button2['command'] != '':
                self.button2.invoke()
            if button == '4' and self.button3['command'] != '':
                self.button3.invoke()
            if button == '5' and self.button4['command'] != '':
                self.button4.invoke()
            if button == '6' and self.button5['command'] != '':
                self.button5.invoke()
            if button == '7' and self.button6['command'] != '':
                self.button6.invoke()
            if button == '8' and self.button7['command'] != '':
                self.button7.invoke()
            if button == '9' and self.button8['command'] != '':
                self.button8.invoke()
            if button == '0' and self.button9['command'] != '':
                self.button9.invoke()


    def change_buttons(self, buttons: dict[int, ControlBarButton]):
        self.gui_clear()
        if 0 in buttons:
            self.button0.gui_set(text=buttons[0].text, command=buttons[0].command, bg=buttons[0].bg)
            self.button0.place(relwidth=1.0, height=CONTROL_BAR_BUTTON_HEIGHT)
        if 1 in buttons:
            self.button1.gui_set(text=buttons[1].text, command=buttons[1].command, bg=buttons[1].bg)
            self.button1.place(y=CONTROL_BAR_BUTTON_HEIGHT, relwidth=1.0, height=CONTROL_BAR_BUTTON_HEIGHT)
        if 2 in buttons:
            self.button2.gui_set(text=buttons[2].text, command=buttons[2].command, bg=buttons[2].bg)
            self.button2.place(y=CONTROL_BAR_BUTTON_HEIGHT*2, relwidth=1.0, height=CONTROL_BAR_BUTTON_HEIGHT)
        if 3 in buttons:
            self.button3.gui_set(text=buttons[3].text, command=buttons[3].command, bg=buttons[3].bg)
            self.button3.place(y=CONTROL_BAR_BUTTON_HEIGHT*3, relwidth=1.0, height=CONTROL_BAR_BUTTON_HEIGHT)
        if 4 in buttons:
            self.button4.gui_set(text=buttons[4].text, command=buttons[4].command, bg=buttons[4].bg)
            self.button4.place(y=CONTROL_BAR_BUTTON_HEIGHT*4, relwidth=1.0, height=CONTROL_BAR_BUTTON_HEIGHT)
        if 5 in buttons:
            self.button5.gui_set(text=buttons[5].text, command=buttons[5].command, bg=buttons[5].bg)
            self.button5.place(y=CONTROL_BAR_BUTTON_HEIGHT*5, relwidth=1.0, height=CONTROL_BAR_BUTTON_HEIGHT)
        if 6 in buttons:
            self.button6.gui_set(text=buttons[6].text, command=buttons[6].command, bg=buttons[6].bg)
            self.button6.place(y=CONTROL_BAR_BUTTON_HEIGHT*6, relwidth=1.0, height=CONTROL_BAR_BUTTON_HEIGHT)
        if 7 in buttons:
            self.button7.gui_set(text=buttons[7].text, command=buttons[7].command, bg=buttons[7].bg)
            self.button7.place(y=CONTROL_BAR_BUTTON_HEIGHT*7, relwidth=1.0, height=CONTROL_BAR_BUTTON_HEIGHT)
        if 8 in buttons:
            self.button8.gui_set(text=buttons[8].text, command=buttons[8].command, bg=buttons[8].bg)
            self.button8.place(y=CONTROL_BAR_BUTTON_HEIGHT*8, relwidth=1.0, height=CONTROL_BAR_BUTTON_HEIGHT)
        if 9 in buttons:
            self.button9.gui_set(text=buttons[9].text, command=buttons[9].command, bg=buttons[9].bg)
            self.button9.place(y=CONTROL_BAR_BUTTON_HEIGHT*9, relwidth=1.0, height=CONTROL_BAR_BUTTON_HEIGHT)


    # GUI Methods

    def gui_clear(self):
        self.button0.config(text=None, command=None, bg=THEME_COLOR_YELLOW)
        self.button0.place_forget()
        self.button1.config(text=None, command=None, bg=THEME_COLOR_YELLOW)
        self.button1.place_forget()
        self.button2.config(text=None, command=None, bg=THEME_COLOR_YELLOW)
        self.button2.place_forget()
        self.button3.config(text=None, command=None, bg=THEME_COLOR_YELLOW)
        self.button3.place_forget()
        self.button4.config(text=None, command=None, bg=THEME_COLOR_YELLOW)
        self.button4.place_forget()
        self.button5.config(text=None, command=None, bg=THEME_COLOR_YELLOW)
        self.button5.place_forget()
        self.button6.config(text=None, command=None, bg=THEME_COLOR_YELLOW)
        self.button6.place_forget()
        self.button7.config(text=None, command=None, bg=THEME_COLOR_YELLOW)
        self.button7.place_forget()
        self.button8.config(text=None, command=None, bg=THEME_COLOR_YELLOW)
        self.button8.place_forget()
        self.button9.config(text=None, command=None, bg=THEME_COLOR_YELLOW)
        self.button9.place_forget()