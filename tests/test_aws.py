import unittest
import discovery.aws as aws
from tests.case import DiscoveryTestCase


class TestFetchAWSServices(DiscoveryTestCase):

    def test_clean_string_no_spaces(self):
        self.assertEqual(aws.clean_string('NoSpaces'), 'nospaces')

    def test_clean_string_spaces_commas_ampersands(self):
        self.assertEqual(aws.clean_string('Spaces, Commas & Ampersands'), 'spaces-commas-and-ampersands')

    def test_clean_summary_html_tags_and_plain_text(self):
        input_str = '<p>This is a test string with HTML tags and plain text.</p>\n'\
                    'It has newlines and carriage returns.\r'
        expected_output = 'This is a test string with HTML tags and plain text.It has newlines and carriage returns.'
        self.assertEqual(aws.clean_summary(input_str), expected_output)

    def test_fetch_aws_services(self):
        services = aws.fetch_aws_services("../custom-services/aws.json")
        self.assertIsNotNone(services)
        self.assertIsInstance(services, list)
        self.assertGreater(len(services), 0)
        for service in services:
            self.assertService(service, 'aws/platform', 'aws/category', 'aws/service')


if __name__ == '__main__':
    unittest.main()
