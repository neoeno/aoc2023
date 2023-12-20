from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
import re
from typing import Any, Literal, NamedTuple, Self, Union

from utility.main import check, every_line, pret, tlog

Signal = Enum("Signal", ["HIGH", "LOW"])

@dataclass
class Node:
    name: str = ""
    children: list[Self] = field(default_factory=list)

    def process(self, signal: Any) -> Any: # What??
        return []

    def add_inbound(self, node: Self):
        return None

@dataclass
class SignalFire:
    src: Node
    dest: Node
    value: Signal

@dataclass
class BroadcasterNode(Node):
    def process(self, signal: SignalFire) -> list[SignalFire]:
        return [SignalFire(self, child, signal.value) for child in self.children]


my_parent = Node()
my_node_a = Node()
my_node_b = Node()
my_broadcaster = BroadcasterNode("bn", [my_node_a, my_node_b])
check(my_broadcaster.process(SignalFire(my_parent, my_broadcaster, Signal.HIGH)), [
    SignalFire(my_broadcaster, my_node_a, Signal.HIGH),
    SignalFire(my_broadcaster, my_node_b, Signal.HIGH),
])
check(my_broadcaster.process(SignalFire(my_parent, my_broadcaster, Signal.LOW)), [
    SignalFire(my_broadcaster, my_node_a, Signal.LOW),
    SignalFire(my_broadcaster, my_node_b, Signal.LOW),
])

@dataclass
class FlipFlopNode(Node):
    state: bool = False

    def process(self, signal: SignalFire) -> list[SignalFire]:
        if signal.value == Signal.LOW:
            self.state = not self.state
            if self.state == True:
                return [SignalFire(self, child, Signal.HIGH) for child in self.children]
            else:
                return [SignalFire(self, child, Signal.LOW) for child in self.children]
        return []

my_node_a = Node()
my_node_b = Node()
my_flipper = FlipFlopNode("fn", [my_node_a, my_node_b])
check(my_flipper.process(SignalFire(my_parent, my_flipper, Signal.HIGH)), [])
check(my_flipper.process(SignalFire(my_parent, my_flipper, Signal.LOW)), [
    SignalFire(my_flipper, my_node_a, Signal.HIGH),
    SignalFire(my_flipper, my_node_b, Signal.HIGH),
])
check(my_flipper.process(SignalFire(my_parent, my_flipper, Signal.HIGH)), [])
check(my_flipper.process(SignalFire(my_parent, my_flipper, Signal.LOW)), [
    SignalFire(my_flipper, my_node_a, Signal.LOW),
    SignalFire(my_flipper, my_node_b, Signal.LOW),
])

@dataclass
class ConjunctionNode(Node):
    state: dict[str, Signal] = field(default_factory=dict)

    def process(self, signal: SignalFire) -> list[SignalFire]:
        self.state[signal.src.name] = signal.value
        if all(value == Signal.HIGH for value in self.state.values()):
            return [SignalFire(self, child, Signal.LOW) for child in self.children]
        else:
            return [SignalFire(self, child, Signal.HIGH) for child in self.children]

    def add_inbound(self, node: Node):
        self.state[node.name] = Signal.LOW

my_node_a = Node()
my_node_b = Node()
my_parent_a = Node("pa")
my_parent_b = Node("pb")
my_conj = ConjunctionNode("cn", [my_node_a, my_node_b])
my_conj.add_inbound(my_parent_a)
my_conj.add_inbound(my_parent_b)
check(my_conj.process(SignalFire(my_parent_a, my_conj, Signal.HIGH)), [
    SignalFire(my_conj, my_node_a, Signal.HIGH),
    SignalFire(my_conj, my_node_b, Signal.HIGH),
])
check(my_conj.process(SignalFire(my_parent_b, my_conj, Signal.HIGH)), [
    SignalFire(my_conj, my_node_a, Signal.LOW),
    SignalFire(my_conj, my_node_b, Signal.LOW),
])
check(my_conj.process(SignalFire(my_parent_b, my_conj, Signal.LOW)), [
    SignalFire(my_conj, my_node_a, Signal.HIGH),
    SignalFire(my_conj, my_node_b, Signal.HIGH),
])

@dataclass
class State():
    nodes: dict[str, Node] = field(default_factory=dict)
    start: BroadcasterNode = field(default_factory=BroadcasterNode)
    presses: int = 0
    highs: dict[str, bool] = field(default_factory=dict)

    def process_press(self):
        signals_processed = 0
        queue = [SignalFire(Node("button"), self.start, Signal.LOW)]
        while len(queue) != 0:
            signal = queue.pop(0)
            # if signal.dest.name == "rx" and signal.value == Signal.LOW:
            #     pret("Result:", self.presses)
            #     exit(1)
            if signal.dest.name == "rm":
                if signal.value == Signal.HIGH:
                    self.highs[signal.src.name] = True
                    print(self.presses, signals_processed, signal.src.name, signal.value)
                elif signal.src.name in self.highs and self.highs[signal.src.name] == True:
                    self.highs[signal.src.name] = False
                    print(self.presses, signals_processed, signal.src.name, signal.value)
            tlog(2, f"{signal.src.name} -{signal.value}-> {signal.dest.name}")
            new_signals = signal.dest.process(signal)
            queue.extend(new_signals)
            signals_processed += 1

    def find_low_rx(self):
        while True:
            self.presses += 1
            self.process_press()
            fun_node = self.nodes["rm"]
            # if fun_node.state["dp"] == Signal.HIGH:
            #     print(f"dp true: {self.presses}")
            # if self.presses % 1000 == 0:
            #     print(self.presses)

    def calc_signal_sum(self, n: int):
        counts = {
            Signal.LOW: 0,
            Signal.HIGH: 0
        }
        for _ in range(0, n):
            round_counts = self.process_press()
            counts[Signal.LOW] += round_counts[Signal.LOW]
            counts[Signal.HIGH] += round_counts[Signal.HIGH]
        return counts[Signal.LOW] * counts[Signal.HIGH]

def parse_line_for_nodes(state: State, line: str, _idx: int) -> State:
    if matches := re.match(r"^%([a-zA-Z]+)\s", line):
        state.nodes[matches.group(1)] = FlipFlopNode(matches.group(1))
    elif matches := re.match(r"^&([a-zA-Z]+)\s", line):
        state.nodes[matches.group(1)] = ConjunctionNode(matches.group(1))
    elif matches := re.match(r"^(broadcaster)\s", line):
        state.start = state.nodes[matches.group(1)] = BroadcasterNode(matches.group(1))
    else:
        raise Exception(f"Could not parse line: {line}")
    return state

def parse_line_for_edges(state: State, line: str, _idx: int) -> State:
    if matches := re.match(r"^[&%]?([a-zA-Z]+) -> (.*)$", line):
        children = matches.group(2).split(", ")
        for child in children:
            if child not in state.nodes:
                print(f"Weird node: {child}")
                state.nodes[child] = Node(child)
            state.nodes[child].add_inbound(state.nodes[matches.group(1)])
        state.nodes[matches.group(1)].children = [
            state.nodes[child] for child in children
        ]
    else:
        raise Exception(f"Could not parse line: {line}")
    return state

def calculate(filename):
    state = State()
    every_line(state, filename, [parse_line_for_nodes])
    every_line(state, filename, [parse_line_for_edges])
    return state.find_low_rx()

# pret("Trial 1:", calculate("trial_1.txt"))
# pret("Trial 2:", calculate("trial_2.txt"))
pret("Input:", calculate("input.txt"))

# Don't forget to add the node to the conjunction on init!!!!

# dh, dp, qd, bb
