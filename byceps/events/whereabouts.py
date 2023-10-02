"""
byceps.events.whereabouts
~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from byceps.services.party.models import PartyID
from byceps.services.user.models.user import UserID

from .base import _BaseEvent


@dataclass(frozen=True)
class WhereaboutsTagCreatedEvent(_BaseEvent):
    tag: str
    user_id: UserID
    user_screen_name: str | None


@dataclass(frozen=True)
class WhereaboutsStatusUpdatedEvent(_BaseEvent):
    party_id: PartyID
    party_title: str
    user_id: UserID
    user_screen_name: str | None
    whereabouts_description: str
