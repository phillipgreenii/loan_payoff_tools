import itertools
import operator
import csv
import datetime
import os.path
import collections

import payment_manager
from payoff_calculator import calculate_payoff
import money


def load_accounts(file_name):
    accounts = []

    def to_date(str):
        datetime.datetime.strptime(str, '%Y-%m-%d').date()
    with open(file_name, 'rb') as f:
        input_file = csv.DictReader(f)
        for row in input_file:
            row = [row['debtor'],
                   row['debtor_id'],
                   row['debtee'],
                   float(row['initial_balance']),
                   float(row['interest']),
                   float(row['minimum_payment']),
                   to_date(row['last_updated'])]
            accounts.append(payment_manager.Account(*row))
    return accounts


def dump_monthly_payments_to_csv(output_file, monthly_payments):
    with open(output_file, 'wb') as f:
        accounts = monthly_payments[0][1].keys()
        ids = sorted(map(str, accounts)) + ['Total']
        headers = ['Date'] + list(itertools.starmap(operator.add, (itertools.product(ids, ['-Paid', '-Remaining']))))
        writer = csv.DictWriter(f, headers)
        writer.writeheader()
        for monthly_info in monthly_payments:
            total_paid = money.ZERO
            total_remaining = money.ZERO
            mp = {}
            current_date, month_payment = monthly_info
            mp['Date'] = current_date
            for account, paid_remaining in month_payment.items():
                paid, remaining = paid_remaining
                mp[str(account)+'-Paid'] = paid
                mp[str(account)+'-Remaining'] = remaining
                total_paid += paid
                total_remaining += remaining
            mp['Total-Paid'] = total_paid
            mp['Total-Remaining'] = total_remaining
            writer.writerow(mp)

AnalysisResults = collections.namedtuple('AnalysisResults', ['max_payment_determiner', 'payment_manager', 'bonus_payment_manager', 'months', 'initial_debt', 'total_paid', 'interest_paid', 'monthly_payments'])


def analyze(max_payment_determiner, payment_manager, bonus_payment_manager, accounts):
    initial_debt = sum([a.initial_balance for a in accounts], money.ZERO)
    (total_paid, months, monthly_payments) = calculate_payoff(max_payment_determiner, payment_manager, bonus_payment_manager, accounts)
    return AnalysisResults(max_payment_determiner, payment_manager, bonus_payment_manager, months, initial_debt, total_paid, total_paid - initial_debt, monthly_payments)
