"""
byceps.services.whereabouts.whereabouts_sound_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from sqlalchemy import select

from byceps.database import db
from byceps.services.user import user_service
from byceps.services.user.models.user import User, UserID

from .dbmodels import DbWhereaboutsUserSound
from .models import WhereaboutsUserSound


def create_user_sound(user: User, filename: str) -> WhereaboutsUserSound:
    """Set a users-specific sound."""
    db_user_sound = DbWhereaboutsUserSound(user.id, filename)

    db.session.add(db_user_sound)
    db.session.commit()

    return _db_entity_to_user_sound(db_user_sound, user)


def find_sound_for_user(user_id: UserID) -> WhereaboutsUserSound | None:
    """Find a sound specific for this user."""
    db_user_sound = db.session.scalars(
        select(DbWhereaboutsUserSound).filter_by(user_id=user_id)
    ).one_or_none()

    if db_user_sound is None:
        return None

    user = user_service.get_user(db_user_sound.user_id, include_avatar=True)

    return _db_entity_to_user_sound(db_user_sound, user)


def get_all_user_sounds() -> list[WhereaboutsUserSound]:
    """Return all user sounds."""
    db_user_sounds = db.session.scalars(select(DbWhereaboutsUserSound)).all()

    user_ids = {db_user_sound.user_id for db_user_sound in db_user_sounds}
    users_by_id = user_service.get_users_indexed_by_id(
        user_ids, include_avatars=True
    )

    return [
        _db_entity_to_user_sound(
            db_user_sound, users_by_id[db_user_sound.user_id]
        )
        for db_user_sound in db_user_sounds
    ]


def _db_entity_to_user_sound(
    db_user_sound: DbWhereaboutsUserSound, user: User
) -> WhereaboutsUserSound:
    return WhereaboutsUserSound(
        user=user,
        filename=db_user_sound.filename,
    )
