"""
byceps.services.whereabouts.whereabouts_client_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from sqlalchemy import select
import structlog

from byceps.database import db
from byceps.events.whereabouts import (
    WhereaboutsClientApprovedEvent,
    WhereaboutsClientRegisteredEvent,
    WhereaboutsClientDeletedEvent,
)
from byceps.services.user.models.user import User

from . import whereabouts_client_domain_service
from .dbmodels import DbWhereaboutsClient
from .models import (
    IPAddress,
    WhereaboutsClient,
    WhereaboutsClientAuthorityStatus,
    WhereaboutsClientCandidate,
    WhereaboutsClientID,
)


log = structlog.get_logger()


# -------------------------------------------------------------------- #
# client


def register_client(
    button_count: int,
    audio_output: bool,
    *,
    source_address: IPAddress | None = None,
) -> tuple[WhereaboutsClientCandidate, WhereaboutsClientRegisteredEvent]:
    """Register a client."""
    candidate, event = whereabouts_client_domain_service.register_client(
        button_count, audio_output
    )

    _persist_client_registration(candidate)

    log.info(
        'Whereabouts client registered',
        button_count=candidate.button_count,
        audio_output=candidate.audio_output,
        id=str(candidate.id),
        source_address=str(source_address),
    )

    return candidate, event


def _persist_client_registration(candidate: WhereaboutsClientCandidate) -> None:
    db_client = DbWhereaboutsClient(
        candidate.id,
        candidate.registered_at,
        candidate.button_count,
        candidate.audio_output,
        WhereaboutsClientAuthorityStatus.pending,
    )

    db.session.add(db_client)
    db.session.commit()


def approve_client(
    candidate: WhereaboutsClientCandidate, initiator: User
) -> tuple[WhereaboutsClient, WhereaboutsClientApprovedEvent]:
    """Approve a client."""
    client, event = whereabouts_client_domain_service.approve_client(
        candidate, initiator
    )

    _persist_client_update(client)

    log.info(
        'Whereabouts client approved',
        id=str(client.id),
        approved_by=initiator.screen_name,
    )

    return client, event


def delete_client_candidate(client: WhereaboutsClient, initiator: User) -> None:
    """Delete a client candidate."""
    if client.approved:
        raise ValueError('An approved client must not be deleted')

    db_client = get_db_client(client.id)

    db.session.delete(db_client)
    db.session.commit()

    log.info(
        'Whereabouts client candidate deleted',
        id=str(client.id),
        deleted_by=initiator.screen_name,
    )


def update_client(
    client: WhereaboutsClient, location: str | None, description: str | None
) -> None:
    """Update a client."""
    db_client = get_db_client(client.id)

    db_client.location = location
    db_client.description = description

    db.session.commit()


def delete_client(
    client: WhereaboutsClient, initiator: User
) -> tuple[WhereaboutsClient, WhereaboutsClientDeletedEvent]:
    """Delete a client."""
    deleted_client, event = whereabouts_client_domain_service.delete_client(
        client, initiator
    )

    _persist_client_update(deleted_client)

    log.info(
        'Whereabouts client deleted',
        id=str(client.id),
        deleted_by=initiator.screen_name,
    )

    return deleted_client, event


def _persist_client_update(updated_client: WhereaboutsClient) -> None:
    db_client = get_db_client(updated_client.id)

    db_client.authority_status = updated_client.authority_status
    db_client.token = updated_client.token

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


def get_all_clients() -> list[WhereaboutsClient]:
    """Return all clients."""
    db_clients = db.session.execute(select(DbWhereaboutsClient)).all()

    return [_db_entity_to_client(db_client) for db_client in db_clients]


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
    )
