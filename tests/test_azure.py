from discovery.azure import fetch_azure_services
from tests.asserts import assertService


def test_fetch_azure_services():
    services = fetch_azure_services()
    assert services is not None
    assert isinstance(services, list)
    assert len(services) > 0
    for service in services:
        assertService(service, 'azure/platform', 'azure/category', 'azure/service')
