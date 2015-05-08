import operator
from datetime import date
import os.path
import functools
import math

import loan_payoff_tools.max_payment_determiner as max_payment_determiner
import loan_payoff_tools.payment_manager as payment_manager
import loan_payoff_tools.analysis as analysis
import loan_payoff_tools.utils as utils
from loan_payoff_tools.money import Money


def round_up_to_nearest_100(x):
    return Money(utils.round_up(x, -2))


def load_accounts():
    return [
        payment_manager.Account('BANKX', "00", "John Doe", 50000, 0.04, 800, date(2014,4,1)),
        payment_manager.Account('BANKX', "01", "John Doe", 30000, 0.05, 900, date(2014,5,1)),
        payment_manager.Account('BANKZ', "AB", "John Doe", 80000, 0.02, 400, date(2014,4,1))
    ]


def load_personal_information():
    # current annual salary
    salary = 50000
    # estimated annual raise each year
    annual_raise_percentage = 0.03
    # estimated bonus percentage each year
    annual_bonus = 0.10
    # roll over date is when the bonus and raise was last applied
    last_rollover_date = date(2014, 4, 1)

    return (salary, annual_raise_percentage, annual_bonus, last_rollover_date)


def generate_scenarios(personal_information, accounts, minimum_payment, increment, iterations=20):
    (salary, annual_raise_percentage, annual_bonus, last_rollover_date) = personal_information

    # This factory determines the maximum monthly payment; it increments over time based upon raises.
    # When the annual bonus is available, it
    max_payment_determiner_factory = functools.partial(max_payment_determiner.AnnualRaiseAndBonusMaxPaymentDeterminer, salary, annual_raise_percentage, annual_bonus, last_rollover_date)
    # This determines how the monthly payments are split amongst the accounts
    even_split_payment_manager = payment_manager.EvenSplitPaymentManager()
    # This determines how the additional monthly payments is split amongst the accounts
    most_interest_bonus_payment_manager = payment_manager.PayMostInterestPaymentPaymentManager()

    scenarios = []
    for i in range(iterations):
        payment = minimum_payment + increment*i
        scenario = analysis.analyze(max_payment_determiner_factory(payment),
                                    even_split_payment_manager,
                                    most_interest_bonus_payment_manager,
                                    accounts)
        scenarios.append(scenario)

    return scenarios


def display_scenarios(scenarios):
    print "{:>12s}, {:>8s}, {:>10s}, {:>10s}".format('max payment', 'months', 'paid', 'over paid')
    for result in scenarios:
        payment = result.max_payment_determiner.initial_max_payment
        months = result.months
        paid = result.total_paid
        over_paid = result.interest_paid
        print "{:>12s}, {:>8d}, {:>10s}, {:>10s}".format(payment, months, paid, over_paid)


def main():
    accounts = load_accounts()

    # minium payment is sum of all minumum payments rounded up to nearest increment
    minimum_payment = round_up_to_nearest_100(sum([a.minimum_payment for a in accounts], Money(0)))
    increment = Money(100)

    scenarios = generate_scenarios(load_personal_information(),
                                   accounts,
                                   minimum_payment, increment)

    display_scenarios(scenarios)

if __name__ == '__main__':
    main()
