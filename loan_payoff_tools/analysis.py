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

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    def dump_monthly_payments_to_png(output_file, monthly_payments):
        # build x y remaining per account
        by_account = {}
        timestamps = []
        for mp in monthly_payments:
            timestamp, payments = mp
            timestamps.append(timestamp)
            for account, (payment, remaining) in payments.items():
                if account not in by_account:
                    by_account[account] = []
                by_account[account].append(float(remaining))

        fig = plt.figure()
        graph = fig.add_subplot(111)
        for account in sorted(by_account.keys(), reverse=True):
            y = by_account[account]
            x = timestamps[:len(y)]
            graph.plot(x, y, label=str(account))

        graph.set_xticks(x)
        graph.set_xticklabels([x.strftime("%Y-%m-%d") for x in x])

        plt.legend(loc='upper right')

        # Shrink current axis by 20%
        box = graph.get_position()
        graph.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        graph.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size':6})

        plt.savefig(output_file)

except ImportError:
    pass

AnalysisResults = collections.namedtuple('AnalysisResults', ['max_payment_determiner', 'payment_manager', 'bonus_payment_manager', 'months', 'initial_debt', 'total_paid', 'interest_paid', 'monthly_payments'])


def analyze(max_payment_determiner, payment_manager, bonus_payment_manager, accounts):
    initial_debt = sum([a.initial_balance for a in accounts], money.ZERO)
    (total_paid, months, monthly_payments) = calculate_payoff(max_payment_determiner, payment_manager, bonus_payment_manager, accounts)
    return AnalysisResults(max_payment_determiner, payment_manager, bonus_payment_manager, months, initial_debt, total_paid, total_paid - initial_debt, monthly_payments)
