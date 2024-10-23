import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import VOLUME_LITERS

from .process_image import process_image

_LOGGER = logging.getLogger(__name__)


class TankLevelSensor(SensorEntity):
    def __init__(self, hass):
        self._state = None
        self._previous_state = None
        self._name = "Tank Level"
        self.hass = hass
        self._refill_mode = False  # Track if refill mode is active

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def device_class(self):
        return "volume"

    @property
    def unit_of_measurement(self):
        return VOLUME_LITERS

    @property
    def refill_threshold(self):
        """Fetch the plausibility threshold from the integration config."""
        return self.hass.data["tank_level"]["refill_threshold"]

    @property
    def plausibility_threshold(self):
        """Fetch the plausibility threshold from the integration config."""
        return self.hass.data["tank_level"]["plausibility_threshold"]

    @property
    def image_path(self):
        """Fetch the image path from the integration config."""
        return self.hass.data["tank_level"]["image_path"]

    def enable_refill_mode(self):
        """Enable refill mode and ignore plausibility checks."""
        self._refill_mode = True
        _LOGGER.info("Refill mode enabled")

    def disable_refill_mode(self):
        """Disable refill mode."""
        self._refill_mode = False
        _LOGGER.info("Refill mode disabled.")

    def update_level(self, new_level):
        if self._state is None:
            _LOGGER.info(f"First tank level reading: {new_level} liters")
            self._state = new_level
        elif self._refill_mode and (new_level - self._state) > self.refill_threshold:
            # If refill mode is active and significant increase detected
            _LOGGER.info(
                f"Significant increase detected in refill mode: {self._state}L to {new_level}L."
            )
            self._previous_state = self._state
            self._state = new_level
            self.disable_refill_mode()  # Reset refill mode after use

        elif abs(new_level - self._state) <= self.plausibility_threshold:
            # Apply plausibility check
            _LOGGER.info(f"Tank level updated from {self._state}L to {new_level}L")
            self._previous_state = self._state
            self._state = new_level
        else:
            _LOGGER.warning(
                f"Tank level change rejected: {self._state}L to {new_level}L (difference exceeds {self.plausibility_threshold}L)"
            )

        self.async_write_ha_state()


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    sensor = TankLevelSensor(hass)
    refill_switch = TankRefillSwitch(sensor)

    async_add_entities([sensor, refill_switch])

    async def process_tank_level_service(call):
        try:
            level = await hass.async_add_executor_job(process_image, sensor.image_path)
            sensor.update_level(level)

            # Check if the refill switch should be turned off
            if refill_switch.is_on and not sensor._refill_mode:
                await refill_switch.async_turn_off()

        except Exception as e:
            _LOGGER.error(f"Error processing tank level: {e}")

    hass.services.async_register(
        "tank_level", "process_snapshot", process_tank_level_service
    )

    return True
