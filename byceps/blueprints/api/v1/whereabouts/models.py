"""
byceps.blueprints.api.v1.whereabouts.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

from pydantic import BaseModel


class SetStatus(BaseModel):
    whereabouts_id: UUID
