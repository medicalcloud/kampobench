import time
import os

import anthropic

from ..types import MessageList, SamplerResponse
from .. import common
from .base_with_retry import SamplerWithRetry

CLAUDE_SYSTEM_MESSAGE_LMSYS = (
    "The assistant is Claude, created by Anthropic. The current date is "
    "{currentDateTime}. Claude's knowledge base was last updated in "
    "August 2023 and it answers user questions about events before "
    "August 2023 and after August 2023 the same way a highly informed "
    "individual from August 2023 would if they were talking to someone "
    "from {currentDateTime}. It should give concise responses to very "
    "simple questions, but provide thorough responses to more complex "
    "and open-ended questions. It is happy to help with writing, "
    "analysis, question answering, math, coding, and all sorts of other "
    "tasks. It uses markdown for coding. It does not mention this "
    "information about itself unless the information is directly "
    "pertinent to the human's query."
).format(currentDateTime="2024-04-01")

class ClaudeCompletionSampler(SamplerWithRetry):
    """
    Sample from Anthropic's Claude API.
    Uses SamplerWithRetry for unified retry logic.
    """

    def __init__(
        self,
        model: str,
        system_message: str | None = None,
        temperature: float | None = None,  # None なら送らない（API の既定に従う）
        max_tokens: int = 4096,
    ):
        self.client = anthropic.Anthropic()
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.model = model
        self.system_message = system_message
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.image_format = "base64"

    def _handle_image(
        self,
        image: str,
        encoding: str = "base64",
        format: str = "png",
        fovea: int = 768,
    ):
        new_image = {
            "type": "image",
            "source": {
                "type": encoding,
                "media_type": f"image/{format}",
                "data": image,
            },
        }
        return new_image

    def _handle_text(self, text):
        return {"type": "text", "text": text}

    def _pack_message(self, role, content):
        return {"role": str(role), "content": content}

    def _sample(self, message_list: MessageList) -> SamplerResponse:
        if not common.has_only_user_assistant_messages(message_list):
            raise ValueError(f"Claude sampler only supports user and assistant messages, got {message_list}")
            
        claude_input_messages: MessageList = message_list
        # 新しいモデルは temperature を受け付けない
        # （`temperature` is deprecated for this model.）。
        # その場合は temperature=None を指定し、リクエストから省く。
        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": message_list,
        }
        if self.temperature is not None:
            kwargs["temperature"] = self.temperature
        if self.system_message:
            response_message = self.client.messages.create(
                system=self.system_message, **kwargs  # type: ignore[arg-type]
            )
            claude_input_messages = [{"role": "system", "content": self.system_message}] + message_list
        else:
            response_message = self.client.messages.create(**kwargs)  # type: ignore[arg-type]
            
        text_blocks = [
            block.text  # type: ignore[union-attr]
            for block in response_message.content
            if hasattr(block, "text")
        ]
        
        response_text = "".join(text_blocks) if text_blocks else "[EMPTY RESPONSE FROM CLAUDE]"
        
        return SamplerResponse(
            response_text=response_text,
            # stop_reason == "max_tokens" は出力が打ち切られたことを示す。
            # 網羅性を問う採点で不利に働くため、測定後に件数を確認できるよう残す。
            response_metadata={
                "stop_reason": response_message.stop_reason,
                "usage": response_message.usage,
            },
            actual_queried_message_list=claude_input_messages,
        )
