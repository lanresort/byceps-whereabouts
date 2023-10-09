"""
byceps.services.whereabouts.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime
import ipaddress
from typing import Optional, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.party.models import PartyID
from byceps.services.user.models.user import UserID

from .models import IPAddress, WhereaboutsID


class DbWhereabouts(db.Model):
    """A user's potential whereabouts."""

    __tablename__ = 'whereabouts'
    __table_args__ = (
        db.UniqueConstraint('party_id', 'name'),
        db.UniqueConstraint('party_id', 'description'),
        db.UniqueConstraint('party_id', 'position'),
    )

    id: Mapped[WhereaboutsID] = mapped_column(db.Uuid, primary_key=True)
    party_id: Mapped[PartyID] = mapped_column(
        db.UnicodeText, db.ForeignKey('parties.id'), index=True
    )
    name: Mapped[str] = mapped_column(db.UnicodeText, index=True)
    description: Mapped[str] = mapped_column(db.UnicodeText)
    position: Mapped[int]
    hide_if_empty: Mapped[bool]
    secret: Mapped[bool]

    def __init__(
        self,
        whereabouts_id: WhereaboutsID,
        party_id: PartyID,
        name: str,
        description: str,
        position: int,
        hide_if_empty: bool,
        secret: bool,
    ) -> None:
        self.id = whereabouts_id
        self.party_id = party_id
        self.name = name
        self.description = description
        self.position = position
        self.hide_if_empty = hide_if_empty
        self.secret = secret


class DbWhereaboutsUserSound(db.Model):
    """A user-specific salutation sound."""

    __tablename__ = 'whereabouts_user_sounds'

    user_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), primary_key=True
    )
    filename: Mapped[str] = mapped_column(db.UnicodeText)

    def __init__(self, user_id: UserID, filename: str) -> None:
        self.user_id = user_id
        self.filename = filename


class DbWhereaboutsStatus(db.Model):
    """A user's most recent whereabouts."""

    __tablename__ = 'whereabouts_statuses'

    user_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), primary_key=True, index=True
    )
    whereabouts_id: Mapped[WhereaboutsID] = mapped_column(
        db.Uuid, db.ForeignKey('whereabouts.id')
    )
    set_at: Mapped[datetime]

    def __init__(
        self, user_id: UserID, whereabouts_id: WhereaboutsID, set_at: datetime
    ) -> None:
        self.user_id = user_id
        self.whereabouts_id = whereabouts_id
        self.set_at = set_at


class DbWhereaboutsUpdate(db.Model):
    """An update on a user's whereabouts."""

    __tablename__ = 'whereabouts_updates'

    id: Mapped[UUID] = mapped_column(db.Uuid, primary_key=True)
    user_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), index=True
    )
    whereabouts_id: Mapped[WhereaboutsID] = mapped_column(
        db.Uuid, db.ForeignKey('whereabouts.id')
    )
    created_at: Mapped[datetime]
    _source_address: Mapped[Optional[str]] = mapped_column(  # noqa: UP007
        'source_address', postgresql.INET
    )

    def __init__(
        self,
        update_id: UUID,
        user_id: UserID,
        whereabouts_id: WhereaboutsID,
        created_at: datetime,
        source_address: IPAddress | None,
    ) -> None:
        self.id = update_id
        self.user_id = user_id
        self.whereabouts_id = whereabouts_id
        self.created_at = created_at
        self.source_address = source_address

    @hybrid_property
    def source_address(self) -> IPAddress | None:
        if not self._source_address:
            return None

        return ipaddress.ip_address(self._source_address)

    @source_address.setter
    def source_address(self, source_address: IPAddress | None) -> None:
        self._source_address = str(source_address) if source_address else None
