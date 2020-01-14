# YOUR BACKEND TESTS HERE
import model
import unittest


class ModelTestCase(unittest.TestCase):
    def test_check_answer(self):
        self.assertEqual(model.check_answer(r'DB\level 1\-\math_7 10 - 10 = 0 .jpg', 1), False)
        self.assertEqual(model.check_answer(r'DB\level 1\-\math_7 10 - 10 = 0 .jpg', 0), True)


if __name__ == '__main__':
    unittest.main()
