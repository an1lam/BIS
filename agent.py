import random
from BIS_constants import *
import numpy as np  
import pdb


class Signal:
    pass


class SignalTracker:
    def __init__(self):
        self.signals = {
            PK1: 0,
            virus: 0,
            apop: 0,
            necro: 0,
            MK1: 0,
            MK2: 0,
            CK1: 0,
            CK2: 0,
            Ab1: 0,
            Ab2: 0,
            comp: 0,
            G1: 0,
        }
        self.agents = {
            PC_agt: [],
            DC1: [],
            DC2: [],
            MP_agt: [],
            T: [],
            T1: [],
            T2: [],
            CTL: [],
            NK_agt: [],
            B: [],
            B1: [],
            B2: [],
            Gran: [],
            portal: []
        }

    def __repr__(self):
        return "Virus: %d\tPK1: %d\n" % (self.signals[virus], self.signals[PK1]) + str(self.agents[MP_agt]) + '\n' + str(self.agents[NK_agt])

    def reset(self):
        for signal in self.signals:
            self.signals[signal] = 0
        for agent in self.agents:
            self.agents[agent] = []


class Agent(object):
    def __init__(self, probe_range=1):
        self.fsm = None
        self.state = None  # TODO: init state
        self.probe_range = probe_range
        self.tracker = SignalTracker()
        self.signals = {}  # Dict {state: (signal, value)}
        self.kind = ""
        self.next_x = 0
        self.next_y = 0

    def probe(self, boxes):
        self.tracker = SignalTracker()
        for box in boxes:
            for agt_type in box.agents:
                for agt in box.agents[agt_type]:
                    if agt is not self:
                        self.tracker.agents[agt_type].append(agt)
                # self.tracker.agents[agt_type] += box.agents[agt_type]
            for signal in box.signals:
                self.tracker.signals[signal] += box.signals[signal]

        # TODO: calculate movement
        # Return number of cells to move horiz/vert
        self.next_x = random.randint(-1, 1)
        self.next_y = random.randint(-1, 1)
        # return x, y

    def move(self):
        return self.next_x, self.next_y

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

        self.agent_type = PC_agt
        self.current_state = 0
        self.state_time = 0
        # init_state, states, transitions
        # states : list (int)
        # transitions : list (int, int, dict, dict)
        # (src, dst, signals, agents)
        # self.scavenged = False
        # self.alive = True
        # self.infected = False
        # TODO: split for multiple signals
        self.signal_level = OutputSignal
        self.kind = PC_agt

    # def probe(self, boxes):
        # super(PC1, self).probe(boxes)
        # return 0, 0

    def move(self):
        return 0, 0

    def update(self):
        signals = self.tracker.signals
        agents = self.tracker.agents

        old_state = self.current_state
        # pdb.set_trace()
        if self.current_state == 0:
            # self.infected = False
            # self.alive = True
            # if signals['virus'] > 0:
            if signals['virus'] > Viral_Infection_Threshold:
                # self.infected = True
                self.current_state = 2
            elif signals[apop] > 0:
                self.current_state = 1

        elif self.current_state == 1:
            if agents[NK_agt]:
                # print "Found NK"
                for nk in agents[NK_agt]:
                    if nk.make_kill():
                        # print "NK killing PC_agt"
                        self.current_state = 4
                        break
            # elif agents[G1]:
                # self.current_state = 5
            elif self.state_time >= DURATION_Stressed:
                self.current_state = 0

        elif self.current_state == 2:
            if agents[NK_agt] or agents[T1] or agents[CTL]:
                for nk in agents[NK_agt]:
                    if nk.make_kill():
                        # print "NK killing PC_agt"
                        self.current_state = 4
                        break
            elif (signals[comp] > 0 and
                  signals[comp] + signals[Ab1] > Ab1_Lysis_Threshold):
                self.current_state = 5
            # elif (signals[Ab2] > 0 and
                  # signals[Ab1] + signals[Ab2] > signals['virus']):
            elif random.randint(1,10) > 8:
                self.current_state = 3

        elif self.current_state == 3:
            if agents[NK_agt] or agents[T1] or agents[CTL]:
                # pdb.set_trace()
                for nk in agents[NK_agt]:
                    if nk.make_kill():
                        # print "NK killing PC_agt"
                        self.current_state = 4
                        break
                # self.current_state = 4
            # elif agents[MP1] and signals[Ab2] > 0:
            # elif agents[MP1]:
            elif MP1 in [agent.kind for agent in agents[MP_agt]]:
                self.current_state = 5

        elif self.current_state == 4 or self.current_state == 5:
            # pdb.set_trace()
            # if len(agents[PC_agt]) >= 2 and self.scavenged:
            # if self.state_time > 3:
            # if any([agt.scavenging() for agt in agents[MP_agt]]):
            if len([agt for agt in agents[PC_agt] if agt.alive()]) >= 2:
                for mp in agents[MP_agt]:
                    if mp.scavenging():
                        # print "scavenged"
                        self.current_state = 6
                        break

        elif self.current_state == 6:
            if self.state_time > DelayRegenerationTime:
                self.current_state = 0

        if old_state != self.current_state:
            # if self.current_state == 0:
                # pdb.set_trace()
            self.state_time = 0
        else:
            self.state_time += 1

    def emit(self):
        if self.current_state == 0 or self.current_state == 6:
            return {}
        if self.current_state == 1:
            return {PK1: self.signal_level}
        if self.current_state == 2 or self.current_state == 3:
            if self.state_time == 10:
                return {PK1: self.signal_level, 'virus': Viral_Output_Signal}
            else:
                return {PK1: self.signal_level}
            # return {PK1: self.signal_level}
        if self.current_state == 4:
            return {apop: self.signal_level}
        if self.current_state == 5:
            return {necro: self.signal_level}

    def alive(self):
        return self.current_state != 4 and self.current_state != 5 and self.current_state != 6

    def infected(self):
        return self.current_state == 2 or self.current_state == 3


class MP(Agent):
    def __init__(self, probe_range=1):
        super(MP, self).__init__(probe_range)

        self.type = MP_agt
        self.current_state = 0
        self.state_time = 0
        self.zone_time = 0
        self.signal_time = 0

        self.kind = MP0
        # init_state, states, transitions
        # states : list (int)
        # transitions : list (int, int, dict, dict)
        # (src, dst, signals, agents)

        self.signal_level = OutputSignal

    def move(self):
        if self.current_state == 5:
            return 0, 0
        else:
            return self.next_x, self.next_y

    def update(self):
        signals = self.tracker.signals
        agents = self.tracker.agents

        old_state = self.current_state

        # If we sense any Parenchymal or Cytokine signals, start hunting
        if self.current_state == 0:
            if (signals[PK1] > 0 or signals[CK1] > 0 or signals[comp] > 0 or
                    signals[necro] > 0):
                self.current_state = 1
            elif signals[apop] > 0 or signals[Ab1] > 0 or signals[Ab2] > 0:
                self.current_state = 2

        # Look for PCs to destroy or scavenge.
        # Destroy PCs if antibodies or infected cells detected.
        elif self.current_state == 1:
            self.kind = MP1
            if len(agents[PC_agt]) > 0:
                # for pc1 in agents[PC_agt]:
                    # if pc1.infected() or signals[Ab2] > 0:
                        # print "MP killing PC_agt"
                        # pc1.alive = False
                        # pc1.necro()

                # Reset signal time and therefore keep emitting MK1.
                self.signal_time = -1
                self.current_state = 3

        # Emit MP2 (dampening) signals. Only scavenge, don't kill.
        elif self.current_state == 2:
            self.kind = MP2
            if len(agents[PC_agt]) > 0:
                # for pc1 in agents[PC_agt]:
                    # if not (pc1.alive() or pc1.scavenged):
                        # pc1.scavenged = True
                self.current_state = 4

        # Scavenge, reset lifespan if T Cells with Ab discovered, and kill
        # PCs if Ab2 around. Killing / scavenging extend signal emission time.
        elif self.current_state == 3:
            if agents[PC_agt]:
                for pc1 in agents[PC_agt]:
                    # Kill Ab2-opsonized cells.
                    if pc1.alive() and signals[Ab2] > 0:
                        # pc1.alive = False
                        self.signal_time = -1

                    # Scavenge dead, un-scavenged PC cells.
                    # elif not (pc1.alive() or pc1.scavenged):
                        # pc1.scavenged = True
                        # self.signal_time = -1

            elif len(agents[T1]) > 0:
                self.zone_time = 0
            elif signals[CK1] > signals[CK2] and signals[apop]:
                self.current_state = 4

        elif self.current_state == 4:
            if len(agents[T2]) > 0:
                self.zone_time = 0

        if old_state != self.current_state:
            self.state_time = 0
        else:
            self.state_time += 1

        self.zone_time += 1
        self.signal_time += 1

        if self.zone_time > LIFE_MO_Zone1:
            self.current_state = 5

    def emit(self):
        if self.kind == MP1 and self.signal_time > DURATION_MK1_Zone1:
            self.signal_level = 0
        elif self.kind == MP2 and self.signal_time > DURATION_MK2_Zone1:
            self.signal_level = 0
        else:
            self.signal_level = OutputSignal

        if self.current_state == 0:
            return {}
        elif self.current_state == 1 or self.current_state == 3:
            return {MK1: self.signal_level}
        elif self.current_state == 2 or self.current_state == 4:
            return {MK2: self.signal_level}
        elif self.current_state == 5:
            return {apop: self.signal_level}

    def scavenging(self):
        if self.current_state == 1 or self.current_state == 2:
            self.current_state += 2
            self.signal_time = 0
            return True
        elif self.current_state == 3 or self.current_state == 4:
            return True
        else:
            return False

    def probe(self, boxes):
        super(MP, self).probe(boxes)

        PK1_map = [box.signals[PK1] for box in boxes]
        PK1_map = np.reshape(PK1_map, (3, 3))
        PK1_max = np.max(PK1_map)

        self.next_x = np.where(PK1_map == PK1_max)[0][0] - 1
        self.next_y = np.where(PK1_map == PK1_max)[1][0] - 1


# A natural killer cell model, typically found in the innate immune system
class NK(Agent):
    def __init__(self, probe_range=1):
        super(NK, self).__init__(probe_range)

        self.type = NK_agt
        self.current_state = 0
        # Number of ticks since initialization or reset
        self.zone_time = 0

        # Number of ticks since last PC kill
        self.last_kill_time = 0

        self.num_killed = 0

        # Number of ticks we've remained in this state
        self.state_time = 0
        self.signal_level = OutputSignal
        self.displayed_antigen = None

    def move(self):
        if self.current_state == 2:
            return 0, 0
        else:
            return self.next_x, self.next_y

    def update(self):

        old_state = self.current_state

        # either detects PK1 and transitions or
        # dies after a prescribed number of ticks
        if self.current_state == 0:
            if self.tracker.signals[PK1]:
                self.current_state = 1
            # self.last_kill_time += 1
        elif self.current_state == 1:
            # if any([agt.alive() for agt in self.tracker.agents[PC_agt]]):
            # # if self.tracker.agents[PC_agt] and self.tracker.signals[PK1] > self.tracker.signals[CK2]:
                # print "NK killing PC_agt"
                # for pc1 in self.tracker.agents[PC_agt]:
                    # # pc1.alive = False
                    # self.num_killed += 1
                    # self.last_kill_time = 0
                    # break
            # else:
                # self.last_kill_time += 1

            if self.num_killed > 0:
                self.last_kill_time += 1

            if self.state_time > DURATION_NK_CK1:
                self.current_state = 0

        # Increment state time and zone time
        if old_state != self.current_state:
            self.state_time = 0
        else:
            self.state_time += 1

        self.zone_time += 1

        if (self.num_killed > NK_KILL_LIMIT or
                self.zone_time > LIFE_NK_Zone1 or
                self.last_kill_time > NUM_TICKS_NK_NO_KILL):
            self.current_state = 2

    def make_kill(self):
        # TODO: check PK1 and CK2 levels
        if self.current_state == 1:
            self.num_killed += 1
            self.last_kill_time = 0
            return True
        else:
            return False

    def emit(self):
        if self.current_state == 0:
            return {}
        elif self.current_state == 1:
            return {CK1: self.signal_level}
        elif self.current_state == 2:
            return {apop: self.signal_level}

    def probe(self, boxes):
        super(NK, self).probe(boxes)

        PK1_map = [box.signals[PK1] for box in boxes]
        PK1_map = np.reshape(PK1_map, (3, 3))
        PK1_max = np.max(PK1_map)

        self.next_x = np.where(PK1_map == PK1_max)[0][0] - 1
        self.next_y = np.where(PK1_map == PK1_max)[1][0] - 1

# class DC(Agent):
    # def __init__(self, probe_range=1):
        # self.current_state = 0  # TODO: init state
        # self.probe_range = probe_range
        # self.tracker = SignalTracker()
        # self.kind = ""
        # self.next_x = 0
        # self.next_y = 0

    # def update(self):
        # # Simplifying model to eliminate DC2 since no innate cells
        # # respond to MK2
        # # Valid states: 0, 1, 6, 2
        
        # signals = self.tracker.signals
        # agents = self.tracker.agents

        # old_state = self.current_state

        # if self.current_state == 0:
            # if signals[virus] > 200:
                # self.current_state = 2
            # elif signasl[PK1] > 0:
                # self.current_state = 1
        # elif self.current_state == 1:
            # if signals[virus] > 0 or any([pc.infected() for 




