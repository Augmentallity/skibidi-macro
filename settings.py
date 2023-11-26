import menu
import utils
import threading


def main():
    m = menu.Menu("Settings")
    m.item(
        menu.MenuItem(
            lambda: f"Waves Per Run : {utils.read_config()['waves_per_run']}",
            waves_per_run,
        )
    )
    m.header("Settings")
    m.show()


def waves_per_run():
    config = utils.read_config()
    print(f"Current value: {config['waves_per_run']}")
    val = input("New value (leave blank to not edit): ")
    parsed = val.strip()
    if len(parsed) > 0 and parsed.isnumeric():
        config["waves_per_run"] = int(parsed)
        utils.save_config(config)
