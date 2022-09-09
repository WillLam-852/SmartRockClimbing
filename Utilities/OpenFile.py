import os

def open_file(filename):
    dst = "~/RockClimbing/Data"
    full_dst = os.path.expanduser(dst)
    return f"{full_dst}/{filename}"
