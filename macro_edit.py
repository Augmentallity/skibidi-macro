import threading
from typing import Callable
import uuid
from macro import MAPPED_TYPES, Macro_Type, get_seq_macro_str
from macro_utils import delete_seq_macro, get_seq_macro, get_macro
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


def repeat_lines(
    macro_id: str,
    macro_type: str,
    macro_seq_id: Callable[[], str] = lambda: str(uuid.uuid4()),
):
    _id = macro_seq_id()
    macro_seq = get_seq_macro(macro_id, macro_type, _id)
    line_start: int | None = macro_seq["lines"][0] if macro_seq != None else None
    line_end: int | None = macro_seq["lines"][1] if macro_seq != None else None
    repeat_type: str = macro_seq["repeat_type"] if macro_seq != None else "timer"
    repeat_until_ms: int = (
        macro_seq["ms"] if macro_seq != None and "ms" in macro_seq else 0
    )
    repeat_until_iter: int = (
        macro_seq["iters"] if macro_seq != None and "iters" in macro_seq else 0
    )

    def toggle_repeat_type():
        nonlocal repeat_type
        if repeat_type == "timer":
            repeat_type = "iterations"
        else:
            repeat_type = "timer"

    def set_repeat_until_ms():
        nonlocal repeat_until_ms
        ms = input(
            "Enter duration (in ms) to repeat for (leave blank to exit): "
        ).strip()
        if ms.isnumeric():
            repeat_until_ms = int(ms)

    def set_repeat_until_iter():
        nonlocal repeat_until_iter
        ms = input(
            "Enter # of iterations to repeat for (leave blank to exit): "
        ).strip()
        if ms.isnumeric():
            repeat_until_iter = int(ms)

    def set_line_start():
        nonlocal line_start
        seq_macros = get_macro(macro_id)[macro_type]
        line_number = input("Enter starting line # (leave blank to leave): ").strip()
        if line_number.isnumeric():
            line_number = int(line_number)
            if line_number > len(seq_macros) or line_number < 1:
                set_line_start()
            else:
                line_start = line_number

    def set_line_end():
        nonlocal line_end
        seq_macros = get_macro(macro_id)[macro_type]
        line_number = input("Enter ending line # (leave blank to leave): ").strip()
        if line_number.isnumeric():
            line_number = int(line_number)
            if line_number > len(seq_macros) or line_number < 1:
                set_line_start()
            else:
                line_end = line_number

    def list_repeat_options():
        if repeat_type == "timer":
            return [
                menu.MenuItem(
                    lambda: f"Repeat duration: {repeat_until_ms}ms", set_repeat_until_ms
                )
            ]
        else:
            return [
                menu.MenuItem(
                    lambda: f"Repeat iterations: {repeat_until_iter}",
                    set_repeat_until_iter,
                )
            ]

    def repeat_lines_menu():
        n = menu.Menu("Set Lines")
        n.item(
            menu.MenuItem(
                lambda: f"From line #: {line_start if line_start != None else 'N/A'}",
                set_line_start,
            )
        )
        n.item(
            menu.MenuItem(
                lambda: f"To line #: {line_end if line_end != None else 'N/A'}",
                set_line_end,
            )
        )
        n.item(menu.MenuItem("Back", lambda: menu.stack.pop()))
        seq_macros = get_macro(macro_id)[macro_type]
        n.text("")
        n.text("\n".join([get_seq_macro_str(x, i) for i, x in enumerate(seq_macros)]))
        n.show()

    def save_changes():
        if repeat_type == "timer":
            if repeat_until_ms == None or line_start == None or line_end == None:
                return

            if macro_seq != None:
                macro_seq["repeat_type"] = repeat_type
                macro_seq["lines"] = [line_start, line_end]
                macro_seq["ms"] = repeat_until_ms
                menu.stack.pop()
            else:
                seq_macros = get_macro(macro_id)[macro_type]
                seq_macros.append(
                    {
                        "type": Macro_Type.REPEAT_LINES,
                        "id": _id,
                        "repeat_type": repeat_type,
                        "lines": [line_start, line_end],
                        "ms": repeat_until_ms,
                    }
                )
                exit_editor()

        else:
            if repeat_until_iter == None or line_start == None or line_end == None:
                return

            if macro_seq != None:
                macro_seq["repeat_type"] = repeat_type
                macro_seq["lines"] = [line_start, line_end]
                macro_seq["iters"] = repeat_until_iter
                menu.stack.pop()
            else:
                seq_macros = get_macro(macro_id)[macro_type]
                seq_macros.append(
                    {
                        "type": Macro_Type.REPEAT_LINES,
                        "id": _id,
                        "repeat_type": repeat_type,
                        "lines": [line_start, line_end],
                        "iters": repeat_until_iter,
                    }
                )
                exit_editor()
        utils.write_macros()

    m = menu.Menu("Repeat Lines Macro")
    m.header("For any repetition, this macro will do it for you.")
    m.item(
        menu.MenuItem(
            lambda: "Repeat Lines : "
            + (
                f"#{line_start} to #{line_end}"
                if line_start != None and line_end != None
                else "N/A"
            ),
            repeat_lines_menu,
        )
    )
    m.item(menu.MenuItem(lambda: f"Repeat Type : {repeat_type}", toggle_repeat_type))
    m.item(list_repeat_options)
    m.item(menu.MenuItem("Save Changes", save_changes))
    delete_menu_item(m, macro_id, macro_type, _id)
    m.item(menu.MenuItem("Back", lambda: menu.stack.pop()))
    m.show()


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


def tiny_task_macro(
    macro_id: str,
    macro_type: str,
    macro_seq_id: Callable[[], str] = lambda: str(uuid.uuid4()),
):
    _id = macro_seq_id()
    sequence = get_macro(macro_id)[macro_type]
    seq_macro: dict[str] | None = None
    i = len(sequence) + 1
    for idx, seq in enumerate(sequence):
        if seq["id"] == _id:
            seq_macro = seq
            i = idx + 1
            break
    file_name = f"{seq_macro['idx'] - 1}.exe" if seq_macro != None else None
    m = menu.Menu("Tiny Task Macro")

    def file_detect():
        nonlocal file_name
        file_path = f"{os.getcwd()}\\macros\\{macro_id}\\{i}.exe"
        exists = os.path.exists(file_path) and os.path.isfile(file_path)
        if exists:
            file_name = f"{i}.exe"
        else:
            file_name = None
        return "File name: " + (file_name if file_name != None else "Not found") + "\n"

    def save_changes():
        if file_name == None:
            return

        if seq_macro == None:
            sequence.append({"type": Macro_Type.TINY_TASK, "id": _id, "idx": i - 1})
            exit_editor()
        else:
            menu.stack.pop()
        utils.write_macros()

    m.header(
        f"To set the file, name your tiny task executable to the # of this macro. The program will automatically detect its presence.\nThe macro # is {i}."
    )
    m.text(f"Macro directory: {os.getcwd()}\\macros\\{macro_id}")
    m.text(file_detect)
    m.item(
        lambda: [
            menu.MenuItem(
                "Execute tiny task macro",
                lambda: os.system(f'"%CD%/macros/{macro_id}/{i}.exe"'),
            )
        ]
        if file_name != None
        else []
    )
    m.item(
        menu.MenuItem(
            "Open directory",
            lambda: os.system(f'explorer.exe "{os.getcwd()}\\macros\\{macro_id}"'),
        )
    )

    def delete():
        delete_seq_macro(macro_id, macro_type, _id)
        try:
            os.remove(f"{os.getcwd()}\\macros\\{macro_id}\\{file_name}")
        except:
            pass

    m.item(menu.MenuItem("Save Changes", save_changes))
    if seq_macro != None:
        m.item(
            menu.MenuItem(
                "Delete Action",
                delete,
            )
        )
    m.item(menu.MenuItem("Back", lambda: menu.stack.pop()))
    m.show()


def exit_editor():
    menu.stack.pop()
    menu.stack.pop()
