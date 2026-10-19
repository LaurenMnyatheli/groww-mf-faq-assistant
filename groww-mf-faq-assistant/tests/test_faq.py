import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app

class FAQTests(unittest.TestCase):
    def test_elss_lock_in_retrieves_official_fact(self):
        result = app.format_answer("What is the lock-in period for HDFC ELSS Tax Saver Fund?")
        self.assertIn("three years", result)
        self.assertIn("Source: https://www.hdfcfund.com/", result)

    def test_advice_is_refused(self):
        result = app.format_answer("Should I buy HDFC Mid Cap Fund?")
        self.assertIn("can’t recommend", result)
        self.assertIn("investor.sebi.gov.in", result)

    def test_unknown_fact_does_not_guess(self):
        result = app.format_answer("What will this fund return next year?")
        self.assertIn("couldn’t verify", result)

    def test_pii_warning(self):
        result = app.format_answer("My PAN is ABCDE1234F, can you check my account?")
        self.assertIn("Please do not share personal information", result)

if __name__ == "__main__":
    unittest.main()
