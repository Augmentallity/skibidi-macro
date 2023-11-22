import keyboard
import pyautogui
import os
import utils
import time
import win32process
import win32gui
import menu

DELAY = 0.128

OPTIONS = [
    "Set LOBBY PLAY BUTTON",
    "Set CANCEL MAP BUTTON",
    "Set START MAP BUTTON",
    "Set WAVE START BUTTON",
    "Set WAVE COMPLETED LABEL",
    "Set DEFEAT LABEL",
    "Set HP BAR ZERO",
    "Set DISCONNECTED DIALOG BOX",
    "Set NORMAL CAMERA ANGLE DETECTION",
    "Configure EXITING MODE",
]

HWND = win32gui.GetForegroundWindow()


def is_focused() -> bool:
    return HWND == win32gui.GetForegroundWindow()


def open_editor(selected_index: int):
    match selected_index:
        case 0:
            edit(
                "LOBBY PLAY BUTTON",
                "The program tracks the existence of the lobby play button as a way to detect if your Roblox has fully loaded in.",
                utils.LOBBY_PLAY_BTN_PROP,
            )
        case 1:
            edit(
                "CANCEL MAP BUTTON",
                "The program tracks the existence of the cancel button as a way to detect if the map selector is opened.",
                utils.CANCEL_MAP_BTN,
            )
        case 2:
            edit(
                "START MAP BUTTON",
                "After selecting a map, the button to start the map will show.\nThe program must detect the presence of this button in order to load into the map (a.k.a press the START button).",
                utils.START_MAP_BTN,
            )
        case 3:
            edit(
                "START WAVE BUTTON",
                "After you load into the map, the button to start the wave will show.\nThe program needs to know when it is on your screen to click it.",
                utils.START_WAVE_BTN,
            )
        case 4:
            edit(
                "WAVE COMPLETED LABEL",
                "During a game, the program needs to know when a wave has completed.\nUsually, this is with the appearance of WAVE COMPLETED! label showing at the end of a wave.\nThis is necessary to execute tinytask macros configured for specific waves.",
                utils.WAVE_COMPLETED_LABEL,
            )
        case 5:
            edit(
                "DEFEAT LABEL",
                "During a game, there is a chance your macros do not work for a camera angle you configured it for.\nIf that is the case, there is a chance you will lose. The program needs\nto detect a loss in order to restart a run immediately.",
                utils.DEFEAT_LABEL,
            )
        case 6:
            edit(
                "HP BAR ZERO",
                "Same as DEFEAT LABEL. To prevent any false positives in the case DEFEAT LABEL gets detected, this must be set to the pixels in the HP bar that have been grayed out for losing HP.\nIt is fine to set this to any pixel within the HP bar that is gray and below 100% HP.",
                utils.HP_BAR_ZERO,
            )
        case 7:
            edit(
                "DISCONNECTED DIALOG BOX",
                "In the event Roblox disconnects your client due to lag, afk timeout, etc., detecting the presence of the disconnected label allows the program to automatically retry connections until you load back in.",
                utils.DISCONNECTED_DIALOG_BOX,
            )
        case 8:
            edit(
                "NORMAL CAMERA ANGLE DETECTION",
                "Marine's ford has two camera angles. One of it is a camera angle almost similar to a bird-eye's view, while the other is a normal camera angle.\nCreating a macro and then for it to not work because a change in the camera angle can be frustrating.\nBy detecting the starting camera angle, the program can execute macros specific to that camera angle.",
                utils.NORMAL_CAMERA_ANGLE_INDICATOR,
            )
        case 9:
            configure_exit_mode()
        case _:
            raise Exception(f"Invalid index {selected_index}")


def configure_exit_mode():
    helper = "Editor: Configure how the program should exit/close Roblox"
    how_to_use = "\nThere are two ways for how the program should exit:\n\t- Programatically (RECOMMENDED)\n\t\tThe program will automatically close/exit Roblox through Windows API\n\t- User-defined macro\n\t\tThe program will call the user's macro to exit/close the game"
    os.system("cls")
    config = utils.read_config()
    print(helper)
    print(how_to_use)
    while not keyboard.is_pressed("escape") or not is_focused():
        pass


def edit(name: str, description: str, config_property: str):
    helper = f"{name} Editor: To confirm changes, press BACKSPACE. To exit, press ESC."
    how_to_use = f"\nWhile holding LEFT SHIFT, place your cursor at the {name} to record its position.\n\n{description}"
    pixel = None
    color = None
    os.system("cls")
    config = utils.read_config()
    print(helper)
    print(how_to_use)
    print("\nSAVED (in animeadventures.config):")
    print(f"\tpos: {config[f'{config_property}_pos']}")
    print(f"\tcolor: {config[f'{config_property}_color']}")
    while not keyboard.is_pressed("escape") or not is_focused():
        if keyboard.is_pressed("left_shift"):
            config = utils.read_config()
            os.system("cls")
            (x, y) = pyautogui.position()
            parse_x = int(x)
            parse_y = int(y)
            pixel = (parse_x, parse_y)
            color = pyautogui.pixel(parse_x, parse_y)
            log = [
                helper,
                how_to_use,
                "",
                "SAVED (in animeadventures.config):",
                f"\tpos: {config[f'{config_property}_pos']}",
                f"\tcolor: {config[f'{config_property}_color']}",
                "",
                "CURRENT:",
                f"\tpos: ({parse_x}, {parse_y})",
                f"\tcolor: ({color[0]}, {color[1]}, {color[2]})",
                "",
            ]
            result = "\n".join(log)
            print(result)
        if keyboard.is_pressed("backspace"):
            if pixel == None or color == None:
                break
            config = utils.read_config()
            config[f"{config_property}_pos"] = pixel
            config[f"{config_property}_color"] = color
            utils.save_config(config)
            print(
                f"The {name} location has been saved to animeadventures.config",
                end="\r",
            )
    print("\nExiting...")
    time.sleep(0.1)


def main():
    selected_index = 0
    pressed_key_time_start = 0
    pressed_key_time_end = 0
    prev_pressed_key = None

    while not keyboard.is_pressed("escape") or not is_focused():
        os.system("cls")
        menu = [
            "Welcome to the in-game event listener editor",
            "",
            "Edit events for how the program should recognize to trigger a macro",
            "That is, evoke a response when X is shown on screen, where X is anything on display"
            "",
            "",
            "Navigate through these events using ↑ and ↓ on your keyboard. To edit it, press SPACE.",
            "",
        ]
        for i in range(len(OPTIONS)):
            if i == selected_index:
                menu.append(f"(*)\t{OPTIONS[i]}")
            else:
                menu.append(f"( )\t{OPTIONS[i]}")
        print("\n".join(menu))
        if pressed_key_time_end - pressed_key_time_start >= DELAY:
            time.sleep(DELAY)
        while True:
            if keyboard.is_pressed("up") and is_focused():
                if prev_pressed_key != "up":
                    selected_index = max(0, selected_index - 1)
                    prev_pressed_key = "up"
                    pressed_key_time_start = time.time()
                pressed_key_time_end = time.time()
                if pressed_key_time_end - pressed_key_time_start >= DELAY:
                    selected_index = max(0, selected_index - 1)

                break
            elif keyboard.is_pressed("down") and is_focused():
                if prev_pressed_key != "down":
                    selected_index = min(selected_index + 1, len(OPTIONS) - 1)
                    prev_pressed_key = "down"
                    pressed_key_time_start = time.time()
                pressed_key_time_end = time.time()
                if pressed_key_time_end - pressed_key_time_start >= DELAY:
                    selected_index = min(selected_index + 1, len(OPTIONS) - 1)
                break
            elif keyboard.is_pressed("escape") and is_focused():
                break
            elif keyboard.is_pressed("space") and is_focused():
                open_editor(selected_index)
                break


if __name__ == "__main__":
    # main()
    m = menu.Menu()
    m.item(menu.MenuItem("a", lambda: print("a")))
    m.item(menu.MenuItem("b", lambda: print("b")))
    m.item(menu.MenuItem("c", lambda: print("c")))
    m.item(menu.MenuItem("d", lambda: print("d")))
    m.show()
