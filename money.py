from decimal import Decimal
import decimal
from functools import total_ordering


@total_ordering
class Money(object):
    _round_amount = Decimal('1.00')

    def __init__(self, value):
        if isinstance(value, Money):
            self._value = value._value
        else:
            if isinstance(value, Decimal):
                value = value
            elif isinstance(value, basestring):
                value = Decimal(value)
            elif isinstance(value, float):
                value = Decimal(value)
            elif isinstance(value, long):
                value = Decimal(value)
            elif isinstance(value, int):
                value = Decimal(value)
            else:
                raise ValueError("Unsupported amount type: {}".format(value))

            self._value = self._round(value)

    def _round(self, x):
        return x.quantize(self._round_amount, decimal.ROUND_HALF_UP)

    def __repr__(self):
        return "${:.2f}".format(self._value)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._value == other._value
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self._value < other._value
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return Money((self._value + other._value))
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, self.__class__):
            return Money((self._value - other._value))
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, int):
            return Money(self._value * other)
        elif isinstance(other, float):
            return Money(self._value * Decimal(other))
        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, int):
            return Money(self._value * other)
        elif isinstance(other, float):
            return Money(self._value * Decimal(other))
        return NotImplemented

    def __div__(self, other):
        if isinstance(other, int):
            return Money(self._value / other)
        elif isinstance(other, float):
            return Money(self._value / Decimal(other))
        return NotImplemented

    def __neg__(self):
        return Money(-self._value)

    def __hash__(self):
        return hash(self._value)

    def __float__(self):
        return float(self._value)

    def __int__(self):
        return int(self._value)

    def __long__(self):
        return long(self._value)

    def __nonzero__(self):
        return bool(self._value)

ZERO = Money(0)
