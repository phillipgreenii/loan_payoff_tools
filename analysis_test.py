import unittest
import os.path
import tempfile
import shutil


import analysis
import max_payment_determiner
import payment_manager
from money import Money


class AnalysisTestCase(unittest.TestCase):
    def setUp(self):
        self.accounts = analysis.load_accounts(os.path.join('testdata','test-accounts.csv'))
        self.temp_dir = tempfile.mkdtemp('analysis-test')

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_analyze(self):
        mpd = max_payment_determiner.ConstantMaxPaymentDeterminer(2000, 50)
        pm = payment_manager.BiggestDebtPaymentManager()
        bpm = payment_manager.EvenSplitPaymentManager()

        (r_mpd, r_pm, r_bpm, months, initial_paid, total_paid, to_interest, monthly_payments) = analysis.analyze(mpd, pm, bpm, self.accounts, details_directory=self.temp_dir)

        self.assertEqual(r_mpd, mpd)
        self.assertEqual(r_pm, pm)
        self.assertEqual(r_bpm, bpm)
        self.assertEqual(months, 75)
        self.assertEqual(initial_paid, Money(133000.00))
        self.assertEqual(total_paid, Money(152349.04))
        self.assertEqual(to_interest, Money(19349.04))
        self.assertIsNotNone(monthly_payments)


if __name__ == '__main__':
    unittest.main()
