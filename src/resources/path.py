import os

print("Discovering path...")
print("Containing: ", os.listdir())
print("Current path: ", os.getcwd())
try:
    os.MEIPASS
    print("Running in PyInstaller bundle as meipass: ", os.MEIPASS)
except AttributeError:
    print("Running regularly in: ", os.path.abspath("."))

def get_path(filename=None):
    try:
        pt = os.MEIPASS
    except AttributeError:
        pt = os.path.abspath(".")
    if filename:
        return os.path.join(pt, filename)
    else:
        return pt
