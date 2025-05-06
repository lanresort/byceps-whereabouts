"""
:Copyright: 2022-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.user.models.user import User
from byceps.services.whereabouts import whereabouts_client_service


def test_client_registration_status_pending(
    api_client,
    api_client_authz_header,
    registered_whereabouts_client,
):
    response = send_request(
        api_client, api_client_authz_header, registered_whereabouts_client
    )

    assert response.status_code == 200
    assert response.json == {'status': 'pending'}


def test_client_registration_status_approved(
    api_client,
    api_client_authz_header,
    approved_whereabouts_client,
):
    response = send_request(
        api_client, api_client_authz_header, approved_whereabouts_client
    )

    assert response.status_code == 200
    assert response.json == {'status': 'approved'}


def test_client_registration_status_deleted(
    api_client,
    api_client_authz_header,
    deleted_whereabouts_client,
):
    response = send_request(
        api_client, api_client_authz_header, deleted_whereabouts_client
    )

    assert response.status_code == 200
    assert response.json == {'status': 'rejected'}


def test_unauthorized(api_client, registered_whereabouts_client):
    client_id = registered_whereabouts_client.id
    url = f'/v1/whereabouts/client/registration_status/{client_id}'

    response = api_client.get(url)

    assert response.status_code == 401
    assert response.json is None


@pytest.fixture(scope='module')
def registered_whereabouts_client(admin):
    candidate, _ = whereabouts_client_service.register_client(
        button_count=3, audio_output=False
    )

    return candidate


@pytest.fixture(scope='module')
def approved_whereabouts_client(admin):
    candidate, _ = whereabouts_client_service.register_client(
        button_count=3, audio_output=False
    )

    approved_client, _ = whereabouts_client_service.approve_client(
        candidate, admin
    )

    return approved_client


@pytest.fixture(scope='module')
def deleted_whereabouts_client(admin):
    candidate, _ = whereabouts_client_service.register_client(
        button_count=3, audio_output=False
    )

    approved_client, _ = whereabouts_client_service.approve_client(
        candidate, admin
    )

    deleted_client, _ = whereabouts_client_service.delete_client(
        approved_client, admin
    )

    return deleted_client


@pytest.fixture(scope='module')
def admin(make_user) -> User:
    return make_user()


def send_request(api_client, api_client_authz_header, whereabouts_client):
    client_id = whereabouts_client.id
    url = f'/v1/whereabouts/client/registration_status/{client_id}'

    headers = [api_client_authz_header]

    return api_client.get(url, headers=headers)
