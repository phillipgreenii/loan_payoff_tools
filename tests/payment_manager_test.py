'''
loan_payoff_tools: Test module.

Meant for use with py.test.
Write each test as a function named test_<something>.
Read more here: http://pytest.org/

Copyright 2014, Phillip Green II
Licensed under MIT
'''

import unittest
from datetime import date

from loan_payoff_tools.payment_manager import Account
from loan_payoff_tools.payment_manager import MinimumPaymentManager
from loan_payoff_tools.payment_manager import PayMostInterestPaymentPaymentManager
from loan_payoff_tools.payment_manager import PayLeastInterestPaymentPaymentManager
from loan_payoff_tools.payment_manager import SmallestDebtPaymentManager
from loan_payoff_tools.payment_manager import BiggestDebtPaymentManager
from loan_payoff_tools.payment_manager import WeightedSplitPaymentManager
from loan_payoff_tools.payment_manager import EvenSplitPaymentManager
from loan_payoff_tools.payment_manager import SpecifiedSplitPaymentManager
from loan_payoff_tools.max_payment_determiner import ConstantMaxPaymentDeterminer
from loan_payoff_tools.money import Money
import loan_payoff_tools.money as money


class PaymentManagerMakePaymentsTestCase(unittest.TestCase):

    def assertMaxTotalPaymentNotExceeded(self, payments):
        fudge_factory = Money("0.01")
        self.assertLessEqual(sum(payments.values(), Money(0)), self.max_total_payment + fudge_factory)

    def assertTotalBalanceNotExceeded(self, payments, initial_account_to_balances):
        fudge_factory = Money("0.01")
        self.assertLessEqual(sum(payments.values(), Money(0)), sum(initial_account_to_balances.values(), Money(0)) + fudge_factory)

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
        self.max_total_payment = Money(1000)
        self.payment_manager = MinimumPaymentManager()

    def test_make_payments_should_pay_minimum(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.02, 55.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 6000, 0.04, 70.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 7000, 0.03, 60.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(100.00), account1: Money(100.00), account2: Money(100.00)}

        expected_payments = {account0: Money(55.00), account1: Money(70.00), account2: Money(60.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)


    def test_make_payments_with_ignored_minimums_should_pay_minimum(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.02, 55.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 6000, 0.04, 70.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 7000, 0.03, 60.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(100.00), account1: Money(100.00), account2: Money(100.00)}

        expected_payments = {account0: Money(55.00), account1: Money(70.00), account2: Money(60.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_pay_no_more_than_current_balance(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.02, 55.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 6000, 0.04, 70.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 7000, 0.03, 60.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(100.00), account1: Money(25.00), account2: Money(45.00)}

        expected_payments = {account0: Money(55.00), account1: Money(25.00), account2: Money(45.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_pay_no_more_than_current_balance(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.02, 55.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 6000, 0.04, 70.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 7000, 0.03, 60.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(100.00), account1: Money(25.00), account2: Money(45.00)}

        expected_payments = {account0: Money(55.00), account1: Money(25.00), account2: Money(45.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

class TestPayMostInterestPaymentPaymentManager(PaymentManagerMakePaymentsTestCase):

    def setUp(self):
        self.max_total_payment = Money(1000)
        self.payment_manager = PayMostInterestPaymentPaymentManager()

    def test_make_payments_should_order_by_debtor_id_debtee_when_identical_accounts_and_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(900.00), account1: Money(50.00), account2: Money(50.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_debtor_id_debtee_when_identical_accounts_and_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(1000.00), account1: Money(0.00), account2: Money(0.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_order_by_highest_balance_when_identical_accounts(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4800.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(50.00), account1: Money(900.00), account2: Money(50.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_highest_balance_when_identical_accounts(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4800.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(0.00), account1: Money(1000.00), account2: Money(0.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_order_by_highest_interest_when_identical_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(900.00), account1: Money(50.00), account2: Money(50.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_highest_interest_when_identical_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(1000.00), account1: Money(0.00), account2: Money(0.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_order_by_weighted_interest_and_balance_when_different(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(500.00), account1: Money(4750.00), account2: Money(4900.00)}

        expected_payments = {account0: Money(50.00), account1: Money(900.00), account2: Money(50.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_weighted_interest_and_balance_when_different(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(500.00), account1: Money(4750.00), account2: Money(4900.00)}

        expected_payments = {account0: Money(0.00), account1: Money(1000.00), account2: Money(0.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(300.00), account1: Money(200.00), account2: Money(200.00)}

        expected_payments = {account0: Money(300.00), account1: Money(200.00), account2: Money(200.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(300.00), account1: Money(200.00), account2: Money(200.00)}

        expected_payments = {account0: Money(300.00), account1: Money(200.00), account2: Money(200.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off_in_order(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(500.00), account1: Money(500.00), account2: Money(100.00)}

        expected_payments = {account0: Money(450.00), account1: Money(500.00), account2: Money(50.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off_in_order(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(500.00), account1: Money(500.00), account2: Money(100.00)}

        expected_payments = {account0: Money(500.00), account1: Money(500.00), account2: Money(00.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)


class TestPayLeastInterestPaymentPaymentManager(PaymentManagerMakePaymentsTestCase):

    def setUp(self):
        self.max_total_payment = Money(1000)
        self.payment_manager = PayLeastInterestPaymentPaymentManager()


    def test_make_payments_should_order_by_debtor_id_debtee_when_identical_accounts_and_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(900.00), account1: Money(50.00), account2: Money(50.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_debtor_id_debtee_when_identical_accounts_and_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(1000.00), account1: Money(0.00), account2: Money(0.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_order_by_lowest_balance_when_identical_accounts(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4600.00), account1: Money(4800.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(50.00), account1: Money(50.00), account2: Money(900.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_lowest_balance_when_identical_accounts(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4600.00), account1: Money(4800.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(0.00), account1: Money(0.00), account2: Money(1000.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_order_by_lowest_interest_when_identical_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(900.00), account1: Money(50.00), account2: Money(50.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_lowest_interest_when_identical_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(1000.00), account1: Money(0.00), account2: Money(0.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_order_by_weighted_interest_and_balance_when_different(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(2500.00), account1: Money(3000.00), account2: Money(4900.00)}

        expected_payments = {account0: Money(50.00), account1: Money(900.00), account2: Money(50.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_weighted_interest_and_balance_when_different(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(2500.00), account1: Money(3000.00), account2: Money(4900.00)}

        expected_payments = {account0: Money(0.00), account1: Money(1000.00), account2: Money(0.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(300.00), account1: Money(200.00), account2: Money(200.00)}

        expected_payments = {account0: Money(300.00), account1: Money(200.00), account2: Money(200.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(300.00), account1: Money(200.00), account2: Money(200.00)}

        expected_payments = {account0: Money(300.00), account1: Money(200.00), account2: Money(200.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off_in_order(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(500.00), account1: Money(500.00), account2: Money(100.00)}

        expected_payments = {account0: Money(500.00), account1: Money(400.00), account2: Money(100.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off_in_order(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(500.00), account1: Money(500.00), account2: Money(100.00)}

        expected_payments = {account0: Money(500.00), account1: Money(400.00), account2: Money(100.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)


class TestSmallestDebtPaymentManager(PaymentManagerMakePaymentsTestCase):

    def setUp(self):
        self.max_total_payment = Money(1000)
        self.payment_manager = SmallestDebtPaymentManager()


    def test_make_payments_should_order_by_debtor_id_debtee_when_identical_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(900.00), account1: Money(50.00), account2: Money(50.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_debtor_id_debtee_when_identical_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(1000.00), account1: Money(0.00), account2: Money(0.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_order_by_lowest_balance(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4300.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(50.00), account1: Money(900.00), account2: Money(50.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_lowest_balance(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4300.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(0.00), account1: Money(1000.00), account2: Money(0.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(300.00), account1: Money(200.00), account2: Money(100.00)}

        expected_payments = {account0: Money(300.00), account1: Money(200.00), account2: Money(100.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(300.00), account1: Money(200.00), account2: Money(100.00)}

        expected_payments = {account0: Money(300.00), account1: Money(200.00), account2: Money(100.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off_in_order(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(600.00), account1: Money(400.00), account2: Money(100.00)}

        expected_payments = {account0: Money(500.00), account1: Money(400.00), account2: Money(100.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off_in_order(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(600.00), account1: Money(400.00), account2: Money(100.00)}

        expected_payments = {account0: Money(500.00), account1: Money(400.00), account2: Money(100.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)


class TestBiggestDebtPaymentManager(PaymentManagerMakePaymentsTestCase):

    def setUp(self):
        self.max_total_payment = Money(1000)
        self.payment_manager = BiggestDebtPaymentManager()


    def test_make_payments_should_order_by_debtor_id_debtee_when_identical_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(900.00), account1: Money(50.00), account2: Money(50.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_debtor_id_debtee_when_identical_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(1000.00), account1: Money(0.00), account2: Money(0.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_order_by_biggest_balance(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4800.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(50.00), account1: Money(900.00), account2: Money(50.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_order_by_biggest_balance(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4800.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(0.00), account1: Money(1000.00), account2: Money(0.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(300.00), account1: Money(200.00), account2: Money(100.00)}

        expected_payments = {account0: Money(300.00), account1: Money(200.00), account2: Money(100.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(300.00), account1: Money(200.00), account2: Money(100.00)}

        expected_payments = {account0: Money(300.00), account1: Money(200.00), account2: Money(100.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off_in_order(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(600.00), account1: Money(400.00), account2: Money(100.00)}

        expected_payments = {account0: Money(600.00), account1: Money(350.00), account2: Money(50.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off_in_order(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(600.00), account1: Money(400.00), account2: Money(100.00)}

        expected_payments = {account0: Money(600.00), account1: Money(400.00), account2: Money(0.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)


class TestWeightedSplitPaymentManager(PaymentManagerMakePaymentsTestCase):

    def setUp(self):
        self.max_total_payment = Money(1000)
        self.payment_manager = WeightedSplitPaymentManager()

    def test_make_payments_should_have_same_payments_when_identical(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(333.33), account1: Money(333.33), account2: Money(333.33)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_same_payments_when_identical(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(333.33), account1: Money(333.33), account2: Money(333.33)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_have_same_payments_when_different_interests(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(333.33), account1: Money(333.33), account2: Money(333.33)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_same_payments_when_different_interests(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(333.33), account1: Money(333.33), account2: Money(333.33)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_weigh_by_balance_when_different_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 100.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 100.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 100.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(1000.00), account1: Money(3000.00), account2: Money(4000.00)}

        expected_payments = {account0: Money(181.82), account1: Money(363.64), account2: Money(454.55)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_weigh_by_balance_when_different_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 100.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 100.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 100.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(1000.00), account1: Money(3000.00), account2: Money(4000.00)}

        expected_payments = {account0: Money(125), account1: Money(375), account2: Money(500)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_have_min_plus_same_payments_when_different_min(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 150.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 200.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(1000.00), account1: Money(1000.00), account2: Money(1000.00)}

        expected_payments = {account0: Money(269.23), account1: Money(346.15), account2: Money(384.62)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_min_plus_same_payments_when_different_min(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 150.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 200.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(1000.00), account1: Money(1000.00), account2: Money(1000.00)}

        expected_payments = {account0: Money(333.33), account1: Money(333.33), account2: Money(333.33)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_have_min_plus_weight_by_balance_when_different_balance_and_different_min(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 150.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 200.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(2000.00), account1: Money(1000.00), account2: Money(1500.00)}

        expected_payments = {account0: Money(335.37), account1: Money(274.39), account2: Money(390.24)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_min_plus_weight_by_balance_when_different_balance_and_different_min(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 150.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 200.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(2000.00), account1: Money(1000.00), account2: Money(1500.00)}

        expected_payments = {account0: Money(444.44), account1: Money(222.22), account2: Money(333.33)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(600.00), account1: Money(400.00), account2: Money(50.00)}

        expected_payments = {account0: Money(569.44), account1: Money(380.56), account2: Money(50.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(600.00), account1: Money(400.00), account2: Money(50.00)}

        expected_payments = {account0: Money(571.43), account1: Money(380.95), account2: Money(47.62)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off_continueally(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(300.00), account1: Money(200.00), account2: Money(100.00)}

        expected_payments = {account0: Money(300.00), account1: Money(200.00), account2: Money(100.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off_continueally(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(300.00), account1: Money(200.00), account2: Money(100.00)}

        expected_payments = {account0: Money(300.00), account1: Money(200.00), account2: Money(100.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)


class TestEvenSplitPaymentManager(PaymentManagerMakePaymentsTestCase):

    def setUp(self):
        self.max_total_payment = Money(1000)
        self.payment_manager = EvenSplitPaymentManager()

    def test_make_payments_should_have_same_payments_when_identical(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(333.33), account1: Money(333.33), account2: Money(333.33)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_same_payments_when_identical(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(333.33), account1: Money(333.33), account2: Money(333.33)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_have_same_payments_when_different_interests(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(333.33), account1: Money(333.33), account2: Money(333.33)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_same_payments_when_different_interests(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(333.33), account1: Money(333.33), account2: Money(333.33)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_have_same_payments_when_different_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(1000.00), account1: Money(3000.00), account2: Money(4000.00)}

        expected_payments = {account0: Money(333.33), account1: Money(333.33), account2: Money(333.33)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_same_payments_when_different_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(1000.00), account1: Money(3000.00), account2: Money(4000.00)}

        expected_payments = {account0: Money(333.33), account1: Money(333.33), account2: Money(333.33)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_have_min_plus_same_payments_when_different_min(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 150.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 200.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(1000.00), account1: Money(1000.00), account2: Money(1000.00)}

        expected_payments = {account0: Money(250.00), account1: Money(350.00), account2: Money(400.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_min_plus_same_payments_when_different_min(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 150.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 200.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(1000.00), account1: Money(1000.00), account2: Money(1000.00)}

        expected_payments = {account0: Money(333.33), account1: Money(333.33), account2: Money(333.33)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 100.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(600.00), account1: Money(400.00), account2: Money(50.00)}

        expected_payments = {account0: Money(550.00), account1: Money(400.00), account2: Money(50.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 100.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(600.00), account1: Money(400.00), account2: Money(50.00)}

        expected_payments = {account0: Money(550.00), account1: Money(400.00), account2: Money(50.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off_continueally(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(300.00), account1: Money(200.00), account2: Money(100.00)}

        expected_payments = {account0: Money(300.00), account1: Money(200.00), account2: Money(100.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off_continueally(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(300.00), account1: Money(200.00), account2: Money(100.00)}

        expected_payments = {account0: Money(300.00), account1: Money(200.00), account2: Money(100.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)


class TestSpecifiedSplitPaymentManager(PaymentManagerMakePaymentsTestCase):

    def setUp(self):
        self.max_total_payment = Money(1000)
        self.payment_manager = SpecifiedSplitPaymentManager({"Bank0": 0.60, "Bank1": 0.40})


    def test_make_payments_should_have_correct_split_payments_when_identical(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(305.00), account1: Money(305.00), account2: Money(390.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_correct_split_payments_when_identical(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(300.00), account1: Money(300.00), account2: Money(400.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_have_correct_split_payments_when_different_interests(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(305.00), account1: Money(305.00), account2: Money(390.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_correct_split_payments_when_different_interests(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.04, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.02, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(4500.00), account1: Money(4500.00), account2: Money(4500.00)}

        expected_payments = {account0: Money(300.00), account1: Money(300.00), account2: Money(400.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_have_correct_split_payments_when_different_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(1000.00), account1: Money(3000.00), account2: Money(4000.00)}

        expected_payments = {account0: Money(174.23), account1: Money(435.77), account2: Money(390.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_correct_split_payments_when_different_balances(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(1000.00), account1: Money(3000.00), account2: Money(4000.00)}

        expected_payments = {account0: Money(150.00), account1: Money(450.00), account2: Money(400.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_have_correct_split_payments_when_different_min_payments(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 150.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 200.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(1000.00), account1: Money(1000.00), account2: Money(1000.00)}

        expected_payments = {account0: Money(240.00), account1: Money(320.00), account2: Money(440.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_have_correct_split_payments_when_different_min_payments(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 150.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 200.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(1000.00), account1: Money(1000.00), account2: Money(1000.00)}

        expected_payments = {account0: Money(300.00), account1: Money(300.00), account2: Money(400.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 100.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(600.00), account1: Money(400.00), account2: Money(50.00)}

        expected_payments = {account0: Money(567.65), account1: Money(382.35), account2: Money(50.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 100.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(600.00), account1: Money(400.00), account2: Money(50.00)}

        expected_payments = {account0: Money(570.00), account1: Money(380.00), account2: Money(50.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)

    def test_make_payments_should_split_excess_if_account_becomes_paid_off_continueally(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(300.00), account1: Money(200.00), account2: Money(100.00)}

        expected_payments = {account0: Money(300.00), account1: Money(200.00), account2: Money(100.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, False)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)
        self.assertMinimumPayments(payments, accounts_to_balances)

    def test_make_payments_with_ignored_minimums_should_split_excess_if_account_becomes_paid_off_continueally(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 5000, 0.03, 50.00, date(2014, 5, 1))
        accounts_to_balances = {account0: Money(300.00), account1: Money(200.00), account2: Money(100.00)}

        expected_payments = {account0: Money(300.00), account1: Money(200.00), account2: Money(100.00)}

        payments = self.payment_manager(self.max_total_payment, accounts_to_balances, True)

        self.assertEqual(payments, expected_payments)
        self.assertMaxTotalPaymentNotExceeded(payments)
        self.assertTotalBalanceNotExceeded(payments, accounts_to_balances)


if __name__ == '__main__':
    unittest.main()
