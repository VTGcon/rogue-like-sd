import queue
from abc import ABC

from shared.player_map import StateChange, PlayerMap


class CommandQueue:
    """
       Queue for exchanging Commands.
    """

    def is_empty(self):
        pass

    def pop(self):
        pass

    def put(self, element):
        pass


class CommandSender:
    """
        CommandQueue interface allowing only writing to queue.
    """

    def __init__(self, queue: CommandQueue):
        self.__queue = queue

    def put(self, element):
        """
        Writes element to queue.
        :param element: element to be added to queue.
        """
        self.__queue.put(element)


class CommandReceiver:
    """
        CommandQueue interface allowing only reading from queue.
    """

    def __init__(self, queue: CommandQueue):
        self.__queue = queue

    def is_empty(self):
        """
        Checks if queue is empty
        :return: true if it is, false otherwise.
        """
        return self.__queue.is_empty()

    def pop(self):
        """
        Pops head element from the queue.
        :return: popped element.
        """
        return self.__queue.pop()


class CommandQueueCreator:
    """
        Class creating sender and receiver interfaces from given queue.
    """

    def __init__(self, queue: CommandQueue):
        self.__queue = queue

    def get_sender(self):
        return CommandSender(self.__queue)

    def get_receiver(self):
        return CommandReceiver(self.__queue)


class LocalQueue(CommandQueue):
    """
        CommandQueue implementation based on the python queue. Enough for local communication.
    """

    def __init__(self):
        self.__queue = queue.Queue()

    def pop(self):
        """
        Pops head element from the queue.
        :return: popped element.
        """
        return self.__queue.get()

    def is_empty(self):
        """
        Checks if queue is empty
        :return: true if it is, false otherwise.
        """
        return self.__queue.empty()

    def put(self, element):
        """
        Writes element to queue.
        :param element: element to be added to queue.
        """

        self.__queue.put(element)


class Command(ABC):
    """
        Abstract class for commands between ui and controller
    """


class ChangeState(Command):
    """
        Send controller user move
    """

    def __init__(self, change: StateChange):
        self.change = change


class AskMap(Command):
    """
        Asking controller about map
    """


class AskItemsList(Command):
    """
        Asking controller about items list
    """


class SendMap(Command):
    """
        Sending players map in response to AskMap
    """

    def __init__(self, player_map: PlayerMap):
        self.map = player_map


class SendItemsList(Command):
    """
        Sending players map in response to AskMap
    """

    def __init__(self, items):
        self.items = items


class LoadGame(Command):
    """
        Load saved game request.
    """


class SaveGame(Command):
    """
        Save current game request.
    """
