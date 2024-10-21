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
from byceps.events.whereabouts import (
    WhereaboutsClientApprovedEvent,
    WhereaboutsClientDeletedEvent,
    WhereaboutsClientRegisteredEvent,
    WhereaboutsStatusUpdatedEvent,
)
from byceps.services.webhooks.models import Announcement, OutgoingWebhook


# client


@with_locale
def announce_whereabouts_client_registered(
    event_name: str,
    event: WhereaboutsClientRegisteredEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    """Announce that a whereabouts client has been registered."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)

    text = gettext(
        'Whereabouts client "%(client_id)s" has been registered.',
        initiator_screen_name=initiator_screen_name,
        client_id=event.client_id,
    )

    return Announcement(text)


@with_locale
def announce_whereabouts_client_approved(
    event_name: str,
    event: WhereaboutsClientApprovedEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    """Announce that a whereabouts client has been approved."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)

    text = gettext(
        '%(initiator_screen_name)s has approved whereabouts client "%(client_id)s".',
        initiator_screen_name=initiator_screen_name,
        client_id=event.client_id,
    )

    return Announcement(text)


@with_locale
def announce_whereabouts_client_deleted(
    event_name: str,
    event: WhereaboutsClientDeletedEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    """Announce that a whereabouts client has been deleted."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)

    text = gettext(
        '%(initiator_screen_name)s has deleted whereabouts client "%(client_id)s".',
        initiator_screen_name=initiator_screen_name,
        client_id=event.client_id,
    )

    return Announcement(text)


# status


@with_locale
def announce_whereabouts_status_updated(
    event_name: str,
    event: WhereaboutsStatusUpdatedEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    """Announce that a user's whereabouts has been updated."""
    user_screen_name = get_screen_name_or_fallback(event.user)

    text = gettext(
        '%(user_screen_name)s\'s whereabouts changed to "%(whereabouts_description)s".',
        user_screen_name=user_screen_name,
        whereabouts_description=event.whereabouts_description,
    )

    return Announcement(text)
