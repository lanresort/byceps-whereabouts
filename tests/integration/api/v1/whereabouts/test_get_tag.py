"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.whereabouts import whereabouts_service


CONTENT_TYPE_JSON = 'application/json'


def test_with_unknown_tag(api_client, api_client_authz_header):
    unknown_tag = '12345'

    response = send_request(api_client, api_client_authz_header, unknown_tag)

    assert response.status_code == 404
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON
    assert response.json == {}


def test_with_known_tag(api_client, api_client_authz_header, tag):
    response = send_request(api_client, api_client_authz_header, tag.tag)

    assert response.status_code == 200
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON

    response_data = response.json
    assert response_data['tag'] == tag.tag
    assert response_data['user']['id'] == str(tag.user.id)
    assert response_data['user']['screen_name'] == tag.user.screen_name
    assert response_data['user']['avatar_url'] == tag.user.avatar_url
    assert response_data['sound_filename'] == tag.sound_filename


def test_with_known_tag_unauthorized(api_client, tag):
    url = f'/api/v1/whereabouts/tags/{tag.tag}'
    response = api_client.get(url)

    assert response.status_code == 401
    assert response.json is None


@pytest.fixture(scope='module')
def tag(user, admin_user):
    tag = '0004283951'
    sound_filename = 'moin.ogg'

    return whereabouts_service.create_tag(
        tag, user, admin_user, sound_filename=sound_filename
    )


def send_request(api_client, api_client_authz_header, tag):
    url = f'/api/v1/whereabouts/tags/{tag}'
    return api_client.get(url, headers=[api_client_authz_header])
