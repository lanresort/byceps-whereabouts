"""
byceps.services.whereabouts.whereabouts_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select

from byceps.database import db, execute_upsert
from byceps.events.whereabouts import WhereaboutsUpdatedEvent
from byceps.services.party import party_service
from byceps.services.party.models import Party
from byceps.services.user import user_service
from byceps.services.user.models.user import User
from byceps.util.uuid import generate_uuid7

from .dbmodels import (
    DbWhereabouts,
    DbWhereaboutsStatus,
    DbWhereaboutsTag,
    DbWhereaboutsUpdate,
)
from .models import (
    Whereabouts,
    WhereaboutsID,
    WhereaboutsStatus,
    WhereaboutsTag,
    WhereaboutsUpdate,
)


# -------------------------------------------------------------------- #
# whereabouts


def create_whereabouts(
    party: Party,
    description: str,
    *,
    position: int | None = None,
    hide_if_empty: bool = False,
    secret: bool = False,
) -> Whereabouts:
    """Create whereabouts."""
    if position is None:
        whereabouts_list = get_whereabouts_list(party)
        if whereabouts_list:
            next_position = max(w.position for w in whereabouts_list) + 1
        else:
            next_position = 0

    db_whereabouts = DbWhereabouts(
        party.id, description, next_position, hide_if_empty, secret=secret
    )
    db.session.add(db_whereabouts)
    db.session.commit()

    return _db_entity_to_whereabouts(db_whereabouts, party)


def find_whereabouts(whereabouts_id: WhereaboutsID) -> Whereabouts | None:
    """Return whereabouts, if found."""
    db_whereabouts = db.session.get(DbWhereabouts, whereabouts_id)

    if db_whereabouts is None:
        return None

    party = party_service.get_party(db_whereabouts.party_id)

    return _db_entity_to_whereabouts(db_whereabouts, party)


def get_whereabouts_list(party: Party) -> list[Whereabouts]:
    """Return possible whereabouts."""
    db_whereabouts_list = db.session.scalars(
        select(DbWhereabouts).filter_by(party_id=party.id)
    ).all()

    return [
        _db_entity_to_whereabouts(db_whereabouts, party)
        for db_whereabouts in db_whereabouts_list
    ]


def _db_entity_to_whereabouts(
    db_whereabouts: DbWhereabouts, party: Party
) -> Whereabouts:
    return Whereabouts(
        id=db_whereabouts.id,
        party=party,
        description=db_whereabouts.description,
        position=db_whereabouts.position,
        hide_if_empty=db_whereabouts.hide_if_empty,
        secret=db_whereabouts.secret,
    )


# -------------------------------------------------------------------- #
# tags


def create_tag(
    tag: str,
    user: User,
    creator: User,
    *,
    sound_filename: str | None = None,
) -> WhereaboutsTag:
    """Create a tag."""
    created_at = datetime.utcnow()

    db_tag = DbWhereaboutsTag(
        created_at, creator.id, tag, user.id, sound_filename=sound_filename
    )
    db.session.add(db_tag)
    db.session.commit()

    return _db_entity_to_tag(db_tag, user)


def find_tag_by_value(value: str) -> WhereaboutsTag | None:
    """Return tag by value."""
    db_tag = db.session.scalars(
        select(DbWhereaboutsTag).filter(
            db.func.lower(DbWhereaboutsTag.tag) == value.lower()
        )
    ).one_or_none()

    if db_tag is None:
        return None

    user = user_service.get_user(db_tag.user_id, include_avatar=True)

    return _db_entity_to_tag(db_tag, user)


def get_all_tags() -> list[WhereaboutsTag]:
    """Return all tags."""
    db_tags = db.session.scalars(select(DbWhereaboutsTag)).all()

    user_ids = {db_tag.user_id for db_tag in db_tags}
    users_by_id = user_service.get_users_indexed_by_id(
        user_ids, include_avatars=True
    )

    return [
        _db_entity_to_tag(db_tag, users_by_id[db_tag.user_id])
        for db_tag in db_tags
    ]


def _db_entity_to_tag(db_tag: DbWhereaboutsTag, user: User) -> WhereaboutsTag:
    return WhereaboutsTag(
        id=db_tag.id,
        tag=db_tag.tag,
        user=user,
        sound_filename=db_tag.sound_filename,
        suspended=db_tag.suspended,
    )


# -------------------------------------------------------------------- #
# status


def set_status(
    user: User, whereabouts: Whereabouts
) -> tuple[WhereaboutsStatus, WhereaboutsUpdate, WhereaboutsUpdatedEvent]:
    """Set a user's whereabouts."""
    now = datetime.utcnow()

    status = WhereaboutsStatus(
        user=user,
        whereabouts_id=whereabouts.id,
        set_at=now,
    )

    update = WhereaboutsUpdate(
        id=generate_uuid7(),
        user=user,
        whereabouts_id=whereabouts.id,
        created_at=now,
    )

    event = WhereaboutsUpdatedEvent(
        occurred_at=now,
        initiator_id=user.id,
        initiator_screen_name=user.screen_name,
        party_id=whereabouts.party.id,
        party_title=whereabouts.party.title,
        user_id=user.id,
        user_screen_name=user.screen_name,
        whereabouts_description=whereabouts.description,
    )

    _persist_update(status, update)

    return status, update, event


def _persist_update(
    status: WhereaboutsStatus, update: WhereaboutsUpdate
) -> None:
    # status
    table = DbWhereaboutsStatus.__table__
    identifier = {
        'user_id': status.user.id,
    }
    replacement = {
        'whereabouts_id': status.whereabouts_id,
        'set_at': status.set_at,
    }
    execute_upsert(table, identifier, replacement)

    # update
    db_update = DbWhereaboutsUpdate(
        update.id, update.user.id, update.whereabouts_id, update.created_at
    )
    db.session.add(db_update)

    db.session.commit()


def find_status(user: User, party: Party) -> WhereaboutsStatus | None:
    """Return user's status for the party, if known."""
    db_status = db.session.scalars(
        select(DbWhereaboutsStatus)
        .join(DbWhereabouts)
        .filter(DbWhereaboutsStatus.user_id == user.id)
        .filter(DbWhereabouts.party_id == party.id)
    ).one_or_none()

    if db_status is None:
        return None

    user = user_service.get_user(db_status.user_id, include_avatar=True)

    return _db_entity_to_status(db_status, user)


def get_statuses(party: Party) -> list[WhereaboutsStatus]:
    """Return user statuses."""
    db_statuses = db.session.scalars(
        select(DbWhereaboutsStatus)
        .join(DbWhereabouts)
        .filter(DbWhereabouts.party_id == party.id)
    ).all()

    user_ids = {db_status.user_id for db_status in db_statuses}
    users_by_id = user_service.get_users_indexed_by_id(
        user_ids, include_avatars=True
    )

    return [
        _db_entity_to_status(db_status, users_by_id[db_status.user_id])
        for db_status in db_statuses
    ]


def _db_entity_to_status(
    db_status: DbWhereaboutsStatus, user: User
) -> WhereaboutsStatus:
    return WhereaboutsStatus(
        user=user,
        whereabouts_id=db_status.whereabouts_id,
        set_at=db_status.set_at,
    )
