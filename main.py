import argparse
import threading

from UI.UI import UI
from controller.map_controller import MapController
from shared.command import CommandQueueCreator, LocalQueue, AskMap, SendMap, AskItemsList, SendItemsList, ChangeState, \
    LoadGame, SaveGame, CommandSender, CommandReceiver
from shared.player_map import PlayerToken, GameSettings


def handle_ui_commands(token: PlayerToken, sender: CommandSender, receiver: CommandReceiver, controller: MapController):
    while True:
        if not receiver.is_empty():
            new_command = receiver.pop()
            if isinstance(new_command, AskMap):
                sender.put(SendMap(controller.get_player_map(token)))
                continue
            if isinstance(new_command, AskItemsList):
                sender.put(SendItemsList(controller.get_player_items(token)))
                continue
            if isinstance(new_command, ChangeState):
                controller.change_state(new_command.change, token)
                continue
            if isinstance(new_command, LoadGame):
                controller.load_game()
                continue
            if isinstance(new_command, SaveGame):
                controller.save_game()
                continue


def main():
    parser = argparse.ArgumentParser(description="Roguelike application")
    parser.add_argument("--width", "-y", help="Map width", required=True, type=int)
    parser.add_argument("--height", "-x", help="Map height", required=True, type=int)
    parser.add_argument("--token", "-t", help="Player username", required=True)

    args = parser.parse_args()

    controller_commands = CommandQueueCreator(LocalQueue())
    ui_commands = CommandQueueCreator(LocalQueue())

    token = PlayerToken(args.token)

    controller = MapController(token, GameSettings(args.height, args.width))

    ui = UI(controller_commands.get_receiver(), ui_commands.get_sender())

    input_commands = ui_commands.get_receiver()
    output_commands = controller_commands.get_sender()

    controller_thread = threading.Thread(target=handle_ui_commands,
                                         args=(token, output_commands, input_commands, controller))
    controller_thread.start()
    ui.start()


if __name__ == "__main__":
    main()
