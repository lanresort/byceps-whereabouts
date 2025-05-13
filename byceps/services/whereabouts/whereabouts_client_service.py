"""
byceps.services.whereabouts.whereabouts_client_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses

import structlog

from byceps.services.global_setting import global_setting_service
from byceps.services.user.models.user import User

from . import whereabouts_client_domain_service, whereabouts_client_repository
from .events import (
    WhereaboutsClientApprovedEvent,
    WhereaboutsClientRegisteredEvent,
    WhereaboutsClientDeletedEvent,
    WhereaboutsClientSignedOffEvent,
    WhereaboutsClientSignedOnEvent,
)
from .models import (
    IPAddress,
    WhereaboutsClient,
    WhereaboutsClientCandidate,
    WhereaboutsClientConfig,
    WhereaboutsClientID,
    WhereaboutsClientWithLivelinessStatus,
)


log = structlog.get_logger()


# -------------------------------------------------------------------- #
# client config


def create_client_config(
    title: str,
    description: str | None,
    content: str,
) -> WhereaboutsClientConfig:
    """Create a client configuration."""
    config = whereabouts_client_domain_service.create_client_config(
        title, description, content
    )

    whereabouts_client_repository.persist_client_config(config)

    return config


def get_all_client_configs() -> list[WhereaboutsClientConfig]:
    """Return all client configurations."""
    return whereabouts_client_repository.get_all_client_configs()


# -------------------------------------------------------------------- #
# client


GLOBAL_SETTINGS_KEY = 'whereabouts_client_registration_status'


def open_registration() -> None:
    """Open client registration."""
    global_setting_service.create_or_update_setting(GLOBAL_SETTINGS_KEY, 'open')


def close_registration() -> None:
    """Close client registration."""
    global_setting_service.create_or_update_setting(
        GLOBAL_SETTINGS_KEY, 'closed'
    )


def is_registration_open() -> bool:
    """Return `True` if client registration is open/allowed."""
    value = global_setting_service.find_setting_value(GLOBAL_SETTINGS_KEY)
    return value == 'open'


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

    whereabouts_client_repository.persist_client_registration(candidate)

    log.info(
        'Whereabouts client registered',
        button_count=candidate.button_count,
        audio_output=candidate.audio_output,
        id=str(candidate.id),
        source_address=str(source_address),
    )

    return candidate, event


def approve_client(
    candidate: WhereaboutsClientCandidate, initiator: User
) -> tuple[WhereaboutsClient, WhereaboutsClientApprovedEvent]:
    """Approve a client."""
    client, event = whereabouts_client_domain_service.approve_client(
        candidate, initiator
    )

    whereabouts_client_repository.persist_client_update(client)

    whereabouts_client_repository.initialize_liveliness_status(client)

    log.info(
        'Whereabouts client approved',
        id=str(client.id),
        approved_by=initiator.screen_name,
    )

    return client, event


def delete_client_candidate(client: WhereaboutsClient, initiator: User) -> None:
    """Delete a client candidate."""
    whereabouts_client_repository.delete_client_candidate(client)

    log.info(
        'Whereabouts client candidate deleted',
        id=str(client.id),
        deleted_by=initiator.screen_name,
    )


def update_client(
    client: WhereaboutsClient, location: str | None, description: str | None
) -> None:
    """Update a client."""
    updated_client = whereabouts_client_domain_service.update_client(
        client, location, description
    )

    whereabouts_client_repository.persist_client_update(updated_client)

    log.info('Whereabouts client updated', id=str(client.id))


def delete_client(
    client: WhereaboutsClient, initiator: User
) -> tuple[WhereaboutsClient, WhereaboutsClientDeletedEvent]:
    """Delete a client."""
    deleted_client, event = whereabouts_client_domain_service.delete_client(
        client, initiator
    )

    whereabouts_client_repository.persist_client_update(deleted_client)

    log.info(
        'Whereabouts client deleted',
        id=str(client.id),
        deleted_by=initiator.screen_name,
    )

    return deleted_client, event


def sign_on_client(
    client: WhereaboutsClient,
    *,
    source_address: IPAddress | None = None,
) -> WhereaboutsClientSignedOnEvent:
    """Sign on a client."""
    event = whereabouts_client_domain_service.sign_on_client(client)

    whereabouts_client_repository.update_liveliness_status(
        client.id, True, event.occurred_at
    )

    log.info(
        'Whereabouts client signed on',
        id=str(client.id),
        source_address=str(source_address),
    )

    return event


def sign_off_client(
    client: WhereaboutsClient,
    *,
    source_address: IPAddress | None = None,
) -> WhereaboutsClientSignedOffEvent:
    """Sign off a client."""
    event = whereabouts_client_domain_service.sign_off_client(client)

    whereabouts_client_repository.update_liveliness_status(
        client.id, False, event.occurred_at
    )

    log.info(
        'Whereabouts client signed off',
        id=str(client.id),
        source_address=str(source_address),
    )

    return event


def find_client(client_id: WhereaboutsClientID) -> WhereaboutsClient | None:
    """Return client, if found."""
    return whereabouts_client_repository.find_client(client_id)


def find_client_by_token(token: str) -> WhereaboutsClient | None:
    """Return client with that token, if found."""
    return whereabouts_client_repository.find_client_by_token(token)


def get_all_clients() -> list[WhereaboutsClientWithLivelinessStatus]:
    """Return all clients."""
    return whereabouts_client_repository.get_all_clients()
