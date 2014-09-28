import unittest
from datetime import date

from payment_manager import Account
from payment_manager import MinimumPaymentManager
from payment_manager import PayMostInterestPaymentPaymentManager
from payment_manager import PayLeastInterestPaymentPaymentManager
from payment_manager import SmallestDebtPaymentManager
from payment_manager import BiggestDebtPaymentManager
from payment_manager import WeightedSplitPaymentManager
from payment_manager import EvenSplitPaymentManager
from payment_manager import SpecifiedSplitPaymentManager
from max_payment_determiner import ConstantMaxPaymentDeterminer


class PaymentManagerMakePaymentsTestCase(unittest.TestCase):

    def assertMaxTotalPaymentNotExceeded(self, payments):
        fudge_factory = 0.005
        self.assertLessEqual(sum(payments.values()), self.max_total_payment+fudge_factory)

    def assertTotalBalanceNotExceeded(self, payments, initial_account_to_balances):
        fudge_factory = 0.005
        self.assertLessEqual(sum(payments.values()), sum(initial_account_to_balances.values())+fudge_factory)

    def assertMinimumPayments(self, payments, initial_account_to_balances):
        def min_for(a):
            return min(a.minimum_payment, initial_account_to_balances[a])
        improper_payment_accounts = [a for a, p in payments.items() if p < min_for(a)]
        if len(improper_payment_accounts) > 0:
            messages = ["\tpayment ({}) for {} is less than minimum ({})".format(payments[a], a, min_for(a))
                        for a in improper_payment_accounts]
            self.fail("Minimum Payments not met\n" + "\n".join(messages))


class TestMinimumPaymentManager(PaymentManagerMakePaymentsTestCase):
    def setUp(self):
        self.max_total_payment = 1000
        self.payment_manager = MinimumPaymentManager()

    def test_make_payments_should_pay_minimum(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.02, 55.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 6000, 0.04, 70.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 7000, 0.03, 60.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 100.00, account1: 100.00, account2: 100.00}

        expected_payments = {account0: 55.00, account1: 70.00, account2: 60.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)


    def test_make_payments_with_ignored_minimums_should_pay_minimum(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.02, 55.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 6000, 0.04, 70.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 7000, 0.03, 60.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 100.00, account1: 100.00, account2: 100.00}

        expected_payments = {account0: 55.00, account1: 70.00, account2: 60.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_pay_no_more_than_current_balance(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.02, 55.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 6000, 0.04, 70.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 7000, 0.03, 60.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 100.00, account1: 25.00, account2: 45.00}

        expected_payments = {account0: 55.00, account1: 25.00, account2: 45.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_pay_no_more_than_current_balance(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.02, 55.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 6000, 0.04, 70.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 7000, 0.03, 60.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 100.00, account1: 25.00, account2: 45.00}

        expected_payments = {account0: 55.00, account1: 25.00, account2: 45.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

class TestPayMostInterestPaymentPaymentManager(PaymentManagerMakePaymentsTestCase):

    def setUp(self):
        self.max_total_payment = 1000
        self.payment_manager = PayMostInterestPaymentPaymentManager()

    def test_make_payments_should_order_by_debtor_id_debtee_when_identical_accounts_and_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 900.00, account1: 50.00, account2: 50.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_debtor_id_debtee_when_identical_accounts_and_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 1000.00, account1: 0.00, account2: 0.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_order_by_highest_balance_when_identical_accounts(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4800.00, account2: 4500.00}

        expected_payments = {account0: 50.00, account1: 900.00, account2: 50.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_highest_balance_when_identical_accounts(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4800.00, account2: 4500.00}

        expected_payments = {account0: 0.00, account1: 1000.00, account2: 0.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_order_by_highest_interest_when_identical_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 900.00, account1: 50.00, account2: 50.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_highest_interest_when_identical_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 1000.00, account1: 0.00, account2: 0.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_order_by_weighted_interest_and_balance_when_different(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 500.00, account1: 4750.00, account2: 4900.00}

        expected_payments = {account0: 50.00, account1: 900.00, account2: 50.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_weighted_interest_and_balance_when_different(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 500.00, account1: 4750.00, account2: 4900.00}

        expected_payments = {account0: 0.00, account1: 1000.00, account2: 0.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 300.00, account1: 200.00, account2: 200.00}

        expected_payments = {account0: 300.00, account1: 200.00, account2: 200.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 300.00, account1: 200.00, account2: 200.00}

        expected_payments = {account0: 300.00, account1: 200.00, account2: 200.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off_in_order(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 500.00, account1: 500.00, account2: 100.00}

        expected_payments = {account0: 450.00, account1: 500.00, account2: 50.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off_in_order(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 500.00, account1: 500.00, account2: 100.00}

        expected_payments = {account0: 500.00, account1: 500.00, account2: 00.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)


class TestPayLeastInterestPaymentPaymentManager(PaymentManagerMakePaymentsTestCase):

    def setUp(self):
        self.max_total_payment = 1000
        self.payment_manager = PayLeastInterestPaymentPaymentManager()


    def test_make_payments_should_order_by_debtor_id_debtee_when_identical_accounts_and_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 900.00, account1: 50.00, account2: 50.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_debtor_id_debtee_when_identical_accounts_and_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 1000.00, account1: 0.00, account2: 0.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_order_by_lowest_balance_when_identical_accounts(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4600.00, account1: 4800.00, account2: 4500.00}

        expected_payments = {account0: 50.00, account1: 50.00, account2: 900.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_lowest_balance_when_identical_accounts(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4600.00, account1: 4800.00, account2: 4500.00}

        expected_payments = {account0: 0.00, account1: 0.00, account2: 1000.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_order_by_lowest_interest_when_identical_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 900.00, account1: 50.00, account2: 50.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_lowest_interest_when_identical_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 1000.00, account1: 0.00, account2: 0.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_order_by_weighted_interest_and_balance_when_different(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 2500.00, account1: 3000.00, account2: 4900.00}

        expected_payments = {account0: 50.00, account1: 900.00, account2: 50.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_weighted_interest_and_balance_when_different(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 2500.00, account1: 3000.00, account2: 4900.00}

        expected_payments = {account0: 0.00, account1: 1000.00, account2: 0.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 300.00, account1: 200.00, account2: 200.00}

        expected_payments = {account0: 300.00, account1: 200.00, account2: 200.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 300.00, account1: 200.00, account2: 200.00}

        expected_payments = {account0: 300.00, account1: 200.00, account2: 200.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off_in_order(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 500.00, account1: 500.00, account2: 100.00}

        expected_payments = {account0: 500.00, account1: 400.00, account2: 100.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off_in_order(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 500.00, account1: 500.00, account2: 100.00}

        expected_payments = {account0: 500.00, account1: 400.00, account2: 100.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)


class TestSmallestDebtPaymentManager(PaymentManagerMakePaymentsTestCase):

    def setUp(self):
        self.max_total_payment = 1000
        self.payment_manager = SmallestDebtPaymentManager()


    def test_make_payments_should_order_by_debtor_id_debtee_when_identical_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 900.00, account1: 50.00, account2: 50.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_debtor_id_debtee_when_identical_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 1000.00, account1: 0.00, account2: 0.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_order_by_lowest_balance(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4300.00, account2: 4500.00}

        expected_payments = {account0: 50.00, account1: 900.00, account2: 50.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_lowest_balance(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4300.00, account2: 4500.00}

        expected_payments = {account0: 0.00, account1: 1000.00, account2: 0.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 300.00, account1: 200.00, account2: 100.00}

        expected_payments = {account0: 300.00, account1: 200.00, account2: 100.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 300.00, account1: 200.00, account2: 100.00}

        expected_payments = {account0: 300.00, account1: 200.00, account2: 100.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off_in_order(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 600.00, account1: 400.00, account2: 100.00}

        expected_payments = {account0: 500.00, account1: 400.00, account2: 100.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off_in_order(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 600.00, account1: 400.00, account2: 100.00}

        expected_payments = {account0: 500.00, account1: 400.00, account2: 100.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)


class TestBiggestDebtPaymentManager(PaymentManagerMakePaymentsTestCase):

    def setUp(self):
        self.max_total_payment = 1000
        self.payment_manager = BiggestDebtPaymentManager()


    def test_make_payments_should_order_by_debtor_id_debtee_when_identical_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 900.00, account1: 50.00, account2: 50.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_debtor_id_debtee_when_identical_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 1000.00, account1: 0.00, account2: 0.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_order_by_biggest_balance(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4800.00, account2: 4500.00}

        expected_payments = {account0: 50.00, account1: 900.00, account2: 50.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_biggest_balance(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4800.00, account2: 4500.00}

        expected_payments = {account0: 0.00, account1: 1000.00, account2: 0.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 300.00, account1: 200.00, account2: 100.00}

        expected_payments = {account0: 300.00, account1: 200.00, account2: 100.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 300.00, account1: 200.00, account2: 100.00}

        expected_payments = {account0: 300.00, account1: 200.00, account2: 100.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off_in_order(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 600.00, account1: 400.00, account2: 100.00}

        expected_payments = {account0: 600.00, account1: 350.00, account2: 50.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off_in_order(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 600.00, account1: 400.00, account2: 100.00}

        expected_payments = {account0: 600.00, account1: 400.00, account2: 0.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)


class TestWeightedSplitPaymentManager(PaymentManagerMakePaymentsTestCase):

    def setUp(self):
        self.max_total_payment = 1000
        self.payment_manager = WeightedSplitPaymentManager()

    def test_make_payments_should_have_same_payments_when_identical(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 1000./3, account1: 1000./3, account2: 1000./3}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_same_payments_when_identical(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 1000./3, account1: 1000./3, account2: 1000./3}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_have_same_payments_when_different_interests(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 1000./3, account1: 1000./3, account2: 1000./3}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_same_payments_when_different_interests(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 1000./3, account1: 1000./3, account2: 1000./3}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_weigh_by_balance_when_different_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 100.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 100.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 100.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 1000.00, account1: 3000.00, account2: 4000.00}

        expected_payments = {account0: 181.8181818181818, account1: 363.6363636363636, account2: 454.5454545454545}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_weigh_by_balance_when_different_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 100.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 100.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 100.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 1000.00, account1: 3000.00, account2: 4000.00}

        expected_payments = {account0: 125, account1: 375, account2: 500}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_have_min_plus_same_payments_when_different_min(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 150.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 200.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 1000.00, account1: 1000.00, account2: 1000.00}

        expected_payments = {account0: 269.2307692307692, account1: 346.1538461538462, account2: 384.61538461538464}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_min_plus_same_payments_when_different_min(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 150.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 200.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 1000.00, account1: 1000.00, account2: 1000.00}

        expected_payments = {account0: 1000./3, account1: 1000./3, account2: 1000./3}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_have_min_plus_weight_by_balance_when_different_balance_and_different_min(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 150.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 200.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 2000.00, account1: 1000.00, account2: 1500.00}

        expected_payments = {account0: 335.3658536585366, account1: 274.390243902439, account2: 390.2439024390244}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_min_plus_weight_by_balance_when_different_balance_and_different_min(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 150.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 200.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 2000.00, account1: 1000.00, account2: 1500.00}

        expected_payments = {account0: 444.4444444444444, account1: 222.2222222222222, account2: 333.3333333333333}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 600.00, account1: 400.00, account2: 50.00}

        expected_payments = {account0: 569.4444444444445, account1: 380.55555555555554, account2: 50.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 600.00, account1: 400.00, account2: 50.00}

        expected_payments = {account0: 571.4285714285714, account1: 380.9523809523809, account2: 47.61904761904761}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off_continueally(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 300.00, account1: 200.00, account2: 100.00}

        expected_payments = {account0: 300.00, account1: 200.00, account2: 100.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off_continueally(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 300.00, account1: 200.00, account2: 100.00}

        expected_payments = {account0: 300.00, account1: 200.00, account2: 100.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)


class TestEvenSplitPaymentManager(PaymentManagerMakePaymentsTestCase):

    def setUp(self):
        self.max_total_payment = 1000
        self.payment_manager = EvenSplitPaymentManager()

    def test_make_payments_should_have_same_payments_when_identical(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 1000./3, account1: 1000./3, account2: 1000./3}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_same_payments_when_identical(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 1000./3, account1: 1000./3, account2: 1000./3}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_have_same_payments_when_different_interests(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 1000./3, account1: 1000./3, account2: 1000./3}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_same_payments_when_different_interests(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 1000./3, account1: 1000./3, account2: 1000./3}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_have_same_payments_when_different_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 1000.00, account1: 3000.00, account2: 4000.00}

        expected_payments = {account0: 1000./3, account1: 1000./3, account2: 1000./3}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_same_payments_when_different_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 1000.00, account1: 3000.00, account2: 4000.00}

        expected_payments = {account0: 1000./3, account1: 1000./3, account2: 1000./3}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_have_min_plus_same_payments_when_different_min(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 150.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 200.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 1000.00, account1: 1000.00, account2: 1000.00}

        expected_payments = {account0: 250.00, account1: 350.00, account2: 400.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_min_plus_same_payments_when_different_min(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 150.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 200.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 1000.00, account1: 1000.00, account2: 1000.00}

        expected_payments = {account0: 333.3333333333333, account1: 333.3333333333333, account2: 333.3333333333333}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 100.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 600.00, account1: 400.00, account2: 50.00}

        expected_payments = {account0: 550.00, account1: 400.00, account2: 50.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 100.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 600.00, account1: 400.00, account2: 50.00}

        expected_payments = {account0: 550.00, account1: 400.00, account2: 50.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off_continueally(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 300.00, account1: 200.00, account2: 100.00}

        expected_payments = {account0: 300.00, account1: 200.00, account2: 100.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off_continueally(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 300.00, account1: 200.00, account2: 100.00}

        expected_payments = {account0: 300.00, account1: 200.00, account2: 100.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)


class TestSpecifiedSplitPaymentManager(PaymentManagerMakePaymentsTestCase):

    def setUp(self):
        self.max_total_payment = 1000
        self.payment_manager = SpecifiedSplitPaymentManager({"Bank0": 0.60, "Bank1": 0.40})


    def test_make_payments_should_have_correct_split_payments_when_identical(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 305.00, account1: 305.00, account2: 390.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_correct_split_payments_when_identical(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 300.00, account1: 300.00, account2: 400.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_have_correct_split_payments_when_different_interests(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 305.00, account1: 305.00, account2: 390.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_correct_split_payments_when_different_interests(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 4500.00, account1: 4500.00, account2: 4500.00}

        expected_payments = {account0: 300.00, account1: 300.00, account2: 400.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_have_correct_split_payments_when_different_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 1000.00, account1: 3000.00, account2: 4000.00}

        expected_payments = {account0: 174.23076923076923, account1: 435.7692307692308, account2: 390.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_correct_split_payments_when_different_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 1000.00, account1: 3000.00, account2: 4000.00}

        expected_payments = {account0: 150.00, account1: 450.00, account2: 400.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_have_correct_split_payments_when_different_min_payments(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 150.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 200.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 1000.00, account1: 1000.00, account2: 1000.00}

        expected_payments = {account0: 240.00, account1: 320.00, account2: 440.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_correct_split_payments_when_different_min_payments(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 150.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 200.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 1000.00, account1: 1000.00, account2: 1000.00}

        expected_payments = {account0: 300.00, account1: 300.00, account2: 400.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 100.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 600.00, account1: 400.00, account2: 50.00}

        expected_payments = {account0: 567.6456692752865, account1: 382.3521832410654, account2: 50.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 100.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 600.00, account1: 400.00, account2: 50.00}

        expected_payments = {account0: 569.998590713856, account1: 379.99906047590406, account2: 50.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off_continueally(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 300.00, account1: 200.00, account2: 100.00}

        expected_payments = {account0: 300.00, account1: 200.00, account2: 100.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off_continueally(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: 300.00, account1: 200.00, account2: 100.00}

        expected_payments = {account0: 300.00, account1: 200.00, account2: 100.00}

        payments = self.payment_manager.make_payments(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)


if __name__ == '__main__':
    unittest.main()
