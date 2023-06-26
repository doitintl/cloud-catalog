import unittest
from discovery.gsuite import fetch_gsuite_services
from tests.case import DiscoveryTestCase


class TestFetchGSuiteServices(DiscoveryTestCase):

    def test_fetch_gsuite_services(self):
        services = fetch_gsuite_services("../custom-services/gsuite.json")
        self.assertIsNotNone(services)
        self.assertIsInstance(services, list)
        self.assertGreater(len(services), 0)
        for service in services:
            self.assertService(service, 'gsuite/platform', 'gsuite/category', 'gsuite/service')


if __name__ == '__main__':
    unittest.main()