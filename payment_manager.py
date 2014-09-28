import itertools
import operator


class Account(object):
    def __init__(self, debtor, debtor_id, debtee, initial_balance, interest, minimum_payment, last_updated):
        self.debtor = debtor
        self.debtor_id = debtor_id
        self.debtee = debtee
        self.initial_balance = initial_balance
        self.interest = interest
        self.minimum_payment = minimum_payment
        self.last_updated = last_updated

    def __repr__(self):
        return "{}:{}".format(self.debtor, self.debtor_id)


class PaymentManager(object):

    @property
    def id(self):
        return str(self)

    def make_payments(self, max_payment, accounts_to_balances, ignore_minimum_payments):
        raise NotImplementedError("implement make_payments(accounts_to_balances)")

    def __call__(self, max_payment, accounts_to_balances, ignore_minimum_payments=False):
        return self.make_payments(max_payment, accounts_to_balances, ignore_minimum_payments=False)


def make_ranked_payments(rank_fn, max_payment, accounts_to_balances, ignore_minimum_payments):
    if ignore_minimum_payments:
        payments = {a: 0 for a, b in accounts_to_balances.items()}
    else:
        payments = {a: min(b, a.minimum_payment) for a, b in accounts_to_balances.items()}

    # find "best" account
    def calc_rank(account):
        return rank_fn(account, accounts_to_balances[account])
    remaining = max_payment - sum(payments.values())
    for current in sorted(accounts_to_balances.keys(), key=calc_rank):
        if remaining <= 0.005:
            break
        amount = min(remaining, accounts_to_balances[current]-payments[current])
        payments[current] += amount
        remaining -= amount
    return payments


class PayMostInterestPaymentPaymentManager(PaymentManager):

    def __repr__(self):
        return "most_interest_payment"

    def make_payments(self, max_payment, accounts_to_balances, ignore_minimum_payments):
        def rank_by_worst(account, balance):
            return (-account.interest * balance,
                    (account.debtor, account.debtor_id, account.debtee))
        return make_ranked_payments(rank_by_worst, max_payment, accounts_to_balances, ignore_minimum_payments)


class PayLeastInterestPaymentPaymentManager(PaymentManager):

    def __repr__(self):
        return "least_interest_payment"

    def make_payments(self, max_payment, accounts_to_balances, ignore_minimum_payments):
        def rank_by_worst(account, balance):
            return (account.interest * balance,
                    (account.debtor, account.debtor_id, account.debtee))
        return make_ranked_payments(rank_by_worst, max_payment, accounts_to_balances, ignore_minimum_payments)


class SmallestDebtPaymentManager(PaymentManager):
    def __repr__(self):
        return "smallest_debt"

    def make_payments(self, max_payment, accounts_to_balances, ignore_minimum_payments):
        def rank_by_smallest_debt(account, balance):
            return (balance,
                    (account.debtor, account.debtor_id, account.debtee))
        return make_ranked_payments(rank_by_smallest_debt, max_payment, accounts_to_balances, ignore_minimum_payments)


class BiggestDebtPaymentManager(PaymentManager):
    def __repr__(self):
        return "biggest_debt"

    def make_payments(self, max_payment, accounts_to_balances, ignore_minimum_payments):
        def rank_by_biggest_debt(account, balance):
            return (-balance,
                    (account.debtor, account.debtor_id, account.debtee))
        return make_ranked_payments(rank_by_biggest_debt, max_payment, accounts_to_balances, ignore_minimum_payments)


def make_split_payments(share_fn, max_payment, accounts_to_balances, ignore_minimum_payments):
    if ignore_minimum_payments:
        payments = {a: 0 for a, b in accounts_to_balances.items()}
    else:
        payments = {a: min(b, a.minimum_payment) for a, b in accounts_to_balances.items()}
    uncomplete_accounts = {a for a in accounts_to_balances.keys() if payments[a] < accounts_to_balances[a]}
    remaining = max_payment - sum(payments.values())
    while remaining > 0.005 and uncomplete_accounts:
        updated_accounts_to_balances = {a: accounts_to_balances[a]-payments[a] for a in uncomplete_accounts}
        shares = share_fn(updated_accounts_to_balances)
        for a in uncomplete_accounts:
            payments[a] = min(shares[a]*remaining + payments[a], accounts_to_balances[a])
        remaining = max_payment - sum(payments.values())
        uncomplete_accounts = {a for a in uncomplete_accounts if payments[a] < accounts_to_balances[a]}
    return payments


class WeightedSplitPaymentManager(PaymentManager):
    def __repr__(self):
        return "weighted_split"

    def make_payments(self, max_payment, accounts_to_balances, ignore_minimum_payments):
        def split_by_balance(a_to_b):
            total = float(sum(a_to_b.values()))
            return {a: b/total for a, b in a_to_b.items()}
        return make_split_payments(split_by_balance, max_payment, accounts_to_balances, ignore_minimum_payments)


class EvenSplitPaymentManager(PaymentManager):
    def __repr__(self):
        return "even_split"

    def make_payments(self, max_payment, accounts_to_balances, ignore_minimum_payments):
        def split_evenly(a_to_b):
            share = 1.0/len(a_to_b)
            return {a: share for a in a_to_b.keys()}
        return make_split_payments(split_evenly, max_payment, accounts_to_balances, ignore_minimum_payments)


class SpecifiedSplitPaymentManager(PaymentManager):

    def __init__(self, split):
        self.split = split

    def __repr__(self):
        values = map(operator.itemgetter(1), sorted(self.split.items()))
        return "specified_split_" + "_".join(map(lambda v: "%.0f"%(10000*v), values))

    def make_payments(self, max_payment, accounts_to_balances, ignore_minimum_payments):
        def split_by_debtor(a_to_b):
            key_fn = operator.attrgetter('debtor')
            debtor_splits = {}
            for group, accounts in itertools.groupby(sorted(a_to_b.keys(), key=key_fn), key_fn):
                accounts = list(accounts)
                group_total = sum([a_to_b[a] for a in accounts])
                for a in accounts:
                    debtor_splits[a] = self.split[group]*a_to_b[a]/group_total
            return debtor_splits
        return make_split_payments(split_by_debtor, max_payment, accounts_to_balances, ignore_minimum_payments)


class MinimumPaymentManager(PaymentManager):

    def __repr__(self):
        return "minimum"

    def make_payments(self, max_payment, accounts_to_balances, ignore_minimum_payments):
        payments = {}
        for account, balance in accounts_to_balances.items():
            payments[account] = min(balance, account.minimum_payment)
        return payments
