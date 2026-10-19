import unittest
from faq_engine import answer_question

class FAQTests(unittest.TestCase):
    def test_covered_schemes(self):
        result = answer_question("What schemes are covered by this assistant?")
        self.assertIn("HDFC Flexi Cap Fund", result)
        self.assertIn("Source:", result)
        self.assertIn("Last updated from sources:", result)

    def test_refuses_advice(self):
        result = answer_question("Should I buy HDFC Mid Cap Fund?")
        self.assertIn("can’t recommend", result)

    def test_pii_warning(self):
        result = answer_question("My PAN is ABCDE1234F")
        self.assertIn("Please do not enter personal information", result)

    def test_exit_load_answer(self):
        result = answer_question("What is the exit load for HDFC Nifty 50 Index Fund?")
        self.assertIn("0.25%", result)
        self.assertIn("Source:", result)

    def test_unknown_fund_falls_back(self):
        result = answer_question("What is the exit load for an unknown fund?")
        self.assertIn("couldn’t verify", result)

if __name__ == "__main__":
    unittest.main()
