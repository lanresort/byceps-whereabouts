"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.party.models import Party
from byceps.services.user.models.user import User
from byceps.services.whereabouts import whereabouts_service
from byceps.services.whereabouts.models import Whereabouts

from tests.helpers import generate_token


CONTENT_TYPE_JSON = 'application/json'


def test_set_status(
    api_client,
    api_client_authz_header,
    user: User,
    party: Party,
    whereabouts: Whereabouts,
):
    status_before = whereabouts_service.find_status(user, party)
    assert status_before is None

    response = send_request(
        api_client, api_client_authz_header, user, party, whereabouts
    )

    assert response.status_code == 204

    status_after = whereabouts_service.find_status(user, party)
    assert status_after is not None
    assert status_after.user.id == user.id
    assert status_after.user.screen_name == user.screen_name
    assert status_after.user.avatar_url == user.avatar_url
    assert status_after.whereabouts_id == whereabouts.id
    assert status_after.set_at == status_after.set_at


def test_unauthorized(api_client, user: User, party: Party):
    url = build_url(user, party)
    response = api_client.post(url)

    assert response.status_code == 401
    assert response.json is None


@pytest.fixture(scope='module')
def user(make_user) -> User:
    return make_user()


@pytest.fixture(scope='module')
def whereabouts(party) -> Whereabouts:
    description = generate_token()
    return whereabouts_service.create_whereabouts(party, description)


def send_request(
    api_client,
    api_client_authz_header,
    user: User,
    party: Party,
    whereabouts: Whereabouts,
):
    url = build_url(user, party)
    payload = {'whereabouts_id': str(whereabouts.id)}

    return api_client.post(url, headers=[api_client_authz_header], json=payload)


def build_url(user: User, party: Party) -> str:
    return f'/v1/whereabouts/statuses/{user.id}/{party.id}'
