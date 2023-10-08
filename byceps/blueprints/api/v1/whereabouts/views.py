"""
byceps.blueprints.api.v1.whereabouts.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ipaddress import ip_address

from flask import abort, jsonify, request
from pydantic import ValidationError

from byceps.blueprints.api.decorators import api_token_required
from byceps.services.authn.identity_tag import authn_identity_tag_service
from byceps.services.party import party_service
from byceps.services.user import user_service
from byceps.services.whereabouts import whereabouts_service
from byceps.signals import whereabouts as whereabouts_signals
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.views import create_empty_json_response, respond_no_content

from .models import SetStatus


blueprint = create_blueprint('whereabouts_api', __name__)


@blueprint.get('/tags/<identifier>')
@api_token_required
def get_tag(identifier):
    """Get details for tag."""
    identity_tag = authn_identity_tag_service.find_tag_by_identifier(identifier)
    if identity_tag is None:
        return create_empty_json_response(404)

    user_sound = whereabouts_service.find_sound_for_user(identity_tag.user.id)

    return jsonify(
        {
            'identifier': identity_tag.identifier,
            'user': {
                'id': identity_tag.user.id,
                'screen_name': identity_tag.user.screen_name,
                'avatar_url': identity_tag.user.avatar_url,
            },
            'sound_filename': user_sound.filename,
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


@blueprint.post('/statuses/<uuid:user_id>/<party_id>')
@api_token_required
@respond_no_content
def set_status(user_id, party_id):
    """Set user's status."""
    user = user_service.find_user(user_id)
    if user is None:
        abort(404, 'Unknown user ID')

    party = party_service.find_party(party_id)
    if user is None:
        abort(404, 'Unknown party ID')

    if not request.is_json:
        abort(415)

    try:
        req = SetStatus.model_validate(request.get_json())
    except ValidationError as e:
        abort(400, str(e.normalized_messages()))

    whereabouts = whereabouts_service.find_whereabouts(req.whereabouts_id)
    if whereabouts is None:
        abort(400, 'Unknown whereabouts ID')

    if whereabouts.party.id != party.id:
        abort(400, 'Whereabouts ID does not belong to this party')

    remote_addr = request.remote_addr
    source_address = ip_address(remote_addr) if remote_addr else None

    _, _, event = whereabouts_service.set_status(
        user, whereabouts, source_address=source_address
    )

    whereabouts_signals.whereabouts_status_updated.send(None, event=event)
