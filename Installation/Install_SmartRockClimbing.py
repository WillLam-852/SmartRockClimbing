import os, sys, shutil
import ctypes

def copytree(src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d)
        else:
            if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                shutil.copy2(s, d)

if hasattr(sys, "_MEIPASS"):
    src = os.path.join(sys._MEIPASS, "Data")
else:
    src = "./Data"
dst = os.path.expanduser("~/RockClimbing/Data")
copytree(src, dst)

MessageBox = ctypes.windll.user32.MessageBoxW
if os.path.exists(os.path.expanduser("~/RockClimbing/Data")):
    MessageBox(None, 'Successful', 'Install RockClimbing', 0)
else:
    MessageBox(None, 'Unsuccessful', 'Install RockClimbing', 0)
