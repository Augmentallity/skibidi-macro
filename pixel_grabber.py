import keyboard
import pyautogui
import win32gui
import win32con
import os

from win32con import (
    IDC_APPSTARTING,
    IDC_ARROW,
    IDC_CROSS,
    IDC_HAND,
    IDC_HELP,
    IDC_IBEAM,
    IDC_ICON,
    IDC_NO,
    IDC_SIZE,
    IDC_SIZEALL,
    IDC_SIZENESW,
    IDC_SIZENS,
    IDC_SIZENWSE,
    IDC_SIZEWE,
    IDC_UPARROW,
    IDC_WAIT,
)


def get_current_cursor():
    curr_cursor_handle = win32gui.GetCursorInfo()[1]
    return Cursor.from_handle(curr_cursor_handle)


class Cursor(object):
    @classmethod
    def from_handle(cls, handle):
        for cursor in DEFAULT_CURSORS:
            if cursor[1].handle == handle:
                return cursor[0]  # DEFAULT_CURSORS.index(cursor) , Cursor.__init__
        return cls(handle=handle)

    def __init__(self, cursor_type=None, handle=None):
        if handle is None:
            handle = win32gui.LoadCursor(0, cursor_type)
        self.type = cursor_type
        self.handle = handle


DEFAULT_CURSORS = (
    ("APPSTARTING", Cursor(IDC_APPSTARTING)),
    ("ARROW", Cursor(IDC_ARROW)),
    ("CROSS", Cursor(IDC_CROSS)),
    ("HAND", Cursor(IDC_HAND)),
    ("HELP", Cursor(IDC_HELP)),
    ("IBEAM", Cursor(IDC_IBEAM)),
    ("ICON", Cursor(IDC_ICON)),
    ("NO", Cursor(IDC_NO)),
    ("SIZE", Cursor(IDC_SIZE)),
    ("SIZEALL", Cursor(IDC_SIZEALL)),
    ("SIZENESW", Cursor(IDC_SIZENESW)),
    ("SIZENS", Cursor(IDC_SIZENS)),
    ("SIZENWSE", Cursor(IDC_SIZENWSE)),
    ("SIZEWE", Cursor(IDC_SIZEWE)),
    ("UPARROW", Cursor(IDC_UPARROW)),
    ("WAIT", Cursor(IDC_WAIT)),
)


if __name__ == "__main__":
    while not keyboard.is_pressed("escape"):
        if keyboard.is_pressed("shift"):
            os.system("cls")
            # hwnd = win32gui.FindWindow(None, "microsoft")
            print(win32gui.GetForegroundWindow())
            # x, y = pyautogui.position()
            # print(f"({x}, {y})")
