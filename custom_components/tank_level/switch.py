import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    # We only want this platform to be set up via discovery.
    if discovery_info is None:
        return
    add_entities([TankRefillSwitch()])
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
