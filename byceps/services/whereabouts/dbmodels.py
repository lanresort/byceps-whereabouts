"""
byceps.services.whereabouts.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from byceps.database import db, generate_uuid4, generate_uuid7
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


class DbWhereaboutsTag(db.Model):
    """A user tag.

    Can be an identifier stored on an RFID transponder, in a barcode,
    etc. Used to identify a user against the whereabouts system.

    A user can have multiple tags.
    """

    __tablename__ = 'whereabouts_tags'

    id = db.Column(db.Uuid, default=generate_uuid4, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    tag = db.Column(db.UnicodeText, unique=True, nullable=False)
    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    sound_filename = db.Column(db.UnicodeText, nullable=True)

    def __init__(
        self,
        created_at: datetime,
        tag: str,
        user_id: UserID,
        *,
        sound_filename: str | None = None,
    ) -> None:
        self.created_at = created_at
        self.tag = tag
        self.user_id = user_id
        self.sound_filename = sound_filename


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

    id = db.Column(db.Uuid, primary_key=True)
    user_id = db.Column(
        db.Uuid, db.ForeignKey('users.id'), index=True, nullable=False
    )
    whereabouts_id = db.Column(
        db.Uuid, db.ForeignKey('whereabouts.id'), nullable=False
    )
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(
        self,
        update_id: UUID,
        user_id: UserID,
        whereabouts_id: WhereaboutsID,
        created_at: datetime,
    ) -> None:
        self.id = update_id
        self.user_id = user_id
        self.whereabouts_id = whereabouts_id
        self.created_at = created_at
