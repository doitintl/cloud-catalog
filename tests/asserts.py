"""
This module contains common asserts for the tests.
"""


def assert_service(service, platform_tag, category_tag_prefix, service_tag_prefix):
    """
    Asserts that a service has the expected properties.

    Args:
        service: The service to assert.
        platform_tag: The expected platform tag.
        category_tag_prefix: The expected category tag prefix.
        service_tag_prefix: The expected service tag prefix.

    Returns:
        None
    """
    assert 'id' in service
    assert 'name' in service
    assert 'summary' in service
    assert 'url' in service
    assert 'categories' in service
    assert isinstance(service['categories'], list)
    assert len(service['categories']) > 0
    for category in service['categories']:
        assert 'id' in category
        assert 'name' in category
    assert 'tags' in service
    assert isinstance(service['tags'], list)
    assert len(service['tags']) > 0
    assert platform_tag in service['tags']
    assert any(tag.startswith(service_tag_prefix) for tag in service['tags'])
    assert any(tag.startswith(category_tag_prefix) for tag in service['tags'])
