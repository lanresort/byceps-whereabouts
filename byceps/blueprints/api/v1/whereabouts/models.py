"""
byceps.blueprints.api.v1.whereabouts.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pydantic import BaseModel


class SetStatus(BaseModel):
    whereabouts_name: str
