import unittest
from money import Money
import decimal


class MoneyTestCase(unittest.TestCase):

    def test_constructor_with_money(self):
        other_money = Money(100.00)
        self.assertEqual(Money(other_money)._cents, 10000)

    def test_constructor_with_string(self):
        self.assertEqual(Money("100.00")._cents, 10000)

    def test_constructor_with_decimal(self):
        self.assertEqual(Money(decimal.Decimal(100.00))._cents, 10000)

    def test_constructor_with_int(self):
        self.assertEqual(Money(int(100))._cents, 10000)

    def test_constructor_with_long(self):
        self.assertEqual(Money(long(100))._cents, 10000)

    def test_constructor_with_float(self):
        self.assertEqual(Money(float(100.00))._cents, 10000)
        self.assertEqual(Money(float(32.34))._cents, 3234)

    def test_str(self):
        self.assertEqual(str(Money(int(100))), "$100.00")

    def test_plus(self):
        result = Money(25) + Money(75)
        self.assertEqual(result, Money(100))

    def test_plus_with_decimals(self):
        result = Money(25.33) + Money(75.67)
        self.assertEqual(result, Money(101))

    def test_iplus(self):
        result = Money(25)
        result += Money(75)
        self.assertEqual(result, Money(100))

    def test_iplus_with_decimals(self):
        result = Money(25.33)
        result += Money(75.67)
        self.assertEqual(result, Money(101))

    def test_negative(self):
        result = -Money(25)
        self.assertEqual(result, Money(-25))

    def test_minus(self):
        result = Money(25) - Money(75)
        self.assertEqual(result, Money(-50))

    def test_minus_with_decimals(self):
        result = Money(25.33) - Money(75.67)
        self.assertEqual(result, Money(-50.34))

    def test_iminus(self):
        result = Money(25)
        result -= Money(75)
        self.assertEqual(result, Money(-50))

    def test_iminus_with_decimals(self):
        result = Money(25.33)
        result -= Money(75.67)
        self.assertEqual(result, Money(-50.34))

    def test_multiply_with_int(self):
        result1 = Money(32.34) * 15
        result2 = 15 * Money(32.34)
        expected_result = Money(485.10)

        self.assertEqual(expected_result, result1)
        self.assertEqual(expected_result, result2)

    def test_multiply_with_float(self):
        result1 = Money(32.34) * 4.4
        result2 = 4.4 * Money(32.34)
        expected_result = Money(142.30)

        self.assertEqual(expected_result, result1)
        self.assertEqual(expected_result, result2)

    def test_multiply_with_float_other(self):
        result1 = Money(100000.00) * 0.0375
        result2 = 0.0375 * Money(100000.00)
        expected_result = Money(3750.0)

        self.assertEqual(expected_result, result1)
        self.assertEqual(expected_result, result2)

    def test_divide_with_int(self):
        result = Money(32.34) / 15
        expected_result = Money(2.16)

        self.assertEqual(expected_result, result)

    def test_divide_with_float(self):
        result = Money(32.34) / 4.4
        expected_result = Money(7.35)

        self.assertEqual(expected_result, result)

    def test_compare(self):
        money1 = Money(2.00)
        money2 = Money(-2.00)

        self.assertLess(money2, money1)
        self.assertGreater(money1, money2)

    def test_equal_with_self(self):
        money = Money(3)

        self.assertTrue(money == money)
        self.assertFalse(money != money)

    def test_equal_with_duplicate(self):
        money = Money(3)
        money_dup = Money(3)

        self.assertTrue(money == money_dup)
        self.assertFalse(money != money_dup)

    def test_not_equal_with_different(self):
        money1 = Money(3)
        money2 = Money(3.40)

        self.assertTrue(money1 != money2)
        self.assertFalse(money1 == money2)

    def test_hash_with_self(self):
        money = Money(3)
        self.assertEqual(hash(money), hash(money))

    def test_hash_with_duplicate(self):
        money = Money(3)
        money_dup = Money(3)
        self.assertEqual(hash(money), hash(money_dup))

    def test_float(self):
        money = Money("3.43")
        result = float(money)
        self.assertEqual(result, float(3.43))

    def test_int(self):
        money = Money("3.43")
        result = int(money)
        self.assertEqual(result, int(3))

    def test_long(self):
        money = Money("3.43")
        result = long(money)
        self.assertEqual(result, long(3))

    def test_not_empty_when_not_empty(self):
        self.assertTrue(Money(1))

    def test_not_empty_when_empty(self):
        self.assertFalse(Money(0))

if __name__ == '__main__':
    unittest.main()
