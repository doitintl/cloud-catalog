import unittest


class DiscoveryTestCase(unittest.TestCase):

    def assertService(self, service, platformTag, categoryTagPrefix, serviceTagPrefix):
        self.assertIn('id', service)
        self.assertIn('name', service)
        self.assertIn('summary', service)
        self.assertIn('url', service)
        self.assertIn('categories', service)
        self.assertIsInstance(service['categories'], list)
        self.assertGreater(len(service['categories']), 0)
        for category in service['categories']:
            self.assertIn('id', category)
            self.assertIn('name', category)
        self.assertIn('tags', service)
        self.assertIsInstance(service['tags'], list)
        self.assertGreater(len(service['tags']), 0)
        self.assertIn(platformTag, service['tags'])
        self.assertTrue(any(tag.startswith(serviceTagPrefix) for tag in service['tags']))
        self.assertTrue(any(tag.startswith(categoryTagPrefix) for tag in service['tags']))
