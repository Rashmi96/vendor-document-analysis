import unittest
from app.services.text_extractor import extract_pdf, extract_word, extract_image

class TestExtractors(unittest.TestCase):

    def test_extract_pdf(self):
        text = extract_pdf('tests/test_file.pdf')
        self.assertIn('Expected text', text)

    def test_extract_word(self):
        text = extract_word('tests/test_file.docx')
        self.assertIn('Expected text', text)

    def test_extract_image(self):
        text = extract_image('tests/test_image.png')
        self.assertIn('Expected text', text)

if __name__ == '__main__':
    unittest.main()
