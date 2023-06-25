import unittest
from discovery.azure import fetch_azure_services
from tests.case import DiscoveryTestCase


class TestFetchAzureServices(DiscoveryTestCase):

    def test_fetch_azure_services(self):
        services = fetch_azure_services()
        self.assertIsNotNone(services)
        self.assertIsInstance(services, list)
        self.assertGreater(len(services), 0)
        for service in services:
            self.assertService(service, 'azure/platform', 'azure/category', 'azure/service')


if __name__ == '__main__':
    unittest.main()
