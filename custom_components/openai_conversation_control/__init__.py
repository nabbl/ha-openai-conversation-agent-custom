"""The OpenAI Conversation Agent Control integration."""
from __future__ import annotations

import logging
from typing import Literal

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, MATCH_ALL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent
from homeassistant.util import ulid

from .const import DOMAIN
from .function_calling import FunctionCalling

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.LIGHT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OpenAI Conversation Agent Control from a config entry."""

    hass.data.setdefault(DOMAIN, {})["API_KEY"] = entry.data[CONF_API_KEY]
    conversation.async_set_agent(hass, entry, OpenAIAgentControl(hass, entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    conversation.async_unset_agent(hass, entry)

    return unload_ok


class OpenAIAgentControl(conversation.AbstractConversationAgent):
    """OpenAI conversation agent."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the agent."""
        self.hass = hass
        self.entry = entry
        self.function_calling = FunctionCalling(hass)

        self.history: dict[str, list[dict]] = {}

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return a list of supported languages."""
        return MATCH_ALL

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """Process a sentence."""

        print(user_input)

        if user_input.conversation_id in self.history:
            conversation_id = user_input.conversation_id
            messages = self.history[conversation_id]
        else:
            conversation_id = ulid.ulid()
            messages = []

        response, messages, responseMessage = await self.hass.async_add_executor_job(
            self.function_calling.run_conversation, user_input.text, messages
        )

        _LOGGER.debug("Response %s", response)
        self.history[conversation_id] = messages

        intent_response = intent.IntentResponse(language=user_input.language)
        intent_response.async_set_speech(response["content"])
        return conversation.ConversationResult(
            response=intent_response, conversation_id=conversation_id
        )
