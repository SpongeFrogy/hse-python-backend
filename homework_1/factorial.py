import math

def factorial(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    return math.factorial(n)