"""
byceps.signals.whereabouts
~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from blinker import Namespace


whereabouts_signals = Namespace()


whereabouts_status_updated = whereabouts_signals.signal(
    'whereabouts-status-updated'
)
