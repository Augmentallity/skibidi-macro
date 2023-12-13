import menu
import settings
import in_game_macros
import event_listeners

if __name__ == "__main__":
    m = menu.Menu("Home")
    m.header("Configuration Tool for Anime Adventures Macros")
    m.item(menu.MenuItem("Event Listener Macros", event_listeners.main))
    m.item(menu.MenuItem("In-Game Macros", in_game_macros.main))
    m.item(menu.MenuItem("Settings", settings.main))
    m.show()
