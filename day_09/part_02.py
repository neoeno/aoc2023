from dataclasses import dataclass, field

from utility.main import check, every_line, hrange, pret

@dataclass
class Sequence:
    nums: list[int]

    def is_all_zeros(self):
        return set(self.nums) == {0}

    def differences(self):
        diffs = []
        for idx in hrange(1, len(self.nums) - 1, len(self.nums) - 1):
            diffs.append(self.nums[idx] - self.nums[idx - 1])
        return Sequence(diffs)

    def generate(self):
        if len(self.nums) == 0:
            raise Exception("Can't generate on empty sequence")
        if self.is_all_zeros():
            return 0
        return self.nums[-1] + self.differences().generate()

    def generate_back(self):
        if len(self.nums) == 0:
            raise Exception("Can't generate on empty sequence")
        if self.is_all_zeros():
            return 0
        return self.nums[0] - self.differences().generate_back()

my_seq = Sequence([0, 0, 0])
check(my_seq.is_all_zeros(), True)
my_seq = Sequence([0, 0, 1])
check(my_seq.is_all_zeros(), False)
my_seq = Sequence([3, 6, 9])
check(my_seq.differences(), Sequence([3, 3]))
check(my_seq.generate(), 12)
check(my_seq.generate_back(), 0)

@dataclass
class State:
    sequences: list[Sequence] = field(default_factory=list)

    def sum_extrapolates(self):
        return sum(seq.generate() for seq in self.sequences)

    def sum_extrapolates_back(self):
        return sum(seq.generate_back() for seq in self.sequences)

def parse_line(state, line, idx):
    state.sequences.append(
        Sequence(list(int(strnum) for strnum in line.split(" ")))
    )
    return state

def calculate(filename):
    state = State()
    every_line(state, filename, [parse_line])
    return state.sum_extrapolates_back()

pret("Trial:", calculate("trial.txt"))
pret("Input:", calculate("input.txt"))
