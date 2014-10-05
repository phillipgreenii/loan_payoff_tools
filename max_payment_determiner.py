from money import Money
import money

class MaxPaymentDeterminer(object):

    @property
    def id(self):
        return str(self)

    def determine_max_payment_for(self, payments_per_year, date):
        raise NotImplementedError("implement determine_max_payment_for(payments_per_year, date)")

    def __call__(self, payments_per_year, date):
        return self.determine_max_payment_for(payments_per_year, date)


class ConstantMaxPaymentDeterminer(MaxPaymentDeterminer):

    def __init__(self, max_payment, bonus=0):
        self.max_payment = Money(max_payment)
        self.bonus = Money(bonus)

    def __repr__(self):
        return "constant_%.0f_%.0f" % (self.max_payment, self.bonus)

    def determine_max_payment_for(self, payments_per_year, date):
        return (self.max_payment, self.bonus)


class MinimumMaxPaymentDeterminer(ConstantMaxPaymentDeterminer):

    def __init__(self, accounts):
        min_payment = sum([a.minimum_payment for a in accounts], money.ZERO)
        ConstantMaxPaymentDeterminer.__init__(self, min_payment, 0)


class AnnualRaiseMaxPaymentDeterminer(MaxPaymentDeterminer):

    def __init__(self, inital_salary, annual_raise_percent, last_raise_date, initial_max_payment):
        self.inital_salary = Money(inital_salary)
        self.annual_raise_percent = annual_raise_percent
        self.last_raise_date = last_raise_date
        self.initial_max_payment = Money(initial_max_payment)
        self.tax_rate = 0.25

    def __repr__(self):
        return "annual_raise_%.0f_%.0f_%.0f" % (self.inital_salary, self.annual_raise_percent * 100, self.initial_max_payment)

    def determine_max_payment_for(self, payments_per_year, date):
        raises = (date - self.last_raise_date).days / 365
        extra_payment = self.inital_salary * (self.annual_raise_percent * raises * (1 - self.tax_rate) / payments_per_year)
        return (self.initial_max_payment + extra_payment, money.ZERO)


class MinimumAnnualRaiseMaxPaymentDeterminer(AnnualRaiseMaxPaymentDeterminer):

    def __init__(self, inital_salary, annual_raise_percent, last_raise_date, accounts):
        min_payment = sum([a.minimum_payment for a in accounts], money.ZERO)
        AnnualRaiseMaxPaymentDeterminer.__init__(self, inital_salary, annual_raise_percent, last_raise_date, min_payment)


class AnnualRaiseAndBonusMaxPaymentDeterminer(MaxPaymentDeterminer):

    def __init__(self, inital_salary, annual_raise_percent, annual_bonus_percent, last_raise_date, initial_max_payment):
        self.inital_salary = Money(inital_salary)
        self.annual_raise_percent = annual_raise_percent
        self.annual_bonus_percent = annual_bonus_percent
        self.last_raise_date = last_raise_date
        self.initial_max_payment = Money(initial_max_payment)
        self.tax_rate = 0.25

    def __repr__(self):
        return "annual_raise_and_bonus_%.0f_%.0f_%.0f_%.0f" % (self.inital_salary, self.annual_raise_percent * 100, self.annual_bonus_percent * 100, self.initial_max_payment)

    def determine_max_payment_for(self, payments_per_year, date):
        days_since_raise = (date - self.last_raise_date).days
        days_between_payments = 365/payments_per_year
        raises = days_since_raise / 365
        adjusted_salary = self.inital_salary * (1 + self.annual_raise_percent * raises)
        extra_payment = (adjusted_salary - self.inital_salary)  * ((1 - self.tax_rate) / payments_per_year)
        # FIXME can this be more clear? need to find if the current date is approximately a year later
        apply_bonus = ((days_since_raise % 365) / days_between_payments == 0) and raises > 0
        bonus = money.ZERO if not apply_bonus else (adjusted_salary * ((self.annual_bonus_percent * (1 - self.tax_rate))))
        return (self.initial_max_payment + extra_payment, bonus)


class MinimumAnnualRaiseAndBonusMaxPaymentDeterminer(AnnualRaiseAndBonusMaxPaymentDeterminer):

    def __init__(self, inital_salary, annual_raise_percent, annual_bonus_percent, last_raise_date, accounts):
        min_payment = sum([a.minimum_payment for a in accounts], money.ZERO)
        AnnualRaiseAndBonusMaxPaymentDeterminer.__init__(self, inital_salary, annual_raise_percent, annual_bonus_percent, last_raise_date, min_payment)
