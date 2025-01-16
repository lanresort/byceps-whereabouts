"""
:Copyright: 2022-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

URL = '/v1/whereabouts/client/register'


def test_success(api_client, api_client_authz_header):
    payload = {
        'button_count': 3,
        'audio_output': True,
    }

    response = send_request(api_client, api_client_authz_header, payload)

    assert response.status_code == 204
    assert response.location.startswith(
        '/v1/whereabouts/client/registration_status/'
    )


def test_unauthorized(api_client):
    response = api_client.post(URL)

    assert response.status_code == 401


def send_request(
    api_client, api_client_authz_header, payload: dict[str, bool | int | str]
):
    return api_client.post(URL, headers=[api_client_authz_header], json=payload)
