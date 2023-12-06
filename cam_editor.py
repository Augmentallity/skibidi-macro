import menu
import win32gui
import win32ui
import win32con
import pyautogui
import time
import os
import numpy as np
from PIL import Image, ImageGrab
import threading
import pynput

SIMILARITY = 0.3


def compare_to(macro_id: str, cam_name: str) -> float:
    hwnd = win32gui.FindWindow(None, "Roblox")
    if hwnd == 0:
        return
    bbox = win32gui.GetWindowRect(hwnd)
    bmp_file = ImageGrab.grab(bbox)
    a = np.array(bmp_file)
    b = np.array(
        Image.open(f"{os.getcwd()}\\macros\\{macro_id}\\{cam_name}\\angle.bmp")
    )
    return np.sum(a == b) / a.size


def camera_edit(macro_id: str, cam_name: str | None = None):
    similarity: float = 0.0
    try:
        bmp_file = Image.open()
    except:
        bmp_file = None
    listening = True
    screenshot_taken = False

    def similarity_listener():
        nonlocal similarity
        while listening:
            hwnd = win32gui.FindWindow(None, "Roblox")
            if hwnd == 0 or bmp_file == None:
                similarity = 0
                continue
            bbox = win32gui.GetWindowRect(hwnd)
            img = ImageGrab.grab(bbox)
            a = np.array(bmp_file)
            b = np.array(img)
            similarity = np.sum(a == b) / a.size

    def capture():
        nonlocal bmp_file
        if cam_name == None:
            return
        hwnd = win32gui.FindWindow(None, "Roblox")
        if hwnd == 0:
            return
        bbox = win32gui.GetWindowRect(hwnd)

        pyautogui.press("alt")
        win32gui.SetForegroundWindow(hwnd)
        bmp_file = ImageGrab.grab(bbox)
        bmp_file.save(f"{os.getcwd()}\\macros\\{macro_id}\\{cam_name}\\angle.bmp")

        def notify():
            nonlocal screenshot_taken
            screenshot_taken = True
            time.sleep(1)
            screenshot_taken = False

        t2 = threading.Thread(target=notify)
        t2.start()

    def screenshot_key_listener(key: pynput.keyboard.Key):
        if key == pynput.keyboard.Key.backspace:
            capture()

    t = threading.Thread(target=similarity_listener)
    keyboard_listener = pynput.keyboard.Listener(on_press=screenshot_key_listener)
    t.start()
    keyboard_listener.start()

    def change_name():
        nonlocal cam_name
        val = input("Set Camera Angle Name: ").strip()
        if len(val) > 0:
            if os.path.exists(f"{os.getcwd()}\\macros\\{macro_id}\\{cam_name}"):
                os.rename(
                    f"{os.getcwd()}\\macros\\{macro_id}\\{cam_name}",
                    f"{os.getcwd()}\\macros\\{macro_id}\\{val}",
                )
            else:
                os.makedirs(f"{os.getcwd()}\\macros\\{macro_id}\\{val}")
            cam_name = val

    def compare():
        if similarity >= SIMILARITY:
            return "Camera angle DETECTED"
        else:
            return "Camera angle not detected"

    def view_screenshot():
        if bmp_file != None:
            return [menu.MenuItem(f"View screenshot", lambda: bmp_file.show())]
        return []

    m = menu.Menu("Add Camera Angle")
    m.header(
        "Maps have different camera angles. To differentiate camera angles,\nthe program needs to capture a screenshot of roblox."
    )
    m.text("")
    m.text(compare)
    m.text("")
    m.item(menu.MenuItem(lambda: f"Camera Angle Name): {cam_name}", change_name))
    m.item(menu.MenuItem("Screenshot Roblox (press BACKSPACE)", capture))
    m.item(view_screenshot)
    m.item(menu.MenuItem("Back", lambda: menu.stack.pop()))
    m.text("")
    m.text(lambda: "Screenshot taken!" if screenshot_taken else "")
    m.show()
    listening = False
    keyboard_listener.stop()
