from dataclasses import dataclass, field
from functools import cache
import re
from typing import Self

from utility.main import check, every_line, pret, show


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

# F, E, C, B, A, G

@dataclass
class State:
    blocks: set[Block] = field(default_factory=set)
    cells: dict[Vec3, Block] = field(default_factory=dict)
    heights: dict[Block, int] = field(default_factory=dict)
    critical: set[Block] = field(default_factory=set)
    belows: dict[Block, set[Block]] = field(default_factory=dict)
    tops: dict[Block, int] = field(default_factory=dict)
    blocks_supporting: dict[Block, set[Block]] = field(default_factory=dict)
    blocks_supporting_this_block: dict[Block, set[Block]] = field(default_factory=dict)
    falls: dict[Block, int] = field(default_factory=dict)

    def count_all_falls(self):
        return sum(self.count_falls(block) - 1 for block in self.critical)

    def count_falls(self, block: Block):
        fallen = {block}
        to_fall = [block]
        to_fall.extend(self.blocks_supporting[block])
        while len(to_fall) != 0:
            falling = to_fall.pop(0)
            if len(self.blocks_supporting_this_block[falling].difference(fallen)) == 0:
                fallen.add(falling)
                to_fall.extend(self.blocks_supporting[falling] - fallen)
        return len(fallen)

    def count_disintegratable(self):
        for block in self.blocks:
            if block not in self.blocks_supporting:
                self.blocks_supporting[block] = set()
                self.blocks_supporting_this_block[block] = set()
            blocks_below = self.below(block)
            if len(blocks_below) == 0:
                self.blocks_supporting_this_block[block] = blocks_below
                continue
            elif len(blocks_below) == 1:
                self.critical.update(blocks_below)
                self.blocks_supporting_this_block[block] = blocks_below
                for below in blocks_below:
                    if below not in self.blocks_supporting:
                        self.blocks_supporting[below] = set()
                    self.blocks_supporting[below].add(block)
            else:
                max_top = max(self.top(block) for block in blocks_below)
                directly_below = {block for block in blocks_below if self.top(block) == max_top}
                if len(directly_below) == 1:
                    self.critical.update(directly_below)
                self.blocks_supporting_this_block[block] = directly_below
                for below in directly_below:
                    if below not in self.blocks_supporting:
                        self.blocks_supporting[below] = set()
                    self.blocks_supporting[below].add(block)
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
    state.count_disintegratable()
    # show(state.blocks_supporting, clear=True)
    # return state.count_falls(Block(Vec3(1, 0, 1), Vec3(1, 2, 1)))
    return state.count_all_falls()

# pret("Trial:", calculate("trial.txt"))
pret("Input:", calculate("input.txt"))
# 1038654847562430945429691581559826288 - too high
# 431900 - too high
# 84878 - too high
# 83457 - wrong
# 63166
