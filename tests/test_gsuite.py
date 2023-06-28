from discovery.gsuite import fetch_gsuite_services
from tests.asserts import assertService


def test_fetch_gsuite_services():
    services = fetch_gsuite_services("../custom-services/gsuite.json")
    assert services is not None
    assert isinstance(services, list)
    assert len(services) > 0
    for service in services:
        assertService(service, 'gsuite/platform', 'gsuite/category', 'gsuite/service')
