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
from byceps.typing import PartyID, UserID

from .dbmodels import DbStatus, DbUpdate, DbWhereabouts
from .models import Status, Whereabouts, WhereaboutsID


# -------------------------------------------------------------------- #
# whereabouts


def create_whereabouts(
    party_id: PartyID,
    description: str,
    *,
    position: int | None = None,
    hide_if_empty: bool = False,
) -> Whereabouts:
    """Create whereabouts."""
    if position is None:
        whereabouts_list = get_whereabouts_list(party_id)
        if whereabouts_list:
            next_position = max(w.position for w in whereabouts_list) + 1
        else:
            next_position = 0

    db_whereabouts = DbWhereabouts(
        party_id, description, next_position, hide_if_empty
    )
    db.session.add(db_whereabouts)
    db.session.commit()

    return _db_entity_to_whereabouts(db_whereabouts)


def find_whereabouts(whereabouts_id: WhereaboutsID) -> Whereabouts | None:
    """Return whereabouts, if found."""
    db_whereabouts = db.session.get(DbWhereabouts, whereabouts_id)

    if db_whereabouts is None:
        return None

    return _db_entity_to_whereabouts(db_whereabouts)


def get_whereabouts_list(party_id: PartyID) -> list[Whereabouts]:
    """Return possible whereabouts."""
    db_whereabouts_list = db.session.scalars(
        select(DbWhereabouts).filter_by(party_id=party_id)
    ).all()

    return [
        _db_entity_to_whereabouts(db_whereabouts)
        for db_whereabouts in db_whereabouts_list
    ]


def _db_entity_to_whereabouts(db_whereabouts: DbWhereabouts) -> Whereabouts:
    return Whereabouts(
        id=db_whereabouts.id,
        party_id=db_whereabouts.party_id,
        description=db_whereabouts.description,
        position=db_whereabouts.position,
        hide_if_empty=db_whereabouts.hide_if_empty,
    )


# -------------------------------------------------------------------- #
# status


def set_status(user_id: UserID, whereabouts_id: WhereaboutsID) -> None:
    """Set a user's whereabouts."""
    now = datetime.utcnow()

    # Add status.
    table = DbStatus.__table__
    identifier = {
        'user_id': user_id,
    }
    replacement = {
        'whereabouts_id': whereabouts_id,
        'set_at': now,
    }
    execute_upsert(table, identifier, replacement)

    # Add update.
    db_update = DbUpdate(user_id, whereabouts_id, now)
    db.session.add(db_update)

    db.session.commit()


def get_statuses(party_id: PartyID) -> list[Status]:
    """Return user statuses."""
    db_statuses = db.session.scalars(
        select(DbStatus)
        .join(DbWhereabouts)
        .filter(DbWhereabouts.party_id == party_id)
    ).all()

    return [_db_entity_to_status(db_status) for db_status in db_statuses]


def _db_entity_to_status(db_status: DbStatus) -> Status:
    return Status(
        user_id=db_status.user_id,
        whereabouts_id=db_status.whereabouts_id,
        set_at=db_status.set_at,
    )
