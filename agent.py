import random
from BIS_constants import *

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


class Agent(object):
    def __init__(self, probe_range=1):
        self.fsm = None
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
        x = random.randint(-1, 1)
        y = random.randint(-1, 1)
        return x, y

    def update(self):
        # update fsm
        # emit signal based on new tpe
        self.fsm.update(self.tracker)

        # return signals to emit in Zone
        signal = []
        return signal


class PC1(Agent):
    def __init__(self, probe_range=1):
        super(PC1, self).__init__(probe_range)

        self.current_state = 2
        self.state_time = 0
        # init_state, states, transitions
        # states : list (int)
        # transitions : list (int, int, dict, dict)
        # (src, dst, signals, agents)
        self.scavenged = False
        # TODO: split for multiple signals
        self.signal_level = OutputSignal

    def update(tracker):
        signals = tracker.signals
        agents = tracker.agents

        old_state = self.current_state
        if self.current_state == 0:
            if signals['virus'] > signals[Ab1] + signals[Ab2]:
                self.current_state = 2
            elif signals[necro] > 0:
                self.current_state = 1

        elif self.current_state == 1:
            if agents[NK]:
                self.current_state = 4
            elif agents['G1']:
                self.current_state = 5
            elif self.state_time >= DURATION_stressed:
                self.current_state = 0

        elif self.current_state == 2:
            if agents[NK] or agents[T1] or agents[CTL]:
                self.current_state = 4
            elif (signals[comp] > 0 and
                  signals[comp] + signals[Ab1] > Ab1_Lysis_Threshold):
                self.current_state = 5
            elif (signals[Ab2] > 0 and
                  signals[Ab1] + signals[Ab2] > signals['virus']):
                self.current_state = 3

        elif self.current_state == 3:
            if agents[NK] or agents[T1] or agents[CTL]:
                self.current_state = 4
            elif agents['MP1'] and signals[Ab2] > 0:
                self.current_state = 5

        elif self.current_state == 4 or self.current_state == 5:
            if agents[PC] >= 2 and self.scavenged:
                self.current_state = 6

        elif self.current_state == 6:
            if self.state_time > DelayRegenerationTime:
                self.current_state = 0

        if old_state != self.current_state:
            self.state_time = 0
        else:
            self.state_time += 1

    def emit(self):
        if self.current_state == 0 or self.current_state == 6:
            return {}
        if self.current_state == 1:
            return {PK1: self.signal_level}
        if self.current_state == 2 or self.current_state == 3:
            return {PK1: self.signal_level, 'virus': self.signal_level}
        if self.current_state == 4:
            return {apop: self.signal_level}
        if self.current_state == 5:
            return {necro: self.signal_level}
