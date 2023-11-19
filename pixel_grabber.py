import keyboard
import pyautogui
import os

if __name__ == "__main__":
    while not keyboard.is_pressed("escape"):
        if keyboard.is_pressed("shift"):
            os.system("cls")
            x, y = pyautogui.position()
            print(f"({x}, {y})")
