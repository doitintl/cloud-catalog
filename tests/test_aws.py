import warnings
from bs4 import MarkupResemblesLocatorWarning
import discovery.aws as aws
from tests.asserts import assert_service


def test_clean_string_no_spaces():
    assert aws.clean_string('NoSpaces') == 'nospaces'


def test_clean_string_spaces_commas_ampersands():
    assert aws.clean_string('Spaces, Commas & Ampersands') == 'spaces-commas-and-ampersands'


def test_clean_summary_html_tags_and_plain_text():
    input_str = '<p>This is a test string with HTML tags and plain text.</p>\n'\
                'It has newlines and carriage returns.\r'
    expected_output = 'This is a test string with HTML tags and plain text.It has newlines and carriage returns.'
    assert aws.clean_summary(input_str) == expected_output


def test_fetch_aws_services():
    warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
    services = aws.fetch_aws_services("../custom-services/aws.json")
    assert services is not None
    assert isinstance(services, list)
    assert len(services) > 0
    for service in services:
        assert_service(service, 'aws/platform', 'aws/category', 'aws/service')
