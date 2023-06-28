import pytest


def assertService(service, platformTag, categoryTagPrefix, serviceTagPrefix):
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
    assert platformTag in service['tags']
    assert any(tag.startswith(serviceTagPrefix) for tag in service['tags'])
    assert any(tag.startswith(categoryTagPrefix) for tag in service['tags'])
