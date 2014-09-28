import unittest
from datetime import date

from payment_manager import Account
from payment_manager import MinimumPaymentManager
from payment_manager import EvenSplitPaymentManager
from max_payment_determiner import ConstantMaxPaymentDeterminer

import payoff_calculator


class PayoffCalculatorTestCase(unittest.TestCase):

    def test_build_date_incrementer_12(self):
        incrementer = payoff_calculator._build_date_incrementer(12)
        self.assertEqual(incrementer(date(2014, 1, 2)), date(2014, 2, 2))
        self.assertEqual(incrementer(date(2014, 1, 30)), date(2014, 2, 28))
        self.assertEqual(incrementer(date(2014, 12, 2)), date(2015, 1, 2))

    def test_combine_payments_single(self):
        account0 = Account("Bank0", "00", "Joe", 1000, 0.03, 100.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 7500, 0.05, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Sam", 9000, 0.06, 900.00, date(2014, 5, 1))

        payment_group0 = {account0: 100.00, account1: 50.00, account2: 900.00}

        expected_payment_group = payment_group0

        self.assertEqual(payoff_calculator._combine_payments(payment_group0), expected_payment_group)

    def test_combine_payments_multiple(self):
        account0 = Account("Bank0", "00", "Joe", 1000, 0.03, 100.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 7500, 0.05, 50.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Sam", 9000, 0.06, 900.00, date(2014, 5, 1))

        payment_group0 = {account0: 100.00, account1: 50.00, account2: 900.00}
        payment_group1 = {account0: 100.00, account1: 100.00, account2: 100.00}

        expected_payment_group = {account0: 200.00, account1: 150.00, account2: 1000.00}

        self.assertEqual(payoff_calculator._combine_payments(payment_group0, payment_group1), expected_payment_group)

    def test_calculate_payoff_with_single_account_and_no_interest(self):
        max_payment_determiner = ConstantMaxPaymentDeterminer(1000)
        payment_determiner = MinimumPaymentManager()
        bonus_payment_determiner = payment_determiner
        account0 = Account("Bank0", "00", "Joe", 1000, 0, 100.00, date(2014, 5, 1))
        accounts = (account0,)
        starting_date = date(2014, 6, 30)

        expected_total_payments_amount = 1000
        expected_total_payments_count = 10
        expected_total_payments = [(date(2014, 6, 30), {account0: (100, 900.00)}),
                                   (date(2014, 7, 30), {account0: (100, 800.00)}),
                                   (date(2014, 8, 30), {account0: (100, 700.00)}),
                                   (date(2014, 9, 30), {account0: (100, 600.00)}),
                                   (date(2014, 10, 30), {account0: (100, 500.00)}),
                                   (date(2014, 11, 30), {account0: (100, 400.00)}),
                                   (date(2014, 12, 30), {account0: (100, 300.00)}),
                                   (date(2015, 1, 30), {account0: (100, 200.00)}),
                                   (date(2015, 2, 28), {account0: (100, 100.00)}),
                                   (date(2015, 3, 28), {account0: (100, 0)})]


        (total_amount, payments_count, total_payoffs) = payoff_calculator.calculate_payoff(max_payment_determiner, payment_determiner, bonus_payment_determiner, accounts, starting_date)

        self.assertAlmostEqual(total_amount, expected_total_payments_amount)
        self.assertEqual(payments_count, expected_total_payments_count)
        self.assertEqual(total_payoffs, expected_total_payments)

    def test_calculate_payoff_with_single_account_and_interest(self):
        max_payment_determiner = ConstantMaxPaymentDeterminer(1000)
        payment_determiner = MinimumPaymentManager()
        bonus_payment_determiner = payment_determiner
        account0 = Account("Bank0", "00", "Joe", 1000, 0.05, 100.00, date(2014, 5, 1))
        accounts = (account0,)
        starting_date = date(2014, 6, 30)

        expected_total_payments_amount = 1023.59470412
        expected_total_payments_count = 11
        expected_total_payments = [(date(2014, 6, 30), {account0: (100, 904.1666666666666)}),
                                   (date(2014, 7, 30), {account0: (100, 807.9340277777777)}),
                                   (date(2014, 8, 30), {account0: (100, 711.3004195601851)}),
                                   (date(2014, 9, 30), {account0: (100, 614.2641713083525)}),
                                   (date(2014, 10, 30), {account0: (100, 516.8236053554706)}),
                                   (date(2014, 11, 30), {account0: (100, 418.97703704445166)}),
                                   (date(2014, 12, 30), {account0: (100, 320.72277469880356)}),
                                   (date(2015, 1, 30), {account0: (100, 222.05911959338192)}),
                                   (date(2015, 2, 28), {account0: (100, 122.98436592502102)}),
                                   (date(2015, 3, 28), {account0: (100, 23.496800783041948)}),
                                   (date(2015, 4, 28), {account0: (23.594704119637957, 0)})]

        (total_amount, payments_count, total_payoffs) = payoff_calculator.calculate_payoff(max_payment_determiner, payment_determiner, bonus_payment_determiner, accounts, starting_date)

        self.assertAlmostEqual(total_amount, expected_total_payments_amount)
        self.assertEqual(payments_count, expected_total_payments_count)
        self.assertEqual(total_payoffs, expected_total_payments)

    def test_calculate_payoff_with_single_account_and_no_interest_and_bonus(self):
        max_payment_determiner = ConstantMaxPaymentDeterminer(50, 50)
        payment_determiner = EvenSplitPaymentManager()
        bonus_payment_determiner = EvenSplitPaymentManager()
        account0 = Account("Bank0", "00", "Joe", 1000, 0, 50.00, date(2014, 5, 1))
        accounts = (account0,)
        starting_date = date(2014, 6, 30)

        expected_total_payments_amount = 1000
        expected_total_payments_count = 10
        expected_total_payments = [(date(2014, 6, 30), {account0: (100, 900.00)}),
                                   (date(2014, 7, 30), {account0: (100, 800.00)}),
                                   (date(2014, 8, 30), {account0: (100, 700.00)}),
                                   (date(2014, 9, 30), {account0: (100, 600.00)}),
                                   (date(2014, 10, 30), {account0: (100, 500.00)}),
                                   (date(2014, 11, 30), {account0: (100, 400.00)}),
                                   (date(2014, 12, 30), {account0: (100, 300.00)}),
                                   (date(2015, 1, 30), {account0: (100, 200.00)}),
                                   (date(2015, 2, 28), {account0: (100, 100.00)}),
                                   (date(2015, 3, 28), {account0: (100, 0)})]

        (total_amount, payments_count, total_payoffs) = payoff_calculator.calculate_payoff(max_payment_determiner, payment_determiner, bonus_payment_determiner, accounts, starting_date)

        self.assertAlmostEqual(total_amount, expected_total_payments_amount)
        self.assertEqual(payments_count, expected_total_payments_count)
        self.assertEqual(total_payoffs, expected_total_payments)

    def test_calculate_payoff_with_single_account_and_interest_and_bonus(self):
        max_payment_determiner = ConstantMaxPaymentDeterminer(50, 50)
        payment_determiner = EvenSplitPaymentManager()
        bonus_payment_determiner = EvenSplitPaymentManager()
        account0 = Account("Bank0", "00", "Joe", 1000, 0.05, 50.00, date(2014, 5, 1))
        accounts = (account0,)
        starting_date = date(2014, 6, 30)

        expected_total_payments_amount = 1023.59470412
        expected_total_payments_count = 11
        expected_total_payments = [(date(2014, 6, 30), {account0: (100, 904.1666666666666)}),
                                   (date(2014, 7, 30), {account0: (100, 807.9340277777777)}),
                                   (date(2014, 8, 30), {account0: (100, 711.3004195601851)}),
                                   (date(2014, 9, 30), {account0: (100, 614.2641713083525)}),
                                   (date(2014, 10, 30), {account0: (100, 516.8236053554706)}),
                                   (date(2014, 11, 30), {account0: (100, 418.97703704445166)}),
                                   (date(2014, 12, 30), {account0: (100, 320.72277469880356)}),
                                   (date(2015, 1, 30), {account0: (100, 222.05911959338192)}),
                                   (date(2015, 2, 28), {account0: (100, 122.98436592502102)}),
                                   (date(2015, 3, 28), {account0: (100, 23.496800783041948)}),
                                   (date(2015, 4, 28), {account0: (23.594704119637957, 0)})]

        (total_amount, payments_count, total_payoffs) = payoff_calculator.calculate_payoff(max_payment_determiner, payment_determiner, bonus_payment_determiner, accounts, starting_date)

        self.assertAlmostEqual(total_amount, expected_total_payments_amount)
        self.assertEqual(payments_count, expected_total_payments_count)
        self.assertEqual(total_payoffs, expected_total_payments)


if __name__ == '__main__':
    unittest.main()
