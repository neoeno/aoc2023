from collections import defaultdict
from dataclasses import dataclass, field

from utility.main import check, every_line, pret


@dataclass
class Hand:
    cards: str
    bid: int
    _score: int | None = None
    _j_score: int | None = None

    def get_shape(self):
        shape_dict = defaultdict(int)
        for char in self.cards:
            shape_dict[char] += 1
        return tuple(sorted(shape_dict.values(), reverse=True))

    def get_shape_j(self):
        shape = self.get_shape()
        if self.cards.count("J") == 0:
            return shape
        elif shape == (2, 2, 1) and self.cards.count("J") == 1:
            return (3, 2)
        elif shape == (2, 2, 1) and self.cards.count("J") == 2:
            return (4, 1)
        else:
            return self.jify_shape[shape]

    def score_j(self):
        if self._j_score is not None:
            return self._j_score
        self._j_score = sum([
            15**5 * Hand.shape_to_score[self.get_shape_j()],
            15**4 * Hand.card_to_score[self.cards[0]],
            15**3 * Hand.card_to_score[self.cards[1]],
            15**2 * Hand.card_to_score[self.cards[2]],
            15**1 * Hand.card_to_score[self.cards[3]],
            15**0 * Hand.card_to_score[self.cards[4]],
        ])
        return self._j_score

    def score(self):
        if self._score is not None:
            return self._score
        self._score = sum([
            15**5 * Hand.shape_to_score[self.get_shape()],
            15**4 * Hand.card_to_score[self.cards[0]],
            15**3 * Hand.card_to_score[self.cards[1]],
            15**2 * Hand.card_to_score[self.cards[2]],
            15**1 * Hand.card_to_score[self.cards[3]],
            15**0 * Hand.card_to_score[self.cards[4]],
        ])
        return self._score

Hand.card_to_score = {
    "A": 13,
    "K": 12,
    "Q": 11,
    "T": 10,
    "9": 9,
    "8": 8,
    "7": 7,
    "6": 6,
    "5": 5,
    "4": 4,
    "3": 3,
    "2": 2,
    "J": 1,
}

Hand.shape_to_score = {
    (5,): 7,
    (4, 1): 6,
    (3, 2): 5,
    (3, 1, 1): 4,
    (2, 2, 1): 3,
    (2, 1, 1, 1): 2,
    (1, 1, 1, 1, 1): 1
}

Hand.jify_shape = {
    (5,): (5,),
    (4, 1): (5,),
    (3, 2): (5,),
    (3, 1, 1): (4, 1),
    (2, 1, 1, 1): (3, 1, 1),
    (1, 1, 1, 1, 1): (2, 1, 1, 1)
}


@dataclass
class State:
    hands: list[Hand] = field(default_factory=list)

    def sort_hands(self):
        return sorted(self.hands, key=lambda h: h.score_j())

    def score(self):
        sorted_hands = self.sort_hands()
        total = 0
        for idx, hand in enumerate(sorted_hands):
            total += hand.bid * (idx + 1)
        return total

def parse_line(state, line, _idx):
    state.hands.append(
        Hand(line[0:5], int(line[6:]))
    )
    return state

def compute(filename):
    my_state = State()
    my_state = every_line(my_state, filename, [parse_line])
    return my_state.score()

pret("Trial result:", compute("trial.txt"))
pret("Input result:", compute("input.txt"))

