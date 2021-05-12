
class StateHandler:
    def __init__(self, original_state):
        self.evaluate = None
        self.entry = None
        self.exit = None
        self.parent = None
        self.children = []
        self.original_state = original_state

