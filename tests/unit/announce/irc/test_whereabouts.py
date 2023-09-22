"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.announce.announce import build_announcement_request
from byceps.events.whereabouts import WhereaboutsUpdatedEvent
from byceps.typing import PartyID, UserID

from tests.helpers import generate_uuid

from .helpers import assert_text, now


OCCURRED_AT = now()
USER_ID = UserID(generate_uuid())


def test_whereabouts_updated(app: Flask, webhook_for_irc):
    expected_text = 'Dingo\'s whereabouts changed to "backstage area".'

    event = WhereaboutsUpdatedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=USER_ID,
        initiator_screen_name='Dingo',
        party_id=PartyID('acmecon-2014'),
        party_title='ACMECon 2014',
        user_id=USER_ID,
        user_screen_name='Dingo',
        whereabouts_description='backstage area',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)
