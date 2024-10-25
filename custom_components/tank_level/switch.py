import logging

from homeassistant.components.switch import SwitchEntity

_LOGGER = logging.getLogger(__name__)


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
