"""
byceps.services.whereabouts.whereabouts_client_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses
from datetime import datetime

from sqlalchemy import select

from byceps.database import db

from .dbmodels import (
    DbWhereaboutsClient,
    DbWhereaboutsClientConfig,
    DbWhereaboutsClientLivelinessStatus,
)
from .models import (
    WhereaboutsClient,
    WhereaboutsClientAuthorityStatus,
    WhereaboutsClientCandidate,
    WhereaboutsClientConfig,
    WhereaboutsClientID,
    WhereaboutsClientWithLivelinessStatus,
)


# -------------------------------------------------------------------- #
# client config


def persist_client_config(config: WhereaboutsClientConfig) -> None:
    """Persist client configurations."""
    db_config = DbWhereaboutsClientConfig(
        config.id,
        config.title,
        config.description,
        config.content,
    )

    db.session.add(db_config)
    db.session.commit()


def get_all_client_configs() -> list[WhereaboutsClientConfig]:
    """Return all client configurations."""
    db_configs = db.session.scalars(select(DbWhereaboutsClientConfig)).all()

    return [_db_entity_to_client_config(db_config) for db_config in db_configs]


def _db_entity_to_client_config(
    db_config: DbWhereaboutsClientConfig,
) -> WhereaboutsClientConfig:
    return WhereaboutsClientConfig(
        id=db_config.id,
        title=db_config.title,
        description=db_config.description,
        content=db_config.content,
    )


# -------------------------------------------------------------------- #
# client


def persist_client_registration(candidate: WhereaboutsClientCandidate) -> None:
    """Persist client registration."""
    db_client = DbWhereaboutsClient(
        candidate.id,
        candidate.registered_at,
        candidate.button_count,
        candidate.audio_output,
        WhereaboutsClientAuthorityStatus.pending,
        candidate.token,
    )

    db.session.add(db_client)
    db.session.commit()


def delete_client_candidate(client: WhereaboutsClient) -> None:
    """Delete a client candidate."""
    if client.approved:
        raise ValueError('An approved client must not be deleted')

    db_client = get_db_client(client.id)

    db.session.delete(db_client)
    db.session.commit()


def persist_client_update(client: WhereaboutsClient) -> None:
    """Update a client."""
    db_client = get_db_client(client.id)

    db_client.authority_status = client.authority_status
    db_client.token = client.token
    db_client.location = client.location
    db_client.description = client.description

    db.session.commit()


def initialize_liveliness_status(client: WhereaboutsClient) -> None:
    """Initialize liveliness status for a client."""
    db_liveliness_status = DbWhereaboutsClientLivelinessStatus(
        client_id=client.id,
        signed_on=False,
        latest_activity_at=client.registered_at,
    )

    db.session.add(db_liveliness_status)
    db.session.commit()


def update_liveliness_status(
    client_id: WhereaboutsClientID,
    signed_on: bool,
    latest_activity_at: datetime,
) -> None:
    """Update liveliness status for a client."""
    db_liveliness_status = db.session.get(
        DbWhereaboutsClientLivelinessStatus, client_id
    )

    if db_liveliness_status is None:
        raise ValueError(f'Unknown client ID: {client_id}')

    db_liveliness_status.signed_on = signed_on
    db_liveliness_status.latest_activity_at = latest_activity_at

    db.session.commit()


def find_db_client(
    client_id: WhereaboutsClientID,
) -> DbWhereaboutsClient | None:
    """Return client, if found."""
    db_client = db.session.get(DbWhereaboutsClient, client_id)

    if db_client is None:
        return None

    return db_client


def get_db_client(client_id: WhereaboutsClientID) -> DbWhereaboutsClient:
    """Return client, or raise exception if not found."""
    db_client = find_db_client(client_id)

    if db_client is None:
        raise ValueError(f'Unknown client ID: {client_id}')

    return db_client


def find_client(client_id: WhereaboutsClientID) -> WhereaboutsClient | None:
    """Return client, if found."""
    db_client = find_db_client(client_id)

    if db_client is None:
        return None

    return _db_entity_to_client(db_client)


def find_client_by_token(token: str) -> WhereaboutsClient | None:
    """Return client with that token, if found."""
    db_client = db.session.scalars(
        select(DbWhereaboutsClient).filter_by(token=token)
    ).one_or_none()

    if db_client is None:
        return None

    return _db_entity_to_client(db_client)


def get_all_clients() -> list[WhereaboutsClientWithLivelinessStatus]:
    """Return all clients."""
    db_clients_with_liveliness_status = db.session.execute(
        select(DbWhereaboutsClient, DbWhereaboutsClientLivelinessStatus).join(
            DbWhereaboutsClientLivelinessStatus, isouter=True
        )
    ).all()

    return [
        _db_entity_to_client_with_liveliness_status(
            db_client, db_liveliness_status
        )
        for db_client, db_liveliness_status in db_clients_with_liveliness_status
    ]


def _db_entity_to_client(db_client: DbWhereaboutsClient) -> WhereaboutsClient:
    return WhereaboutsClient(
        id=db_client.id,
        registered_at=db_client.registered_at,
        button_count=db_client.button_count,
        audio_output=db_client.audio_output,
        authority_status=db_client.authority_status,
        token=db_client.token,
        location=db_client.location,
        description=db_client.description,
        config_id=db_client.config_id,
    )


def _db_entity_to_client_with_liveliness_status(
    db_client: DbWhereaboutsClient,
    db_liveliness_status: DbWhereaboutsClientLivelinessStatus,
) -> WhereaboutsClientWithLivelinessStatus:
    client = _db_entity_to_client(db_client)

    signed_on = (
        db_liveliness_status.signed_on if db_liveliness_status else False
    )

    latest_activity_at = (
        db_liveliness_status.latest_activity_at
        if db_liveliness_status
        else client.registered_at
    )

    return WhereaboutsClientWithLivelinessStatus(
        **dataclasses.asdict(client),
        signed_on=signed_on,
        latest_activity_at=latest_activity_at,
    )
