from utility.main import check, every_line, hrange, pret, show


def is_digit_at_point(line, idx):
    if line[idx:idx + 3] == "one":
        return True
    if line[idx:idx + 3] == "two":
        return True
    if line[idx:idx + 5] == "three":
        return True
    if line[idx:idx + 4] == "four":
        return True
    if line[idx:idx + 4] == "five":
        return True
    if line[idx:idx + 3] == "six":
        return True
    if line[idx:idx + 5] == "seven":
        return True
    if line[idx:idx + 5] == "eight":
        return True
    if line[idx:idx + 4] == "nine":
        return True
    return line[idx].isdigit()

check(is_digit_at_point("1abc2", 0), True)
check(is_digit_at_point("1abc2", 1), False)
check(is_digit_at_point("1abc2", 4), True)
check(is_digit_at_point("one1nine", 0), True)
check(is_digit_at_point("two1nine", 0), True)
check(is_digit_at_point("two1nine", 1), False)
check(is_digit_at_point("two1nine", 2), False)
check(is_digit_at_point("two1nine", 3), True)
check(is_digit_at_point("two1nine", 4), True)
check(is_digit_at_point("two1nine", 5), False)
check(is_digit_at_point("two1nine", 6), False)
check(is_digit_at_point("two1nine", 7), False)
check(is_digit_at_point("4nineeightseven2", 1), True)

def find_first_digit(line):
    for idx, char in enumerate(line):
        if is_digit_at_point(line, idx):
            return idx

check(find_first_digit("1abc2"), 0)
check(find_first_digit("pqr3stu8vwx"), 3)

def find_last_digit(line):
    for idx in range(len(line) - 1, -1, -1):
        if is_digit_at_point(line, idx):
            return idx

check(find_last_digit("1abc2"), 4)
check(find_last_digit("pqr3stu8vwx"), 7)
check(find_last_digit("1abc"), 0)

def make_calibration_value(a, b):
    return int(f"{a}{b}")

check(make_calibration_value("3", "2"), 32)

add_calibration_values = sum

def make_number(line, idx):
    if line[idx:idx + 3] == "one":
        return 1
    if line[idx:idx + 3] == "two":
        return 2
    if line[idx:idx + 5] == "three":
        return 3
    if line[idx:idx + 4] == "four":
        return 4
    if line[idx:idx + 4] == "five":
        return 5
    if line[idx:idx + 3] == "six":
        return 6
    if line[idx:idx + 5] == "seven":
        return 7
    if line[idx:idx + 5] == "eight":
        return 8
    if line[idx:idx + 4] == "nine":
        return 9
    return int(line[idx])

check(make_number("two1nine", 0), 2)
check(make_number("two1nine", 3), 1)
check(make_number("two1nine", 4), 9)

def calculate_line(line):
    return make_calibration_value(
        make_number(line, find_first_digit(line)),
        make_number(line, find_last_digit(line)))

check(calculate_line("1abc2"), 12)
check(calculate_line("pqr3stu8vwx"), 38)
check(calculate_line("1abc"), 11)

def calculate(filename):
    values = []
    with open(filename) as f:
        for line in f:
            values.append(calculate_line(line))
    return add_calibration_values(values)

check(pret("Trial result: ", calculate("trial_2.txt")), 281)
pret("Real result: ", calculate("input.txt"))

