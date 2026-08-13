import os
import tempfile
import unittest
from unittest.mock import patch

class TestSecurity(unittest.TestCase):
    def test_password_hash_and_verify(self):
        from security import hash_password, verify_password
        hashed = hash_password("secret123")
        self.assertNotEqual(hashed, "secret123")
        self.assertTrue(verify_password("secret123", hashed))
        self.assertFalse(verify_password("wrong", hashed))

class TestBilling(unittest.TestCase):
    def test_fee_calculation(self):
        from billing import calculate_fee
        minutes, amount = calculate_fee(
            "2026-01-01T10:00:00",
            "2026-01-01T11:30:00"
        )
        self.assertEqual(minutes, 90)
        self.assertEqual(amount, 10.0)

if __name__ == "__main__":
    unittest.main()
