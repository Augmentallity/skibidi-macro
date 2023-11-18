import utils
import pyautogui
import keyboard
import pynput
import time
import os
import win32gui
import win32con


def windowEnumerationHandler(hwnd, top_windows):
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))


runs = 0
losses = 0
disconnections = 0


def main():
    # Tracking variables
    time_elapsed = time.time()

    # Controller
    kb_controller = pynput.keyboard.Controller()

    run_till_start_of_wave = 10
    config = utils.read_config()
    run_till_start_of_wave = config["waves_per_run"] + 1

    def execute_run(skip_joining_private_server: bool):
        global runs
        config = utils.read_config()

        while True:
            now = time.time()
            seconds = int((now - time_elapsed) % 60)
            minutes = int(((now - time_elapsed) // 60) % 60)
            hours = int(((now - time_elapsed) // 3600) % 60)
            log = [
                "-----------------------------------------------",
                f"\tTotal # of runs completed: {runs}",
                f"\tTime elapsed: {hours}h {minutes}m {seconds}s",
                f"\tWaves per run: {run_till_start_of_wave - 1}",
                f"\tGames lost: {losses}",
                f"\tGames won: {runs - losses}",
                f"\tWin rate: {f'{((runs-losses)/runs)*100}%' if runs > 0 else 'N/A'}",
                f"\t# of disconnections throughout session: {disconnections}",
                "-----------------------------------------------",
                "",
                "To stop farming for gems, press BACKSPACE on your keyboard",
                "",
            ]
            os.system("cls")
            print("\n".join(log))
            print("\tLaunching roblox...")
            # Auto-start anime adventures private server
            if not skip_joining_private_server:
                os.system("%CD%/bin/joinprivateserver.exe")

            is_opened = False
            while not is_opened:
                detect_stop()
                top_windows = []
                win32gui.EnumWindows(windowEnumerationHandler, top_windows)
                for process in top_windows:
                    HWND = process[0]
                    if process[1] == "Roblox":
                        is_opened = True
                        print("\tDetected Roblox application")
                        win32gui.ShowWindow(HWND, win32con.SW_RESTORE)
                        win32gui.SetWindowPos(
                            HWND,
                            win32con.HWND_NOTOPMOST,
                            0,
                            0,
                            0,
                            0,
                            win32con.SWP_NOMOVE + win32con.SWP_NOSIZE,
                        )
                        win32gui.SetWindowPos(
                            HWND,
                            win32con.HWND_TOPMOST,
                            0,
                            0,
                            0,
                            0,
                            win32con.SWP_NOMOVE + win32con.SWP_NOSIZE,
                        )
                        win32gui.SetWindowPos(
                            HWND,
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
            while True:
                detect_stop()
                color = pyautogui.pixel(
                    config[f"{utils.LOBBY_PLAY_BTN_PROP}_pos"][0],
                    config[f"{utils.LOBBY_PLAY_BTN_PROP}_pos"][1],
                )
                if color == config[f"{utils.LOBBY_PLAY_BTN_PROP}_color"]:
                    print("\tSuccessfully loaded in-game")
                    os.system("%CD%/bin/lobbyclickplay.exe")
                    # pyautogui.moveTo(x=153, y=479, duration=DELAY)
                    # pyautogui.click(clicks=2, interval=DELAY)
                    break

            start = time.time()
            kb_controller.press("d")
            kb_controller.press("w")
            kb_controller.press(pynput.keyboard.Key.shift_l)
            while True:
                listeners()
                if time.time() - start > 2:
                    kb_controller.release("d")
                    kb_controller.release("w")
                    kb_controller.release(pynput.keyboard.Key.shift_l)
                    break

            while True:
                listeners()
                color = pyautogui.pixel(
                    config[f"{utils.CANCEL_MAP_BTN}_pos"][0],
                    config[f"{utils.CANCEL_MAP_BTN}_pos"][1],
                )
                if color == config[f"{utils.CANCEL_MAP_BTN}_color"]:
                    os.system("%CD%/bin/selectmarineford.exe")
                    break

            while True:
                listeners()
                color = pyautogui.pixel(
                    config[f"{utils.START_MAP_BTN}_pos"][0],
                    config[f"{utils.START_MAP_BTN}_pos"][1],
                )
                if color == config[f"{utils.START_MAP_BTN}_color"]:
                    os.system("%CD%/bin/startmarineford.exe")
                    break

            is_normal_camera_angle = False
            macro_parent_folder = ""

            while True:
                listeners()
                color = pyautogui.pixel(
                    config[f"{utils.START_WAVE_BTN}_pos"][0],
                    config[f"{utils.START_WAVE_BTN}_pos"][1],
                )
                if color == config[f"{utils.START_WAVE_BTN}_color"]:
                    color2 = pyautogui.pixel(
                        config[f"{utils.NORMAL_CAMERA_ANGLE_INDICATOR}_pos"][0],
                        config[f"{utils.NORMAL_CAMERA_ANGLE_INDICATOR}_pos"][1],
                    )
                    is_normal_camera_angle = utils.is_approximate_color(
                        config[f"{utils.NORMAL_CAMERA_ANGLE_INDICATOR}_color"],
                        color2,
                        20,
                    )
                    if is_normal_camera_angle:
                        print("Using NORMAL camera angle macros!")
                        macro_parent_folder = "normal"
                    else:
                        print("Using BIRD-EYE camera angle macros!")
                        macro_parent_folder = "birdeye"
                    os.system("%CD%/bin/clickwavestart.exe")
                    break

            # Listen for wave completions
            wave = 1
            files = os.listdir(f"./wave_events/{macro_parent_folder}")

            while True:
                listeners()
                color = pyautogui.pixel(
                    config[f"{utils.WAVE_COMPLETED_LABEL}_pos"][0],
                    config[f"{utils.WAVE_COMPLETED_LABEL}_pos"][1],
                )
                if color == config[f"{utils.WAVE_COMPLETED_LABEL}_color"]:
                    print(f"\tWave {wave} completed")
                    if "every_wave_completed.exe" in files:
                        os.system(
                            f"%CD%/wave_events/{macro_parent_folder}/every_wave_completed.exe"
                        )
                    wave += 1

                    if str(wave) in files:
                        wave_actions = os.listdir(
                            f"wave_events/{macro_parent_folder}/{wave}"
                        )
                        for action in wave_actions:
                            os.system(
                                f"%CD%/wave_events/{macro_parent_folder}/{wave}/{action}"
                            )
                    else:
                        print(
                            f"\t- No action found for this wave. Waiting till the end of wave {wave}..."
                        )
                    # if wave >= 2 and wave < RUN_TILL_START_OF_WAVE:
                    #     os.system("upgradeunit.exe")
                    if wave == run_till_start_of_wave:
                        runs += 1
                        os.system("%CD%/bin/closegame.exe")
                        skip_joining_private_server = False
                        break

                    s = time.time()
                    while time.time() - s <= 5:
                        detect_stop()

    def detect_stop():
        if keyboard.is_pressed("backspace"):
            now = time.time()
            seconds = int((now - time_elapsed) % 60)
            minutes = int(((now - time_elapsed) // 60) % 60)
            hours = int(((now - time_elapsed) // 3600) % 60)
            os.system("cls")
            results = [
                "",
                "Run cancelled by user.",
                "",
                "" "-----------------------------------------------",
                f"\tTotal # of runs completed: {runs}",
                f"\tTime elapsed: {hours}h {minutes}m {seconds}s",
                f"\tWaves per run: {run_till_start_of_wave - 1}",
                f"\tGames lost: {losses}",
                f"\tGames won: {runs - losses}",
                f"\tWin rate: {f'{((runs-losses)/runs)*100}%' if runs > 0 else 'N/A'}",
                f"\t# of disconnections throughout session: {disconnections}",
                "-----------------------------------------------",
            ]
            raise Exception("\n" + "\n".join(results))

    def detect_disconnection():
        global disconnections
        color = pyautogui.pixel(
            config[f"{utils.DISCONNECTED_DIALOG_BOX}_pos"][0],
            config[f"{utils.DISCONNECTED_DIALOG_BOX}_pos"][1],
        )
        roblox = win32gui.FindWindow(None, "Roblox")
        if roblox:
            tup = win32gui.GetWindowPlacement(roblox)
            if (
                color == config[f"{utils.DISCONNECTED_DIALOG_BOX}_color"]
                and tup[1] == win32con.SW_SHOWMAXIMIZED
            ):
                disconnections += 1
                print(
                    "\tDetected user has been disconnected. Attempting to reconnect..."
                )
                os.system("%CD%/bin/closegame.exe")
                while True:
                    if keyboard.is_pressed("backspace"):
                        raise Exception()
                    os.system("%CD%/bin/joinprivateserver.exe")
                    start = time.time()
                    while time.time() - start <= 1:
                        if keyboard.is_pressed("backspace"):
                            raise Exception()
                    if pyautogui.pixel(x=953, y=482) == (255, 255, 255):
                        break
                    start = time.time()
                    while time.time() - start <= 0.1:
                        if keyboard.is_pressed("backspace"):
                            raise Exception()

                    pyautogui.click(x=943, y=602)  # OK button
                execute_run(True)

    def detect_loss():
        global runs
        global losses
        color1 = pyautogui.pixel(
            config[f"{utils.DEFEAT_LABEL}_pos"][0],
            config[f"{utils.DEFEAT_LABEL}_pos"][1],
        )
        color2 = pyautogui.pixel(
            config[f"{utils.HP_BAR_ZERO}_pos"][0], config[f"{utils.HP_BAR_ZERO}_pos"][1]
        )
        if (
            color1 == config[f"{utils.DEFEAT_LABEL}_color"]
            and color2 == config[f"{utils.HP_BAR_ZERO}_color"]
        ):
            print("\tLoss detected. Redoing run...")
            runs += 1
            losses += 1
            os.system("%CD%/bin/closegame.exe")
            execute_run(False)

    def listeners():
        detect_stop()
        detect_disconnection()
        detect_loss()

    execute_run(False)


if __name__ == "__main__":
    main()
