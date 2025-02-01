from action import Action
from state import State
from typing import Callable

class Agent:
    STATES: list[State] = [] # Override this in the subclass
    ACTIONS: list[Action] = {} # Override this in the subclass
    ACTION_ON_STATE_CHANGE: dict[State, Action] = {} # Override this in the subclass

    def __class__valid():
        assert len(Agent.STATES) > 0, "STATES must be overridden in the subclass"
        assert len(Agent.ACTIONS) > 0, "ACTIONS must be overridden in the subclass"
        assert len(Agent.ACTION_ON_STATE_CHANGE) == len(Agent.STATES), "ACTION_ON_STATE_CHANGE must be overridden in the subclass"
        assert all([state in Agent.ACTION_ON_STATE_CHANGE for state in Agent.STATES]), "ACTION_ON_STATE_CHANGE must be overridden in the subclass"]
        assert all([action in Agent.ACTIONS for action in Agent.ACTION_ON_STATE_CHANGE.values()]), "ACTION_ON_STATE_CHANGE must be overridden in the subclass"]

    def __init__(self):
        self.state: str = ""
        self.action_queue: list[Action] = []

    def change_state(self, new_state: State):
        if new_state not in self.STATES:
            raise ValueError(f"Invalid state: {new_state}")
        self.state = new_state
        Agent.ACTIONS[Agent.ACTION_ON_STATE_CHANGE[new_state]]()

        


        
