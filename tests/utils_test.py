'''
loan_payoff_tools: Test module.

Meant for use with py.test.
Write each test as a function named test_<something>.
Read more here: http://pytest.org/

Copyright 2014, Phillip Green II
Licensed under MIT
'''

import unittest

import loan_payoff_tools.utils as utils


class UtilsTestCase(unittest.TestCase):

    def test_round_up_with_0_places(self):
        self.assertEqual(utils.round_up(100), 100)
        self.assertEqual(utils.round_up(4.5), 5)
        self.assertEqual(utils.round_up(3.2), 4)
        self.assertEqual(utils.round_up(0.02), 1)

    def test_round_up_with_2_places(self):
        self.assertEqual(utils.round_up(100, 2), 100)
        self.assertEqual(utils.round_up(4.5, 2), 4.5)
        self.assertEqual(utils.round_up(3.2, 2), 3.2)
        self.assertEqual(utils.round_up(0.02, 2), 0.02)
        self.assertEqual(utils.round_up(0.004, 2), 0.01)
        self.assertEqual(utils.round_up(0.045, 2), 0.05)
        self.assertEqual(utils.round_up(0.032, 2), 0.04)

    def test_round_up_with_neg_2_places(self):
        self.assertEqual(utils.round_up(100, -2), 100)
        self.assertEqual(utils.round_up(4.5, -2), 100)
        self.assertEqual(utils.round_up(3334, -2), 3400)
        self.assertEqual(utils.round_up(212, -2), 300)
        self.assertEqual(utils.round_up(3490, -2), 3500)

if __name__ == '__main__':
    unittest.main()
