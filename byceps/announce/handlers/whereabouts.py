"""
byceps.announce.handlers.guest_server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce guest server events.

:Copyright: 2022-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from flask_babel import gettext

from byceps.announce.helpers import (
    get_screen_name_or_fallback,
    with_locale,
)
from byceps.events.whereabouts import WhereaboutsStatusUpdatedEvent
from byceps.services.webhooks.models import Announcement, OutgoingWebhook


@with_locale
def announce_whereabouts_status_updated(
    event_name: str,
    event: WhereaboutsStatusUpdatedEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    """Announce that a user's whereabouts has been updated."""
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    text = gettext(
        '%(user_screen_name)s\'s whereabouts changed to "%(whereabouts_description)s".',
        user_screen_name=user_screen_name,
        whereabouts_description=event.whereabouts_description,
    )

    return Announcement(text)
