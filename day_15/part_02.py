from dataclasses import dataclass, field
import re

from utility.main import check, every_line, pret

def calc_hash(chunk: str):
    val = 0
    for char in chunk:
        val += ord(char)
        val *= 17
        val %= 256
    return val

check(calc_hash("HASH"), 52)
check(calc_hash("rn=1"), 30)

@dataclass
class Lens:
    label: str
    focal_length: int

@dataclass
class Box:
    box_no: int
    lenses: list[Lens] = field(default_factory=list)

    def calc_focusing_power(self):
        return sum(
            (self.box_no + 1) * (idx + 1) * lens.focal_length
            for idx, lens in enumerate(self.lenses)
        )

    def get_lens(self, label: str):
        return next((lens for lens in self.lenses if lens.label == label), None)

    def remove_lens(self, label: str):
        self.lenses = list(lens for lens in self.lenses if lens.label != label)


my_box = Box(0, [Lens("rn", 1), Lens("cm", 2)])
check(my_box.calc_focusing_power(), 5)
my_box = Box(3, [
            Lens("ot", 7),
            Lens("ab", 5),
            Lens("pc", 6)
        ])
check(my_box.calc_focusing_power(), 28+40+72)

@dataclass
class State:
    boxes: dict[int, Box] = field(default_factory=dict)
    line: str = ""

    def instructions(self):
        for chunk in re.finditer(r"[^,\s]+", self.line):
            yield chunk.group(0)

    def calc_focusing_power(self):
        return sum(
            box.calc_focusing_power() for box in self.boxes.values()
        )

    def execute_instructions(self):
        for instruction in self.instructions():
            if "=" in instruction:
                broken = instruction.split("=")
                self.execute_eq_instruction(broken[0], int(broken[1]))
            else:
                label = instruction.removesuffix("-")
                self.execute_hy_instruction(label)


    def execute_eq_instruction(self, label: str, focal_length: int):
        box_no = calc_hash(label)
        if box_no not in self.boxes:
            self.boxes[box_no] = Box(box_no)
        box = self.boxes[box_no]
        lens = box.get_lens(label)
        if lens is None:
            box.lenses.append(Lens(label, focal_length))
        else:
            lens.focal_length = focal_length

    def execute_hy_instruction(self, label: str):
        box_no = calc_hash(label)
        if box_no not in self.boxes:
            self.boxes[box_no] = Box(box_no)
        box = self.boxes[box_no]
        box.remove_lens(label)

my_state = State(
    {
        0: Box(0, [Lens("rn", 1), Lens("cm", 2)]),
        3: Box(3, [
            Lens("ot", 7),
            Lens("ab", 5),
            Lens("pc", 6)
        ])
    }
)

check(my_state.calc_focusing_power(), 145)

my_state = State()
my_state.execute_eq_instruction("rn", 1)
check(my_state.boxes, {
    0: Box(0, [Lens("rn", 1)])
})
my_state.execute_hy_instruction("cm")
check(my_state.boxes, {
    0: Box(0, [Lens("rn", 1)])
})
my_state.execute_eq_instruction("qp", 3)
check(my_state.boxes, {
    0: Box(0, [Lens("rn", 1)]),
    1: Box(1, [Lens("qp", 3)]),
})
my_state.execute_eq_instruction("cm", 2)
check(my_state.boxes, {
    0: Box(0, [Lens("rn", 1), Lens("cm", 2)]),
    1: Box(1, [Lens("qp", 3)]),
})
my_state.execute_hy_instruction("qp")
check(my_state.boxes, {
    0: Box(0, [Lens("rn", 1), Lens("cm", 2)]),
    1: Box(1, []),
})

def parse_line(state, line, idx):
    state.line = line

def calculate(filename):
    state = State()
    every_line(state, filename, [parse_line])
    state.execute_instructions()
    return state.calc_focusing_power()

pret("Trial:", calculate("trial.txt"))
pret("Input:", calculate("input.txt"))
