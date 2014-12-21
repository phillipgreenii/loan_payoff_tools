import math


def round_up(value, decimal_places=0):
    factor = math.pow(10, -decimal_places)
    val = math.ceil(value / factor) * factor
    if decimal_places <= 0:
        return int(val)
    else:
        return val
