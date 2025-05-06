"""
byceps.services.whereabouts.blueprints.api.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ipaddress import ip_address

from flask import abort, jsonify, request, Request, url_for
from pydantic import ValidationError

from byceps.services.authn.identity_tag import authn_identity_tag_service
from byceps.services.party import party_service
from byceps.services.user import user_service
from byceps.services.whereabouts import (
    signals as whereabouts_signals,
    whereabouts_client_service,
    whereabouts_service,
    whereabouts_sound_service,
)
from byceps.services.whereabouts.models import IPAddress, WhereaboutsClient
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.views import (
    api_token_required,
    create_empty_json_response,
    respond_no_content,
)

from .models import RegisterClientRequestModel, SetStatusRequestModel


blueprint = create_blueprint('whereabouts_api', __name__)


@blueprint.post('/client/register')
@api_token_required
def register_client():
    """Register a client."""
    if not request.is_json:
        abort(415)

    try:
        req = RegisterClientRequestModel.model_validate(request.get_json())
    except ValidationError as e:
        abort(400, e.json())

    source_address = _get_source_ip_address(request)

    candidate, event = whereabouts_client_service.register_client(
        req.button_count, req.audio_output, source_address=source_address
    )

    whereabouts_signals.whereabouts_client_registered.send(None, event=event)

    url = url_for('.get_client_registration_status', client_id=candidate.id)

    response = jsonify({'token': candidate.token})
    response.status_code = 201
    response.headers['Location'] = url
    return response


@blueprint.get('/client/registration_status/<client_id>')
@api_token_required
def get_client_registration_status(client_id):
    """Get a client's registration status."""
    client = whereabouts_client_service.find_client(client_id)
    if not client:
        abort(404)

    if client.pending:
        response_data = {'status': 'pending'}
    elif client.approved:
        response_data = {'status': 'approved'}
    else:
        response_data = {'status': 'rejected'}

    return jsonify(response_data)


@blueprint.post('/client/sign_on')
@api_token_required
@respond_no_content
def sign_on_client():
    """Sign on a client."""
    client = _get_approved_client()

    source_address = _get_source_ip_address(request)

    event = whereabouts_client_service.sign_on_client(
        client, source_address=source_address
    )

    whereabouts_signals.whereabouts_client_signed_on.send(None, event=event)


@blueprint.post('/client/sign_off')
@api_token_required
@respond_no_content
def sign_off_client():
    """Sign off a client."""
    client = _get_approved_client()

    source_address = _get_source_ip_address(request)

    event = whereabouts_client_service.sign_off_client(
        client, source_address=source_address
    )

    whereabouts_signals.whereabouts_client_signed_off.send(None, event=event)


@blueprint.get('/tags/<identifier>')
@api_token_required
def get_tag(identifier):
    """Get details for tag."""
    identity_tag = authn_identity_tag_service.find_tag_by_identifier(identifier)
    if identity_tag is None:
        return create_empty_json_response(404)

    user_sound = whereabouts_sound_service.find_sound_for_user(
        identity_tag.user.id
    )

    return jsonify(
        {
            'identifier': identity_tag.identifier,
            'user': {
                'id': identity_tag.user.id,
                'screen_name': identity_tag.user.screen_name,
                'avatar_url': identity_tag.user.avatar_url,
            },
            'sound_filename': user_sound.filename if user_sound else None,
        }
    )


@blueprint.get('/statuses/<uuid:user_id>/<party_id>')
@api_token_required
def get_status(user_id, party_id):
    """Get user's status at party."""
    user = user_service.find_user(user_id)
    if user is None:
        abort(404, 'Unknown user ID')

    party = party_service.find_party(party_id)
    if user is None:
        abort(404, 'Unknown party ID')

    status = whereabouts_service.find_status(user, party)
    if status is None:
        return create_empty_json_response(404)

    whereabouts = whereabouts_service.find_whereabouts(status.whereabouts_id)
    if whereabouts is None:
        abort(500, 'Unknown whereabouts ID')  # not a client error

    return jsonify(
        {
            'user': {
                'id': user.id,
                'screen_name': user.screen_name,
                'avatar_url': user.avatar_url,
            },
            'whereabouts': {
                'id': whereabouts.id,
                'name': whereabouts.name,
                'description': whereabouts.description,
            },
            'set_at': status.set_at.isoformat(),
        }
    )


@blueprint.post('/statuses')
@api_token_required
@respond_no_content
def set_status():
    """Set user's status."""
    client = _get_approved_client()

    if not request.is_json:
        abort(415)

    try:
        req = SetStatusRequestModel.model_validate(request.get_json())
    except ValidationError as e:
        abort(400, e.json())

    user = user_service.find_user(req.user_id)
    if user is None:
        abort(400, 'Unknown user ID')

    party = party_service.find_party(req.party_id)
    if party is None:
        abort(400, 'Unknown party ID')

    whereabouts = whereabouts_service.find_whereabouts_by_name(
        party.id, req.whereabouts_name
    )
    if whereabouts is None:
        abort(400, 'Unknown whereabouts name for this party')

    if whereabouts.party.id != party.id:
        abort(400, 'Whereabouts name does not belong to this party')

    source_address = _get_source_ip_address(request)

    _, _, event = whereabouts_service.set_status(
        client, user, whereabouts, source_address=source_address
    )

    whereabouts_signals.whereabouts_status_updated.send(None, event=event)


# helpers


def _get_source_ip_address(request: Request) -> IPAddress | None:
    remote_addr = request.remote_addr
    return ip_address(remote_addr) if remote_addr else None


def _get_approved_client() -> WhereaboutsClient:
    client = _get_client()

    if not client.approved:
        abort(400, 'Invalid client token')

    return client


def _get_client() -> WhereaboutsClient:
    client = _find_client()

    if not client:
        abort(400, 'Invalid client token')

    return client


def _find_client() -> WhereaboutsClient | None:
    token = request.headers.get('x-whereabouts-client-token')
    if not token:
        return None

    client = whereabouts_client_service.find_client_by_token(token)
    if not client:
        return None

    return client
