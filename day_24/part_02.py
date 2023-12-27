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

        if "y" in self.dims:
            if p1.traj_y().m == p2.traj_y().m:
                if p1.traj_y().c == p2.traj_y().c:
                    return (True, None, "HIT")
                return (False, None, "Y parallel")
            y_intersection = self.intersect(p1.traj_y(), p2.traj_y())
            if y_intersection.x < 0:
                return (False, y_intersection, "Y X below zero")
            if y_intersection.x.to_integral_value() != y_intersection.x:
                return (False, y_intersection, "Y X inexact")
            if y_intersection.y.to_integral_value() != y_intersection.y:
                return (False, y_intersection, "Y Y inexact")

        if "z" in self.dims:
            if p1.traj_z().m == p2.traj_z().m:
                if p1.traj_z().c == p2.traj_z().c:
                    return (True, None, "HIT")
                return (False, None, "Z parallel")
            z_intersection = self.intersect(p1.traj_z(), p2.traj_z())
            if z_intersection.x < 0:
                return (False, z_intersection, "Z X below zero")
            if z_intersection.x.to_integral_value() != z_intersection.x:
                return (False, z_intersection, "Z X inexact")
            if z_intersection.y.to_integral_value() != z_intersection.y:
                return (False, z_intersection, "Z Y inexact")

        return (True, Vec(0, 0), "HIT")

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
    import argparse
    parser = argparse.ArgumentParser(description='Do AoC')
    parser.add_argument('-l', '--log', default=999, type=int)
    parser.add_argument('-d', '--dim', default="x,y,z", type=str)
    args = parser.parse_args()
    best_cand = g = Particle(Vec(D("309721960025816"), D("434470227085520"), D("164429529509188")), Vec(D("-63"), D("-263"), D("195")))
    state.dims = set(args.dim.split(","))
    print(state.dims)
    best_count, coords = state.check(g)
    print(f"INIT: {g} {best_count}/{len(state.particles)}")
    strats = []
    if "x" in state.dims:
        strats.append("px")
        strats.append("dx")
    if "y" in state.dims:
        strats.append("py")
        strats.append("dy")
    if "z" in state.dims:
        strats.append("pz")
        strats.append("dz")
        strats.append("xz")
    divg = False
    while True:
        strat = sample(strats, randint(1, len(strats)))
        cand = g
        if "px" in strat:
            cand = Particle(Vec(cand.p.x + randint(-10000000, 10000000) * choice([540, 5040, 1, 55440, 942480, 95760]), cand.p.y, cand.p.z), cand.d)
        if "py" in strat:
            cand = Particle(Vec(cand.p.x, cand.p.y + randint(-1000000, 1000000) * choice([1, 630, 630*630, 630*2]), cand.p.z), cand.d)
        if "pz" in strat:
            cand = Particle(Vec(cand.p.x, cand.p.y, cand.p.z + randint(-10000000, 10000000) * choice([1, 495, 5040, 55440, 40320, 388080, 942480, 95760])), cand.d)
        if "dx" in strat:
            cand = Particle(cand.p, Vec(cand.d.x + randint(-100, 100), cand.d.y, cand.d.z))
        if "dy" in strat:
            cand = Particle(cand.p, Vec(cand.d.x, cand.d.y + randint(-100, 100), cand.d.z))
        if "xz" in strat:
            cand = Particle(cand.p, Vec(cand.d.x, cand.d.y, D(choice([-45, -25, -15]))))
        if "dz" in strat:
            cand = Particle(cand.p, Vec(cand.d.x, cand.d.y, cand.d.z + randint(-100, 100)))
        if cand.d.x == 0 or cand.d.y == 0 or cand.d.z == 0:
            continue
        count, coords = state.check(cand)
        if count > best_count:
            print(f"BEZT: {cand} {count}/{len(state.particles)}")
            best_cand = g = cand
            best_count = count
        elif count >= best_count and best_cand != cand:
            print(f" OK: {cand} {count}/{len(state.particles)}")
            best_cand = g = cand
        elif randint(0, best_count) == 1 and count > (best_count // 2):
            # print(f" DIV: {cand} {count}/{len(state.particles)}")
            g = cand
            divg = True
        if divg and randint(0, 1000) == 1:
            # print(f" RET: {cand} {count}/{len(state.particles)}")
            g = best_cand
            divg = False
    print(count)
    # shuffle(state.particles)
    # best = 0
    # best_inters = []
    # state.dims = {"x", "y"}
    # # pool = state.particles[0:5]
    # pool = state.particles
    # qn = 0
    # while len(pool) <= len(state.particles):
    #     qn += 1
    #     if qn % 10000 == 0:
    #         print(qn)

    #     pool = sample(state.particles, 3)
    #     # n = randint(0, 1 + qn // 100)
    #     n = qn

    #     for p in pool:
    #         for dy in range(-100, 100):
    #             for dz in [1]: # -15 -45 #sample(range(-50, 50), 5):
    #                 if n == 0 or dy == 0 or dz == 0:
    #                     continue
    #                 cand = Particle(Vec(D("309721960025816"), p.p.y + (p.d.y * n) - (dy * n), p.p.z + (p.d.z * n) - (dz * n)), Vec(D(-63), D(dy), D(dz)))
    #                 count, inters = state.check(cand, pool)
    #                 if count == len(state.particles):
    #                     print(f"YOU WIN: {n} {cand} {count}/{len(state.particles)}")
    #                     exit(1)
    #                 elif count == len(pool):
    #                     # print(f"GOOD: {n} {cand} {count}/{len(pool)}")
    #                     count, inters = state.check(cand)
    #                     if count == len(state.particles):
    #                         print(f"YOU WIN: {n} {p} {cand} {count}/{len(state.particles)}")
    #                         exit(1)
    #                     if count > (best // 2):
    #                         # print(f"CHECK: {n} {p} {cand} {count}/{len(state.particles)}")
    #                         pass
    #                     if count >= best:
    #                         print(f"BEZT: {n} {p} {cand} {count}/{len(state.particles)}")
    #                         best_inters = inters
    #                         best = count
    #                     # shuffle(state.particles)
    #                     # pool = state.particles[0:5]
    #                     # print("\n".join(str(i) for i in pool))
    #                     # n = 0
    #                 elif count >= best:
    #                     best_inters = inters
    #                     best = count
    #                     print(f"BEST: {n} {p} {cand} {count}/{len(pool)}")
    #                     pass
    #                 else:
    #                     # print(f"BAD: {count}/{len(state.particles)}")
    #                     pass
    # print("\n".join(str(i) for i in best_inters))



# pret("Trial:", calculate("trial.txt", good_particle))

pret("Input:", calculate("input.txt", None))

# 431282096438444 - too low
# 472978148847396 - too low
# 715263060564866 - too low
