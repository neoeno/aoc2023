from dataclasses import dataclass, field
from functools import cache
import re
from typing import Self

from utility.main import check, every_line, pret


@dataclass(frozen=True)
class Vec2:
    x: int
    y: int

    def add(self, other: Self):
        return Vec2(self.x + other.x, self.y + other.y)


@dataclass(frozen=True)
class Vec3:
    x: int
    y: int
    z: int

    def add(self, other: Self):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def between(self, other: Self):
        if self.x != other.x and self.y == other.y and self.z == other.z:
            return {Vec3(x, self.y, self.z) for x in range(min(self.x, other.x + 1), max(self.x, other.x + 1))}
        elif self.y != other.y and self.x == other.x and self.z == other.z:
            return {Vec3(self.x, y, self.z) for y in range(min(self.y, other.y + 1), max(self.y, other.y + 1))}
        elif self.z != other.z and self.x == other.x and self.y == other.y:
            return {Vec3(self.x, self.y, z) for z in range(min(self.z, other.z + 1), max(self.z, other.z + 1))}
        elif self.z == other.z and self.x == other.x and self.y == other.y:
            return {self}
        else:
            raise Exception(f"Between called with too much variance {self}, {other}")

my_vec3 = Vec3(0, 0, 0)
check(my_vec3.between(Vec3(2, 0, 0)), {
    Vec3(0, 0, 0),
    Vec3(1, 0, 0),
    Vec3(2, 0, 0),
})
check(my_vec3.between(Vec3(0, 2, 0)), {
    Vec3(0, 0, 0),
    Vec3(0, 1, 0),
    Vec3(0, 2, 0),
})
check(my_vec3.between(Vec3(0, 0, 2)), {
    Vec3(0, 0, 0),
    Vec3(0, 0, 1),
    Vec3(0, 0, 2),
})
check(my_vec3.between(Vec3(0, 0, 0)), {
    Vec3(0, 0, 0),
})

@dataclass(frozen=True)
class Block:
    start: Vec3
    end: Vec3

    def cells(self):
        return self.start.between(self.end)

    # Unverified
    def cells_below(self):
        if self.start.z != self.end.z:
            return { Vec3(self.start.x, self.start.y, min(self.start.z, self.end.z) - 1)}
        return {
            vec.add(Vec3(0, 0, -1)) for vec in self.cells()
        }

    def height(self):
        return abs(self.start.z - self.end.z) + 1

my_block = Block(Vec3(1, 1, 1), Vec3(2, 1, 1))
check(my_block.cells_below(), {Vec3(x=2, y=1, z=0), Vec3(x=1, y=1, z=0)})
my_block = Block(Vec3(1, 1, 1), Vec3(1, 1, 2))
check(my_block.cells_below(), {Vec3(1, 1, 0)})

@dataclass
class State:
    blocks: set[Block] = field(default_factory=set)
    cells: dict[Vec3, Block] = field(default_factory=dict)
    heights: dict[Block, int] = field(default_factory=dict)
    critical: set[Block] = field(default_factory=set)
    belows: dict[Block, set[Block]] = field(default_factory=dict)
    tops: dict[Block, int] = field(default_factory=dict)

    def count_disintegratable(self):
        for block in self.blocks:
            blocks_below = self.below(block)
            if len(blocks_below) == 0:
                continue
            elif len(blocks_below) == 1:
                self.critical.update(blocks_below)
            else:
                max_top = max(self.top(block) for block in blocks_below)
                directly_below = {block for block in blocks_below if self.top(block) == max_top}
                if len(directly_below) == 1:
                    self.critical.update(directly_below)
        return len(self.blocks.difference(self.critical))

    def below(self, block: Block):
        if block in self.belows:
            return self.belows[block]
        self.belows[block] = set()
        for cell in block.cells_below():
            for z in range(cell.z, 0, -1):
                if Vec3(cell.x, cell.y, z) in self.cells:
                    self.belows[block].add(self.cells[Vec3(cell.x, cell.y, z)])
        return self.belows[block]

    def top(self, block: Block):
        if block in self.tops:
            return self.tops[block]
        if len(self.below(block)) == 0:
            return 0 + block.height()
        self.tops[block] = max(
            self.top(below) + block.height()
            for below in self.below(block)
        )
        return self.tops[block]

def parse_line(state: State, line: str, _idx: int) -> State:
    if matches := re.match(r"(\d+),(\d+),(\d+)~(\d+),(\d+),(\d+)", line):
        x1, y1, z1, x2, y2, z2 = (int(numstr) for numstr in matches.groups())
        block = Block(Vec3(x1, y1, z1), Vec3(x2, y2, z2))
        state.blocks.add(block)
        for cell in block.cells():
            if cell in state.cells:
                raise Exception(f"Cell clash! {block}, {cell}, {state.cells[cell]}")
            state.cells[cell] = block
    return state


def calculate(filename):
    state = State()
    every_line(state, filename, [parse_line])
    return state.count_disintegratable()

pret("Trial:", calculate("trial.txt"))
pret("Input:", calculate("input.txt"))
