from pusta.generator.model import StateHandler

class CStateHandler(StateHandler):
    def __init__(self, original_state):
        super().__init__(original_state)
        self.enumerator = None
