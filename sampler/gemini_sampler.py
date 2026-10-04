import os
import time
from typing import Any

from google import genai
from google.genai import types

from ..types import MessageList, SamplerResponse
from .base_with_retry import SamplerWithRetry

GEMINI_SYSTEM_MESSAGE_DEFAULT = "You are a helpful assistant."

class GeminiCompletionSampler(SamplerWithRetry):
    """
    Sample from Google's Gemini API using the new google-genai package.
    Uses SamplerWithRetry for unified retry logic.
    """

    def __init__(
        self,
        model: str = "gemini-1.5-pro",
        system_message: str | None = None,
        temperature: float | None = None,   # None なら送らない（API の既定に従う）
        max_tokens: int = 8192,
    ):
        self.api_key_name = "GEMINI_API_KEY"
        api_key = os.environ.get(self.api_key_name)
        if not api_key:
            print(f"Warning: {self.api_key_name} environment variable not set.")
        
        self.client = genai.Client()
        
        if model.startswith("models/"):
            self.model_name = model[7:]
        else:
            self.model_name = model
            
        self.system_message = system_message
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _convert_message_list(self, message_list: MessageList):
        contents = []
        for msg in message_list:
            role = msg["role"]
            if role == "assistant":
                role = "model"
            elif role == "system":
                continue
                
            msg_content = msg["content"]
            parts = []
            if isinstance(msg_content, str):
                parts.append(types.Part.from_text(text=msg_content))
            else:
                for item in msg_content:
                    if item["type"] == "text":
                        parts.append(types.Part.from_text(text=item["text"]))
            
            contents.append(types.Content(role=role, parts=parts))
            
        return contents

    def _sample(self, message_list: MessageList) -> SamplerResponse:
        sys_instruct = self.system_message
        sys_msgs = [m["content"] for m in message_list if m["role"] == "system"]
        if sys_msgs:
            if sys_instruct:
                sys_instruct = sys_instruct + "\n" + "\n".join(sys_msgs)
            else:
                sys_instruct = "\n".join(sys_msgs)

        cfg_kwargs = {}
        if self.temperature is not None:      # None のときは送らない（API の既定に従う）
            cfg_kwargs["temperature"] = self.temperature
        config = types.GenerateContentConfig(
            **cfg_kwargs,
            max_output_tokens=self.max_tokens,
            system_instruction=sys_instruct,
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="BLOCK_NONE",
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH",
                    threshold="BLOCK_NONE",
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="BLOCK_NONE",
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="BLOCK_NONE",
                ),
            ]
        )

        contents = self._convert_message_list(message_list)

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=config
        )
        
        # Handle blocked or empty responses
        if not response.text:
            candidate_info = str(response.candidates[0]) if response.candidates else "No candidates"
            fr = "UNKNOWN"
            if response.candidates and response.candidates[0].finish_reason:
                fr = str(response.candidates[0].finish_reason)
                
            # 空文字やブロックの場合は、リトライさせずに安全なプレースホルダーを返してループを完走させます
            print(f"Warning: Empty or blocked response detected ({fr}). Returning placeholder to avoid infinite retries.")
            return SamplerResponse(
                response_text=f"[BLOCKED OR EMPTY BY GEMINI: {fr}]",
                response_metadata={"error": "empty_or_blocked", "finish_reason": fr},
                actual_queried_message_list=message_list,
            )
            
        # finish_reason == MAX_TOKENS が打ち切り。件数を測定後に確認できるよう残す。
        finish_reason = None
        if response.candidates and response.candidates[0].finish_reason:
            finish_reason = str(response.candidates[0].finish_reason)
        return SamplerResponse(
            response_text=response.text,
            response_metadata={"stop_reason": finish_reason},
            actual_queried_message_list=message_list,
        )
