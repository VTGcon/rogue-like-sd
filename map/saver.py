import pickle
import os.path
import os


class MapSaver:
    """
        Creates a MapSaver object, providing ability to save game sessions locally.
    """
    def __init__(self):
        self.filename = "saved.rgl"

    """
        Saves session.
    """
    def save(self, session):
        with open(self.filename, "wb") as file:
            pickle.dump(session, file)

    """
        Loads previous session from file.
    """
    def load(self):
        with open(self.filename, "rb") as file:
            result = pickle.load(file)
        return result

    """
        Returns true if previous session exists saved.
    """
    def exist_saved(self):
        return os.path.exists(self.filename)

    """
        Removes the previous session information.
    """
    def remove_saved(self):
        return os.remove(self.filename)
