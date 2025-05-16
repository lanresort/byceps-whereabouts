"""
byceps.services.whereabouts.whereabouts_sound_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import select

from byceps.database import db
from byceps.services.user.models.user import UserID

from .dbmodels import DbWhereaboutsUserSound


def create_user_sound(user_id: UserID, filename: str) -> DbWhereaboutsUserSound:
    """Set a users-specific sound."""
    db_user_sound = DbWhereaboutsUserSound(user_id, filename)

    db.session.add(db_user_sound)
    db.session.commit()

    return db_user_sound


def find_sound_for_user(user_id: UserID) -> DbWhereaboutsUserSound | None:
    """Find a sound specific for this user."""
    return db.session.scalars(
        select(DbWhereaboutsUserSound).filter_by(user_id=user_id)
    ).one_or_none()


def get_all_user_sounds() -> list[DbWhereaboutsUserSound]:
    """Return all user sounds."""
    return db.session.scalars(select(DbWhereaboutsUserSound)).all()
