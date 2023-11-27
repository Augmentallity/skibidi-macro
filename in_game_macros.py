import os
import threading
import time
from typing import Callable
import win32con
import win32gui
import pyautogui
from macro import MAPPED_TYPES, Macro_Type
import macro_edit
import menu
import uuid
import json
import utils
import pynput
from pynput.keyboard import Key

"""
{
    "id": str,
    "name": str,
    "lobby_sequence": list[{
        "type": str
    }],
    "ingame_sequence": list[{
        "type": str
    }]
}
"""


def create_macro():
    macros = utils.read_macros()
    name = input("Name your macro (leave blank to go back): ").strip()
    if len(name) > 0:
        macros.append(
            {
                "name": name,
                "id": str(uuid.uuid4()),
                "lobby_sequence": [],
                "ingame_sequence": [],
            }
        )  # changeable
        utils.write_macros(macros)


def list_macros():
    macros = utils.read_macros()
    r = []
    for x in macros:
        callback = (lambda y: (lambda: macro_editor(y)))(x)
        r.append(menu.MenuItem(x["name"], callback))
    return r


def delete_macro(id: str):
    macros = utils.read_macros()
    confirmation = None

    while confirmation != "" and confirmation != "DELETE":
        confirmation = input(
            f"Type DELETE to confirm deletion (leave blank to go back): "
        ).strip()
    if len(confirmation) > 0 and confirmation == "DELETE":
        i = 0
        while i < len(macros):
            if macros[i]["id"] == id:
                break
            i += 1
        del macros[i]
        utils.write_macros()
        menu.stack.pop()
        menu.stack[-1].set_index(0)


def edit_macro_name(id: str):
    macros = utils.read_macros()
    new_name = input("Enter a new name (leave blank to go back): ").strip()
    if new_name != "":
        for i in range(len(macros)):
            if macros[i]["id"] == id:
                macros[i]["name"] = new_name
        utils.write_macros(macros)
        menu.stack.pop()


def list_sequence_macros(macro_id: str, seq_name: str):
    sequence: list[dict[str]] = macro_edit.get_macro(macro_id)[seq_name]
    r = []

    def callback(x: dict[str]):
        nonlocal macro_id
        nonlocal seq_name
        return (lambda y, z, p: (lambda: edit_sequence_macro(y, z, p)))(
            x, macro_id, seq_name
        )

    for i, x in enumerate(sequence):
        match x["type"]:
            case Macro_Type.CLICK:
                r.append(
                    menu.MenuItem(
                        f"[{i + 1}]\t{MAPPED_TYPES[Macro_Type.CLICK]}({x['position'][0]}, {x['position'][1]}){' [R]' if x['roblox_bypass'] else ''}",
                        callback(x),
                    )
                )
            case Macro_Type.WAIT:
                r.append(
                    menu.MenuItem(
                        f"[{i + 1}]\t{MAPPED_TYPES[Macro_Type.WAIT]}({x['ms']}ms)",
                        callback(x),
                    )
                )
            case Macro_Type.WAIT_CONDITIONALLY:
                r.append(
                    menu.MenuItem(
                        f"[{i + 1}]\t{MAPPED_TYPES[Macro_Type.WAIT_CONDITIONALLY]}({x['position'][0]}, {x['position'][1]}) - rgb({x['color'][0]}, {x['color'][1]}, {x['color'][2]})",
                        callback(x),
                    )
                )
            case Macro_Type.KEY_PRESS:
                r.append(
                    menu.MenuItem(
                        f"[{i + 1}]\t{MAPPED_TYPES[Macro_Type.KEY_PRESS]}({str(x['key'])})",
                        callback(x),
                    )
                )
            case Macro_Type.KEY_UP:
                r.append(
                    menu.MenuItem(
                        f"[{i + 1}]\t{MAPPED_TYPES[Macro_Type.KEY_UP]}({str(x['key'])})",
                        callback(x),
                    )
                )
            case Macro_Type.KEY_DOWN:
                r.append(
                    menu.MenuItem(
                        f"[{i + 1}]\t{MAPPED_TYPES[Macro_Type.KEY_DOWN]}({str(x['key'])})",
                        callback(x),
                    )
                )
    return r


def edit_sequence_macro(macro: dict[str], macro_id: str, macro_type: str):
    def callback(x: Callable[[str, str, Callable[[], str]], None]):
        x(macro_id, macro_type, lambda: macro["id"])

    match macro["type"]:
        case Macro_Type.CLICK:
            callback(macro_edit.click)
        case Macro_Type.WAIT:
            callback(macro_edit.wait)
        case Macro_Type.WAIT_CONDITIONALLY:
            callback(macro_edit.wait_condition)
        case Macro_Type.KEY_PRESS:
            callback(macro_edit.generate_key_macro(Macro_Type.KEY_PRESS))
        case Macro_Type.KEY_DOWN:
            callback(macro_edit.generate_key_macro(Macro_Type.KEY_DOWN))
        case Macro_Type.KEY_UP:
            callback(macro_edit.generate_key_macro(Macro_Type.KEY_UP))


def add_sequence_macro(macro_id: str, macro_type: str):
    m = menu.Menu("Macro Sequence Editor")
    m.header("Add a macro to the sequence:")

    m.item(
        menu.MenuItem(
            "Click",
            lambda: macro_edit.click(macro_id, macro_type),
            description="Simulates a left click from the mouse",
        )
    )
    m.item(
        menu.MenuItem(
            "Wait",
            lambda: macro_edit.wait(macro_id, macro_type),
            description="Waits for a specific time before executing the next macro action",
        )
    )
    m.item(
        menu.MenuItem(
            "Wait (condition)",
            lambda: macro_edit.wait_condition(macro_id, macro_type),
            description="Waits for a specific pixel to show on screen before executing the next macro action",
        )
    )
    m.item(
        menu.MenuItem(
            "Key Down",
            lambda: macro_edit.generate_key_macro(Macro_Type.KEY_DOWN)(
                macro_id, macro_type
            ),
            description="Simulates holding down a keystroke",
        )
    )
    m.item(
        menu.MenuItem(
            "Key Up",
            lambda: macro_edit.generate_key_macro(Macro_Type.KEY_UP)(
                macro_id, macro_type
            ),
            description="Simulates releasing a keystroke",
        )
    )
    m.item(
        menu.MenuItem(
            "Key Press",
            lambda: macro_edit.generate_key_macro(Macro_Type.KEY_PRESS)(
                macro_id, macro_type
            ),
            description="Simulates a keystroke press. Combination of Key Up and Key Down",
        )
    )
    m.show()


def change_action_position(macro_id: str, macro_type: str):
    seq_macros = len(macro_edit.get_macro(macro_id)[macro_type])
    if seq_macros < 2:
        return
    position = input("\nEnter the Action #: ").strip()
    insert_at = input("Enter the # to switch this position to: ").strip()
    if position.isnumeric() and insert_at.isnumeric():
        position = int(position)
        insert_at = int(insert_at)
    else:
        return

    if position < 1 or insert_at < 1:
        print(f"Invalid position(s). Please enter a # between 1 and {seq_macros}")
        time.sleep(1)
        return

    macro = macro_edit.get_macro(macro_id)
    tmp = macro[macro_type][position - 1]
    del macro[macro_type][position - 1]
    macro[macro_type].insert(insert_at - 1, tmp)


def test_macro_seq(macro_id: str, macro_seq: str):
    macro = macro_edit.get_macro(macro_id)
    sequence = macro[macro_seq]
    keyboard = pynput.keyboard.Controller()
    for macro_seq in sequence:
        match macro_seq["type"]:
            case Macro_Type.CLICK:
                if macro_seq["roblox_bypass"]:
                    win32gui.GetCursorInfo()

                    def click(active: Callable[[], bool]):
                        x, y = macro_seq["position"]
                        while active():
                            pyautogui.click(x, y)

                    active = True
                    t1 = threading.Thread(
                        target=lambda: os.system('"%CD%/bin/mouse_movement.exe"')
                    )
                    t2 = threading.Thread(target=lambda: click(lambda: active))
                    t1.start()
                    t2.start()
                    x, y = macro_seq["position"]
                    s = time.perf_counter()
                    cursor_state_pointer = win32gui.LoadCursor(0, win32con.IDC_HAND)
                    while True:
                        cursor_state = win32gui.GetCursorInfo()[1]
                        if not t1.is_alive():
                            t1 = threading.Thread(
                                target=lambda: os.system(
                                    '"%CD%/bin/mouse_movement.exe"'
                                )
                            )
                            t1.start()

                        if cursor_state >= cursor_state_pointer:  # issue
                            active = False
                            pyautogui.click(x, y)
                            break
                        if time.perf_counter() - s >= 5:
                            active = False
                            break

                else:
                    pyautogui.click(macro_seq["position"][0], macro_seq["position"][1])
            case Macro_Type.WAIT:
                time.sleep(macro_seq["ms"] / 1000)
            case Macro_Type.WAIT_CONDITIONALLY:
                x, y = macro_seq["position"]
                color = macro_seq["color"]
                while not pyautogui.pixelMatchesColor(x, y, color):
                    pass
            case Macro_Type.KEY_DOWN:
                keyboard.press(eval(macro_seq["key"]))
            case Macro_Type.KEY_UP:
                keyboard.release(eval(macro_seq["key"]))
            case Macro_Type.KEY_PRESS:
                keyboard.tap(eval(macro_seq["key"]))


def macro_editor(props: dict[str]):
    name = props["name"]
    id = props["id"]
    m = menu.Menu(f"Macro Editor: {name}")
    m.item(menu.MenuItem(f"Delete name", lambda: delete_macro(id)))
    m.item(menu.MenuItem(f"Change name", lambda: edit_macro_name(id)))
    m.item(menu.MenuItem(f"Test macro", lambda: test_macro_seq(id, "lobby_sequence")))
    m.text("=== Lobby (Pre-Game) ===")
    m.item(
        menu.MenuItem("Add Action", lambda: add_sequence_macro(id, "lobby_sequence"))
    )
    m.item(
        menu.MenuItem(
            "Change Action Position #",
            lambda: change_action_position(
                id,
                "lobby_sequence",
            ),
        )
    )
    m.text("")
    m.item(lambda: list_sequence_macros(id, "lobby_sequence"))
    m.text("")
    m.text("=== In-Game ===")
    m.item(
        menu.MenuItem("Add Action", lambda: add_sequence_macro(id, "ingame_sequence"))
    )
    m.item(lambda: list_sequence_macros(id, "ingame_sequence"))
    m.show()


def main():
    m = menu.Menu("In-Game Macros")
    m.item(menu.MenuItem("Create a macro", create_macro))
    m.text("\n=== User Defined Macros ===\n")
    m.item(list_macros)
    m.show()
