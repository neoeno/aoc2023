from collections import defaultdict
from dataclasses import dataclass, field
from itertools import product
from math import prod
from random import choice, sample
import re
from time import sleep

import graphviz

from utility.main import every_line, pret, show


@dataclass(frozen=True, order=True)
class Node:
    name: str

@dataclass(order=True)
class Edge:
    name: str
    a: Node
    b: Node

    def copy(self):
        return Edge(self.name, self.a, self.b)

@dataclass
class Graph:
    nodes: set[Node] = field(default_factory=set)
    edges: list[Edge] = field(default_factory=list)
    node_to_edges: defaultdict[Node, list[Edge]] = field(default_factory=lambda: defaultdict(list))
    nodes_absorbed: defaultdict[Node, int] = field(default_factory=lambda: defaultdict(lambda: 1))

    def find_min_cut(self, state):
        while len(self.nodes) > 20:
            r_edge = choice(self.edges).copy()
            new_node = self.contract(r_edge)
            self.nodes_absorbed[new_node] = self.nodes_absorbed[r_edge.a] + self.nodes_absorbed[r_edge.b]
            # state.viz()
            # sleep(0.1)
        return (len(self.edges), (self.nodes_absorbed[n] for n in self.nodes))


    def contract(self, edge: Edge):
        edge = edge.copy()
        self.edges.remove(edge)
        self.nodes.remove(edge.a)
        self.nodes.remove(edge.b)
        new_node = Node(edge.a.name)
        new_edges = []
        for c_edge in self.node_to_edges[edge.a]:
            if c_edge.a.name in [edge.a.name, edge.b.name]:
                c_edge.a = new_node
            if c_edge.b.name in [edge.a.name, edge.b.name]:
                c_edge.b = new_node
            if c_edge.a.name != c_edge.b.name:
                new_edges.append(c_edge)
        for c_edge in self.node_to_edges[edge.b]:
            if c_edge.a.name in [edge.a.name, edge.b.name]:
                c_edge.a = new_node
            if c_edge.b.name in [edge.a.name, edge.b.name]:
                c_edge.b = new_node
            if c_edge.a.name != c_edge.b.name:
                new_edges.append(c_edge)
        self.node_to_edges[new_node] = new_edges
        self.nodes.add(new_node)
        self.edges = [e for e in self.edges if e.a.name != e.b.name]
        return new_node

@dataclass
class State:
    graph: Graph

    def viz(self):
        dot = graphviz.Graph(comment='Day 25!', format="png")
        for node in sorted(self.graph.nodes):
            dot.node(node.name, label=f"{node.name}:{self.graph.nodes_absorbed[node]}")
        for edge in sorted(self.graph.edges):
            dot.edge(edge.a.name, edge.b.name)
        show(dot.source, clear=True)
        dot.render('graph')

def parse_line(state: State, line: str, _idx: int) -> State:
    if matches := re.match(r"([a-z]+): ([a-z ]+)", line):
        main_node = Node(matches.group(1))
        subnodes = [Node(name) for name in matches.group(2).split(" ")]
        state.graph.nodes.add(main_node)
        state.graph.nodes.update(subnodes)
        edges = [
            Edge(f"{main_node.name} -> {subnode.name}", main_node, subnode)
            for subnode in subnodes
        ]
        state.graph.edges.extend(edges)
        for edge in edges:
            state.graph.node_to_edges[edge.a].append(edge)
            state.graph.node_to_edges[edge.b].append(edge)
        return state
    else:
        raise Exception(f"Cannot parse: {line}")

def calculate(filename: str):
    found = 0
    result = []
    while found != 3:
        state = State(Graph())
        every_line(state, filename, [parse_line])
        # state.viz()
        found, result = state.graph.find_min_cut(state)
        state.viz()
        sleep(1)
        print(found)
    return prod(result)


# pret("Trial:", calculate("trial.txt"))
pret("Input:", calculate("input.txt"))

# 2+1+763 + 1+1+3+1+1+1+1+1 = 776

# 1+696+1+2+1+1+1+1+1 = 705
# 547080


        # btc [label="btc:2"]
        # dcd [label="dcd:1"]
        # dgk [label="dgk:1"]
        # fmz [label="fmz:2"]
        # fzf [label="fzf:1"]
        # hbz [label="hbz:1"]
        # hst [label="hst:1"]
        # jjq [label="jjq:1"]
        # kjk [label="kjk:1"]
        # mnv [label="mnv:1"]
        # ptn [label="ptn:1"]
        # qjb [label="qjb:1"]
        # rqk [label="rqk:1"]
        # sgs [label="sgs:1"]
        # smz [label="smz:1"]
        # tcv [label="tcv:763"]
        # vfz [label="vfz:3"]
        # vsn [label="vsn:1"]
        # xxq [label="xxq:1"]
        # zkg [label="zkg:696"]
