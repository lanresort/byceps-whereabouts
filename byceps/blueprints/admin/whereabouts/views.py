"""
byceps.blueprints.admin.whereabouts.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict

from flask import abort, render_template, request
from flask_babel import gettext

from byceps.services.party import party_service
from byceps.services.user import user_service
from byceps.services.whereabouts import whereabouts_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import permission_required, redirect_to, textified

from .forms import CreateForm


blueprint = create_blueprint('whereabouts_admin', __name__)


@blueprint.get('/for_party/<party_id>')
@permission_required('whereabouts.view')
@templated
def index(party_id):
    """Show whereabouts for party."""
    party = _get_party_or_404(party_id)

    whereabouts_list = whereabouts_service.get_whereabouts_list(party.id)

    statuses = whereabouts_service.get_statuses(party.id)
    statuses_by_whereabouts = defaultdict(list)
    for status in statuses:
        statuses_by_whereabouts[status.whereabouts_id].append(status)

    user_ids = {status.user_id for status in statuses}
    users = user_service.get_users(user_ids, include_avatars=True)
    users_by_id = user_service.index_users_by_id(users)

    return {
        'party': party,
        'whereabouts_list': whereabouts_list,
        'statuses_by_whereabouts': statuses_by_whereabouts,
        'users_by_id': users_by_id,
    }


@blueprint.get('/tags')
@permission_required('whereabouts.administrate')
@templated
def tags():
    """Show tags."""
    tags = whereabouts_service.get_all_tags()

    return {
        'tags': tags,
    }


@blueprint.get('/tags/export')
@permission_required('whereabouts.administrate')
@templated('tags_export.toml')
@textified
def tags_export():
    """Export tags as TOML."""
    tags = whereabouts_service.get_all_tags()

    return render_template('admin/whereabouts/tags_export.toml', tags=tags)


@blueprint.get('/for_party/<party_id>/whereabouts/create')
@permission_required('whereabouts.administrate')
@templated
def create_form(party_id, erroneous_form=None):
    """Show form to add whereabouts."""
    party = _get_party_or_404(party_id)

    form = erroneous_form if erroneous_form else CreateForm()

    return {
        'party': party,
        'form': form,
    }


@blueprint.post('/for_party/<party_id>/whereabouts')
@permission_required('whereabouts.administrate')
def create(party_id):
    """Add whereabouts."""
    party = _get_party_or_404(party_id)

    form = CreateForm(request.form)
    if not form.validate():
        return create_form(form)

    description = form.description.data.strip()
    hide_if_empty = form.hide_if_empty.data

    whereabouts_service.create_whereabouts(
        party.id, description, hide_if_empty=hide_if_empty
    )

    flash_success(gettext('The object has been created.'))

    return redirect_to('.index', party_id=party.id)


def _get_party_or_404(party_id):
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party
