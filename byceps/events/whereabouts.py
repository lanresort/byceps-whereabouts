"""
byceps.events.whereabouts
~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from .base import _BaseEvent, EventParty, EventUser


@dataclass(frozen=True)
class WhereaboutsStatusUpdatedEvent(_BaseEvent):
    party: EventParty
    user: EventUser
    whereabouts_description: str
