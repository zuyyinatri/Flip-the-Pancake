import random
from dataclasses import dataclass
import settings as cfg
import bfs

@dataclass
class Level:
    number: int
    stack: list
    optimal: int
    max_flips: int

def flip(stack, k):
    return stack[:k][::-1] + stack[k:]

def is_sorted(stack):
    return all(value == i + 1 for i, value in enumerate(stack))

def pancakes_for_level(level):
    n = cfg.BASE_PANCAKES + (level - 1) // cfg.LEVELS_PER_TIER
    return min(cfg.MAX_PANCAKES, n)

def bonus_for_level(level):
    return max(0, cfg.BASE_BONUS_FLIP - (level - 1) // cfg.LEVELS_PER_TIER)

def generate_stack(n):
    min_optimal = max(2, n - 1)
    stack = list(range(1, n + 1))
    best_stack, best_optimal = stack[:], -1

    for _ in range(500):
        random.shuffle(stack)
        optimal = bfs.optimal_flips(stack)
        if optimal > best_optimal:
            best_stack, best_optimal = stack[:], optimal
        if optimal >= min_optimal:
            break
    return best_stack, best_optimal

def create_level(number):
    n = pancakes_for_level(number)
    stack, optimal = generate_stack(n)
    return Level(
        number=number,
        stack=stack,
        optimal=optimal,
        max_flips=optimal + bonus_for_level(number),
    )
