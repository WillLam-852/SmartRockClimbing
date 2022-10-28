import os

def open_file(filename):
    dst = "~/SmartRockClimbing/Data"
    full_dst = os.path.expanduser(dst)
    return f"{full_dst}/{filename}"
