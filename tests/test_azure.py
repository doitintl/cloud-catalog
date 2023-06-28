from discovery.azure import fetch_azure_services
from tests.asserts import assert_service


def test_fetch_azure_services():
    services = fetch_azure_services()
    assert services is not None
    assert isinstance(services, list)
    assert len(services) > 0
    for service in services:
        assert_service(service, 'azure/platform', 'azure/category', 'azure/service')
