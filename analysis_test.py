import unittest
import os.path
import tempfile
import shutil


import analysis
import max_payment_determiner
import payment_manager


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

        (mpd_id, pm_id, bpm_id, months, total_paid, to_interest) = analysis.analyze(mpd, pm, bpm, self.accounts, details_directory=self.temp_dir)

        self.assertEqual(mpd_id, mpd.id)
        self.assertEqual(pm_id, pm.id)
        self.assertEqual(bpm_id, bpm.id)
        self.assertEqual(months, 54)
        self.assertEqual(total_paid, 146069.99671309063)
        self.assertEqual(to_interest, 13069.99671309063)


if __name__ == '__main__':
    unittest.main()
