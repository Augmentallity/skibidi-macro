from macro import Macro_Type
import os
import menu
import utils


def delete_seq_macro(macro_id: str, macro_seq_name: str, _id: str):
    macro = get_macro(macro_id)
    i = 0
    while i < len(macro[macro_seq_name]):
        if macro[macro_seq_name][i]["id"] == _id:
            break
        i += 1

    del macro[macro_seq_name][i]
    utils.write_macros()
    on_macro_change(macro_id, macro_seq_name)
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


def on_macro_change(macro_id: str, macro_type: str):
    macro = get_macro(macro_id)
    for i, seq_macro in enumerate(macro[macro_type]):
        if seq_macro["type"] == Macro_Type.TINY_TASK:
            old_idx: int = seq_macro["idx"]
            if old_idx != i:
                os.rename(
                    f"{os.getcwd()}\\macros\\{macro_id}\\{old_idx + 1}.exe",
                    f"{os.getcwd()}\\macros\\{macro_id}\\tmp_{old_idx + 1}.exe",
                )
    for i, seq_macro in enumerate(macro[macro_type]):
        if seq_macro["type"] == Macro_Type.TINY_TASK:
            old_idx: int = seq_macro["idx"]
            if old_idx != i:
                os.rename(
                    f"{os.getcwd()}\\macros\\{macro_id}\\tmp_{old_idx + 1}.exe",
                    f"{os.getcwd()}\\macros\\{macro_id}\\{i + 1}.exe",
                )
                seq_macro["idx"] = i
