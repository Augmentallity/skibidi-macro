import threading
from event_listeners import EVENT_LISTENERS_MAPPED
from macro import Macro_Type
import utils
import pyautogui
import keyboard
import pynput
import time
import os
import win32gui
import win32con
from typing import Callable
from pynput.keyboard import Key
import pydirectinput
import macro_edit
import menu
import cam_editor
import keyboard
import traceback


def close_roblox():
    hwnd = win32gui.FindWindow(None, "Roblox")
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)


def to_date(f: float):
    s = int(f)
    seconds = s % 60
    minutes = (s % 3600) // 60
    hours = (s % 86400) // 3600
    return f"{hours}h {minutes}m {seconds}s"


def main(macro_id: str):
    print("Executing macro in 3...", end="\r")
    time.sleep(1)
    print("Executing macro in 2...", end="\r")
    time.sleep(1)
    print("Executing macro in 1...", end="\r")
    time.sleep(1)
    should_stop = False
    is_disconnected = False
    time_runs = []  # A list of time of each run
    logs = []  # Output during ingame macro execution
    browser_window: int | None = None
    losses = 0
    wins = 0
    disconnections = 0

    config = utils.read_config()
    macro = macro_edit.get_macro(macro_id)

    def cancel_listener(key: pynput.keyboard.Key):
        nonlocal should_stop
        if key == pynput.keyboard.Key.backspace:
            should_stop = True

    def disconnection_listener(
        should_stop_get: Callable[[], bool], get_is_disconnected: Callable[[], bool]
    ):
        nonlocal is_disconnected
        while not should_stop_get():
            hwnd = win32gui.FindWindow(None, "Roblox")
            pos, color = utils.get_config_prop(utils.DISCONNECTED_DIALOG_BOX)
            x, y = pos
            if (
                pyautogui.pixelMatchesColor(x, y, color)
                and hwnd == win32gui.GetForegroundWindow()
            ):
                time.sleep(5)
                if (
                    pyautogui.pixelMatchesColor(x, y, color)
                    and hwnd == win32gui.GetForegroundWindow()
                ):
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                    is_disconnected = True
                    while get_is_disconnected():
                        pass

    def info_listener(should_stop_get: Callable[[], bool]):
        nonlocal time_runs
        nonlocal wins
        nonlocal losses
        nonlocal disconnections

        s = time.perf_counter()

        info = "\n\t".join(
            [
                f"\tTime elapsed: {to_date(time.perf_counter() - s)}",
                f"# of runs completed: {len(time_runs)}",
                f"Current run #: {len(time_runs) + 1}",
            ]
        )
        while not should_stop_get():
            info = "\n\t".join(
                [
                    "",
                    "\t[INFO]",
                    f"Time elapsed: {to_date(time.perf_counter() - s)}",
                    f"# of waves per run: {macro['waves']}",
                    f"  - # of wins: {wins}",
                    f"  - # of losses: {losses}",
                    f"  - win rate: {(f'{round((wins/len(time_runs)) * 10000)/100}%') if len(time_runs) != 0 else 'N/A'}",
                    f"Current run #: {len(time_runs) + 1}",
                    f"# of runs completed: {len(time_runs)}",
                    f"  - Fastest run time: {to_date(min(time_runs)) if len(time_runs) != 0 else 'N/A'}",
                    f"  - Slowest run time: {to_date(max(time_runs)) if len(time_runs) != 0 else 'N/A'}",
                    f"  - Average run time: {to_date(sum(time_runs)/len(time_runs)) if len(time_runs) != 0 else 'N/A'}",
                    f"# of disconnections: {disconnections}",
                    "",
                    "[LOGS]",
                    "",
                    *logs,
                ]
            )
            os.system("cls")
            print(info)
            time.sleep(menu.Menu.TICK_RATE)
        os.system("cls")
        print(info)

    listener = pynput.keyboard.Listener(on_press=cancel_listener)
    keyboard_controller = pynput.keyboard.Controller()
    d_listener = threading.Thread(
        target=disconnection_listener,
        args=(lambda: should_stop, lambda: is_disconnected),
    )
    i_listener = threading.Thread(target=info_listener, args=(lambda: should_stop,))
    listener.start()
    d_listener.start()
    i_listener.start()

    def execute_macros(
        is_disconnected: Callable[[], bool],
        should_stop: Callable[[], bool],
        start: int | None = None,
        end: int | None = None,
    ):
        nonlocal browser_window
        seq_macros: list[dict[str]] = macro_edit.get_macro(macro_id)["lobby_sequence"]
        seq_macros = seq_macros[
            start - 1 if start != None else 0 : end if end != None else len(seq_macros)
        ]
        for i, macro_seq in enumerate(seq_macros):
            if is_disconnected() or should_stop():
                return
            match macro_seq["type"]:
                case Macro_Type.TINY_TASK:
                    logs.append(f"Executing tiny task {i + 1}.exe")
                    os.system(f'"%CD%/macros/{macro_id}/{i + 1}.exe"')
                case Macro_Type.CLICK:
                    x, y = macro_seq["position"]
                    logs.append(f"Clicked ({x}, {y})")
                    try:
                        pydirectinput.click(x, y)  # NOT CLICKING WHEN NO FOUCSED WINDOW
                    except Exception as e:
                        print(e)
                        should_stop = True
                        os._exit(1)
                    if macro_seq["should_fullscreen_roblox"]:
                        if browser_window == None:
                            browser_window = win32gui.GetForegroundWindow()
                        logs.append("Waiting for Roblox application...")
                        elapsed = time.perf_counter()
                        while not is_disconnected() and not should_stop():
                            hwnd = win32gui.FindWindow(None, "Roblox")
                            if time.perf_counter() - elapsed >= 10:
                                logs.append(
                                    "Failed to detect Roblox within 10 seconds. Attempting to relaunch..."
                                )
                                elapsed = time.perf_counter()
                                try:
                                    pydirectinput.click(x, y)
                                except Exception as e:
                                    print(e)
                                    should_stop = True
                                    os._exit(1)
                            if hwnd != 0:
                                logs.append(
                                    "Maximized Roblox application. Continuing..."
                                )
                                win32gui.ShowWindow(
                                    win32gui.FindWindow(None, "Roblox"),
                                    win32con.SW_RESTORE,
                                )
                                win32gui.SetWindowPos(
                                    hwnd,
                                    win32con.HWND_NOTOPMOST,
                                    0,
                                    0,
                                    0,
                                    0,
                                    win32con.SWP_NOMOVE + win32con.SWP_NOSIZE,
                                )
                                win32gui.SetWindowPos(
                                    hwnd,
                                    win32con.HWND_TOPMOST,
                                    0,
                                    0,
                                    0,
                                    0,
                                    win32con.SWP_NOMOVE + win32con.SWP_NOSIZE,
                                )
                                win32gui.SetWindowPos(
                                    hwnd,
                                    win32con.HWND_NOTOPMOST,
                                    0,
                                    0,
                                    0,
                                    0,
                                    win32con.SWP_SHOWWINDOW
                                    + win32con.SWP_NOMOVE
                                    + win32con.SWP_NOSIZE,
                                )
                                break
                case Macro_Type.WAIT:
                    time.sleep(macro_seq["ms"] / 1000)
                case Macro_Type.WAIT_CONDITIONALLY:
                    x, y = macro_seq["position"]
                    color = macro_seq["color"]
                    logs.append(f"Waiting for condition...")
                    while (
                        not pyautogui.pixelMatchesColor(x, y, color)
                        and not should_stop()
                        and not is_disconnected()
                    ):
                        pass
                    logs.append(f"Condition fulfilled. Continuing...")
                case Macro_Type.KEY_DOWN:
                    keyboard_controller.press(eval(macro_seq["key"]))
                case Macro_Type.KEY_UP:
                    keyboard_controller.release(eval(macro_seq["key"]))
                case Macro_Type.KEY_PRESS:
                    keyboard_controller.tap(eval(macro_seq["key"]))
                case Macro_Type.REPEAT_LINES:
                    if macro_seq["repeat_type"] == "timer":
                        s = time.perf_counter()
                        seconds = macro_seq["ms"] / 1000
                        start, end = macro_seq["lines"]
                        logs.append(
                            f"Repeating #{start} to #{end} for {seconds} seconds."
                        )
                        while time.perf_counter() - s <= seconds:
                            execute_macros(is_disconnected, should_stop, start, end)
                        logs.append(f"Finished repeating task. Continuing...")
                case Macro_Type.GLOBAL_TINY_TASK:
                    logs.append(f"Executing bin tinytask {macro_seq['file_name']}")
                    os.system(f'"%CD%/bin/{macro_seq["file_name"]}"')
                case Macro_Type.LISTENER:
                    try:
                        val = EVENT_LISTENERS_MAPPED[macro_seq["name"]]
                        logs.append(
                            f"Waiting for response from {macro_seq['name']} whose key value is {val}..."
                        )
                        pos, color = utils.get_config_prop(val)

                        x, y = pos
                        while (
                            not pyautogui.pixelMatchesColor(x, y, color)
                            and not should_stop()
                            and not is_disconnected()
                        ):
                            pass
                        logs.append("\t- Response received!")
                    except Exception:
                        should_stop = True
                        time.sleep(5)
                        print(traceback.format_exc())
                        print(EVENT_LISTENERS_MAPPED)
                        print(macro_seq["name"])
                        os._exit(1)

    def ingame_macros(
        is_disconnected: Callable[[], bool],
        should_stop: Callable[[], bool],
        starting_run_time: float,
    ):
        nonlocal logs
        nonlocal time_runs
        nonlocal wins
        nonlocal losses

        has_lost = False
        run_ended = False
        if is_disconnected() or should_stop():
            return

        def detect_loss(
            should_stop: Callable[[], bool],
            is_disconnected: Callable[[], bool],
            run_ended: Callable[[], bool],
        ):
            nonlocal has_lost
            while not should_stop() and not is_disconnected() and not run_ended():
                pos1, color1 = utils.get_config_prop(utils.DEFEAT_LABEL)
                pos2, color2 = utils.get_config_prop(utils.HP_BAR_ZERO)

                x1, y1 = pos1
                x2, y2 = pos2
                if pyautogui.pixelMatchesColor(
                    x1, y1, color1
                ) and pyautogui.pixelMatchesColor(x2, y2, color2):
                    has_lost = True

        loss_detector = threading.Thread(
            target=detect_loss,
            args=(should_stop, is_disconnected, lambda: run_ended),
        )
        loss_detector.start()
        dirs = [
            path
            for path in os.listdir(f"{os.getcwd()}\\macros\\{macro_id}")
            if os.path.isdir(f"{os.getcwd()}\\macros\\{macro_id}\\{path}")
        ]
        disabled_cam_angles = set(macro["disabled_cam_angles"])
        while not is_disconnected() and not should_stop():
            found_cam_angle_name = None
            has_lost = False

            s = time.perf_counter()
            e = s
            while (
                not should_stop()
                and found_cam_angle_name == None
                and e - s <= 30
                and len(dirs) > 0
                and not is_disconnected()
            ):
                e = time.perf_counter()
                for cam_angle in dirs:
                    if (
                        cam_angle not in disabled_cam_angles
                        and cam_editor.compare_to(macro_id, cam_angle)
                        >= cam_editor.SIMILARITY
                    ):
                        found_cam_angle_name = cam_angle
                        logs.append(f"Detected {found_cam_angle_name}")
                        break

            current_wave = 1
            while not should_stop() and not is_disconnected():
                x, y = config[f"{utils.START_WAVE_BTN}_pos"]
                color = config[f"{utils.START_WAVE_BTN}_color"]

                if pyautogui.pixelMatchesColor(x, y, color):
                    os.system('"%CD%/bin/clickwavestart.exe"')
                    break

            if len(dirs) == 0:
                logs.append("No camera angles found for this macro")

            if e - s >= 30:
                logs.append("Failed to detect camera angles")

            while not should_stop() and not is_disconnected() and not has_lost:
                x, y = config[f"{utils.WAVE_COMPLETED_LABEL}_pos"]
                color = config[f"{utils.WAVE_COMPLETED_LABEL}_color"]
                if pyautogui.pixelMatchesColor(x, y, color):
                    current_wave += 1
                    if current_wave > macro["waves"]:
                        pyautogui.press("alt")
                        win32gui.SetForegroundWindow(browser_window)
                        close_roblox()
                        wins += 1
                        time_runs.append(time.perf_counter() - starting_run_time)
                        return
                    path = f"{os.getcwd()}\\macros\\{macro_id}\\{found_cam_angle_name}\\{current_wave}"
                    if os.path.exists(path):
                        macros_in_wave = os.listdir(path)
                        for executable in macros_in_wave:
                            os.system(
                                f'"%CD%/macros/{macro_id}/{found_cam_angle_name}/{current_wave}/{executable}"'
                            )
                    else:
                        logs.append(f"No macros found for wave {current_wave}")
                    time.sleep(5)

            if has_lost:
                logs.append("Loss detected. Retrying...")
                losses += 1
                now = time.perf_counter()
                time_runs.append(now - starting_run_time)
                os.system('"%CD%/bin/retryfromloss.exe"')
                time.sleep(3)
            else:
                run_ended = True
                break

    while not should_stop:
        starting_run_time = time.perf_counter()
        logs.append("Executing pre-game macro sequence...")
        execute_macros(lambda: is_disconnected, lambda: should_stop)
        logs.append("")
        ingame_macros(lambda: is_disconnected, lambda: should_stop, starting_run_time)
        logs.clear()
        if is_disconnected:
            logs.append("Detected disconnection. Attempting to reconnect...")
            close_roblox()
            pyautogui.press("alt")
            win32gui.SetForegroundWindow(browser_window)
            while not utils.has_internet():
                logs.append("There is no internet connection! Waiting...")
            is_disconnected = False

    listener.stop()
    should_exit = False

    def on_escape(key: pynput.keyboard.Key):
        nonlocal should_exit
        if (
            key == pynput.keyboard.Key.esc
            and win32gui.GetForegroundWindow() == menu.HWND
        ):
            should_exit = True

    exit_listener = pynput.keyboard.Listener(on_press=on_escape)
    exit_listener.start()
    print("\nPress ESCAPE to return to macro profile selector")
    time.sleep(0.1)
    while not should_exit:
        pass
    exit_listener.stop()


def list_macros() -> list[menu.MenuItem]:
    macros = utils.read_macros()
    return [
        menu.MenuItem(x["name"], (lambda y: lambda: main(y["id"]))(x)) for x in macros
    ]


if __name__ == "__main__":
    m = menu.Menu("Roblox Macro Executor")
    m.header("Select a macro profile to execute")
    m.item(list_macros)
    m.show()
