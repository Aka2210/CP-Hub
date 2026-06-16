def exp_to_next(level: int) -> int:
    return int(100 * level**1.5)


def level_from_exp(total_exp: int) -> int:
    level = 1
    accumulated = 0
    while True:
        needed = exp_to_next(level)
        if accumulated + needed > total_exp:
            return level
        accumulated += needed
        level += 1


def exp_progress(total_exp: int) -> tuple[int, int, int]:
    """Returns (exp_in_current_level, exp_needed_for_next, current_level)."""
    level = 1
    accumulated = 0
    while True:
        needed = exp_to_next(level)
        if accumulated + needed > total_exp:
            return total_exp - accumulated, needed, level
        accumulated += needed
        level += 1
