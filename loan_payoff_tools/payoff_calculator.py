import itertools
import operator
import datetime
import calendar
import collections
from money import Money


def _add_months(source_date, months):
    '''Source: http://stackoverflow.com/a/4131114/388006'''
    month = source_date.month - 1 + months
    year = source_date.year + month / 12
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def _build_date_incrementer(payments_per_year):
    if payments_per_year != 12:
        raise ValueError("only 12 payments per year is supported")

    def monthly_increment(date_to_increment):
        return _add_months(date_to_increment, 1)

    return monthly_increment


def _combine_payments(*payment_groups):
    combined_payments = {}
    for payments in payment_groups:
        for a, p in payments.items():
            if a not in combined_payments:
                combined_payments[a] = Money(0)
            combined_payments[a] += p
    return combined_payments


def calculate_payoff(max_payment_determiner, payment_manager, bonus_payment_manager, accounts, starting_date=None, payments_per_year=12):
    def calculate_remaining_accounts_balance(remaining_accounts_balance, payments):
        return {a: b-payments[a] for a, b in remaining_accounts_balance.items() if payments[a] < b}
    payment_date_incrementer = _build_date_incrementer(payments_per_year)
    # TODO should this default to start of the month?
    current_payment_date = starting_date or datetime.date.today()
    remaining_accounts_balance = {a: a.initial_balance for a in accounts}
    monthly_payments = []
    total_paid = Money(0)
    while remaining_accounts_balance:
        # apply interest
        for account in remaining_accounts_balance.keys():
            remaining_accounts_balance[account] *= (1+account.interest/payments_per_year)
        (max_payment, bonus) = max_payment_determiner(payments_per_year, current_payment_date)
        account_payments = payment_manager(max_payment, remaining_accounts_balance)

        remaining_accounts_balance = calculate_remaining_accounts_balance(remaining_accounts_balance, account_payments)
        if bonus:
            bonus_account_payments = bonus_payment_manager(bonus, remaining_accounts_balance, ignore_minimum_payments = True)
            remaining_accounts_balance = calculate_remaining_accounts_balance(remaining_accounts_balance, bonus_account_payments)
            account_payments = _combine_payments(account_payments, bonus_account_payments)
        total_paid += sum(account_payments.values(), Money(0))
        monthly_payments.append((current_payment_date, {a: (p, remaining_accounts_balance.get(a, Money(0))) for a, p in account_payments.items()}))
        current_payment_date = payment_date_incrementer(current_payment_date)
    return total_paid, len(monthly_payments), monthly_payments
