import itertools
import operator
import csv
import datetime
import os.path

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


def _dump_to_file(accounts, monthly_infos, output_dir, id):
    with open(os.path.join(output_dir, id + ".csv"), 'wb') as f:
        ids = sorted(map(str, accounts)) + ['Total']
        headers = ['Date'] + list(itertools.starmap(operator.add, (itertools.product(ids, ['-Paid', '-Remaining']))))
        writer = csv.DictWriter(f, headers)
        writer.writeheader()
        for monthly_info in monthly_infos:
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


def analyze(max_payment_determiner, payment_manager, bonus_payment_manager, accounts, generate_details=True, details_directory='results'):
    initial_debt = sum([a.initial_balance for a in accounts], money.ZERO)
    (total_paid, months, monthly_payments) = calculate_payoff(max_payment_determiner, payment_manager, bonus_payment_manager, accounts)
    if generate_details:
        _dump_to_file(accounts, monthly_payments, details_directory, max_payment_determiner.id + '_' + payment_manager.id + '_' + bonus_payment_manager.id)
    return (max_payment_determiner.id, payment_manager.id, bonus_payment_manager.id, months, total_paid, total_paid - initial_debt)
