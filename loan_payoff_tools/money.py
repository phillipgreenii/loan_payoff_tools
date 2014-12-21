from decimal import Decimal
import decimal
from functools import total_ordering


@total_ordering
class Money(object):
    _round_amount = Decimal('1.00')

    def __init__(self, dollars=None, cents=None):
        if isinstance(dollars, Money):
            if cents:
                raise ValueError("if dollars is Money, then cents should not be specified")
            self._cents = dollars._cents
        else:
            total_cents = 0
            round = False
            if dollars:
                #handle dollars
                if isinstance(dollars, long):
                    total_cents += dollars * 100
                elif isinstance(dollars, int):
                    total_cents += dollars * 100
                elif isinstance(dollars, float):
                    total_cents += dollars * 100
                    round = True
                elif isinstance(dollars, Decimal):
                    total_cents += float(dollars*100)
                    round = True
                elif isinstance(dollars, basestring):
                    total_cents += float(Decimal(dollars)*100)
                    round = True
                else:
                    raise ValueError("Unsupported dollars type: {} ({})".format(type(dollars), dollars))
            if cents:
                #handle cents
                if isinstance(cents, long):
                    total_cents += cents
                elif isinstance(cents, int):
                    total_cents += cents
                elif isinstance(cents, float):
                    total_cents += cents
                    round = True
                elif isinstance(cents, Decimal):
                    total_cents += float(cents)
                    round = True
                elif isinstance(cents, basestring):
                    total_cents += float(Decimal(cents))
                    round = True
                else:
                    raise ValueError("Unsupported cents type: {} ({})".format(type(cents), cents))

            if round:
                total_cents = self._round(total_cents)
            self._cents = total_cents

    def _round(self, cents):
        if cents > 0:
            return long(cents + 0.5)
        elif cents < 0:
            return long(cents - 0.5)
        else:
            return 0

    def __repr__(self):
        return "${:.2f}".format(self._cents/100.0)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._cents == other._cents
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self._cents < other._cents
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return Money(cents=(self._cents + other._cents))
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, self.__class__):
            return Money(cents=(self._cents - other._cents))
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, int):
            return Money(cents=(self._cents * other))
        elif isinstance(other, float):
            return Money(cents=(self._cents * other))
        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, int):
            return Money(cents=(self._cents * other))
        elif isinstance(other, float):
            return Money(cents=(self._cents * other))
        return NotImplemented

    def __div__(self, other):
        if isinstance(other, int):
            return Money(cents=(float(self._cents) / other))
        elif isinstance(other, float):
            return Money(cents=(float(self._cents) / other))
        return NotImplemented

    def __neg__(self):
        return Money(cents=-self._cents)

    def __hash__(self):
        return hash(self._cents)

    def __float__(self):
        return float(self._cents/100.00)

    def __int__(self):
        return int(self._cents/100)

    def __long__(self):
        return long(self._cents/100)

    def __nonzero__(self):
        return bool(self._cents)

ZERO = Money(0)
