"""
byceps.events.whereabouts
~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from byceps.typing import PartyID, UserID

from .base import _BaseEvent


@dataclass(frozen=True)
class WhereaboutsUpdatedEvent(_BaseEvent):
    party_id: PartyID
    party_title: str
    user_id: UserID
    user_screen_name: str | None
    whereabouts_description: str
