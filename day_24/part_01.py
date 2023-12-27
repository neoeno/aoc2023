from collections import defaultdict
from dataclasses import dataclass, field
from decimal import Decimal as D
from itertools import combinations, permutations
from math import ceil, floor
import re
from typing import Self

from utility.main import check, every_line, pret

@dataclass(frozen=True)
class Vec:
    x: D
    y: D
    z: D = D(0)

    def add(self, other):
        return Vec(self.x + other.x, self.y + other.y)

    def hdist(self, to: Self) -> D:
        return abs(to.x - self.x) + abs(to.y - self.y)

    def __repr__(self):
        return f"V({self.x}, {self.y})"

@dataclass(frozen=True)
class Line:
    m: D
    c: D

    def y_at_x(self, x: D) -> D:
        return self.m * x + self.c

    def x_at_y(self, y: D) -> D:
        return (y - self.c) / self.m

    def __repr__(self):
        return f"y = {self.m}x + {self.c}"

my_line = Line(D("-0.5"), D("22.5"))
check(my_line.y_at_x(D("19")), D("13"))
check(my_line.x_at_y(D("13")), D("19"))

@dataclass(frozen=True)
class Particle:
    p: Vec
    d: Vec
    _line: Line | None = None

    def line(self):
        # if self._line != None:
        #     return self._line

        m = self.d.y / self.d.x
        c = self.p.y - m * self.p.x
        return Line(m, c)

        # return self._line

    def n_for_xy(self, pt: Vec) -> D:
        return abs(self.p.x - pt.x) / abs(self.d.x)

    def xy_for_n(self, n):
        return Vec(self.p.x + self.d.x * n, self.p.y + self.d.y * n)

    def __repr__(self):
        p, d = self.p, self.d
        return f"{p.x}, {p.y}, _ @ {d.x}, {d.y}, _"

my_particle = Particle(Vec(D("19"), D("13")), Vec(D("-2"), D("1")))
check(my_particle.line(), Line(D("-0.5"), D("22.5")))

@dataclass
class State:
    area: tuple[int, int]
    particles: list[Particle] = field(default_factory=list)
    intersections: defaultdict[Particle, set[Vec]] = field(default_factory=lambda: defaultdict(set))

    def count_intersections(self):
        total = 0
        for pair in combinations(self.particles, r=2):
            if self.is_good_intersection(pair[0], pair[1]):
                total += 1
        return total

    def is_good_intersection(self, a: Particle, b: Particle) -> bool:
        if a.line().m == b.line().m: # Parallel
            return False
        intersection = self.intersect(a.line(), b.line())
        if not self.is_in_future(a, intersection):
            return False
        if not self.is_in_future(b, intersection):
            return False
        if not self.is_within_area(intersection):
            return False
        self.intersections[a].add(intersection)
        self.intersections[b].add(intersection)
        return True

    def intersect(self, a: Line, b: Line):
        y = ((a.m * b.c) - (b.m * a.c)) / (a.m - b.m)
        x = a.x_at_y(y)
        return Vec(x, y)

    def is_within_area(self, v: Vec):
        return v.x >= self.area[0] and v.y >= self.area[0] \
           and v.x <= self.area[1] and v.y <= self.area[1]

    def is_in_future(self, particle, intersect):
        if particle.d.x < 0 and intersect.x >= particle.p.x:
            return False
        if particle.d.x > 0 and intersect.x <= particle.p.x:
            return False
        if particle.d.x == 0 and intersect.x == particle.p.x:
            return False
        if particle.d.y < 0 and intersect.y >= particle.p.y:
            return False
        if particle.d.y > 0 and intersect.y <= particle.p.y:
            return False
        if particle.d.y == 0 and intersect.y == particle.p.y:
            return False
        return True


def parse_line(state: State, line: str, _idx: int):
    if matches := re.match(r"(-?\d+),\s+(-?\d+),\s+(-?\d+)\s+@\s+(-?\d+),\s+(-?\d+),\s+(-?\d+)", line):
        particle = Particle(
            Vec(D(matches.group(1)), D(matches.group(2))),
            Vec(D(matches.group(4)), D(matches.group(5))),
        )
        state.particles.append(particle)
        return state
    else:
        raise Exception(f"Cannot parse line: '{line}'")

my_state = State((7, 27))
my_state = parse_line(my_state, "19, 13, 30 @ -2, 1, -2", 0)
check(my_state.particles[0], Particle(Vec(D("19"), D("13")), Vec(D("-2"), D("1"))))

def calculate(area, filename):
    state = State(area)
    state = every_line(state, filename, [parse_line])
    retval = state.count_intersections()
    max_ints = max(len(s) for s in state.intersections.values())
    for p in state.intersections.keys():
        # print(f"{len(state.intersections[p])}: {p}")
        if max_ints == len(state.intersections[p]):
            for i in state.intersections[p]:
                print(i)
    return retval

# pret("Trial:", calculate((7, 27), "trial.txt"))
pret("Input:", calculate((D("200000000000000"), D("400000000000000")), "input.txt"))
