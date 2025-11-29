from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING, cast

import obstore
import pydantic_obstore
import restate
import structlog
import workstate
import workstate.obstore
from elevenlabs import ElevenLabs
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .restate_elevenlabs import Executor, create_service

if TYPE_CHECKING:
    from obstore.store import ClientConfig


class ObstoreSettings(pydantic_obstore.Config):
    url: str | None = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")  # pyright: ignore[reportUnannotatedClassAttribute]

    obstore: ObstoreSettings = Field(default_factory=ObstoreSettings)

    service_name: str = "ElevenLabs"

    inactivity_timeout: timedelta | None = Field(
        alias="restate_inactivity_timeout",
        default=timedelta(minutes=10),
    )
    abort_timeout: timedelta | None = Field(alias="restate_abort_timeout", default=None)
    identity_keys: list[str] = Field(alias="restate_identity_keys", default=[])


settings = Settings()  # pyright: ignore[reportCallIssue]

# logging.basicConfig(level=logging.INFO)
structlog.stdlib.recreate_defaults(log_level=logging.INFO)

store: obstore.store.ObjectStore | None = None
client_options: ClientConfig | None = None

if settings.obstore.client_options:
    client_options = cast(
        "ClientConfig",
        settings.obstore.client_options.model_dump(exclude_none=True),
    )

if settings.obstore.url:
    store = obstore.store.from_url(settings.obstore.url, client_options=client_options)

loader = workstate.obstore.FileLoader(
    store,
    client_options=client_options,
    logger=structlog.get_logger("workstate"),
)

persister = workstate.obstore.FilePersister(
    store,
    client_options=client_options,
    logger=structlog.get_logger("workstate"),
)

executor = Executor(
    ElevenLabs(),
    loader,
    persister,
    logger=structlog.get_logger("elevenlabs"),
)

service = create_service(
    executor,
    service_name=settings.service_name,
    inactivity_timeout=settings.inactivity_timeout,
    abort_timeout=settings.abort_timeout,
)

app = restate.app(services=[service], identity_keys=settings.identity_keys)
