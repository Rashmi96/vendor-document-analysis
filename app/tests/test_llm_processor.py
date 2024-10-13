import unittest
from app.services.llm_processor import extract_fields_with_llm

class TestLLMProcessor(unittest.TestCase):

    def test_extract_fields(self):
        text = "Sample text containing a Name: John Doe, Email: john@example.com, Phone: 123-456-7890."
        fields = extract_fields_with_llm(text)
        self.assertIn('Name:', fields)
        self.assertIn('Email:', fields)

if __name__ == '__main__':
    unittest.main()
