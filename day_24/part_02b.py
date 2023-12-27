from collections import defaultdict
from dataclasses import dataclass, field
from decimal import Decimal as D
from itertools import combinations, permutations
from random import choice, randint, sample, shuffle
import re
from time import sleep
from typing import Self

from utility.main import check, every_line, pret, tlog

@dataclass(frozen=True)
class Vec:
    x: D
    y: D
    z: D = D("0")

    def add(self, other):
        return Vec(self.x + other.x, self.y + other.y, self.z + other.z)

    def mul(self, other):
        return Vec(self.x * other.x, self.y * other.y, self.z * other.z)

    def hdist(self, to: Self) -> D:
        return abs(to.x - self.x) + abs(to.y - self.y) + abs(to.z - self.z)

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
        m = self.d.y / self.d.x
        c = self.p.y - m * self.p.x
        return Line(m, c)

    def traj_x(self):
        return Line(self.d.x, self.p.x)

    def traj_y(self):
        return Line(self.d.y, self.p.y)

    def traj_z(self):
        return Line(self.d.z, self.p.z)

    def coord_at_n(self, n: D):
        return self.p.add(self.d.mul(Vec(n, n, n)))

    def __repr__(self):
        p, d = self.p, self.d
        return f"{p.x}, {p.y}, {p.z} @ {d.x}, {d.y}, {d.z}"


my_particle = Particle(Vec(D("19"), D("13")), Vec(D("-2"), D("1")))
check(my_particle.line(), Line(D("-0.5"), D("22.5")))

@dataclass
class State:
    particles: list[Particle] = field(default_factory=list)
    intersections: defaultdict[Particle, set[Particle]] = field(default_factory=lambda: defaultdict(set))
    dims: set[str] = field(default_factory=list)

    def check(self, candidate: Particle, pool = None) -> tuple[int, list[Vec]]:
        total = 0
        coords = []
        for p in pool or self.particles:
            hit, coord, msg = self.does_hit(candidate, p)
            if hit:
                tlog(2, f"HIT: {p} {coord} {msg}")
                coords.append(p)
                total += 1
            else:
                if pool != None:
                    return total, coords
                tlog(3, f"MISS: {p} {msg}")
        return total, coords

    def does_hit(self, p1: Particle, p2: Particle) -> tuple[bool, Vec | None, str]:
        if p1.traj_x().m == p2.traj_x().m:
            if p1.traj_x().c == p2.traj_x().c:
                return (True, None, "HIT")
            return (False, None, "X parallel")
        x_intersection = self.intersect(p1.traj_x(), p2.traj_x())
        if x_intersection.x < 0:
            return (False, x_intersection, "X below zero")
        if x_intersection.x.to_integral_value() != x_intersection.x:
            return (False, x_intersection, "X X inexact")
        if x_intersection.y.to_integral_value() != x_intersection.y:
            return (False, x_intersection, "X Y inexact")


        return (True, x_intersection, "HIT")

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
        self.intersections[a].add(b)
        self.intersections[b].add(a)
        return True

    def intersect(self, a: Line, b: Line):
        y = ((a.m * b.c) - (b.m * a.c)) / (a.m - b.m)
        x = a.x_at_y(y)
        return Vec(x, y)

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
            Vec(D(matches.group(1)), D(matches.group(2)), D(matches.group(3))),
            Vec(D(matches.group(4)), D(matches.group(5)), D(matches.group(6))),
        )
        state.particles.append(particle)
        return state
    else:
        raise Exception(f"Cannot parse line: '{line}'")

my_state = State()
my_state = parse_line(my_state, "19, 13, 30 @ -2, 1, -2", 0)
check(my_state.particles[0], Particle(Vec(D("19"), D("13"), D("30")), Vec(D("-2"), D("1"), D("-2"))))

def calculate(filename, good_particle = None):
    state = State()
    state = every_line(state, filename, [parse_line])
    good_particle = Particle(Vec(D("309721960025816"), D("0"), D("0")), Vec(D("-63"), D("1"), D("1")))
    for p in state.particles[0:20]:
        # print(state.does_hit(good_particle, p))
        flag, coord, msg = state.does_hit(good_particle, p)
        if coord is None:
            continue
        # print(good_particle.coord_at_n(coord.x))
        print(f"{coord.x}: {p.coord_at_n(coord.x).z}")



# pret("Trial:", calculate("trial.txt", good_particle))

pret("Input:", calculate("input.txt", None))

# 431282096438444 - too low
# 472978148847396 - too low
# 715263060564866 - too low
