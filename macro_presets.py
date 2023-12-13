import menu
import macro_edit
import utils


def use_quick_play_map(macro_id: str):
    macro = macro_edit.get_macro(macro_id)
    macro["lobby_sequence"] = [
        {
            "id": "3ac6fcbf-32b2-447c-a074-67a3e16e8f6c",
            "type": 0,
            "position": [491, 931],
            "should_fullscreen_roblox": True,
        },
        {
            "type": 9,
            "id": "d6983152-a6e9-4c3c-b897-73fc2bc2f978",
            "name": "Play Button Listener",
        },
        {
            "id": "c8a50e04-3656-46e3-91e7-6385d44d722d",
            "type": 8,
            "file_name": "clickplay.exe",
        },
        {"id": "4cfafb2c-7481-4215-a6c6-eede5268bf5c", "type": 4, "key": "'w'"},
        {"id": "5d3f5875-6cea-46e4-b605-4eee91944b5d", "type": 4, "key": "Key.shift"},
        {"id": "c1a65c5a-55b7-46fb-be8b-a3f344cb6b81", "type": 4, "key": "'d'"},
        {"type": 1, "id": "66d94221-6574-4a9f-9081-bac3d6e7d01e", "ms": 1750},
        {"id": "4ae7ed77-82dc-41be-9580-de047fb5b9f4", "type": 3, "key": "Key.shift"},
        {"id": "91cb32ce-6179-455f-a7cb-695ed8b5f6ae", "type": 3, "key": "'d'"},
        {"id": "7fb4b0ce-fb77-45e6-9bcf-174c38af377a", "type": 4, "key": "'a'"},
        {"type": 1, "id": "e6ad0235-a559-46df-a1ce-9a3be17be803", "ms": 10},
        {"id": "0548d7b8-c5dc-40c5-9aad-deff29bdec4b", "type": 3, "key": "'a'"},
        {"id": "b90da746-29f0-4375-b40b-94c7e6a52421", "type": 4, "key": "'d'"},
        {"type": 1, "id": "41a8108b-7637-4c54-a42b-9b0e1a13a739", "ms": 10},
        {
            "type": 6,
            "id": "534e8807-e26a-4e57-a1b8-f6ea065917a2",
            "repeat_type": "timer",
            "lines": [9, 14],
            "ms": 500,
        },
        {"id": "a5e4f4f9-333c-479d-9481-d346ea241d96", "type": 3, "key": "'d'"},
        {"id": "f7ceb6b3-8ccd-4875-8a16-35d2256206d3", "type": 3, "key": "'w'"},
        {
            "type": 9,
            "id": "704f869b-10dd-47cf-9554-dd0aabc42f91",
            "name": "Map Menu Listener",
        },
        {"type": 7, "id": "99d783ac-4343-4879-82ea-4eac4f27a423", "idx": 18},
        {
            "type": 9,
            "id": "5178c8b8-e97a-444f-bc19-95a2e84888a1",
            "name": "Start Map Listener",
        },
        {
            "id": "cf1061b4-ff37-4148-8cc9-9f94bf5e246b",
            "type": 8,
            "file_name": "startmap.exe",
        },
    ]
    utils.write_macros()
    menu.stack.pop()


def main(macro_id: str):
    m = menu.Menu("Lobby Presets")
    m.item(menu.MenuItem("Use 'Quick Play Map'", lambda: use_quick_play_map(macro_id)))
    m.item(menu.MenuItem("Back", lambda: menu.stack.pop()))
    m.show()
