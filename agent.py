import random

class Signal:
    pass


class SignalTracker:
    def __init__(self):
        self.signals = {
            'CK1': 0,
            'CK2': 0
        }
        self.agents = {
            'DC1': False,
            'DC2': False,
        }

    def reset(self):
        for signal in self.signals:
            self.signals[signal] = 0
        for agent in self.agents:
            self.agents[agent] = False


class FSM:
    """

    Attributes
    ----------
    init_state : int
    states : list (int)
    transitions : list (int, int, dict, dict)
        (src, dst, signals, agents)

    """
    def __init__(self, init_state, states, transitions):
        self.current = init_state
        self.states = states
        self.transitions = transitions

    def update(self, tracker):
        passed = []
        for tn in transitions:
            if tn[0] == self.current:
                signals_passed = True
                for signal in tn[2].keys():
                    if tracker[signal] <= tn[2][signal]:
                        signals_passed = False

                agents_passed = True
                for agent in tn[3].keys():
                    if tracker[agent] != tn[3][agent]:
                        agents_passed = False

                if signals_passed and agents_passed:
                    passed.append(tn[1])

        if len(passed) > 1:
            self.current = passed(random.randint(0, len(passed) - 1))
        elif len(passed) == 1:
            self.current = passed[0]


class Agent:
    def __init__(self, fsm=None, probe_range=1):
        self.fsm = fsm
        self.state = None  # TODO: init state
        self.probe_range = probe_range
        self.tracker = SignalTracker()
        self.signals = {} # Dict {state: (signal, value)}
        self.kind = ""
        # self.life
        # self.duration

    def probe(self, boxes):
        for box in boxes:
            for agent in box.agents:
                self.tracker[agent.kind] = True
            for signal in box.signals:
                self.tracker[signal.kind] += signal.value

        # TODO: calculate movment
        # Return number of cells to move horiz/vert
        x = -1
        y = 1
        return x, y

    def update(self):
        # update fsm
        # emit signal based on new tpe
        self.fsm.update(self.tracker)

        # return signals to emit in Zone
        signal = []
        return signal

