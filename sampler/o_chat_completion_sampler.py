import time
from typing import Any

import openai
from openai import OpenAI

from ..types import MessageList, SamplerResponse
from .base_with_retry import SamplerWithRetry

class OChatCompletionSampler(SamplerWithRetry):
    """
    Sample from OpenAI's chat completion API for o series models.
    Uses SamplerWithRetry for unified retry logic.
    """

    def __init__(
        self,
        *,
        reasoning_effort: str | None = None,
        model: str = "o1-mini",
    ):
        self.api_key_name = "OPENAI_API_KEY"
        self.client = OpenAI()
        self.model = model
        self.image_format = "url"
        self.reasoning_effort = reasoning_effort

    def _handle_image(
        self,
        image: str,
        encoding: str = "base64",
        format: str = "png",
        fovea: int = 768,
    ):
        new_image = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/{format};{encoding},{image}",
            },
        }
        return new_image

    def _handle_text(self, text: str):
        return {"type": "text", "text": text}

    def _pack_message(self, role: str, content: Any):
        return {"role": str(role), "content": content}

    def _sample(self, message_list: MessageList) -> SamplerResponse:
        try:
            kwargs = {
                "model": self.model,
                "messages": message_list,
            }
            if self.reasoning_effort:
                kwargs["reasoning_effort"] = self.reasoning_effort
                
            response = self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            
            return SamplerResponse(
                response_text=content,
                response_metadata={"usage": response.usage},
                actual_queried_message_list=message_list,
            )
        except openai.BadRequestError as e:
            # NOTE: BadRequestError is triggered once for MMMU
            print("Bad Request Error", e)
            return SamplerResponse(
                response_text="",
                response_metadata={"usage": None, "error": "bad_request"},
                actual_queried_message_list=message_list,
            )
        # Other exceptions will be caught by SamplerWithRetry
