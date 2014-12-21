'''
loan_payoff_tools: Test module.

Meant for use with py.test.
Write each test as a function named test_<something>.
Read more here: http://pytest.org/

Copyright 2014, Phillip Green II
Licensed under MIT
'''

import unittest
import os.path
import tempfile
import shutil
import datetime

import loan_payoff_tools.analysis as analysis
import loan_payoff_tools.max_payment_determiner as max_payment_determiner
import loan_payoff_tools.payment_manager as payment_manager
from loan_payoff_tools.money import Money
from loan_payoff_tools.payment_manager import Account

class AnalysisTestCase(unittest.TestCase):
    def setUp(self):
        self.accounts = analysis.load_accounts(os.path.join('tests', 'data','test-accounts.csv'))
        self.temp_dir = tempfile.mkdtemp('analysis-test')

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_analyze(self):
        mpd = max_payment_determiner.ConstantMaxPaymentDeterminer(2000, 50)
        pm = payment_manager.BiggestDebtPaymentManager()
        bpm = payment_manager.EvenSplitPaymentManager()

        (r_mpd, r_pm, r_bpm, months, initial_paid, total_paid, to_interest, monthly_payments) = analysis.analyze(mpd, pm, bpm, self.accounts)
        self.assertEqual(r_mpd, mpd)
        self.assertEqual(r_pm, pm)
        self.assertEqual(r_bpm, bpm)
        self.assertEqual(months, 75)
        self.assertEqual(initial_paid, Money(133000.00))
        self.assertEqual(total_paid, Money(152349.04))
        self.assertEqual(to_interest, Money(19349.04))
        self.assertIsNotNone(monthly_payments)

    def test_dump_monthly_payments_to_csv(self):
        account0 = Account("Bank1", "00", "Person2", 5000.00, 0.05, 50.00, datetime.date(2014, 10, 7))
        account1 = Account("Bank1", "01", "Person2", 3000.00, 0.04, 40.00, datetime.date(2014, 10, 7))
        account2 = Account("Bank1", "02", "Person2", 7000.00, 0.03, 100.00, datetime.date(2014, 10, 7))

        monthly_payments = [
            (datetime.date(2014, 10, 6), {account2: (Money(1926.67), Money(5090.83)), account0: (Money(66.67), Money(4954.16)), account1: (Money(56.67), Money(2953.33))}),
            (datetime.date(2014, 11, 6), {account2: (Money(1926.67), Money(3176.89)), account0: (Money(66.67), Money(4908.13)), account1: (Money(56.67), Money(2906.50))}),
            (datetime.date(2014, 12, 6), {account2: (Money(116.67), Money(3068.16)), account0: (Money(1876.67), Money(3051.91)), account1: (Money(56.67), Money(2859.52))}),
            (datetime.date(2015, 1, 6), {account2: (Money(1926.67), Money(1149.16)), account0: (Money(66.67), Money(2997.96)), account1: (Money(56.67), Money(2812.38))}),
            (datetime.date(2015, 2, 6), {account2: (Money(116.67), Money(1035.36)), account0: (Money(1876.67), Money(1133.78)), account1: (Money(56.67), Money(2765.08))}),
            (datetime.date(2015, 3, 6), {account2: (Money(116.67), Money(921.28)), account0: (Money(66.67), Money(1071.83)), account1: (Money(1866.67), Money(907.63))}),
            (datetime.date(2015, 4, 6), {account2: (Money(908.70), Money(14.88)), account0: (Money(1076.30), Money(0.00)), account1: (Money(65.00), Money(845.66))}),
            (datetime.date(2015, 5, 6), {account2: (Money(14.92), Money(0.00)), account1: (Money(848.48), Money(0.00))})
            ]

        output_file = os.path.join(self.temp_dir, 'test.csv')
        analysis.dump_monthly_payments_to_csv(output_file, monthly_payments)
        self.assertTrue(os.path.isfile(output_file))
        self.assertEqual(open(output_file).readlines(), open(os.path.join('tests', 'data', 'expected-test-results-dump.csv')).readlines())

    def test_dump_monthly_payments_to_png(self):
        account0 = Account("Bank1", "00", "Person2", 5000.00, 0.05, 50.00, datetime.date(2014, 10, 7))
        account1 = Account("Bank1", "01", "Person2", 3000.00, 0.04, 40.00, datetime.date(2014, 10, 7))
        account2 = Account("Bank1", "02", "Person2", 7000.00, 0.03, 100.00, datetime.date(2014, 10, 7))

        monthly_payments = [
            (datetime.date(2014, 10, 6), {account2: (Money(1926.67), Money(5090.83)), account0: (Money(66.67), Money(4954.16)), account1: (Money(56.67), Money(2953.33))}),
            (datetime.date(2014, 11, 6), {account2: (Money(1926.67), Money(3176.89)), account0: (Money(66.67), Money(4908.13)), account1: (Money(56.67), Money(2906.50))}),
            (datetime.date(2014, 12, 6), {account2: (Money(116.67), Money(3068.16)), account0: (Money(1876.67), Money(3051.91)), account1: (Money(56.67), Money(2859.52))}),
            (datetime.date(2015, 1, 6), {account2: (Money(1926.67), Money(1149.16)), account0: (Money(66.67), Money(2997.96)), account1: (Money(56.67), Money(2812.38))}),
            (datetime.date(2015, 2, 6), {account2: (Money(116.67), Money(1035.36)), account0: (Money(1876.67), Money(1133.78)), account1: (Money(56.67), Money(2765.08))}),
            (datetime.date(2015, 3, 6), {account2: (Money(116.67), Money(921.28)), account0: (Money(66.67), Money(1071.83)), account1: (Money(1866.67), Money(907.63))}),
            (datetime.date(2015, 4, 6), {account2: (Money(908.70), Money(14.88)), account0: (Money(1076.30), Money(0.00)), account1: (Money(65.00), Money(845.66))}),
            (datetime.date(2015, 5, 6), {account2: (Money(14.92), Money(0.00)), account1: (Money(848.48), Money(0.00))})
            ]

        output_file = os.path.join(self.temp_dir, 'test.png')
        analysis.dump_monthly_payments_to_png(output_file, monthly_payments)
        self.assertTrue(os.path.isfile(output_file))

if __name__ == '__main__':
    unittest.main()
