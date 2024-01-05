"""
:Copyright: 2022-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from flask import Flask

from byceps.announce.announce import build_announcement_request
from byceps.events.base import EventParty
from byceps.events.whereabouts import WhereaboutsStatusUpdatedEvent

from .helpers import assert_text


def test_whereabouts_status_updated(
    app: Flask,
    now: datetime,
    party: EventParty,
    make_event_user,
    webhook_for_irc,
):
    expected_text = 'Dingo\'s whereabouts changed to "backstage area".'

    user = make_event_user(screen_name='Dingo')

    event = WhereaboutsStatusUpdatedEvent(
        occurred_at=now,
        initiator=user,
        party=party,
        user=user,
        whereabouts_description='backstage area',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)
