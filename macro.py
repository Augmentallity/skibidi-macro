class Macro_Type:
    CLICK = 0
    WAIT = 1
    WAIT_CONDITIONALLY = 2
    KEY_UP = 3
    KEY_DOWN = 4
    KEY_PRESS = 5


MAPPED_TYPES = {
    Macro_Type.CLICK: "Click",
    Macro_Type.WAIT: "Wait",
    Macro_Type.WAIT_CONDITIONALLY: "Wait (Conditional)",
    Macro_Type.KEY_UP: "Key Up",
    Macro_Type.KEY_DOWN: "Key Down",
    Macro_Type.KEY_PRESS: "Key Press",
}
