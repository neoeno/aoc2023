import sys
from dataclasses import dataclass
from typing import Any, Callable, Collection, Sequence, Tuple, TypeVar
from collections.abc import Iterable
# from PIL import Image, ImageDraw

# == Check ==
# To replace assert and show nicer errors

def check(act, exp):
    if act == exp:
        return True
    else:
        print("== Check failed ==")
        print("ACT:", act)
        print("EXP:", exp)
        exit(1)

# == pret ==
# Print and return

def pret(str: str, item):
    print(str, item, flush=True)
    return item

# == tlog ==
# Log at a level and hide if needed
import argparse
parser = argparse.ArgumentParser(description='Do AoC')
parser.add_argument('-l', '--log', default=999, type=int)
args = parser.parse_args()
def tlog(level: int, line: str, spaces="  "):
    assert level > 0, "Don't log at zero, you can't turn it off."
    if level <= args.log:
        print(spaces * level, line, flush=True)

# == hrange ==
# To replace range in a way that checks length is as expected and is inclusive

def hrange(first: int, last: int, length: int):
    r = range(first, last + 1)
    assert first in r, f"hrange({first}, {last} should include {first}), but does not."
    assert last in r, f"hrange({first}, {last} should include {last}), but does not."
    assert len(r) == length, f"Length of hrange({first}, {last}) should be {length}, is {len(r)}."
    return r

check(
    act = len(hrange(1, 100, 100)),
    exp = 100
)

# == Every ==
# Iterates over every item in the list and calls a fn state, item, idx -> state

STATE = TypeVar('STATE')
ITEM = TypeVar('ITEM')
StateFn = Callable[[STATE, ITEM, int], STATE]

def every(state: STATE, items: Collection[ITEM], fns: list[StateFn[STATE, ITEM]]) -> STATE:
    items_length = len(items)
    for idx, item in enumerate(items):
        for fn in fns:
            state = fn(state, item, idx)
            assert items_length == len(items), "Items length changed! Not allowed by every. Consider using eat"
    return state

def eat(state: STATE, items: Sequence[ITEM], fns: list[StateFn[STATE, ITEM]]) -> STATE:
    while len(items) > 0:
        for fn in fns:
            state = fn(state, items[0], 0)
    return state

def every_line(state: STATE, file: str, fns: list[StateFn[STATE, ITEM]], strip=True) -> STATE:
    with open(file) as opened:
        for idx, line in enumerate(opened):
            if strip:
                line = line.strip()
            else:
                line = line.rstrip("\n")
            for fn in fns:
                state = fn(state, line, idx)
    return state

@dataclass
class NiceState:
    items: list

def add_(state: NiceState, item, idx: int):
    state.items.append(item)
    state.items.append(idx)
    return state

def ladd_(state: NiceState, item: str | int, _idx: int) -> NiceState:
    state.items.append(item)
    return state

check(
    act = every(state=NiceState(items=[]), items=['a', 'b', 'c'], fns=[add_, ladd_]),
    exp = NiceState(items=['a', 0, 'a', 'b', 1, 'b', 'c', 2, 'c'])
)

check(
    act = every(state=NiceState(items=[]), items=hrange(4, 6, 3), fns=[add_, ladd_]),
    exp = NiceState(items=[4, 0, 4, 5, 1, 5, 6, 2, 6])
)

# == eprint ==
# To print to stderr
# Thanks to https://stackoverflow.com/a/14981125

def show(string: str, clear = None):
    if clear:
        print("\033c", file=sys.stderr)
    print(string, file=sys.stderr)

# == adjacents ==
# To calculate adjacent cells
def adj(x, y, factory=None):
    coords = {
        (x - 1, y - 1),
        (x, y - 1),
        (x + 1, y - 1),
        (x + 1, y),
        (x + 1, y + 1),
        (x, y + 1),
        (x - 1, y + 1),
        (x - 1, y),
    }
    if factory is not None:
        return {factory(t[0], t[1]) for t in coords}
    return coords


# == Imager ==

COLORS = {
    ".": "white",
    "#": "black",
    "R": "red",
    "G": "green",
    "B": "blue",
    "/": "gray"
}
def imagify(filename: str, grid: list[list[Any]], scale=5):
    s = lambda x: x * scale
    height = s(len(grid))
    width = s(max([len(row) for row in grid]))
    with Image.new("RGBA", (width, height), "magenta") as im:
        draw = ImageDraw.Draw(im)
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                clr = str(cell)
                text = None
                if len(clr) > 1:
                    text = clr[1]
                    clr = clr[0]
                color = COLORS.get(str(clr), "magenta")
                draw.rectangle((s(x), s(y), s(x) + s(1), s(y) + s(1)), fill=color)
                if text:
                    draw.text((s(x), s(y)), text)
        im.save(filename, "PNG")

# imagify("try.png", [
#     [".", "#"],
#     ["#", "."],
#     ["R", "G"],
#     ["B", "/"],
#     ["/"]
# ], scale=20)

@dataclass(frozen=True)
class C3:
    coord: Tuple[int, int, int]
    faces: str = "######"
                # btlrfb

    def colors(self):
        if len(self.faces) == 6:
            return [COLORS.get(face, "magenta") for face in self.faces]
        elif len(self.faces) == 1:
            return [COLORS.get(self.faces, "magenta") for _ in range(6)]
        else:
            raise Exception(f"Invalid faces {self.faces}")

# import matplotlib.pyplot as plt
# import numpy as np

# class CubeChart:
#     def __init__(self):
#         self.ax = plt.figure().add_subplot(projection='3d')
#         self.drawn = False
#         self.frame = 0

#     def __enter__(self):
#         plt.ion()
#         plt.show()
#         return self

#     def redraw(self, items: list[C3], pause=0.001, recolor=False, filename=None):
#         if self.drawn is False or recolor is False:
#             self.items_length = len(items)
#             self.ax.clear()
#             self.ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/2:.0f}"))
#             self.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/2:.0f}"))
#             self.ax.zaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/2:.0f}"))
#             self.ax.set_aspect('equal', 'box')
#             self.ax.set_box_aspect((1, 1, 1))
#             maxes = [max([item.coord[i] for item in items]) + 1 for i in range(3)]
#             overall_max = max(maxes)
#             self.ax.set_xlim(0, overall_max * 2 + 1)
#             self.ax.set_ylim(0, overall_max * 2 + 1)
#             self.ax.set_zlim(0, overall_max * 2 + 1)
#             data = np.zeros(tuple(maxes))
#             for item in items:
#                 data[*item.coord] = True
#             data = self.explode(data)
#             x, y, z = self.expand_coordinates(np.indices(np.array(data.shape) + 1))
#             self.drawn = self.ax.voxels(x, y, z, data, facecolors="magenta", edgecolor="black", linewidth=0.1)
#         for item in items:
#             coord = (item.coord[0] * 2, item.coord[1] * 2, item.coord[2] * 2)
#             if coord in self.drawn:
#                 self.drawn[coord].set_facecolor(item.colors())
#         if filename:
#             plt.savefig(filename.replace("NNN", f"{self.frame:03d}"))
#             self.frame += 1
#         else:
#             plt.draw()
#             plt.pause(pause)

#     def explode(self, data):
#         size = np.array(data.shape)*2
#         data_e = np.zeros(size - 1, dtype=data.dtype)
#         data_e[::2, ::2, ::2] = data
#         return data_e

#     def expand_coordinates(self, indices):
#         x, y, z = indices
#         x[1::2, :, :] += 1
#         y[:, 1::2, :] += 1
#         z[:, :, 1::2] += 1
#         return x, y, z

#     def __exit__(self, exc_type, exc_value, traceback):
#         plt.ioff()
#         plt.close()

# # with CubeChart() as chart:
# #     from random import randint
# #     while True:
# #         random_tuple = (randint(0, 9), randint(0, 9), randint(0, 9))
# #         chart.redraw([C3(random_tuple, "RRGGBB"), C3((1, 1, 1), "RRGGBB")])


