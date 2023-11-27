import menu
import utils
import pynput
import pyautogui


def create_listener(listener_name: str, listener_prop: str, listener_description: str):
    pos, color = utils.get_config_prop(listener_prop)
    pos_copy = (pos[0], pos[1])
    color_copy = (color[0], color[1], color[2])
    m = menu.Menu(listener_name)

    def on_press(key: pynput.keyboard.Key):
        nonlocal pos_copy
        nonlocal color_copy
        if key == pynput.keyboard.Key.shift_l:
            p = pyautogui.position()
            pos_copy = (p[0], p[1])
            color_copy = pyautogui.pixel(pos_copy[0], pos_copy[1])

    listener = pynput.keyboard.Listener(on_press)
    listener.start()
    m.header(listener_description)

    def save_changes():
        utils.set_config_prop(listener_prop, pos_copy, color_copy)
        menu.stack.pop()

    m.text(lambda: f"Current pixel to detect : {pos_copy} - rgb{color_copy}")
    m.item(menu.MenuItem("Save Changes", save_changes))
    m.item(menu.MenuItem("Back", lambda: menu.stack.pop()))
    m.show()
    listener.stop()


EVENT_LISTENERS = [
    "Disconnected Listener",
    "Game Lost Listener",
    "Wave Completed Listener",
    "Wave Start Button Listener",
    "Map Menu Listener",
    "Start Map Listener",
]

EVENT_LISTENER_CALLBACK = {
    EVENT_LISTENERS[0]: lambda: create_listener(
        EVENT_LISTENERS[0],
        utils.DISCONNECTED_DIALOG_BOX,
        "This event listener detects when the user has been disconnected\nby roblox. For example, when your internet connection\nis unstable, this event listener can detect that.",
    ),
    EVENT_LISTENERS[1]: lambda: create_listener(
        EVENT_LISTENERS[1], utils.DEFEAT_LABEL, "Defeat label"
    ),
    EVENT_LISTENERS[2]: lambda: create_listener(
        EVENT_LISTENERS[2],
        utils.WAVE_COMPLETED_LABEL,
        "This event listener detects when a wave has been completed in-game.\nThis must be set so that macros for a corresponding wave can be executed.",
    ),
    EVENT_LISTENERS[3]: lambda: create_listener(
        EVENT_LISTENERS[3],
        utils.START_WAVE_BTN,
        "This event listener detects when the user can start the first wave in a game.\nUsually, this should be set to the start button when the user loads into the game\nand is prompted to start the wave early.\n\nThis must be set because this is a way to tell if the map has been loaded completely.",
    ),
    EVENT_LISTENERS[4]: lambda: create_listener(
        EVENT_LISTENERS[4],
        utils.CANCEL_MAP_BTN,
        "This event listener detects when the map menu selector is opened. This must\nbe set so the program knows when the map menu is opened and is the only way to\nprogrammatically select a map.\n\nYou can use the Cancel button as an indicator to show the presence\nof the map menu selector.",
    ),
    EVENT_LISTENERS[5]: lambda: create_listener(
        EVENT_LISTENERS[5],
        utils.START_MAP_BTN,
        "This event listener when the user can start the map that has been selected.\nThis must be set so that the program can automatically start the chosen map.",
    ),
}


def main():
    m = menu.Menu("Event Listener Macros")
    m.header(
        "Event Listener Macros listen for events and respond to them when a corresponding event is detected via through pixel shown on screen.\nConfigure these to match with your system as these are necessary for your macros to work properly."
    )
    for i in range(len(EVENT_LISTENERS)):
        m.item(
            menu.MenuItem(
                EVENT_LISTENERS[i], EVENT_LISTENER_CALLBACK[EVENT_LISTENERS[i]]
            )
        )
    m.show()
