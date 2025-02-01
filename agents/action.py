from enum import Enum

class Action:
    def __init__(self,
                 name: Enum = None,
                 description: str = None,
                 attributes: dict[str, str] = None,
    ):
        self.name = name
        self.description = description
        self.attributes = attributes

    def __eq__(self, other):
        if not isinstance(other, Action):
            return False
        return self.name == other.name and self.attributes == other.attributes