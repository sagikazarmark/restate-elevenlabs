from datetime import timedelta

import restate

from .executor import Executor
from .model import (
    SpeechToTextConvertAsyncResponse,
    SpeechToTextConvertFileAsyncRequest,
    SpeechToTextConvertFileRequest,
    SpeechToTextConvertResponse,
    SpeechToTextConvertUrlAsyncRequest,
    SpeechToTextConvertUrlRequest,
)


def create_service(
    executor: Executor,
    service_name: str = "ElevenLabs",
    inactivity_timeout: timedelta | None = None,
    abort_timeout: timedelta | None = None,
) -> restate.Service:
    service = restate.Service(
        service_name,
        description="ElevenLabs service",
        inactivity_timeout=inactivity_timeout,
        abort_timeout=abort_timeout,
    )

    register_service(executor, service)

    return service


def register_service(
    executor: Executor,
    service: restate.Service,
):
    @service.handler("speechToTextConvertUrl")
    async def speech_to_text_convert_url(
        ctx: restate.Context,
        request: SpeechToTextConvertUrlRequest,
    ) -> SpeechToTextConvertResponse:
        return await ctx.run_typed(
            "speech_to_text_convert_url",
            executor.speech_to_text_convert_url,
            request=request,
        )

    @service.handler("speechToTextConvertUrlAsync")
    async def speech_to_text_convert_url_async(
        ctx: restate.Context,
        request: SpeechToTextConvertUrlAsyncRequest,
    ) -> SpeechToTextConvertAsyncResponse:
        return await ctx.run_typed(
            "speech_to_text_convert_url_async",
            executor.speech_to_text_convert_url_async,
            request=request,
        )

    @service.handler("speechToTextConvertFile")
    async def speech_to_text_convert_file(
        ctx: restate.Context,
        request: SpeechToTextConvertFileRequest,
    ) -> SpeechToTextConvertResponse:
        return await ctx.run_typed(
            "speech_to_text_convert_file",
            executor.speech_to_text_convert_file,
            request=request,
        )

    @service.handler("speechToTextConvertFileAsync")
    async def speech_to_text_convert_file_async(
        ctx: restate.Context,
        request: SpeechToTextConvertFileAsyncRequest,
    ) -> SpeechToTextConvertAsyncResponse:
        return await ctx.run_typed(
            "speech_to_text_convert_file_async",
            executor.speech_to_text_convert_file_async,
            request=request,
        )
