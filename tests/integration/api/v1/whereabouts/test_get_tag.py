"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.authn.identity_tag import authn_identity_tag_service
from byceps.services.authn.identity_tag.models import UserIdentityTag
from byceps.services.user.models.user import User
from byceps.services.whereabouts import whereabouts_service
from byceps.services.whereabouts.models import WhereaboutsUserSound


CONTENT_TYPE_JSON = 'application/json'


def test_with_unknown_identifier(api_client, api_client_authz_header):
    unknown_identifier = '12345'

    response = send_request(
        api_client, api_client_authz_header, unknown_identifier
    )

    assert response.status_code == 404
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON
    assert response.json == {}


def test_with_known_identifier(
    api_client,
    api_client_authz_header,
    identity_tag: UserIdentityTag,
    user_sound: WhereaboutsUserSound,
):
    response = send_request(
        api_client, api_client_authz_header, identity_tag.identifier
    )

    assert response.status_code == 200
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON

    response_data = response.json
    assert response_data['identifier'] == identity_tag.identifier
    assert response_data['user']['id'] == str(identity_tag.user.id)
    assert response_data['user']['screen_name'] == identity_tag.user.screen_name
    assert response_data['user']['avatar_url'] == identity_tag.user.avatar_url
    assert response_data['sound_filename'] == user_sound.filename


def test_with_known_identifier_unauthorized(
    api_client, identity_tag: UserIdentityTag, user_sound: WhereaboutsUserSound
):
    url = f'/api/v1/whereabouts/tags/{identity_tag.identifier}'
    response = api_client.get(url)

    assert response.status_code == 401
    assert response.json is None


@pytest.fixture(scope='module')
def identity_tag(user: User, admin_user: User) -> UserIdentityTag:
    identifier = '0004283951'
    return authn_identity_tag_service.create_tag(admin_user, identifier, user)


@pytest.fixture(scope='module')
def user_sound(user: User) -> WhereaboutsUserSound:
    return whereabouts_service.create_user_sound(user, 'moin.ogg')


def send_request(api_client, api_client_authz_header, identifier: str):
    url = f'/api/v1/whereabouts/tags/{identifier}'
    return api_client.get(url, headers=[api_client_authz_header])
