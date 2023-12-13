import shutil
from typing import Callable
from uuid import uuid4
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
import utils

SIMILARITY = 0.3

memoized = {}


def compare_to(macro_id: str, cam_name: str) -> float:
    global memoized
    hwnd = win32gui.FindWindow(None, "Roblox")
    if hwnd == 0:
        return
    bbox = win32gui.GetWindowRect(hwnd)
    bmp_file = ImageGrab.grab(bbox)
    a = np.array(bmp_file)
    if cam_name not in memoized:
        b = np.array(
            Image.open(f"{os.getcwd()}\\macros\\{macro_id}\\{cam_name}\\angle.bmp")
        )
        memoized[cam_name] = b
    else:
        b = memoized[cam_name]
    return np.sum(a == b) / a.size


def camera_edit(macro_id: str, cam_name: str | None = None):
    similarity: float = 0.0
    try:
        bmp_file = Image.open(
            f"{os.getcwd()}\\macros\\{macro_id}\\{cam_name}\\angle.bmp"
        )
    except:
        bmp_file = None
    listening = True
    screenshot_taken = False
    user_prompted = False
    lock_screenshot = bool(bmp_file)
    wave = 1

    def similarity_listener(listening: Callable[[], bool]):
        nonlocal similarity
        nonlocal wave
        while listening():
            hwnd = win32gui.FindWindow(None, "Roblox")
            if hwnd == 0 or bmp_file == None:
                similarity = 0
                wave = 1
                continue
            bbox = win32gui.GetWindowRect(hwnd)
            img = ImageGrab.grab(bbox)
            a = np.array(bmp_file)
            b = np.array(img)
            similarity = np.sum(a == b) / a.size

    def capture():
        nonlocal bmp_file
        if cam_name == None or user_prompted or lock_screenshot:
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

    def automatic_tinytask_move(listening: Callable[[], bool]):
        nonlocal wave
        while listening():
            pos, color = utils.get_config_prop(utils.WAVE_COMPLETED_LABEL)
            x, y = pos
            matches = pyautogui.pixelMatchesColor(x, y, color)
            if matches:
                wave += 1
                time.sleep(5)

            if cam_name == None or not os.path.exists(
                f"{os.getcwd()}\\macros\\{macro_id}\\{cam_name}"
            ):
                continue

            tinytasks = [
                x
                for x in os.listdir(f"{os.getcwd()}\\macros\\{macro_id}\\{cam_name}")
                if x.endswith(".exe")
            ]
            for tinytask in tinytasks:
                exec_path = f"{os.getcwd()}\\macros\\{macro_id}\\{cam_name}\\{tinytask}"
                wave_folder_path = (
                    f"{os.getcwd()}\\macros\\{macro_id}\\{cam_name}\\{wave}"
                )
                file_name = tinytask[:-4]

                if file_name.isnumeric():
                    custom_wave_path = (
                        f"{os.getcwd()}\\macros\\{macro_id}\\{cam_name}\\{file_name}"
                    )
                    if not os.path.exists(custom_wave_path):
                        os.mkdir(custom_wave_path)
                    shutil.move(exec_path, f"{custom_wave_path}\\{uuid4()}.exe")

                else:
                    if not os.path.exists(wave_folder_path) or not os.path.isdir(
                        wave_folder_path
                    ):
                        os.mkdir(wave_folder_path)
                    shutil.move(exec_path, f"{wave_folder_path}\\{uuid4()}.exe")

    t1 = threading.Thread(target=similarity_listener, args=(lambda: listening,))
    t2 = threading.Thread(target=automatic_tinytask_move, args=(lambda: listening,))
    keyboard_listener = pynput.keyboard.Listener(on_press=screenshot_key_listener)
    t1.start()
    t2.start()
    keyboard_listener.start()

    def change_name():
        nonlocal cam_name
        nonlocal user_prompted
        user_prompted = True
        val = input("Set Camera Angle Name: ").strip()
        user_prompted = False
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
            return f"Camera angle DETECTED\nCurrent Threshold:\t{similarity}\nRequired Threshold for similarity:\t{SIMILARITY}"
        else:
            return f"Camera angle not detected\nCurrent Threshold: {similarity}\nRequired Threshold for similarity:\t{SIMILARITY}"

    def view_screenshot():
        if bmp_file != None:
            return [menu.MenuItem(f"View screenshot", lambda: bmp_file.show())]
        return []

    def toggle_lock():
        nonlocal lock_screenshot
        lock_screenshot = not lock_screenshot

    def delete_cam_angle():
        nonlocal user_prompted
        user_prompted = True
        confirmation = input("Type DELETE to confirm: ").strip()
        user_prompted = False
        if confirmation == "DELETE":
            menu.stack.pop()
            try:
                shutil.rmtree(f"{os.getcwd()}\\macros\\{macro_id}\\{cam_name}")
            except:
                pass

    m = menu.Menu("Add Camera Angle")
    m.header(
        "Maps have different camera angles. To differentiate camera angles,\nthe program needs to capture a screenshot of roblox.\n\nTo add macros for waves, record a tinytask and compile the\nmacro into the folder that matches the camera angle name.\n\n(Note: the compiled tinytask will automatically be moved to corresponding wave folders)"
    )
    m.text(compare)
    m.text("")
    m.item(menu.MenuItem(lambda: f"Camera Angle Name: {cam_name}", change_name))
    m.item(
        lambda: (
            [menu.MenuItem("Screenshot Roblox (press BACKSPACE)", capture)]
            if (cam_name and not lock_screenshot) or not cam_name
            else []
        )
    )
    m.item(
        lambda: (
            [
                menu.MenuItem(
                    lambda: f"{'Unlock' if lock_screenshot else 'Lock'} screenshot",
                    toggle_lock,
                )
            ]
            if bmp_file != None
            else []
        )
    )
    m.item(view_screenshot)
    m.item(
        lambda: [
            menu.MenuItem(
                "Open directory",
                lambda: os.system(
                    f'explorer.exe "{os.getcwd()}\\macros\\{macro_id}\\{cam_name}'
                ),
            )
        ]
        if cam_name
        else []
    )
    m.item(
        lambda: (
            [menu.MenuItem("Delete Camera Angle", delete_cam_angle)] if cam_name else []
        )
    )
    m.item(menu.MenuItem("Back", lambda: menu.stack.pop()))
    m.text("")
    m.text(lambda: "Screenshot taken!" if screenshot_taken else "")
    m.text("Waves containing macros:")
    m.text(
        lambda: (
            "\t\n".join(
                [
                    x
                    for x in os.listdir(
                        f"{os.getcwd()}\\macros\\{macro_id}\\{cam_name}"
                    )
                    if os.path.isdir(
                        f"{os.getcwd()}\\macros\\{macro_id}\\{cam_name}\\{x}"
                    )
                ]
            )
            if cam_name != None
            and os.path.exists(f"{os.getcwd()}\\macros\\{macro_id}\\{cam_name}")
            else ""
        )
    )
    m.show()
    listening = False
    keyboard_listener.stop()
