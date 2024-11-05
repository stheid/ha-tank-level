import logging

from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfVolume
from homeassistant.core import DOMAIN, HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    sensor = TankLevelSensor(hass)
    async_add_entities([sensor])
    hass.data[DOMAIN] = {
        "sensor": sensor,
    }


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    sensor = TankLevelSensor(hass)
    async_add_entities([sensor])
    hass.data[DOMAIN] = {
        "sensor": sensor,
    }




class TankLevelSensor(SensorEntity):
    _attr_name = "Volume"
    _attr_native_unit_of_measurement = UnitOfVolume.LITERS
    _attr_device_class = SensorDeviceClass.VOLUME
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, hass):
        self.hass = hass

    @property
    def refill_threshold(self):
        """Fetch the plausibility threshold from the integration config."""
        return self.hass.data["tank_level"]["refill_threshold"]

    @property
    def plausibility_threshold(self):
        """Fetch the plausibility threshold from the integration config."""
        return self.hass.data["tank_level"]["plausibility_threshold"]

    @property
    def _refill_mode(self):
        return self.hass.data[DOMAIN]["switch"].is_on

    async def disable_refill_mode(self):
        _LOGGER.info("Refill mode disabled.")
        return await self.hass.data[DOMAIN]["switch"].async_turn_off()

    def update_level(self, new_level):
        if self._attr_native_value is None:
            _LOGGER.info(f"First tank level reading: {new_level} liters")
            self._attr_native_value = new_level
        elif self._refill_mode and (new_level - self._attr_native_value) > self.refill_threshold:
            # If refill mode is active and significant increase detected
            _LOGGER.info(
                f"Significant increase detected in refill mode: {self._attr_native_value}L to {new_level}L."
            )
            self._attr_native_value = new_level
            self.disable_refill_mode()

        elif abs(new_level - self._attr_native_value) <= self.plausibility_threshold:
            # Apply plausibility check
            _LOGGER.info(f"Tank level updated from {self._attr_native_value}L to {new_level}L")
            self._attr_native_value = new_level
        else:
            _LOGGER.warning(
                f"Tank level change rejected: {self._attr_native_value}L to {new_level}L"
                f" (difference exceeds {self.plausibility_threshold}L)"
            )

        self.async_write_ha_state()
