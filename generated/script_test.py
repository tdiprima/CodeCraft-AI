# Here are the Python unit tests for the provided code:
import unittest
from script import validate_password  # assuming script.py is the file name where the function is defined


class TestPasswordValidation(unittest.TestCase):
    def test_basic_functionality(self):
        # Test valid password
        self.assertEqual(validate_password("Password1$"), "Password is valid.")
        # Test password with missing uppercase letter
        self.assertEqual(validate_password("password1$"), "Password should contain at least one uppercase letter.")
        # Test password with missing lowercase letter
        self.assertEqual(validate_password("PASSWORD1$"), "Password should contain at least one lowercase letter.")
        # Test password with missing number
        self.assertEqual(validate_password("Password$"), "Password should contain at least one number.")
        # Test password with missing special character
        self.assertEqual(validate_password("Password1"), "Password should contain at least one special character (_@$).")

    def test_edge_cases(self):
        # Test password with minimum length
        self.assertEqual(validate_password("Pass1$"), "Password should be at least 8 characters long.")
        # Test empty password
        self.assertEqual(validate_password(""), "Password should be at least 8 characters long.")
        # Test password with spaces
        self.assertEqual(validate_password("Password 1$"), "Password is valid.")

    def test_error_handling(self):
        # Test non-string password
        with self.assertRaises(TypeError):
            validate_password(12345678)
        # Test None as password
        with self.assertRaises(TypeError):
            validate_password(None)


if __name__ == "__main__":
    unittest.main()
