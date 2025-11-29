import logging
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Optional, Protocol, TypeVar, cast

from elevenlabs import (
    ElevenLabs,
    SpeechToTextChunkResponseModel,
    SpeechToTextWebhookResponseModel,
)
from elevenlabs.core import ApiError
from pydantic import AnyUrl, BaseModel
from restate.exceptions import TerminalError

from .model import (
    SpeechToTextConvertAsyncResponse,
    SpeechToTextConvertFileAsyncRequest,
    SpeechToTextConvertFileRequest,
    SpeechToTextConvertRequestOutputMixin,
    SpeechToTextConvertResponse,
    SpeechToTextConvertUrlAsyncRequest,
    SpeechToTextConvertUrlRequest,
)

_logger = logging.getLogger(__name__)


class Loader(Protocol):
    def load(self, ref: AnyUrl | PurePosixPath, dst: Path): ...


class Persister(Protocol):
    def persist(
        self,
        ref: AnyUrl | PurePosixPath,
        src: bytes | bytearray | memoryview,
    ): ...


class Executor:
    def __init__(
        self,
        elevenlabs: ElevenLabs,
        loader: Loader,
        persister: Persister,
        logger: logging.Logger = _logger,
    ):
        self.elevenlabs = elevenlabs
        self.loader = loader
        self.persister = persister
        self.logger = logger

    def _handle_response(
        self,
        request: SpeechToTextConvertRequestOutputMixin,
        response: BaseModel,
    ) -> bool:
        return_ = (
            bool(request.output.destination)
            if request.output.return_ is None
            else request.output.return_
        )

        if request.output.destination:
            self.persister.persist(
                request.output.destination,
                response.model_dump_json(indent=4).encode(),
            )

        return return_

    def speech_to_text_convert_url(
        self, request: SpeechToTextConvertUrlRequest
    ) -> SpeechToTextConvertResponse:
        self.logger.info("Transcribing URL", extra={"url": str(request.url)})

        try:
            response = self.elevenlabs.speech_to_text.convert(
                cloud_storage_url=request.url,
                #
                model_id=request.options.model_id,
                enable_logging=request.options.enable_logging,
                language_code=optional(request.options.language_code),
                tag_audio_events=optional(request.options.tag_audio_events),
                num_speakers=optional(request.options.num_speakers),
                timestamps_granularity=optional(request.options.timestamps_granularity),
                diarize=optional(request.options.diarize),
                diarization_threshold=optional(request.options.diarization_threshold),
                additional_formats=optional(request.options.additional_formats),
                file_format=optional(request.options.file_format),
                temperature=optional(request.options.temperature),
                seed=optional(request.options.seed),
                # use_multi_channel=optional(request.options.use_multi_channel), # Multi channel response is not handled at the moment
                request_options=request.options.request_options,
            )
            assert isinstance(response, SpeechToTextChunkResponseModel)

            return_ = self._handle_response(request, response)

            if return_:
                return SpeechToTextConvertResponse.model_validate(response.model_dump())

            return SpeechToTextConvertResponse()
        except ApiError as err:
            if _is_terminal(err):
                raise _convert_api_error(err) from err

            raise err

    def speech_to_text_convert_url_async(
        self,
        request: SpeechToTextConvertUrlAsyncRequest,
    ) -> SpeechToTextConvertAsyncResponse:
        self.logger.info("Transcribing URL", extra={"url": str(request.url)})

        try:
            response = self.elevenlabs.speech_to_text.convert(
                cloud_storage_url=request.url,
                #
                webhook=True,
                webhook_id=request.options.webhook_id,
                webhook_metadata=request.options.webhook_metadata,
                #
                model_id=request.options.model_id,
                enable_logging=request.options.enable_logging,
                language_code=optional(request.options.language_code),
                tag_audio_events=optional(request.options.tag_audio_events),
                num_speakers=optional(request.options.num_speakers),
                timestamps_granularity=optional(request.options.timestamps_granularity),
                diarize=optional(request.options.diarize),
                diarization_threshold=optional(request.options.diarization_threshold),
                additional_formats=optional(request.options.additional_formats),
                file_format=optional(request.options.file_format),
                temperature=optional(request.options.temperature),
                seed=optional(request.options.seed),
                # use_multi_channel=optional(request.options.use_multi_channel), # Multi channel response is not handled at the moment
                request_options=request.options.request_options,
            )
            assert isinstance(response, SpeechToTextWebhookResponseModel)

            return SpeechToTextConvertAsyncResponse.model_validate(
                response.model_dump(),
            )
        except ApiError as err:
            if _is_terminal(err):
                raise _convert_api_error(err) from err

            raise err

    def speech_to_text_convert_file(
        self, request: SpeechToTextConvertFileRequest
    ) -> SpeechToTextConvertResponse:
        self.logger.info("Transcribing file", extra={"file": str(request.file)})

        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            self.loader.load(request.file, Path(temp_file.name))

            try:
                with open(temp_file.name, "rb") as file:
                    response = self.elevenlabs.speech_to_text.convert(
                        file=file,
                        #
                        model_id=request.options.model_id,
                        enable_logging=request.options.enable_logging,
                        language_code=optional(request.options.language_code),
                        tag_audio_events=optional(request.options.tag_audio_events),
                        num_speakers=optional(request.options.num_speakers),
                        timestamps_granularity=optional(
                            request.options.timestamps_granularity
                        ),
                        diarize=optional(request.options.diarize),
                        diarization_threshold=optional(
                            request.options.diarization_threshold
                        ),
                        additional_formats=optional(request.options.additional_formats),
                        file_format=optional(request.options.file_format),
                        temperature=optional(request.options.temperature),
                        seed=optional(request.options.seed),
                        # use_multi_channel=optional(request.options.use_multi_channel), # Multi channel response is not handled at the moment
                        request_options=request.options.request_options,
                    )
                    assert isinstance(response, SpeechToTextChunkResponseModel)

                    return_ = self._handle_response(request, response)

                    if return_:
                        return SpeechToTextConvertResponse.model_validate(
                            response.model_dump()
                        )

                    return SpeechToTextConvertResponse()
            except ApiError as err:
                if _is_terminal(err):
                    raise _convert_api_error(err) from err

                raise err

    def speech_to_text_convert_file_async(
        self,
        request: SpeechToTextConvertFileAsyncRequest,
    ) -> SpeechToTextConvertAsyncResponse:
        self.logger.info("Transcribing file", extra={"file": str(request.file)})

        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            self.loader.load(request.file, Path(temp_file.name))

            try:
                with open(temp_file.name, "rb") as file:
                    response = self.elevenlabs.speech_to_text.convert(
                        file=file,
                        #
                        webhook=True,
                        webhook_id=request.options.webhook_id,
                        webhook_metadata=request.options.webhook_metadata,
                        #
                        model_id=request.options.model_id,
                        enable_logging=request.options.enable_logging,
                        language_code=optional(request.options.language_code),
                        tag_audio_events=optional(request.options.tag_audio_events),
                        num_speakers=optional(request.options.num_speakers),
                        timestamps_granularity=optional(
                            request.options.timestamps_granularity
                        ),
                        diarize=optional(request.options.diarize),
                        diarization_threshold=optional(
                            request.options.diarization_threshold
                        ),
                        additional_formats=optional(request.options.additional_formats),
                        file_format=optional(request.options.file_format),
                        temperature=optional(request.options.temperature),
                        seed=optional(request.options.seed),
                        # use_multi_channel=optional(request.options.use_multi_channel), # Multi channel response is not handled at the moment
                        request_options=request.options.request_options,
                    )
                    assert isinstance(response, SpeechToTextWebhookResponseModel)

                return SpeechToTextConvertAsyncResponse.model_validate(
                    response.model_dump(),
                )
            except ApiError as err:
                if _is_terminal(err):
                    raise _convert_api_error(err) from err

                raise err


T = TypeVar("T")

OMIT = cast(Any, ...)


def optional(value: T | None) -> T | Optional[T]:
    return OMIT if value is None else value


def _is_terminal(err: ApiError) -> bool:
    # TODO: this should be better
    return err.status_code == 400


def _convert_api_error(err: ApiError) -> TerminalError:
    if isinstance(err.body, dict):
        msg = err.body.get("detail", {}).get("message", err.body)
    else:
        msg = f"{err.body}"

    return TerminalError(
        msg,
        status_code=err.status_code or 500,
    )
