# accounts/services/llm_service.py
"""
Unified LLM Service — Routes text/chat completions to OpenAI or Gemini.

Usage:
    from accounts.services.llm_service import get_llm_service

    service = get_llm_service(request.user)
    result = service.chat_completion(
        messages=[
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello!"},
        ],
        temperature=0.7,
        max_tokens=500,
    )
    if result.success:
        text = result.content
"""

import logging
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

import requests as http_requests

logger = logging.getLogger(__name__)


# ── Model Mapping ──────────────────────────────────────────────────

OPENAI_TO_GEMINI = {
    'gpt-4o': 'gemini-2.0-flash',
    'gpt-4o-mini': 'gemini-2.0-flash-lite',
    'gpt-4-turbo': 'gemini-1.5-pro',
}

GEMINI_TO_OPENAI = {v: k for k, v in OPENAI_TO_GEMINI.items()}


# ── Normalised Response ────────────────────────────────────────────

@dataclass
class LLMResponse:
    """Provider-agnostic response from any LLM."""
    success: bool
    content: str = ''
    model: str = ''
    provider: str = ''
    tokens_used: int = 0
    finish_reason: str = ''
    error: str = ''
    raw_response: Any = None


# ── Unified Service ────────────────────────────────────────────────

class UnifiedLLMService:
    """
    Accepts OpenAI-format messages and routes to the user's preferred provider.
    Handles model mapping, message format conversion, JSON mode, and vision.
    """

    def __init__(
        self,
        openai_key: Optional[str] = None,
        gemini_key: Optional[str] = None,
        preferred_provider: str = 'openai',
        openai_model: str = 'gpt-4o-mini',
        gemini_model: str = 'gemini-2.0-flash',
    ):
        self.openai_key = openai_key
        self.gemini_key = gemini_key
        self.preferred_provider = preferred_provider
        self.openai_model = openai_model
        self.gemini_model = gemini_model

    # ── Public API ─────────────────────────────────────────────────

    def chat_completion(
        self,
        messages: List[Dict],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        response_format: Optional[Dict] = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Main entry point.  Accepts OpenAI-format messages list.

        Args:
            messages:  [{"role": "system"|"user"|"assistant", "content": str|list}]
            model:     Requested model (auto-mapped to active provider)
            temperature, max_tokens:  Generation parameters
            response_format:  {"type": "json_object"} to enable JSON mode
            **kwargs:  Extra provider-specific params forwarded to OpenAI only
        """
        provider = self._resolve_provider()
        if not provider:
            return LLMResponse(
                success=False,
                error='No AI API key configured. Go to Settings to add your OpenAI or Gemini key.',
            )

        resolved_model = self._resolve_model(provider, model)

        if provider == 'openai':
            return self._openai_completion(
                messages, resolved_model, temperature, max_tokens,
                response_format, **kwargs,
            )
        return self._gemini_completion(
            messages, resolved_model, temperature, max_tokens,
            response_format,
        )

    # ── Provider Resolution ────────────────────────────────────────

    def _resolve_provider(self) -> Optional[str]:
        if self.preferred_provider == 'gemini':
            if self.gemini_key:
                return 'gemini'
            if self.openai_key:
                logger.info('Gemini key missing, falling back to OpenAI')
                return 'openai'
        else:  # openai (default)
            if self.openai_key:
                return 'openai'
            if self.gemini_key:
                logger.info('OpenAI key missing, falling back to Gemini')
                return 'gemini'
        return None

    def _resolve_model(self, provider: str, requested: Optional[str] = None) -> str:
        if not requested:
            return self.gemini_model if provider == 'gemini' else self.openai_model

        if provider == 'openai':
            if requested.startswith('gpt'):
                return requested
            return GEMINI_TO_OPENAI.get(requested, self.openai_model)
        else:
            if requested.startswith('gemini'):
                return requested
            return OPENAI_TO_GEMINI.get(requested, self.gemini_model)

    # ── OpenAI ─────────────────────────────────────────────────────

    def _openai_completion(self, messages, model, temperature, max_tokens,
                           response_format, **kwargs) -> LLMResponse:
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_key)

            params: Dict[str, Any] = {
                'model': model,
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens,
            }
            if response_format:
                params['response_format'] = response_format
            params.update(kwargs)

            resp = client.chat.completions.create(**params)

            return LLMResponse(
                success=True,
                content=resp.choices[0].message.content or '',
                model=resp.model,
                provider='openai',
                tokens_used=resp.usage.total_tokens if resp.usage else 0,
                finish_reason=resp.choices[0].finish_reason or '',
                raw_response=resp,
            )
        except Exception as e:
            logger.error('OpenAI completion failed: %s', e)
            return LLMResponse(success=False, error=str(e), provider='openai')

    # ── Gemini (REST API) ──────────────────────────────────────────

    GEMINI_BASE = 'https://generativelanguage.googleapis.com/v1beta'

    def _gemini_completion(self, messages, model, temperature, max_tokens,
                           response_format) -> LLMResponse:
        try:
            url = f'{self.GEMINI_BASE}/models/{model}:generateContent?key={self.gemini_key}'

            gemini_contents, system_instruction = self._to_gemini_messages(messages)

            payload: Dict[str, Any] = {
                'contents': gemini_contents,
                'generationConfig': {
                    'temperature': temperature,
                    'maxOutputTokens': max_tokens,
                },
            }

            if system_instruction:
                payload['systemInstruction'] = {
                    'parts': [{'text': system_instruction}],
                }

            if response_format and response_format.get('type') == 'json_object':
                payload['generationConfig']['responseMimeType'] = 'application/json'

            resp = http_requests.post(
                url,
                headers={'Content-Type': 'application/json'},
                json=payload,
                timeout=120,
            )

            if resp.status_code != 200:
                error_msg = f'Gemini API error {resp.status_code}'
                try:
                    error_msg = resp.json().get('error', {}).get('message', error_msg)
                except Exception:
                    pass
                return LLMResponse(success=False, error=error_msg, provider='gemini')

            result = resp.json()

            # Extract text
            content = ''
            candidates = result.get('candidates', [])
            if candidates:
                parts = candidates[0].get('content', {}).get('parts', [])
                content = ''.join(p.get('text', '') for p in parts)

            # Strip markdown code fences (Gemini sometimes wraps JSON)
            content = content.strip()
            if content.startswith('```'):
                content = content.split('\n', 1)[1] if '\n' in content else content[3:]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()

            # Token usage
            usage = result.get('usageMetadata', {})
            tokens = usage.get('promptTokenCount', 0) + usage.get('candidatesTokenCount', 0)

            finish = candidates[0].get('finishReason', '') if candidates else ''

            return LLMResponse(
                success=True,
                content=content,
                model=model,
                provider='gemini',
                tokens_used=tokens,
                finish_reason=finish,
                raw_response=result,
            )
        except Exception as e:
            logger.error('Gemini completion failed: %s', e)
            return LLMResponse(success=False, error=str(e), provider='gemini')

    # ── Message Format Conversion ──────────────────────────────────

    @staticmethod
    def _to_gemini_messages(messages: List[Dict]):
        """
        Convert OpenAI message format → Gemini format.

        OpenAI:  [{"role": "system", "content": "..."}, ...]
        Gemini:  systemInstruction + contents: [{"role": "user", "parts": [...]}]

        Handles vision content (base64 images in content arrays).
        """
        system_parts: List[str] = []
        gemini_contents: List[Dict] = []

        for msg in messages:
            role = msg['role']
            content = msg['content']

            if role == 'system':
                system_parts.append(content if isinstance(content, str) else str(content))
                continue

            gemini_role = 'model' if role == 'assistant' else 'user'

            if isinstance(content, str):
                gemini_contents.append({
                    'role': gemini_role,
                    'parts': [{'text': content}],
                })
            elif isinstance(content, list):
                # Vision content: text + image_url items
                parts = []
                for item in content:
                    if item.get('type') == 'text':
                        parts.append({'text': item['text']})
                    elif item.get('type') == 'image_url':
                        image_url = item['image_url']['url']
                        if image_url.startswith('data:'):
                            header, data = image_url.split(',', 1)
                            mime = header.split(':')[1].split(';')[0]
                            parts.append({
                                'inlineData': {'mimeType': mime, 'data': data},
                            })
                        else:
                            parts.append({
                                'fileData': {'mimeType': 'image/jpeg', 'fileUri': image_url},
                            })
                if parts:
                    gemini_contents.append({'role': gemini_role, 'parts': parts})

        system_instruction = '\n\n'.join(system_parts) if system_parts else None
        return gemini_contents, system_instruction


# ── Factory ────────────────────────────────────────────────────────

def get_llm_service(user) -> UnifiedLLMService:
    """
    Build a UnifiedLLMService from user settings.
    Primary entry point for all AI call sites.
    """
    from accounts.api_keys import get_openai_key, get_gemini_key

    openai_key = get_openai_key(user)
    gemini_key = get_gemini_key(user)

    preferred_provider = 'openai'
    openai_model = 'gpt-4o-mini'
    gemini_model = 'gemini-2.0-flash'

    try:
        from ai_caption.models import UserAPISettings
        settings = UserAPISettings.objects.get(user=user)
        preferred_provider = getattr(settings, 'default_llm_provider', 'openai')
        openai_model = settings.default_model or 'gpt-4o-mini'
        gemini_model = getattr(settings, 'default_gemini_model', 'gemini-2.0-flash')
    except Exception:
        pass

    return UnifiedLLMService(
        openai_key=openai_key,
        gemini_key=gemini_key,
        preferred_provider=preferred_provider,
        openai_model=openai_model,
        gemini_model=gemini_model,
    )
