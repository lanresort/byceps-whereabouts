"""
byceps.blueprints.api.v1.whereabouts.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pydantic import BaseModel


class SetStatusRequestModel(BaseModel):
    user_id: str
    party_id: str
    whereabouts_name: str
