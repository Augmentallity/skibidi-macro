from typing import Callable
import win32gui
import pynput
import time
import os

HWND = win32gui.GetForegroundWindow()
DELAY = 0.125


def is_focused() -> bool:
    return HWND == win32gui.GetForegroundWindow()


class MenuItem:
    def __init__(
        self, name: Callable[[], str] | str, on_press: Callable[[], None]
    ) -> None:
        self._name = name
        self._on_press = on_press


stack = []


class Menu:
    def __init__(self, name: str) -> None:
        self._items: list[MenuItem] = []
        self._name = name
        self._idx: int = 0
        self._prev_idx: None | int = None
        self._description: str = ""
        self._prev_pressed: pynput.keyboard.Key | pynput.keyboard.KeyCode | None = None
        self._pressed: pynput.keyboard.Key | pynput.keyboard.KeyCode | None = None

    def item(self, menu_item: MenuItem):
        self._items.append(menu_item)
        return self

    def header(self, description: str):
        self._description = description

    def set_index(self, idx: int):
        self._prev_idx = self._idx
        self._idx = idx

    def on_press_handler(self, key: pynput.keyboard.Key | pynput.keyboard.KeyCode):
        global stack
        if stack[-1] == self:
            self._pressed = key

    def on_release_handler(self, key: pynput.keyboard.Key | pynput.keyboard.KeyCode):
        global stack
        if stack[-1] == self:
            self._prev_pressed = key
            self._pressed = None

    def show(self):
        global stack
        stack.append(self)
        prev_key_pressed = 0
        kb_listener = pynput.keyboard.Listener(
            on_press=self.on_press_handler, on_release=self.on_release_handler
        )
        kb_listener.start()

        while True:
            os.system("cls")
            items: list[str] = []
            for i in range(len(self._items)):
                items.append(
                    f"({'*' if i == self._idx else ' '}) {self._items[i]._name() if callable(self._items[i]._name) else self._items[i]._name}"
                )

            print(
                "\n".join(
                    [
                        " / ".join([x._name for x in stack]),
                        "",
                        self._description,
                        "",
                        *items,
                        "",
                        "Press SPACE to interact, ESC to go back. Navigate using ↑ and ↓ keys",
                        "",
                    ]
                )
            )

            if is_focused():
                match self._pressed:
                    case pynput.keyboard.Key.down:
                        if self._prev_pressed != pynput.keyboard.Key.down:
                            self._prev_pressed = pynput.keyboard.Key.down
                            self.set_index(min(self._idx + 1, len(self._items) - 1))
                            prev_key_pressed = time.time()
                        elif time.time() - prev_key_pressed >= DELAY:
                            self.set_index(min(self._idx + 1, len(self._items) - 1))
                            prev_key_pressed = time.time()
                    case pynput.keyboard.Key.up:
                        if self._prev_pressed != pynput.keyboard.Key.up:
                            self._prev_pressed = pynput.keyboard.Key.up
                            self.set_index(max(self._idx - 1, 0))
                            prev_key_pressed = time.time()
                        elif time.time() - prev_key_pressed >= DELAY:
                            self.set_index(max(self._idx - 1, 0))
                            prev_key_pressed = time.time()

                    case pynput.keyboard.Key.esc:
                        if stack[-1] == self:
                            stack.pop()
                            return
                    case pynput.keyboard.Key.space:
                        if stack[-1] == self:
                            self._prev_pressed = None
                            self._pressed = None
                            self._items[self._idx]._on_press()
            time.sleep(1 / 30)
