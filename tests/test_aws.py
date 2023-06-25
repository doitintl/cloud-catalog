import unittest
from discovery.aws import fetch_aws_services
from tests.case import DiscoveryTestCase


class TestFetchAWSServices(DiscoveryTestCase):

    def test_fetch_aws_services(self):
        services = fetch_aws_services("../custom-services/aws.json")
        self.assertIsNotNone(services)
        self.assertIsInstance(services, list)
        self.assertGreater(len(services), 0)
        for service in services:
            self.assertService(service, 'aws/platform', 'aws/category', 'aws/service')


if __name__ == '__main__':
    unittest.main()
