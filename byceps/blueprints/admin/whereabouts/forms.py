"""
byceps.blueprints.admin.whereabouts.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import BooleanField, StringField
from wtforms.validators import InputRequired

from byceps.util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    description = StringField(lazy_gettext('Description'), [InputRequired()])
    hide_if_empty = BooleanField(lazy_gettext('Hide if empty'))
