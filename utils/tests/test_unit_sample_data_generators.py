import math
from decimal import Decimal

from django.test import TestCase

from utils.sample_data_generators import generate_decimal_with_decimal_places
from utils.sample_data_generators import generate_decimal_with_digits


class DecimalDataGenerators(TestCase):
    def test_digits_based_decimal_generator_should_return_decimal_with_declared_digits_number(self):
        result = generate_decimal_with_digits(digits=2)
        decimal_places = len(str(result).split(".")[1])
        digits = len(str(result).replace(".", ""))
        self.assertEqual(decimal_places, 1)
        self.assertEqual(digits, 2)

    def test_digits_based_decimal_generator_generator_should_return_result_based_on_provided_constant(self):
        result = generate_decimal_with_digits(digits=3, constant=math.pi)
        self.assertAlmostEqual(result, Decimal(math.pi) * 10, 1)

    def test_decimal_places_based_decimal_generator_should_return_decimal_with_declared_decimal_places(self):
        result = generate_decimal_with_decimal_places(decimal_places=3)
        decimal_places = len(str(result).split(".")[1])
        digits = len(str(result).replace(".", ""))
        self.assertEqual(decimal_places, 3)
        self.assertEqual(digits, 4)

    def test_decimal_places_based_decimal_generator_should_return_result_based_on_provided_constant(self):
        result = generate_decimal_with_decimal_places(decimal_places=3, constant=math.pi)
        self.assertAlmostEqual(result, Decimal(math.pi), 2)
