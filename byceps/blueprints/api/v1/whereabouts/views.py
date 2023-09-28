"""
byceps.blueprints.api.v1.whereabouts.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, jsonify, request
from pydantic import ValidationError

from byceps.blueprints.api.decorators import api_token_required
from byceps.services.party import party_service
from byceps.services.user import user_service
from byceps.services.whereabouts import whereabouts_service
from byceps.signals import whereabouts as whereabouts_signals
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.views import create_empty_json_response, respond_no_content

from .models import SetStatus


blueprint = create_blueprint('whereabouts_api', __name__)


@blueprint.get('/tags/<tag_value>')
@api_token_required
def get_tag(tag_value):
    """Get details for tag."""
    tag = whereabouts_service.find_tag_by_value(tag_value)

    if tag is None:
        return create_empty_json_response(404)

    return jsonify(
        {
            'tag': tag.tag,
            'user': {
                'id': tag.user.id,
                'screen_name': tag.user.screen_name,
                'avatar_url': tag.user.avatar_url,
            },
            'sound_filename': tag.sound_filename,
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
                'description': whereabouts.description,
            },
            'set_at': status.set_at.isoformat(),
        }
    )


@blueprint.post('/set_status')
@api_token_required
@respond_no_content
def set_status():
    """Set status for user."""
    if not request.is_json:
        abort(415)

    try:
        req = SetStatus.model_validate(request.get_json())
    except ValidationError as e:
        abort(400, str(e.normalized_messages()))

    user = user_service.find_user(req.user_id)
    if user is None:
        abort(400, 'Unknown user ID')

    whereabouts = whereabouts_service.find_whereabouts(req.whereabouts_id)
    if whereabouts is None:
        abort(400, 'Unknown whereabouts ID')

    _, _, event = whereabouts_service.set_status(user, whereabouts)

    whereabouts_signals.whereabouts_updated.send(None, event=event)
