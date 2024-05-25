import pyscreenshot as ImageGrab
import sqlite3
import subprocess
import os

def screenshot():
    img = ImageGrab.grab()
    # make dir if not exist
    if not os.path.exists("./Screenshots"):
        os.makedirs("./Screenshots")
    img.save("./Screenshots/screenshot.png")
    print("Screenshot taken")


def save_to_db():
    conn = sqlite3.connect('recall.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS screenshots 
                 (id INTEGER PRIMARY KEY, name TEXT, path TEXT)''')
    conn.commit()
    conn.close()
    print("Database created")


screenshot()
window_id = str(subprocess.check_output(['kdotool', 'getactivewindow']))[2:-3]
window_name = subprocess.check_output(['kdotool', 'getwindowname', window_id])

