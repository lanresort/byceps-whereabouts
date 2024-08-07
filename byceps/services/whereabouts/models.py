"""
byceps.services.whereabouts.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from typing import NewType
from uuid import UUID

from byceps.services.party.models import Party
from byceps.services.user.models.user import User


WhereaboutsID = NewType('WhereaboutsID', UUID)


IPAddress = IPv4Address | IPv6Address


@dataclass(frozen=True)
class Whereabouts:
    id: WhereaboutsID
    party: Party
    name: str
    description: str
    position: int
    hide_if_empty: bool
    secret: bool


@dataclass(frozen=True)
class WhereaboutsUserSound:
    user: User
    filename: str


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
    source_address: IPAddress | None
