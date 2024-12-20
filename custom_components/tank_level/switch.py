import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        async_add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None,
) -> None:
    switch = TankRefillSwitch()
    async_add_entities([switch])
    hass.data[DOMAIN]["switch"] = switch


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    switch = TankRefillSwitch()
    async_add_entities([switch])
    hass.data[DOMAIN]["switch"] = switch


class TankRefillSwitch(SwitchEntity):
    _attr_name = "Refill mode"

    def __init__(self):
        self._is_on = False

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self.name.lower()}"

    @property
    def is_on(self):
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        self._is_on = True
        _LOGGER.info("Refill mode enabled.")

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        self._is_on = False
        _LOGGER.info("Refill mode disabled.")
