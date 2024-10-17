from numbers import Number
from typing import List


def mean(input: List[Number]) -> float:
    if len(input) == 0:
        raise ValueError("input must be non-empty")
    return sum(input) / len(input)