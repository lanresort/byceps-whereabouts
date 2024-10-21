"""
byceps.blueprints.admin.whereabouts.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict
from datetime import datetime, timedelta

from flask import abort, request
from flask_babel import gettext

from byceps.services.party import party_service
from byceps.services.whereabouts import whereabouts_service, whereabouts_sound_service
from byceps.services.whereabouts.models import WhereaboutsStatus
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_success
from byceps.util.framework.templating import templated
from byceps.util.iterables import partition
from byceps.util.views import permission_required, redirect_to

from .forms import UserSoundCreateForm, WhereaboutsCreateForm


blueprint = create_blueprint('whereabouts_admin', __name__)


STALE_THRESHOLD = timedelta(hours=12)


# -------------------------------------------------------------------- #
# whereabouts


@blueprint.get('/for_party/<party_id>')
@permission_required('whereabouts.view')
@templated
def index(party_id):
    """Show whereabouts for party."""
    party = _get_party_or_404(party_id)

    whereabouts_list = whereabouts_service.get_whereabouts_list(party)

    statuses = whereabouts_service.get_statuses(party)

    now = datetime.utcnow()

    def _is_status_stale(status: WhereaboutsStatus) -> bool:
        return (now - STALE_THRESHOLD) > status.set_at

    stale_statuses, recent_statuses = partition(statuses, _is_status_stale)

    recent_statuses_by_whereabouts = defaultdict(list)
    for status in recent_statuses:
        recent_statuses_by_whereabouts[status.whereabouts_id].append(status)

    return {
        'party': party,
        'whereabouts_list': whereabouts_list,
        'recent_statuses_by_whereabouts': recent_statuses_by_whereabouts,
        'stale_statuses': stale_statuses,
    }


@blueprint.get('/for_party/<party_id>/whereabouts/create')
@permission_required('whereabouts.administrate')
@templated
def create_form(party_id, erroneous_form=None):
    """Show form to add whereabouts."""
    party = _get_party_or_404(party_id)

    form = erroneous_form if erroneous_form else WhereaboutsCreateForm()

    return {
        'party': party,
        'form': form,
    }


@blueprint.post('/for_party/<party_id>/whereabouts')
@permission_required('whereabouts.administrate')
def create(party_id):
    """Add whereabouts."""
    party = _get_party_or_404(party_id)

    form = WhereaboutsCreateForm(request.form)
    if not form.validate():
        return create_form(form)

    name = form.name.data.strip()
    description = form.description.data.strip()
    hide_if_empty = form.hide_if_empty.data
    secret = form.secret.data

    whereabouts_service.create_whereabouts(
        party, name, description, hide_if_empty=hide_if_empty, secret=secret
    )

    flash_success(gettext('The object has been created.'))

    return redirect_to('.index', party_id=party.id)


# -------------------------------------------------------------------- #
# user sounds


@blueprint.get('/user_sounds')
@permission_required('whereabouts.administrate')
@templated
def user_sound_index():
    """List user sounds."""
    user_sounds = whereabouts_sound_service.get_all_user_sounds()

    return {
        'user_sounds': user_sounds,
    }


@blueprint.get('/user_sounds/create')
@permission_required('whereabouts.administrate')
@templated
def user_sound_create_form(erroneous_form=None):
    """Show form to specify a sound for a user."""
    form = erroneous_form if erroneous_form else UserSoundCreateForm()

    return {
        'form': form,
    }


@blueprint.post('/user_sounds')
@permission_required('whereabouts.administrate')
def user_sound_create():
    """Specify a sound for a user."""
    form = UserSoundCreateForm(request.form)
    if not form.validate():
        return user_sound_create_form(form)

    user = form.user.data
    filename = form.filename.data.strip()

    whereabouts_sound_service.create_user_sound(user, filename)

    flash_success(gettext('The object has been created.'))

    return redirect_to('.user_sound_index')


# -------------------------------------------------------------------- #
# helpers


def _get_party_or_404(party_id):
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party
