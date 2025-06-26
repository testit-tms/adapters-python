import os
import unittest
from testit_python_commons.utils.html_escape_utils import HtmlEscapeUtils


class SampleData:
    def __init__(self, name="Test Name", description="<script>alert('xss')</script>"):
        self.name = name
        self.description = description
        self.tags = ["<tag>", "normal_tag"]


class TestHtmlEscapeUtils(unittest.TestCase):

    def test_escape_html_tags_basic(self):
        """Test basic HTML tag escaping"""
        text = "Hello <script>alert('test')</script> world"
        result = HtmlEscapeUtils.escape_html_tags(text)
        expected = "Hello \\<script\\>alert('test')\\</script\\> world"
        self.assertEqual(result, expected)

    def test_escape_html_tags_no_html_content(self):
        """Test that strings without HTML tags are returned unchanged"""
        text = "Just plain text without any tags"
        result = HtmlEscapeUtils.escape_html_tags(text)
        self.assertEqual(result, text)  # Should be identical object
        
        text_with_empty_brackets = "Text with & symbols and other <> but not HTML tags"
        result = HtmlEscapeUtils.escape_html_tags(text_with_empty_brackets)
        # This should remain unchanged because <> is not a valid HTML tag
        self.assertEqual(result, text_with_empty_brackets)


    def test_escape_html_tags_none(self):
        """Test handling of None input"""
        result = HtmlEscapeUtils.escape_html_tags(None)
        self.assertIsNone(result)

    def test_escape_html_tags_no_double_escaping(self):
        """Test that already escaped characters are not double-escaped"""
        text = "Already \\<escaped\\> and <not_escaped>"
        result = HtmlEscapeUtils.escape_html_tags(text)
        expected = "Already \\<escaped\\> and \\<not_escaped\\>"
        self.assertEqual(result, expected)

    def test_escape_html_tags_various_tags(self):
        """Test escaping of various HTML tag types"""
        test_cases = [
            ("<div>content</div>", "\\<div\\>content\\</div\\>"),
            ("<img src='test.jpg'/>", "\\<img src='test.jpg'/\\>"),
            ("<br>", "\\<br\\>"),
            ("<span class='test'>text</span>", "\\<span class='test'\\>text\\</span\\>"),
            ("No tags here", "No tags here"),  # Should remain unchanged
            ("<>", "<>"),  # Empty angle brackets - should remain unchanged
            ("< >", "< >"),  # Spaced angle brackets - should remain unchanged
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = HtmlEscapeUtils.escape_html_tags(input_text)
                self.assertEqual(result, expected)

    def test_escape_html_in_object(self):
        """Test HTML escaping in object attributes"""
        test_obj = SampleData()
        result = HtmlEscapeUtils.escape_html_in_object(test_obj)
        
        self.assertEqual(result.name, "Test Name")  # No escaping needed
        self.assertEqual(result.description, "\\<script\\>alert('xss')\\</script\\>")  # Escaped
        self.assertEqual(result.tags[0], "\\<tag\\>")  # Escaped
        self.assertEqual(result.tags[1], "normal_tag")  # No escaping needed

    def test_escape_html_in_object_list(self):
        """Test HTML escaping in list of objects"""
        test_list = [
            SampleData("First", "<div>content</div>"),
            SampleData("Second", "<span>more</span>")
        ]
        result = HtmlEscapeUtils.escape_html_in_object_list(test_list)
        
        self.assertEqual(result[0].description, "\\<div\\>content\\</div\\>")
        self.assertEqual(result[1].description, "\\<span\\>more\\</span\\>")

    def test_escape_disabled_by_env_var(self):
        """Test that escaping can be disabled via environment variable"""
        os.environ[HtmlEscapeUtils.NO_ESCAPE_HTML_ENV_VAR] = "true"
        
        try:
            text = "Hello <script>alert('test')</script> world"
            result = HtmlEscapeUtils.escape_html_tags(text)
            self.assertEqual(result, text)  # Should be unchanged
            
            test_obj = SampleData()
            result = HtmlEscapeUtils.escape_html_in_object(test_obj)
            self.assertEqual(result.description, "<script>alert('xss')</script>")  # Should be unchanged
        finally:
            # Clean up environment variable
            del os.environ[HtmlEscapeUtils.NO_ESCAPE_HTML_ENV_VAR]

    def test_escape_html_in_dictionary(self):
        """Test HTML escaping in dictionary objects"""
        test_dict = {
            "name": "Test",
            "description": "<script>alert('xss')</script>",
            "tags": ["<tag>", "normal_tag"]
        }
        result = HtmlEscapeUtils.escape_html_in_object(test_dict)
        
        self.assertEqual(result["name"], "Test")
        self.assertEqual(result["description"], "\\<script\\>alert('xss')\\</script\\>")
        self.assertEqual(result["tags"][0], "\\<tag\\>")
        self.assertEqual(result["tags"][1], "normal_tag")


if __name__ == '__main__':
    unittest.main() 