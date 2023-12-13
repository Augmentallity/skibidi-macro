import menu
import utils
import threading


def main():
    m = menu.Menu("Settings")
    m.item(
        menu.MenuItem(
            lambda: f"Reconnection interval: {utils.read_config()['reconnection_attempt_interval']} seconds",
            reconnection_interval,
            description="The interval in which the program checks for internet availability. Necessary for relaunching Roblox after disconnection.",
        )
    )
    m.header("Settings")
    m.show()


def reconnection_interval():
    config = utils.read_config()
    print(f"Current value: {config['reconnection_attempt_interval']}")
    val = input("New value (leave blank to not edit): ").strip()
    if len(val) > 0 and val.isnumeric():
        config["reconnection_attempt_interval"] = val
        utils.save_config(config)
