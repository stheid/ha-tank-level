import logging

from homeassistant.components.switch import SwitchEntity

_LOGGER = logging.getLogger(__name__)


class TankRefillSwitch(SwitchEntity):
    def __init__(self, sensor):
        self.sensor = sensor
        self._name = "Refill Tank Level"
        self._is_on = False

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        self._is_on = True
        self.sensor.enable_refill_mode()
        _LOGGER.info("Refill mode switch turned on.")

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        self._is_on = False
        self.sensor.disable_refill_mode()
        _LOGGER.info("Refill mode switch turned off.")
