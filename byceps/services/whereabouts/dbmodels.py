"""
byceps.services.whereabouts.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.database import db, generate_uuid7
from byceps.typing import PartyID, UserID

from .models import WhereaboutsID


class DbWhereabouts(db.Model):
    """A user's potential whereabouts."""

    __tablename__ = 'whereabouts'
    __table_args__ = (
        db.UniqueConstraint('party_id', 'description'),
        db.UniqueConstraint('party_id', 'position'),
    )

    id = db.Column(db.Uuid, default=generate_uuid7, primary_key=True)
    party_id = db.Column(
        db.UnicodeText, db.ForeignKey('parties.id'), index=True, nullable=False
    )
    description = db.Column(db.UnicodeText, nullable=False)
    position = db.Column(db.Integer, nullable=False)
    hide_if_empty = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(
        self,
        party_id: PartyID,
        description: str,
        position: int,
        hide_if_empty: bool,
    ) -> None:
        self.party_id = party_id
        self.description = description
        self.position = position
        self.hide_if_empty = hide_if_empty


class DbWhereaboutsStatus(db.Model):
    """A user's most recent whereabouts."""

    __tablename__ = 'whereabouts_statuses'

    user_id = db.Column(
        db.Uuid, db.ForeignKey('users.id'), primary_key=True, index=True
    )
    whereabouts_id = db.Column(
        db.Uuid, db.ForeignKey('whereabouts.id'), nullable=False
    )
    set_at = db.Column(db.DateTime, nullable=False)

    def __init__(
        self, user_id: UserID, whereabouts_id: WhereaboutsID, set_at: datetime
    ) -> None:
        self.user_id = user_id
        self.whereabouts_id = whereabouts_id
        self.set_at = set_at


class DbWhereaboutsUpdate(db.Model):
    """An update on a user's whereabouts."""

    __tablename__ = 'whereabouts_updates'

    id = db.Column(db.Uuid, default=generate_uuid7, primary_key=True)
    user_id = db.Column(
        db.Uuid, db.ForeignKey('users.id'), index=True, nullable=False
    )
    whereabouts_id = db.Column(
        db.Uuid, db.ForeignKey('whereabouts.id'), nullable=False
    )
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(
        self,
        user_id: UserID,
        whereabouts_id: WhereaboutsID,
        created_at: datetime,
    ) -> None:
        self.user_id = user_id
        self.whereabouts_id = whereabouts_id
        self.created_at = created_at
