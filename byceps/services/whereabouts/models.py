"""
byceps.services.whereabouts.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import NewType
from uuid import UUID

from byceps.typing import PartyID, UserID


WhereaboutsID = NewType('WhereaboutsID', UUID)


@dataclass(frozen=True)
class Whereabouts:
    id: WhereaboutsID
    party_id: PartyID
    description: str
    position: int
    hide_if_empty: bool


@dataclass(frozen=True)
class WhereaboutsStatus:
    user_id: UserID
    whereabouts_id: WhereaboutsID
    set_at: datetime


@dataclass(frozen=True)
class WhereaboutsUpdate:
    id: UUID
    user_id: UserID
    whereabouts_id: WhereaboutsID
    created_at: datetime
