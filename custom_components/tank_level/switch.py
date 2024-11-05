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
    """Set up MoldIndicator sensor."""
    async_add_entities([TankRefillSwitch()])
    hass.data[DOMAIN] = {
        "switch": TankRefillSwitch(),
    }


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Mold indicator sensor entry."""
    async_add_entities([TankRefillSwitch()])
    hass.data[DOMAIN] = {
        "switch": TankRefillSwitch(),
    }


class TankRefillSwitch(SwitchEntity):
    _attr_name = "Refill mode"

    def __init__(self):
        self._is_on = False

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
