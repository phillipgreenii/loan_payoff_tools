
import unittest
from datetime import date

from payment_manager import Account
from max_payment_determiner import ConstantMaxPaymentDeterminer
from max_payment_determiner import MinimumMaxPaymentDeterminer
from max_payment_determiner import AnnualRaiseMaxPaymentDeterminer
from max_payment_determiner import MinimumAnnualRaiseMaxPaymentDeterminer
from max_payment_determiner import AnnualRaiseAndBonusMaxPaymentDeterminer
from max_payment_determiner import MinimumAnnualRaiseAndBonusMaxPaymentDeterminer


class ConstantMaxPaymentDeterminerTestCase(unittest.TestCase):
    def setUp(self):
        self.payment_manager = ConstantMaxPaymentDeterminer(1000)

    def test_id(self):
        self.assertEqual(self.payment_manager.id, 'constant_1000_0')

    def test_determine_max_payment_for_should_return_constant_with_different_dates(self):
        payments_per_year = 12
        expected_max_payment = (1000, 0)
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 1, 1)), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 6, 1)), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2015, 6, 1)), expected_max_payment)

    def test_determine_max_payment_for_should_return_constant_with_different_payments_per_year(self):
        payment_date = date(2014, 1, 1)
        expected_max_payment = (1000, 0)
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
        expected_max_payment = (1000, 100)
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 1, 1)), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 6, 1)), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2015, 6, 1)), expected_max_payment)

    def test_determine_max_payment_for_should_return_constant_with_different_payments_per_year(self):
        payment_date = date(2014, 1, 1)
        expected_max_payment = (1000, 100)
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
        expected_max_payment = (500, 0)
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 1, 1)), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 6, 1)), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2015, 6, 1)), expected_max_payment)

    def test_determine_max_payment_for_should_return_constant_with_different_payments_per_year(self):
        payment_date = date(2014, 1, 1)
        expected_max_payment = (500, 0)
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
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 1, 1)), (1000.00, 0))
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 6, 1)), (1312.50, 0))
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2015, 6, 1)), (1625.00, 0))

    def test_determine_max_payment_for_should_return_correct_values_when_payments_per_year_when_no_raise(self):
        payment_date = date(2014, 1, 1)
        expected_max_payment = (1000, 0)
        self.assertEqual(self.payment_manager.determine_max_payment_for(1, payment_date), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(4, payment_date), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(12, payment_date), expected_max_payment)

    def test_determine_max_payment_for_should_return_correct_values_when_payments_per_year_when_raise(self):
        payment_date = date(2014, 10, 1)
        self.assertEqual(self.payment_manager.determine_max_payment_for(1, payment_date), (4750.00, 0))
        self.assertEqual(self.payment_manager.determine_max_payment_for(4, payment_date), (1937.50, 0))
        self.assertEqual(self.payment_manager.determine_max_payment_for(12, payment_date), (1312.50, 0))


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
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 1, 1)), (500.00, 0))
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 6, 1)), (812.50, 0))
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2015, 6, 1)), (1125.00, 0))

    def test_determine_max_payment_for_should_return_correct_values_when_payments_per_year_when_no_raise(self):
        payment_date = date(2014, 1, 1)
        expected_max_payment = (500, 0)
        self.assertEqual(self.payment_manager.determine_max_payment_for(1, payment_date), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(4, payment_date), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(12, payment_date), expected_max_payment)

    def test_determine_max_payment_for_should_return_correct_values_when_payments_per_year_when_raise(self):
        payment_date = date(2014, 10, 1)
        self.assertEqual(self.payment_manager.determine_max_payment_for(1, payment_date), (4250.00, 0))
        self.assertEqual(self.payment_manager.determine_max_payment_for(4, payment_date), (1437.50, 0))
        self.assertEqual(self.payment_manager.determine_max_payment_for(12, payment_date), (812.50, 0))


class AnnualRaiseAndBonusMaxPaymentDeterminerTestCaseTestCase(unittest.TestCase):
    def setUp(self):
        self.payment_manager = AnnualRaiseAndBonusMaxPaymentDeterminer(100000, 0.05, 0.10, date(2013, 5, 1), 1000)

    def test_id(self):
        self.assertEqual(self.payment_manager.id, 'annual_raise_and_bonus_100000_5_10_1000')

    def test_determine_max_payment_for_should_return_correct_values_when_different_dates(self):
        payments_per_year = 12
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 1, 1)), (1000.00, 0))
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 6, 1)), (1312.50, 0))
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2015, 6, 1)), (1625.00, 0))

    def test_determine_max_payment_for_should_return_correct_values_when_payments_per_year_when_no_raise(self):
        payment_date = date(2014, 1, 1)
        expected_max_payment = (1000, 0)
        self.assertEqual(self.payment_manager.determine_max_payment_for(1, payment_date), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(4, payment_date), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(12, payment_date), expected_max_payment)

    def test_determine_max_payment_for_should_return_correct_values_when_payments_per_year_when_raise(self):
        payment_date = date(2014, 10, 1)
        self.assertEqual(self.payment_manager.determine_max_payment_for(1, payment_date), (4750.00, 7500.00))
        self.assertEqual(self.payment_manager.determine_max_payment_for(4, payment_date), (1937.50, 0))
        self.assertEqual(self.payment_manager.determine_max_payment_for(12, payment_date), (1312.50, 0))


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
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 1, 1)), (500.00, 0))
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2014, 6, 1)), (812.50, 0))
        self.assertEqual(self.payment_manager.determine_max_payment_for(payments_per_year, date(2015, 6, 1)), (1125.00, 0))

    def test_determine_max_payment_for_should_return_correct_values_when_payments_per_year_when_no_raise(self):
        payment_date = date(2014, 1, 1)
        expected_max_payment = (500, 0)
        self.assertEqual(self.payment_manager.determine_max_payment_for(1, payment_date), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(4, payment_date), expected_max_payment)
        self.assertEqual(self.payment_manager.determine_max_payment_for(12, payment_date), expected_max_payment)

    def test_determine_max_payment_for_should_return_correct_values_when_payments_per_year_when_raise(self):
        payment_date = date(2014, 10, 1)
        self.assertEqual(self.payment_manager.determine_max_payment_for(1, payment_date), (4250.00, 7500.00))
        self.assertEqual(self.payment_manager.determine_max_payment_for(4, payment_date), (1437.50, 0))
        self.assertEqual(self.payment_manager.determine_max_payment_for(12, payment_date), (812.50, 0))

if __name__ == '__main__':
    unittest.main()
