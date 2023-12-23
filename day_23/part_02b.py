

from collections import defaultdict
from dataclasses import dataclass, field
from heapq import heappop, heappush
import math
from typing import Self


@dataclass(frozen=True, order=True)
class Vec:
    x: int
    y: int

    def add(self, other):
        return Vec(self.x + other.x, self.y + other.y)

    def hdist(self, to: Self) -> int:
        return abs(to.x - self.x) + abs(to.y - self.y)


data = {Vec(x=1, y=0): {(Vec(x=15, y=19), 178)}, Vec(x=15, y=19): {(Vec(x=37, y=7), 159), (Vec(x=9, y=37), 165), (Vec(x=1, y=0), 178)}, Vec(x=9, y=37): {(Vec(x=29, y=39), 95), (Vec(x=15, y=19), 165), (Vec(x=19, y=65), 259)}, Vec(x=37, y=7): {(Vec(x=29, y=39), 265), (Vec(x=61, y=11), 165), (Vec(x=15, y=19), 159)}, Vec(x=19, y=65): {(Vec(x=41, y=53), 103), (Vec(x=9, y=37), 259), (Vec(x=19, y=85), 217)}, Vec(x=29, y=39): {(Vec(x=9, y=37), 95), (Vec(x=41, y=53), 75), (Vec(x=65, y=43), 173), (Vec(x=37, y=7), 265)}, Vec(x=41, y=53): {(Vec(x=19, y=65), 103), (Vec(x=29, y=39), 75), (Vec(x=57, y=55), 103), (Vec(x=35, y=89), 239)}, Vec(x=19, y=85): {(Vec(x=35, y=89), 57), (Vec(x=9, y=99), 141), (Vec(x=19, y=65), 217)}, Vec(x=61, y=11): {(Vec(x=75, y=19), 175), (Vec(x=37, y=7), 165), (Vec(x=65, y=43), 221)}, Vec(x=65, y=43): {(Vec(x=61, y=11), 221), (Vec(x=57, y=55), 65), (Vec(x=79, y=39), 35), (Vec(x=29, y=39), 173)}, Vec(x=57, y=55): {(Vec(x=65, y=43), 65), (Vec(x=41, y=53), 103), (Vec(x=83, y=65), 105), (Vec(x=65, y=81), 167)}, Vec(x=79, y=39): {(Vec(x=75, y=19), 69), (Vec(x=109, y=31), 211), (Vec(x=65, y=43), 35), (Vec(x=83, y=65), 191)}, Vec(x=35, y=89): {(Vec(x=29, y=111), 93), (Vec(x=19, y=85), 57), (Vec(x=41, y=53), 239), (Vec(x=65, y=81), 151)}, Vec(x=9, y=99): {(Vec(x=19, y=85), 141), (Vec(x=29, y=111), 133), (Vec(x=31, y=135), 383)}, Vec(x=75, y=19): {(Vec(x=61, y=11), 175), (Vec(x=113, y=13), 309), (Vec(x=79, y=39), 69)}, Vec(x=109, y=31): {(Vec(x=133, y=31), 165), (Vec(x=113, y=13), 91), (Vec(x=101, y=61), 231), (Vec(x=79, y=39), 211)}, Vec(x=83, y=65): {(Vec(x=57, y=55), 105), (Vec(x=87, y=83), 67), (Vec(x=79, y=39), 191), (Vec(x=101, y=61), 127)}, Vec(x=29, y=111): {(Vec(x=31, y=135), 171), (Vec(x=35, y=89), 93), (Vec(x=9, y=99), 133), (Vec(x=53, y=105), 155)}, Vec(x=65, y=81): {(Vec(x=57, y=55), 167), (Vec(x=87, y=83), 73), (Vec(x=53, y=105), 169), (Vec(x=35, y=89), 151)}, Vec(x=113, y=13): {(Vec(x=109, y=31), 91), (Vec(x=133, y=31), 327), (Vec(x=75, y=19), 309)}, Vec(x=133, y=31): {(Vec(x=109, y=31), 165), (Vec(x=135, y=61), 189), (Vec(x=113, y=13), 327)}, Vec(x=31, y=135): {(Vec(x=29, y=111), 171), (Vec(x=9, y=99), 383), (Vec(x=55, y=131), 149)}, Vec(x=53, y=105): {(Vec(x=77, y=109), 117), (Vec(x=29, y=111), 155), (Vec(x=65, y=81), 169), (Vec(x=55, y=131), 157)}, Vec(x=87, y=83): {(Vec(x=77, y=109), 205), (Vec(x=65, y=81), 73), (Vec(x=113, y=81), 137), (Vec(x=83, y=65), 67)}, Vec(x=101, y=61): {(Vec(x=109, y=31), 231), (Vec(x=83, y=65), 127), (Vec(x=135, y=61), 179), (Vec(x=113, y=81), 121)}, Vec(x=55, y=131): {(Vec(x=53, y=105), 157), (Vec(x=75, y=131), 141), (Vec(x=31, y=135), 149)}, Vec(x=77, y=109): {(Vec(x=53, y=105), 117), (Vec(x=75, y=131), 173), (Vec(x=107, y=109), 183), (Vec(x=87, y=83), 205)}, Vec(x=113, y=81): {(Vec(x=107, y=109), 179), (Vec(x=101, y=61), 121), (Vec(x=87, y=83), 137), (Vec(x=127, y=89), 67)}, Vec(x=75, y=131): {(Vec(x=55, y=131), 141), (Vec(x=77, y=109), 173), (Vec(x=103, y=137), 135)}, Vec(x=107, y=109): {(Vec(x=77, y=109), 183), (Vec(x=103, y=137), 149), (Vec(x=113, y=81), 179), (Vec(x=125, y=111), 105)}, Vec(x=135, y=61): {(Vec(x=133, y=31), 189), (Vec(x=127, y=89), 229), (Vec(x=101, y=61), 179)}, Vec(x=127, y=89): {(Vec(x=125, y=111), 177), (Vec(x=113, y=81), 67), (Vec(x=135, y=61), 229)}, Vec(x=103, y=137): {(Vec(x=129, y=137), 167), (Vec(x=75, y=131), 135), (Vec(x=107, y=109), 149)}, Vec(x=125, y=111): {(Vec(x=129, y=137), 235), (Vec(x=127, y=89), 177), (Vec(x=107, y=109), 105)}, Vec(x=129, y=137): {(Vec(x=103, y=137), 167), (Vec(x=139, y=139), 29), (Vec(x=125, y=111), 235)}, Vec(x=139, y=139): {(Vec(x=129, y=137), 29), (Vec(x=139, y=140), 1)}, Vec(x=139, y=140): {(Vec(x=139, y=139), 1)}}



@dataclass(frozen=True, order=True)
class Cursor:
    pos: Vec
    visited: frozenset[Vec] = field(default_factory=frozenset)

@dataclass
class State:
    start: Vec = Vec(1, 0)
    end: Vec = Vec(139, 140)
    # end: Vec = Vec(21, 22)
    height: int = 0
    width: int = 0
    focus: Vec = Vec(0, 0)
    best_path: list[Vec] = field(default_factory=list)
    _neighbours: dict[Cursor, set[tuple[Cursor, int]]] = field(default_factory=dict)

    def count_steps_in_longest_path(self):
        to_check: list[tuple[float, Cursor]] = []
        starting_cursor = Cursor(self.start, frozenset())
        heappush(to_check, (self.start.hdist(self.end), starting_cursor))
        came_from: dict[Cursor, Cursor] = {}
        g_score: dict[Cursor, float] = defaultdict(lambda: math.inf)
        g_score[starting_cursor] = 0
        f_score: dict[Cursor, float] = defaultdict(lambda: math.inf)
        f_score[starting_cursor] = self.start.hdist(self.end)
        ends: set[Cursor] = set()
        pairs: dict[tuple[Vec, Vec], int] = dict()
        best: float = 0.0

        while len(to_check) != 0:
            _, current = heappop(to_check)
            if current.pos == self.end:
                ends.add(current)
                if best > g_score[current]:
                    best = g_score[current]
                    print("NEW BEST")
                    print(self.reconstruct_path(came_from, current, pairs))

            for neighbour, cost in self.neighbours(current):
                tentative_g_score = g_score[current] - cost + 1
                if tentative_g_score < g_score[neighbour]:
                    came_from[neighbour] = current
                    pairs[(current.pos, neighbour.pos)] = cost - 1
                    g_score[neighbour] = tentative_g_score
                    f_score[neighbour] = tentative_g_score - neighbour.pos.hdist(self.end)
                    if neighbour not in to_check:
                        heappush(to_check, (f_score[neighbour], neighbour))

        end = min(ends, key=lambda e: g_score[e])
        print(self.reconstruct_path(came_from, end, pairs))
        return -1*min(g_score[end] for end in ends) + 1

    def reconstruct_path(self, came_from: dict[Cursor, Cursor], current: Cursor, pairs) -> int:
        total = 0
        total_path: list[Vec] = [current.pos]
        while current in came_from:
            current = came_from[current]
            total_path.append(current.pos)
            if len(total_path) > 1:
                total += pairs[(total_path[-1], total_path[-2])]
        # return list(reversed(total_path))
        return total + 1


    def neighbours(self, cursor: Cursor) -> set[tuple[Cursor, int]]:
        if cursor in self._neighbours:
            return self._neighbours[cursor]
        # print(len(cursor.visited))
        visited = frozenset({*cursor.visited, cursor.pos})
        self._neighbours[cursor] = {
            (Cursor(pos, visited), cost)
            for pos, cost in data[cursor.pos]
            if pos not in visited
        }
        return self._neighbours[cursor]

print(State().count_steps_in_longest_path())
