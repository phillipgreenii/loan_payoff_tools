import itertools
import operator

from money import Money
import money

class Account(object):
    def __init__(self, debtor, debtor_id, debtee, initial_balance, interest, minimum_payment, last_updated):
        self.debtor = debtor
        self.debtor_id = debtor_id
        self.debtee = debtee
        self.initial_balance = Money(initial_balance)
        self.interest = interest
        self.minimum_payment = Money(minimum_payment)
        self.last_updated = last_updated

    def __repr__(self):
        return "{}:{}".format(self.debtor, self.debtor_id)


class PaymentManager(object):

    @property
    def id(self):
        return str(self)

    def _make_payments(self, max_payment, accounts_to_balances, ignore_minimum_payments):
        raise NotImplementedError("implement _make_payments(accounts_to_balances)")

    def __call__(self, max_payment, accounts_to_balances, ignore_minimum_payments=False):
        return self._make_payments(max_payment, accounts_to_balances, ignore_minimum_payments)


def make_ranked_payments(rank_fn, max_payment, accounts_to_balances, ignore_minimum_payments):
    if ignore_minimum_payments:
        payments = {a: money.ZERO for a, b in accounts_to_balances.items()}
    else:
        payments = {a: min(b, a.minimum_payment) for a, b in accounts_to_balances.items()}

    # find "best" account
    def calc_rank(account):
        return rank_fn(account, accounts_to_balances[account])
    remaining = max_payment - sum(payments.values(), money.ZERO)
    for current in sorted(accounts_to_balances.keys(), key=calc_rank):
        if not remaining:
            break
        amount = min(remaining, accounts_to_balances[current]-payments[current])
        payments[current] += amount
        remaining -= amount
    return payments


class PayMostInterestPaymentPaymentManager(PaymentManager):

    def __repr__(self):
        return "most_interest_payment"

    def _make_payments(self, max_payment, accounts_to_balances, ignore_minimum_payments):
        def rank_by_worst(account, balance):
            return (-account.interest * balance,
                    (account.debtor, account.debtor_id, account.debtee))
        return make_ranked_payments(rank_by_worst, max_payment, accounts_to_balances, ignore_minimum_payments)


class PayLeastInterestPaymentPaymentManager(PaymentManager):

    def __repr__(self):
        return "least_interest_payment"

    def _make_payments(self, max_payment, accounts_to_balances, ignore_minimum_payments):
        def rank_by_worst(account, balance):
            return (account.interest * balance,
                    (account.debtor, account.debtor_id, account.debtee))
        return make_ranked_payments(rank_by_worst, max_payment, accounts_to_balances, ignore_minimum_payments)


class SmallestDebtPaymentManager(PaymentManager):
    def __repr__(self):
        return "smallest_debt"

    def _make_payments(self, max_payment, accounts_to_balances, ignore_minimum_payments):
        def rank_by_smallest_debt(account, balance):
            return (balance,
                    (account.debtor, account.debtor_id, account.debtee))
        return make_ranked_payments(rank_by_smallest_debt, max_payment, accounts_to_balances, ignore_minimum_payments)


class BiggestDebtPaymentManager(PaymentManager):
    def __repr__(self):
        return "biggest_debt"

    def _make_payments(self, max_payment, accounts_to_balances, ignore_minimum_payments):
        def rank_by_biggest_debt(account, balance):
            return (-balance,
                    (account.debtor, account.debtor_id, account.debtee))
        return make_ranked_payments(rank_by_biggest_debt, max_payment, accounts_to_balances, ignore_minimum_payments)

def make_split_payments(share_fn, max_payment, accounts_to_balances, ignore_minimum_payments):
    if ignore_minimum_payments:
        payments = {a: money.ZERO for a, b in accounts_to_balances.items()}
    else:
        payments = {a: min(b, a.minimum_payment) for a, b in accounts_to_balances.items()}
    uncomplete_accounts = {a for a in accounts_to_balances.keys() if payments[a] < accounts_to_balances[a]}
    remaining = max_payment - sum(payments.values(), money.ZERO)
    changing = True
    while changing and uncomplete_accounts and remaining > money.ZERO:
        changing = False
        updated_accounts_to_balances = {a: accounts_to_balances[a]-payments[a] for a in uncomplete_accounts}
        shares = share_fn(updated_accounts_to_balances)
        # adjust shares for missing accounts (ie accounts that have already been paid off)
        # if shares doesn't equal up to 1, then all remaining money won't be allocated, so the iterations go
        # way up
        shares_total = sum([s for a, s in shares.items()])
        for a in uncomplete_accounts:
            p = min((shares[a]/shares_total*remaining) + payments[a], accounts_to_balances[a])
            if payments[a] != p:
                payments[a] = p
                changing = True
        remaining = max(max_payment - sum(payments.values(), money.ZERO), money.ZERO)
        uncomplete_accounts = {a for a in uncomplete_accounts if payments[a] < accounts_to_balances[a]}
    return payments


class WeightedSplitPaymentManager(PaymentManager):
    def __repr__(self):
        return "weighted_split"

    def _make_payments(self, max_payment, accounts_to_balances, ignore_minimum_payments):
        def split_by_balance(a_to_b):
            total = float(sum(a_to_b.values(), money.ZERO))
            return {a: float(b)/total for a, b in a_to_b.items()}
        return make_split_payments(split_by_balance, max_payment, accounts_to_balances, ignore_minimum_payments)


class EvenSplitPaymentManager(PaymentManager):
    def __repr__(self):
        return "even_split"

    def _make_payments(self, max_payment, accounts_to_balances, ignore_minimum_payments):
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

    def _make_payments(self, max_payment, accounts_to_balances, ignore_minimum_payments):
        def split_by_debtor(a_to_b):
            key_fn = operator.attrgetter('debtor')
            debtor_splits = {}
            for group, accounts in itertools.groupby(sorted(a_to_b.keys(), key=key_fn), key_fn):
                accounts = list(accounts)
                group_total = sum([a_to_b[a] for a in accounts], money.ZERO)
                for a in accounts:
                    debtor_splits[a] = self.split[group]*float(a_to_b[a])/float(group_total)
            return debtor_splits
        return make_split_payments(split_by_debtor, max_payment, accounts_to_balances, ignore_minimum_payments)


class MinimumPaymentManager(PaymentManager):

    def __repr__(self):
        return "minimum"

    def _make_payments(self, max_payment, accounts_to_balances, ignore_minimum_payments):
        payments = {}
        for account, balance in accounts_to_balances.items():
            payments[account] = min(balance, account.minimum_payment)
        return payments
