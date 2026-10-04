import os
import time
from typing import Any

import openai
from openai import OpenAI

from ..types import MessageList, SamplerResponse
from .base_with_retry import SamplerWithRetry

class ResponsesSampler(SamplerWithRetry):
    """
    Sample from OpenAI's responses API.
    Uses SamplerWithRetry for unified retry logic.
    """

    def __init__(
        self,
        model: str = "gpt-4.1",
        system_message: str | None = None,
        temperature: float | None = None,   # None なら送らない（API の既定に従う）
        max_tokens: int = 1024,
        reasoning_model: bool = False,
        reasoning_effort: str | None = None,
    ):
        self.api_key_name = "OPENAI_API_KEY"
        assert os.environ.get("OPENAI_API_KEY"), "Please set OPENAI_API_KEY"
        self.client = OpenAI()
        self.model = model
        self.system_message = system_message
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.image_format = "url"
        self.reasoning_model = reasoning_model
        self.reasoning_effort = reasoning_effort

    def _handle_image(
        self,
        image: str,
        encoding: str = "base64",
        format: str = "png",
        fovea: int = 768,
    ) -> dict[str, Any]:
        new_image = {
            "type": "input_image",
            "image_url": f"data:image/{format};{encoding},{image}",
        }
        return new_image

    def _handle_text(self, text: str) -> dict[str, Any]:
        return {"type": "input_text", "text": text}

    def _pack_message(self, role: str, content: Any) -> dict[str, Any]:
        return {"role": role, "content": content}

    def _sample(self, message_list: MessageList) -> SamplerResponse:
        full_message_list = message_list
        if self.system_message:
            full_message_list = [
                self._pack_message("developer", self.system_message)
            ] + message_list
            
        try:
            # Construct API parameters
            kwargs = {
                "model": self.model,
                "input": full_message_list,
                "max_output_tokens": self.max_tokens,
            }

            # Add reasoning parameters for reasoning models
            if self.reasoning_model:
                if self.reasoning_effort:
                    kwargs["reasoning"] = {"effort": self.reasoning_effort}

            # Temperature is not supported by gpt-5/o1/o3/o4
            if (
                self.temperature is not None
                and not self.model.startswith(("gpt-5", "o1", "o3", "o4"))
            ):
                kwargs["temperature"] = self.temperature

            response = self.client.responses.create(**kwargs)                
            # status == "incomplete" かつ incomplete_details.reason == "max_output_tokens"
            # が打ち切り。件数を測定後に確認できるよう残す。
            incomplete = getattr(response, "incomplete_details", None)
            return SamplerResponse(
                response_text=response.output_text,
                response_metadata={
                    "usage": response.usage,
                    "stop_reason": getattr(response, "status", None),
                    "incomplete_reason": getattr(incomplete, "reason", None),
                },
                actual_queried_message_list=full_message_list,
            )
        except openai.BadRequestError as e:
            # Special handling for BadRequestError (e.g., content filter)
            # We return an empty response instead of retrying
            print("Bad Request Error", e)
            return SamplerResponse(
                response_text="",
                response_metadata={"usage": None, "error": "bad_request"},
                actual_queried_message_list=full_message_list,
            )
        # Other exceptions (RateLimit, Connection, etc.) will be caught by SamplerWithRetry
