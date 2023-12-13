class Macro_Type:
    CLICK = 0
    WAIT = 1
    WAIT_CONDITIONALLY = 2
    KEY_UP = 3
    KEY_DOWN = 4
    KEY_PRESS = 5
    REPEAT_LINES = 6
    TINY_TASK = 7
    GLOBAL_TINY_TASK = 8
    LISTENER = 9


MAPPED_TYPES = {
    Macro_Type.CLICK: "Click",
    Macro_Type.WAIT: "Wait",
    Macro_Type.WAIT_CONDITIONALLY: "Wait (Conditional)",
    Macro_Type.KEY_UP: "Key Up",
    Macro_Type.KEY_DOWN: "Key Down",
    Macro_Type.KEY_PRESS: "Key Press",
    Macro_Type.REPEAT_LINES: "Repeat Lines",
    Macro_Type.TINY_TASK: "Tiny Task",
    Macro_Type.GLOBAL_TINY_TASK: "Tiny Task (/bin)",
    Macro_Type.LISTENER: "Event Listener",
}


def get_seq_macro_str(x: dict[str], i: int):
    match x["type"]:
        case Macro_Type.CLICK:
            return f"[{i + 1}]\t{MAPPED_TYPES[Macro_Type.CLICK]}({x['position'][0]}, {x['position'][1]}) {'- Joins private server' if x['should_fullscreen_roblox'] else ''}"
        case Macro_Type.WAIT:
            return f"[{i + 1}]\t{MAPPED_TYPES[Macro_Type.WAIT]}({x['ms']}ms)"
        case Macro_Type.WAIT_CONDITIONALLY:
            return f"[{i + 1}]\t{MAPPED_TYPES[Macro_Type.WAIT_CONDITIONALLY]}({x['position'][0]}, {x['position'][1]}) - rgb({x['color'][0]}, {x['color'][1]}, {x['color'][2]})"
        case Macro_Type.KEY_PRESS:
            return f"[{i + 1}]\t{MAPPED_TYPES[Macro_Type.KEY_PRESS]}({str(x['key'])})"
        case Macro_Type.KEY_UP:
            return f"[{i + 1}]\t{MAPPED_TYPES[Macro_Type.KEY_UP]}({str(x['key'])})"
        case Macro_Type.KEY_DOWN:
            return f"[{i + 1}]\t{MAPPED_TYPES[Macro_Type.KEY_DOWN]}({str(x['key'])})"
        case Macro_Type.REPEAT_LINES:
            return (
                f"[{i + 1}]\t{MAPPED_TYPES[Macro_Type.REPEAT_LINES]} from #{x['lines'][0]} to #{x['lines'][1]} "
                + (
                    f"for {x['ms']}ms"
                    if x["repeat_type"] == "timer"
                    else f"up to {x['iters']} time(s)"
                )
            )
        case Macro_Type.TINY_TASK:
            return f"[{i + 1}]\t{MAPPED_TYPES[Macro_Type.TINY_TASK]} Macro"
        case Macro_Type.GLOBAL_TINY_TASK:
            return f"[{i + 1}]\t{MAPPED_TYPES[Macro_Type.GLOBAL_TINY_TASK]} Macro ({x['file_name']})"
        case Macro_Type.LISTENER:
            return f"[{i + 1}]\t{MAPPED_TYPES[Macro_Type.LISTENER]} ({x['name']})"
        case _:
            return x["type"]
