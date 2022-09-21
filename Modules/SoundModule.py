import ctypes
import i18n
import playsound
from Utilities.Constants import SOUND_FILES_LOCATION
from Utilities.OpenFile import open_file

class SoundModule:

    def test_sound(self):
        self.play_sound("test_sound.wav", isAlert=True)

    def countdown(self):
        self.play_sound("countdown.wav")

    def good_point(self):
        self.play_sound("good_point.wav")

    def bad_point(self):
        self.play_sound("bad_point.wav")

    def danger_alert(self):
        self.play_sound("danger_alert.wav")

    def play_sound(self, filename, isAlert=False):
        try:
            playsound.playsound(open_file(f"{SOUND_FILES_LOCATION}{filename}"), False)
        except Exception as exceptionMessage:
            if isAlert:
                ctypes.windll.user32.MessageBoxW(0, str(exceptionMessage), i18n.t('t.alert'), 0)
            else:
                print(exceptionMessage)
