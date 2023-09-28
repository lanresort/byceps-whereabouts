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
    print('\n' + ('-' * 40))
    print('status before:', status_before)

    response = send_request(api_client, api_client_authz_header, user, whereabouts)

    assert response.status_code == 204

    status_after = whereabouts_service.find_status(user, party)
    print('status after:', status_after)



def test_unauthorized(api_client, user: User):
    url = build_url(user)
    response = api_client.post(url)

    assert response.status_code == 401
    assert response.json is None


@pytest.fixture(scope='module')
def whereabouts(party) -> Whereabouts:
    description = generate_token()
    return whereabouts_service.create_whereabouts(party, description)


def send_request(api_client, api_client_authz_header, user: User, whereabouts: Whereabouts):
    url = build_url(user)
    payload = {'whereabouts_id': str(whereabouts.id)}

    return api_client.post(url, headers=[api_client_authz_header], json=payload)


def build_url(user: User) -> str:
    return f'/api/v1/whereabouts/statuses/{user.id}'
