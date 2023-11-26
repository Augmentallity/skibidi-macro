import json

LOBBY_PLAY_BTN_PROP = "lobby_play_btn"
CANCEL_MAP_BTN = "cancel_map_btn"
START_MAP_BTN = "start_map_btn"
START_WAVE_BTN = "start_wave_btn"
WAVE_COMPLETED_LABEL = "wave_cmplt_label"
DISCONNECTED_DIALOG_BOX = "disconnected_dialog_box"
DEFEAT_LABEL = "defeat_label"
HP_BAR_ZERO = "hp_zero_bar"
NORMAL_CAMERA_ANGLE_INDICATOR = "normal_camera_detector"

DEFAULT_CONFIG = {
    "waves_per_run": 10,
    f"{LOBBY_PLAY_BTN_PROP}_pos": (160, 497),
    f"{LOBBY_PLAY_BTN_PROP}_color": (32, 242, 235),
    f"{CANCEL_MAP_BTN}_pos": (961, 878),
    f"{CANCEL_MAP_BTN}_color": (238, 0, 0),
    f"{START_MAP_BTN}_pos": (1053, 797),
    f"{START_MAP_BTN}_color": (48, 234, 0),
    f"{START_WAVE_BTN}_pos": (934, 178),
    f"{START_WAVE_BTN}_color": (37, 208, 0),
    f"{WAVE_COMPLETED_LABEL}_pos": (1205, 774),
    f"{WAVE_COMPLETED_LABEL}_color": (95, 255, 71),
    f"{DISCONNECTED_DIALOG_BOX}_pos": (987, 619),
    f"{DISCONNECTED_DIALOG_BOX}_color": (57, 59, 61),
    f"{DEFEAT_LABEL}_pos": (615, 284),
    f"{DEFEAT_LABEL}_color": (222, 0, 0),
    f"{HP_BAR_ZERO}_pos": (603, 67),
    f"{HP_BAR_ZERO}_color": (25, 22, 22),
    f"{NORMAL_CAMERA_ANGLE_INDICATOR}_pos": (1370, 144),
    f"{NORMAL_CAMERA_ANGLE_INDICATOR}_color": (16, 71, 132),
}


def merge_with_default_config(config: dict[str, any]):
    for key in DEFAULT_CONFIG:
        if key not in config:
            config[key] = DEFAULT_CONFIG[key]


def read_config() -> dict[str, any]:
    try:
        file = open("animeadventures.config", "r+")
        config = {}
        for line in file:
            (prop, value) = line.split("=")
            config[prop] = eval(value)
        merge_with_default_config(config)
        return config
    except:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG


def save_config(config: dict[str, str]):
    file = open("animeadventures.config", "w+")
    contents = []
    for key, value in config.items():
        contents.append(f"{key}={value}")
    file.write("\n".join(contents))


macros = None


def read_macros() -> list[dict[str]]:
    """
    Reads the macros from macros.json

    Returns:
        A list containing macro objects
    """
    global macros
    if macros == None:
        try:
            with open("macros.json", "r+") as file:
                macros = json.load(file)
        except:
            with open("macros.json", "w+") as file:
                macros = []
                file.write("[]")

    return macros


def write_macros(_macros: list[dict[str]] = read_macros()):
    global macros
    macros = _macros
    with open("macros.json", "w+") as file:
        file.write(json.dumps(_macros))
    macros


def is_approximate_color(
    color1: tuple[int, int, int], color2: tuple[int, int, int], difference: int
):
    return (
        abs(color1[0] - color2[0]) <= difference
        and abs(color1[1] - color2[1]) <= difference
        and abs(color1[2] - color2[2]) <= difference
    )


def to_human_time(d: int | float):
    seconds = round(d % 60)
    minutes = round((d / 60) % 60)
    hours = round((d / 3600) % 60)
    return f"{hours}h {minutes}m {seconds}s"
