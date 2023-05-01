"""
byceps.permissions.whereabouts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from byceps.util.authorization import register_permissions


register_permissions(
    'whereabouts',
    [
        ('administrate', lazy_gettext('Administrate whereabouts')),
        ('view', lazy_gettext('View whereabouts')),
    ],
)
