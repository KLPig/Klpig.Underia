import os
from tkinter import messagebox

DEBUG = False

if not DEBUG:
    pt = '/Library/Underia'
else:
    pt = '.'

print("Discovering path...")
d = os.listdir(pt)
if 'assets' not in d:
    print('Assets not found.')
    messagebox.showerror('Error', 'Assets not found. Please reinstall the package.')
    exit()


def get_path(filename=None):
    global pt
    if filename:
        return os.path.join(pt, filename)
    else:
        return pt


save_path = os.path.join(os.environ.get('HOME'), '.underia')
if not os.path.exists(save_path):
    os.makedirs(save_path)


def get_save_path(filename):
    global save_path
    print(save_path, filename)
    return os.path.join(save_path, filename)
