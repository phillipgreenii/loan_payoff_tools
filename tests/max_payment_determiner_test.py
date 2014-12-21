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
from loan_payoff_tools.max_payment_determiner import ConstantMaxPaymentDeterminer
from loan_payoff_tools.max_payment_determiner import MinimumMaxPaymentDeterminer
from loan_payoff_tools.max_payment_determiner import AnnualRaiseMaxPaymentDeterminer
from loan_payoff_tools.max_payment_determiner import MinimumAnnualRaiseMaxPaymentDeterminer
from loan_payoff_tools.max_payment_determiner import AnnualRaiseAndBonusMaxPaymentDeterminer
from loan_payoff_tools.max_payment_determiner import MinimumAnnualRaiseAndBonusMaxPaymentDeterminer
from loan_payoff_tools.money import Money

class ConstantMaxPaymentDeterminerTestCase(unittest.TestCase):
    def setUp(self):
        self.payment_manager = ConstantMaxPaymentDeterminer(1000)

    def test_id(self):
        self.assertEqual(self.payment_manager.id, 'constant_1000_0')

    def test_determine_max_payment_for_should_return_constant_with_different_dates(self):
        payments_per_year = 12
        expected_max_payment = (Money(1000), Money(0))
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 1, 1)), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 6, 1)), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2015, 6, 1)), expected_max_payment)

    def test_determine_max_payment_for_should_return_constant_with_different_payments_per_year(self):
        payment_date = date(2014, 1, 1)
        expected_max_payment = (Money(1000), Money(0))
        self.assertEqual(self.payment_manager.determine_max_payment_for(1, payment_date), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(4, payment_date), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(12, payment_date), expected_max_payment)


class ConstantMaxPaymentDeterminerWithBonusTestCase(unittest.TestCase):
    def setUp(self):
        self.payment_manager = ConstantMaxPaymentDeterminer(1000, 100)

    def test_id(self):
        self.assertEqual(self.payment_manager.id, 'constant_1000_100')

    def test_determine_max_payment_for_should_return_constant_with_different_dates(self):
        payments_per_year = 12
        expected_max_payment = (Money(1000), Money(100))
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 1, 1)), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 6, 1)), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2015, 6, 1)), expected_max_payment)

    def test_determine_max_payment_for_should_return_constant_with_different_payments_per_year(self):
        payment_date = date(2014, 1, 1)
        expected_max_payment = (Money(1000), Money(100))
        self.assertEqual(self.payment_manager.determine_max_payment_for(1, payment_date), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(4, payment_date), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(12, payment_date), expected_max_payment)


class MinimumMaxPaymentDeterminerTestCase(unittest.TestCase):
    def setUp(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.02, 100.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 6000, 0.04, 300.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 7000, 0.03, 100.00, date(2014, 5, 1))
        self.payment_manager = MinimumMaxPaymentDeterminer([account0, account1, account2])

    def test_id(self):
        self.assertEqual(self.payment_manager.id, 'constant_500_0')

    def test_determine_max_payment_for_should_return_constant_with_different_dates(self):
        payments_per_year = 12
        expected_max_payment = (Money(500), Money(0))
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 1, 1)), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 6, 1)), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2015, 6, 1)), expected_max_payment)

    def test_determine_max_payment_for_should_return_constant_with_different_payments_per_year(self):
        payment_date = date(2014, 1, 1)
        expected_max_payment = (Money(500), Money(0))
        self.assertEqual(self.payment_manager.determine_max_payment_for(1, payment_date), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(4, payment_date), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(12, payment_date), expected_max_payment)


class AnnualRaiseMaxPaymentDeterminerTestCase(unittest.TestCase):
    def setUp(self):
        self.payment_manager = AnnualRaiseMaxPaymentDeterminer(100000, 0.05, date(2013, 5, 1), 1000)

    def test_id(self):
        self.assertEqual(self.payment_manager.id, 'annual_raise_100000_5_1000')

    def test_determine_max_payment_for_should_return_correct_values_when_different_dates(self):
        payments_per_year = 12
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 1, 1)), (Money(1000.00), Money(0)))
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 6, 1)), (Money(1312.50), Money(0)))
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2015, 6, 1)), (Money(1625.00), Money(0)))

    def test_determine_max_payment_for_should_return_correct_values_when_payments_per_year_when_no_raise(self):
        payment_date = date(2014, 1, 1)
        expected_max_payment = (Money(1000), Money(0))
        self.assertEqual(self.payment_manager.determine_max_payment_for(1, payment_date), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(4, payment_date), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(12, payment_date), expected_max_payment)

    def test_determine_max_payment_for_should_return_correct_values_when_payments_per_year_when_raise(self):
        payment_date = date(2014, 10, 1)
        self.assertEqual(self.payment_manager.determine_max_payment_for(1, payment_date), (Money(4750.00), Money(0)))
        self.assertEqual(self.payment_manager.determine_max_payment_for(4, payment_date), (Money(1937.50), Money(0)))
        self.assertEqual(self.payment_manager.determine_max_payment_for(12, payment_date), (Money(1312.50), Money(0)))


class MinimumAnnualRaiseMaxPaymentDeterminerTestCase(unittest.TestCase):
    def setUp(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.02, 100.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 6000, 0.04, 300.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 7000, 0.03, 100.00, date(2014, 5, 1))
        self.payment_manager = MinimumAnnualRaiseMaxPaymentDeterminer(100000, 0.05, date(2013, 5, 1), [account0, account1, account2])

    def test_id(self):
        self.assertEqual(self.payment_manager.id, 'annual_raise_100000_5_500')

    def test_determine_max_payment_for_should_return_correct_values_when_different_dates(self):
        payments_per_year = 12
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 1, 1)), (Money(500.00), Money(0)))
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 6, 1)), (Money(812.50), Money(0)))
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2015, 6, 1)), (Money(1125.00), Money(0)))

    def test_determine_max_payment_for_should_return_correct_values_when_payments_per_year_when_no_raise(self):
        payment_date = date(2014, 1, 1)
        expected_max_payment = (Money(500), Money(0))
        self.assertEqual(self.payment_manager.determine_max_payment_for(1, payment_date), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(4, payment_date), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(12, payment_date), expected_max_payment)

    def test_determine_max_payment_for_should_return_correct_values_when_payments_per_year_when_raise(self):
        payment_date = date(2014, 10, 1)
        self.assertEqual(self.payment_manager.determine_max_payment_for(1, payment_date), (Money(4250.00), Money(0)))
        self.assertEqual(self.payment_manager.determine_max_payment_for(4, payment_date), (Money(1437.50), Money(0)))
        self.assertEqual(self.payment_manager.determine_max_payment_for(12, payment_date), (Money(812.50), Money(0)))


class AnnualRaiseAndBonusMaxPaymentDeterminerTestCaseTestCase(unittest.TestCase):
    def setUp(self):
        self.payment_manager = AnnualRaiseAndBonusMaxPaymentDeterminer(100000, 0.05, 0.10, date(2013, 5, 1), 1000)

    def test_id(self):
        self.assertEqual(self.payment_manager.id, 'annual_raise_and_bonus_100000_5_10_1000')

    def test_determine_max_payment_for_should_return_correct_values_when_different_dates(self):
        payments_per_year = 12
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 1, 1)), (Money(1000.00), Money(0)))
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 6, 1)), (Money(1312.50), Money(0)))
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2015, 6, 1)), (Money(1625.00), Money(0)))

    def test_determine_max_payment_for_should_return_correct_values_when_payments_per_year_when_no_raise(self):
        payment_date = date(2014, 1, 1)
        expected_max_payment = (Money(1000), Money(0))
        self.assertEqual(self.payment_manager.determine_max_payment_for(1, payment_date), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(4, payment_date), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(12, payment_date), expected_max_payment)

    def test_determine_max_payment_for_should_return_correct_values_when_payments_per_year_when_raise(self):
        payment_date = date(2014, 10, 1)
        self.assertEqual(self.payment_manager.determine_max_payment_for(1, payment_date), (Money(4750.00), Money(7875.00)))
        self.assertEqual(self.payment_manager.determine_max_payment_for(4, payment_date), (Money(1937.50), Money(0)))
        self.assertEqual(self.payment_manager.determine_max_payment_for(12, payment_date), (Money(1312.50), Money(0)))


class MinimumAnnualRaiseAndBonusMaxPaymentDeterminerTestCase(unittest.TestCase):
    def setUp(self):
        account0 = Account("Bank0", "00", "Joe", 5000, 0.02, 100.00, date(2014, 5, 1))
        account1 = Account("Bank0", "01", "Joe", 6000, 0.04, 300.00, date(2014, 5, 1))
        account2 = Account("Bank1", "00", "Joe", 7000, 0.03, 100.00, date(2014, 5, 1))
        self.payment_manager = MinimumAnnualRaiseAndBonusMaxPaymentDeterminer(100000, 0.05, 0.10, date(2013, 5, 1), [account0, account1, account2])

    def test_id(self):
        self.assertEqual(self.payment_manager.id, 'annual_raise_and_bonus_100000_5_10_500')

    def test_determine_max_payment_for_should_return_correct_values_when_different_dates(self):
        payments_per_year = 12
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 1, 1)), (Money(500.00), Money(0)))
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 6, 1)), (Money(812.50), Money(0)))
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2015, 6, 1)), (Money(1125.00), Money(0)))

    def test_determine_max_payment_for_should_return_correct_values_when_payments_per_year_when_no_raise(self):
        payment_date = date(2014, 1, 1)
        expected_max_payment = (Money(500), Money(0))
        self.assertEqual(self.payment_manager.determine_max_payment_for(1, payment_date), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(4, payment_date), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(12, payment_date), expected_max_payment)

    def test_determine_max_payment_for_should_return_correct_values_when_payments_per_year_when_raise(self):
        payment_date = date(2014, 10, 1)
        self.assertEqual(self.payment_manager.determine_max_payment_for(1, payment_date), (Money(4250.00), Money(7875.00)))
        self.assertEqual(self.payment_manager.determine_max_payment_for(4, payment_date), (Money(1437.50), Money(0)))
        self.assertEqual(self.payment_manager.determine_max_payment_for(12, payment_date), (Money(812.50), Money(0)))

if __name__ == '__main__':
    unittest.main()
