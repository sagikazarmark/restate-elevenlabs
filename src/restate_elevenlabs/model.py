from pathlib import PurePosixPath
from typing import Any, Dict, List

from elevenlabs import (
    AdditionalFormatResponseModel,
    AdditionalFormats,
    SpeechToTextConvertRequestFileFormat,
    SpeechToTextConvertRequestTimestampsGranularity,
    SpeechToTextWordResponseModel,
)
from elevenlabs.core import RequestOptions
from pydantic import AnyUrl, BaseModel, ConfigDict, Field


class SpeechToTextConvertRequestOutput(BaseModel):
    destination: AnyUrl | PurePosixPath | None = Field(
        default=None,
        description="The destination of the transcription file",
        union_mode="left_to_right",  # This is important to keep best match order (TODO: consider using a custom discriminator)
    )

    return_: bool | None = Field(
        alias="return",
        default=None,
        description="Whether to return the transcription",
    )


class SpeechToTextConvertRequestOutputMixin:
    output: SpeechToTextConvertRequestOutput = Field(
        default_factory=SpeechToTextConvertRequestOutput,
        description="Output configuration",
    )


class SpeechToTextConvertRequestOptions(BaseModel):
    model_id: str = Field(
        ...,
        description="The ID of the model to use for transcription, currently only 'scribe_v1' and 'scribe_v1_experimental' are available.",
    )

    enable_logging: bool | None = Field(
        default=None,
        description="When enable_logging is set to false zero retention mode will be used for the request. This will mean log and transcript storage features are unavailable for this request. Zero retention mode may only be used by enterprise customers.",
    )

    language_code: str | None = Field(
        default=None,
        description="An ISO-639-1 or ISO-639-3 language_code corresponding to the language of the audio file. Can sometimes improve transcription performance if known beforehand. Defaults to null, in this case the language is predicted automatically.",
    )

    tag_audio_events: bool | None = Field(
        default=None,
        description="Whether to tag audio events like (laughter), (footsteps), etc. in the transcription.",
    )

    num_speakers: int | None = Field(
        default=None,
        description="The maximum amount of speakers talking in the uploaded file. Can help with predicting who speaks when. The maximum amount of speakers that can be predicted is 32. Defaults to null, in this case the amount of speakers is set to the maximum value the model supports.",
    )

    timestamps_granularity: SpeechToTextConvertRequestTimestampsGranularity | None = (
        Field(
            default=None,
            description="The granularity of the timestamps in the transcription. 'word' provides word-level timestamps and 'character' provides character-level timestamps per word.",
        )
    )

    diarize: bool | None = Field(
        default=None,
        description="Whether to annotate which speaker is currently talking in the uploaded file.",
    )

    diarization_threshold: float | None = Field(
        default=None,
        description="Diarization threshold to apply during speaker diarization. A higher value means there will be a lower chance of one speaker being diarized as two different speakers but also a higher chance of two different speakers being diarized as one speaker (less total speakers predicted). A low value means there will be a higher chance of one speaker being diarized as two different speakers but also a lower chance of two different speakers being diarized as one speaker (more total speakers predicted). Can only be set when diarize=True and num_speakers=None. Defaults to None, in which case we will choose a threshold based on the model_id (0.22 usually).",
    )

    additional_formats: AdditionalFormats | None = Field(
        default=None,
        description="A list of additional formats to export the transcript to.",
    )

    file_format: SpeechToTextConvertRequestFileFormat | None = Field(
        default=None,
        description="The format of input audio. Options are 'pcm_s16le_16' or 'other' For `pcm_s16le_16`, the input audio must be 16-bit PCM at a 16kHz sample rate, single channel (mono), and little-endian byte order. Latency will be lower than with passing an encoded waveform.",
    )

    temperature: float | None = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="Controls the randomness of the transcription output. Accepts values between 0.0 and 2.0, where higher values result in more diverse and less deterministic results. If omitted, we will use a temperature based on the model you selected which is usually 0.",
    )

    seed: int | None = Field(
        default=None,
        ge=0,
        le=2147483647,
        description="If specified, our system will make a best effort to sample deterministically, such that repeated requests with the same seed and parameters should return the same result. Determinism is not guaranteed. Must be an integer between 0 and 2147483647.",
    )

    use_multi_channel: bool | None = Field(
        default=None,
        description="Whether the audio file contains multiple channels where each channel contains a single speaker. When enabled, each channel will be transcribed independently and the results will be combined. Each word in the response will include a 'channel_index' field indicating which channel it was spoken on. A maximum of 5 channels is supported.",
    )

    request_options: RequestOptions | None = Field(
        default=None, description="Request-specific configuration."
    )


class SpeechToTextConvertAsyncRequestOptions(SpeechToTextConvertRequestOptions):
    webhook_id: str | None = Field(
        default=None,
        description="Optional specific webhook ID to send the transcription result to. Only valid when webhook is set to true. If not provided, transcription will be sent to all configured speech-to-text webhooks.",
    )

    webhook_metadata: str | Dict[str, Any] | None = Field(
        default=None,
        description="Optional metadata to be included in the webhook response. This should be a JSON string representing an object with a maximum depth of 2 levels and maximum size of 16KB. Useful for tracking internal IDs, job references, or other contextual information.",
    )


class SpeechToTextConvertUrlRequestMixin(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "url": "https://example.com/audio.wav",
                    "options": {
                        "model_id": "scribe_v1",
                    },
                },
            ]
        }
    )

    url: str = Field(
        description="The HTTPS URL of the file to transcribe. URLs can be pre-signed or include authentication tokens in query parameters.",
    )


class SpeechToTextConvertUrlRequest(
    SpeechToTextConvertUrlRequestMixin,
    SpeechToTextConvertRequestOutputMixin,
):
    options: SpeechToTextConvertRequestOptions = Field(
        description="Transcription options",
    )


class SpeechToTextConvertUrlAsyncRequest(
    SpeechToTextConvertUrlRequestMixin,
    SpeechToTextConvertRequestOutputMixin,
):
    options: SpeechToTextConvertAsyncRequestOptions = Field(
        description="Transcription options",
    )


class SpeechToTextConvertFileRequestMixin(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "file": "s3://bucket/audio.wav",
                    "options": {
                        "model_id": "scribe_v1",
                    },
                },
            ]
        }
    )

    file: AnyUrl | PurePosixPath = Field(
        description="The audio file to transcribe",
        union_mode="left_to_right",  # This is important to keep best match order (TODO: consider using a custom discriminator)
    )


class SpeechToTextConvertFileRequest(
    SpeechToTextConvertFileRequestMixin,
    SpeechToTextConvertRequestOutputMixin,
):
    options: SpeechToTextConvertRequestOptions = Field(
        description="Transcription options",
    )


class SpeechToTextConvertFileAsyncRequest(
    SpeechToTextConvertFileRequestMixin,
    SpeechToTextConvertRequestOutputMixin,
):
    options: SpeechToTextConvertAsyncRequestOptions = Field(
        description="Transcription options",
    )


# AdditionalFormatResponseModel.is_base_64_encoded = Field(alias="is_base64_encoded")
# AdditionalFormatResponseModel.model_rebuild()

# AdditionalFormatResponseModel.model_fields["is_base_64_encoded"] = (
#     pydantic.fields.FieldInfo(alias="is_base64_encoded", default=False)
# )
# AdditionalFormatResponseModel.model_rebuild()


# https://github.com/elevenlabs/elevenlabs-python/issues/694
class SpeechToTextConvertResponseAdditionalFormat(AdditionalFormatResponseModel):
    is_base_64_encoded: bool = Field(
        default=False,
        alias="is_base64_encoded",
    )


class SpeechToTextConvertResponse(BaseModel):
    language_code: str | None = Field(
        default=None,
        description="The detected language code (e.g. 'eng' for English).",
    )

    language_probability: float | None = Field(
        default=None,
        description="The confidence score of the language detection (0 to 1).",
    )

    text: str | None = Field(
        default=None,
        description="The raw text of the transcription.",
    )

    words: List[SpeechToTextWordResponseModel] | None = Field(
        default=None,
        description="List of words with their timing information.",
    )

    channel_index: int | None = Field(
        default=None,
        description="The channel index this transcript belongs to (for multichannel audio).",
    )

    additional_formats: (
        List[SpeechToTextConvertResponseAdditionalFormat | None] | None
    ) = Field(
        default=None,
        description="Requested additional formats of the transcript.",
    )

    transcription_id: str | None = Field(
        default=None,
        description="The transcription ID of the response.",
    )


class SpeechToTextConvertAsyncResponse(BaseModel):
    message: str = Field(description="The message of the webhook response.")

    request_id: str = Field(description="The request ID of the webhook response.")

    transcription_id: str | None = Field(
        default=None,
        description="The transcription ID of the webhook response.",
    )
