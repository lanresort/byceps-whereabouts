"""
byceps.services.whereabouts.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import NewType
from uuid import UUID

from byceps.services.party.models import Party
from byceps.services.user.models.user import User


WhereaboutsID = NewType('WhereaboutsID', UUID)


@dataclass(frozen=True)
class Whereabouts:
    id: WhereaboutsID
    party: Party
    description: str
    position: int
    hide_if_empty: bool
    secret: bool


@dataclass(frozen=True)
class WhereaboutsTag:
    id: UUID
    tag: str
    user: User
    sound_filename: str | None
    suspended: bool


@dataclass(frozen=True)
class WhereaboutsStatus:
    user: User
    whereabouts_id: WhereaboutsID
    set_at: datetime


@dataclass(frozen=True)
class WhereaboutsUpdate:
    id: UUID
    user: User
    whereabouts_id: WhereaboutsID
    created_at: datetime
