"""
byceps.services.whereabouts.whereabouts_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

from byceps.events.whereabouts import (
    WhereaboutsStatusUpdatedEvent,
    WhereaboutsTagCreatedEvent,
)
from byceps.services.party.models import Party
from byceps.services.user.models.user import User
from byceps.util.uuid import generate_uuid4, generate_uuid7

from .models import (
    IPAddress,
    Whereabouts,
    WhereaboutsID,
    WhereaboutsStatus,
    WhereaboutsTag,
    WhereaboutsUpdate,
)


def create_whereabouts(
    party: Party,
    name: str,
    description: str,
    position: int,
    *,
    hide_if_empty: bool = False,
    secret: bool = False,
) -> Whereabouts:
    """Create whereabouts."""
    whereabouts_id = WhereaboutsID(generate_uuid7())

    return Whereabouts(
        id=whereabouts_id,
        party=party,
        name=name,
        description=description,
        position=position,
        hide_if_empty=hide_if_empty,
        secret=secret,
    )


def create_tag(
    tag: str,
    creator: User,
    user: User,
    *,
    sound_filename: str | None = None,
    suspended: bool = False,
) -> tuple[WhereaboutsTag, WhereaboutsTagCreatedEvent]:
    """Create a tag."""
    tag_id = generate_uuid4()
    created_at = datetime.utcnow()

    tag_obj = WhereaboutsTag(
        id=tag_id,
        created_at=created_at,
        creator=creator,
        tag=tag,
        user=user,
        sound_filename=sound_filename,
        suspended=suspended,
    )

    event = WhereaboutsTagCreatedEvent(
        occurred_at=created_at,
        initiator_id=creator.id,
        initiator_screen_name=creator.screen_name,
        tag=tag,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )

    return tag_obj, event


def set_status(
    user: User,
    whereabouts: Whereabouts,
    *,
    source_address: IPAddress | None = None,
) -> tuple[WhereaboutsStatus, WhereaboutsUpdate, WhereaboutsStatusUpdatedEvent]:
    """Set a user's whereabouts."""
    update_id = generate_uuid7()
    set_at = datetime.utcnow()

    status = WhereaboutsStatus(
        user=user,
        whereabouts_id=whereabouts.id,
        set_at=set_at,
    )

    update = WhereaboutsUpdate(
        id=update_id,
        user=user,
        whereabouts_id=whereabouts.id,
        created_at=set_at,
        source_address=source_address,
    )

    event = WhereaboutsStatusUpdatedEvent(
        occurred_at=set_at,
        initiator_id=user.id,
        initiator_screen_name=user.screen_name,
        party_id=whereabouts.party.id,
        party_title=whereabouts.party.title,
        user_id=user.id,
        user_screen_name=user.screen_name,
        whereabouts_description=whereabouts.description,
    )

    return status, update, event
