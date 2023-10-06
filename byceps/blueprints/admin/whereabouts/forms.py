"""
byceps.blueprints.admin.whereabouts.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import BooleanField, StringField
from wtforms.validators import InputRequired, ValidationError

from byceps.services.user import user_service
from byceps.services.whereabouts import whereabouts_service
from byceps.util.l10n import LocalizedForm


class WhereaboutsCreateForm(LocalizedForm):
    name = StringField(lazy_gettext('Name'), [InputRequired()])
    description = StringField(lazy_gettext('Description'), [InputRequired()])
    hide_if_empty = BooleanField(lazy_gettext('Hide if empty'))


def validate_user_screen_name(form, field):
    screen_name = field.data.strip()

    user = user_service.find_user_by_screen_name(
        screen_name, case_insensitive=True
    )

    if user is None:
        raise ValidationError(lazy_gettext('Unknown username'))

    existing_user_sound = whereabouts_service.find_sound_for_user(user.id)
    if existing_user_sound:
        raise ValidationError(
            lazy_gettext('The user already has a sound assigned.')
        )

    field.data = user


class UserSoundCreateForm(LocalizedForm):
    user = StringField(
        lazy_gettext('Username'),
        [InputRequired(), validate_user_screen_name],
    )
    filename = StringField(lazy_gettext('Sound filename'), [InputRequired()])
