from typing import Callable
import uuid
from macro import MAPPED_TYPES, Macro_Type
import menu
import pynput
import utils
import pyautogui
import os


def delete_menu_item(
    n: menu.Menu, macro_id: str, macro_seq_name: str, macro_seq_id: str
):
    seq_macro = get_seq_macro(macro_id, macro_seq_name, macro_seq_id)
    if seq_macro != None:
        n.item(
            menu.MenuItem(
                "Delete Action",
                lambda: delete_seq_macro(macro_id, macro_seq_name, macro_seq_id),
            )
        )


def delete_seq_macro(macro_id: str, macro_seq_name: str, _id: str):
    macro = get_macro(macro_id)
    i = 0
    while i < len(macro[macro_seq_name]):
        if macro[macro_seq_name][i]["id"] == _id:
            break
        i += 1

    del macro[macro_seq_name][i]
    menu.stack.pop()


def get_macro(id: str, macros: list[dict[str]] = utils.read_macros()) -> dict[str]:
    for macro in macros:
        if macro["id"] == id:
            return macro
    raise Exception(f"{id} does not exist as a macro")


def get_seq_macro(
    macro_id: str, macro_seq_name: str, macro_seq_id: str
) -> dict[str] | None:
    """
    Gets a macro from a sequence

    Returns:
        The reference to a macro from a sequence is returned, of which
        contains a "type" property that indicates the type of macro it is
        (CLICK, WAIT, etc.)
    """
    macros = utils.read_macros()
    for macro in macros:
        if macro["id"] == macro_id:
            for seq_macro in macro[macro_seq_name]:
                if seq_macro["id"] == macro_seq_id:
                    return seq_macro
    return None


def click(
    macro_id: str,
    macro_type: str,
    macro_seq_id: Callable[[], str] = lambda: str(uuid.uuid4()),
):
    """
    Defines click callback for menu
    """
    _id = macro_seq_id()
    seq_macro = get_seq_macro(macro_id, macro_type, _id)
    n = menu.Menu("Click Macro")
    pos: tuple[int, int] | None = seq_macro["position"] if seq_macro != None else None
    roblox_bypass = seq_macro["roblox_bypass"] if seq_macro != None else False

    def toggle_bypass():
        nonlocal roblox_bypass
        roblox_bypass = not roblox_bypass

    def on_press(key: pynput.keyboard.Key):
        nonlocal pos
        if key == pynput.keyboard.Key.shift_l:
            pos = pyautogui.position()

    listener = pynput.keyboard.Listener(on_press=on_press)
    listener.start()

    def save_changes():
        nonlocal pos
        nonlocal _id
        if seq_macro != None:
            seq_macro["position"] = (pos[0], pos[1])
            seq_macro["roblox_bypass"] = roblox_bypass
            menu.stack.pop()
            utils.write_macros()
            return

        if pos == None:
            return

        macro = get_macro(macro_id)

        macro[macro_type].append(
            {
                "id": _id,
                "type": Macro_Type.CLICK,
                "position": (pos[0], pos[1]),
                "roblox_bypass": roblox_bypass,
            }
        )
        exit_editor()

        utils.write_macros()

    n.item(
        menu.MenuItem(
            lambda: f"Confirm : ({pos[0]}, {pos[1]})"
            if pos != None
            else f"Confirm : N/A",
            save_changes,
        )
    )
    n.item(
        menu.MenuItem(
            lambda: f"[{'✓' if roblox_bypass else ' '}] In-Game Roblox UI Click Bypass",
            toggle_bypass,
            description="Bypasses Roblox's anti-macro UI click by masking a simulated click with real mouse hardware movement.",
        )
    )

    delete_menu_item(n, macro_id, macro_type, _id)

    n.item(menu.MenuItem("Back", lambda: menu.stack.pop()))
    n.header("Press SHIFT to grab cursor position")
    n.show()
    listener.stop()


def wait(
    macro_id: str,
    macro_type: str,
    macro_seq_id: Callable[[], str] = lambda: str(uuid.uuid4()),
):
    """
    Defines wait callback for macro
    """
    _id = macro_seq_id()
    seq_macro = get_seq_macro(macro_id, macro_type, _id)
    ms: int | None = seq_macro["ms"] if seq_macro != None else None
    m = menu.Menu("Wait Macro")

    def save_changes():
        if seq_macro == None:
            macro = get_macro(macro_id)
            macro[macro_type].append(
                {"type": Macro_Type.WAIT, "id": macro_seq_id(), "ms": ms}
            )
            exit_editor()
        else:
            seq_macro["ms"] = ms
            menu.stack.pop()
        utils.write_macros()

    def get_user_input():
        nonlocal ms
        user_input = input(
            "Enter # of ms to wait for (leave blank to go back): "
        ).strip()
        if user_input.isnumeric():
            ms = int(user_input)

    m.item(
        menu.MenuItem(
            lambda: f"Current : {f'{ms}ms' if ms != None else 'N/A'}", get_user_input
        )
    )
    m.item(menu.MenuItem("Save Changes", save_changes))
    delete_menu_item(m, macro_id, macro_type, _id)
    m.item(menu.MenuItem("Back", lambda: menu.stack.pop()))
    m.show()

    # os.system("cls")
    # val = input("Enter # of ms to wait for (leave blank to go back): ").strip()
    # if len(val) > 0 and val.isnumeric():
    #     seq_macro = get_seq_macro(macro_id, macro_type, macro_seq_id())
    #     if seq_macro == None:
    #         macro = get_macro(macro_id)
    #         macro[macro_type].append(
    #             {"type": Macro_Type.WAIT, "id": macro_seq_id(), "ms": int(val)}
    #         )
    #         menu.stack.pop()
    #     else:
    #         seq_macro["ms"] = int(val)
    #     utils.write_macros()


def wait_condition(
    macro_id: str,
    macro_type: str,
    macro_seq_id: Callable[[], str] = lambda: str(uuid.uuid4()),
):
    _id = macro_seq_id()
    macro_seq = get_seq_macro(macro_id, macro_type, _id)
    pos: tuple[int, int] = macro_seq["position"] if macro_seq != None else None
    color: tuple[int, int, int] = macro_seq["color"] if macro_seq != None else None

    def on_press(key: pynput.keyboard.Key):
        nonlocal pos
        nonlocal color
        if key == pynput.keyboard.Key.shift_l:
            pos = pyautogui.position()
            color = pyautogui.pixel(pos[0], pos[1])

    def save_changes():
        nonlocal macro_seq
        nonlocal pos
        nonlocal color
        nonlocal macro_id
        if pos == None or color == None:
            return

        if macro_seq != None:
            macro_seq["position"] = pos
            macro_seq["color"] = color
            menu.stack.pop()
            utils.write_macros()
            return

        macro = get_macro(macro_id)
        macro[macro_type].append(
            {
                "id": _id,
                "type": Macro_Type.WAIT_CONDITIONALLY,
                "position": pos,
                "color": color,
            }
        )
        exit_editor()
        utils.write_macros()

    listener = pynput.keyboard.Listener(on_press=on_press)
    listener.start()

    m = menu.Menu("Wait (Conditional) Macro")
    m.header(
        "Wait conditionally works similar to wait, except that\nit waits for a specified pixel to appear on screen before\nexecuting the next macro. This is extremely useful for interactions\nwhose timing is not always the same and is influenced by outside\nfactors such as lag.\n\nPress SHIFT to capture the pixel at the cursor"
    )
    m.item(
        menu.MenuItem(
            lambda: f"Confirm: {f'({pos[0]}, {pos[1]}), rgb({color[0]}, {color[1]}, {color[2]})' if color != None and pos != None else 'N/A'}",
            save_changes,
        )
    )
    delete_menu_item(m, macro_id, macro_type, _id)
    m.item(menu.MenuItem("Back", lambda: menu.stack.pop()))
    m.show()
    listener.stop()


def generate_key_macro(macro_type_enum: int):
    def key_press(
        macro_id: str,
        macro_type: str,
        macro_seq_id: Callable[[], str] = lambda: str(uuid.uuid4()),
    ):
        _id = macro_seq_id()
        macro_seq = get_seq_macro(macro_id, macro_type, _id)
        key: str = macro_seq["key"] if macro_seq != None else None

        def save_changes():
            nonlocal key
            if key == None:
                return

            if macro_seq != None:
                macro_seq["key"] = str(key)
                menu.stack.pop()
            else:
                macro = get_macro(macro_id)
                macro[macro_type].append(
                    {"id": _id, "type": macro_type_enum, "key": str(key)}
                )
                exit_editor()
            utils.write_macros()

        def listen_for_key():
            nonlocal key
            m = menu.Menu(f"Set {MAPPED_TYPES[macro_type_enum]}")

            def on_press(event: pynput.keyboard.Key):
                nonlocal key
                if event != pynput.keyboard.Key.esc:
                    key = str(event)
                menu.stack.pop()

            listener = pynput.keyboard.Listener(on_press)
            listener.start()
            m.header(f"Current key : {str(key)}")
            m.item(
                menu.MenuItem(
                    lambda: f"Press any key to change. Press ESC to go back without making any changes",
                )
            )
            m.show()
            listener.stop()

        m = menu.Menu(f"{MAPPED_TYPES[macro_type_enum]} Macro")
        m.item(
            menu.MenuItem(
                lambda: f"Current (SPACE to edit) : {str(key) if key != None else 'N/A'}",
                listen_for_key,
            )
        )
        m.item(menu.MenuItem("Save changes", save_changes))
        delete_menu_item(m, macro_id, macro_type, _id)
        m.item(menu.MenuItem("Back", lambda: menu.stack.pop()))
        m.show()

    return key_press


def exit_editor():
    menu.stack.pop()
    menu.stack.pop()
