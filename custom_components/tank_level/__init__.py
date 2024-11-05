import logging

import voluptuous as vol
from homeassistant.const import Platform
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, DEFAULT_REFILL_THRESHOLD, DEFAULT_PLAUSIBILITY_THRESHOLD
from .process_image import process_image
from .sensor import TankLevelSensor
from .switch import TankRefillSwitch

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.SWITCH,
                             Platform.SENSOR]


async def async_setup_entry(hass, config_entry):
    hass.data[DOMAIN] = {
        "plausibility_threshold": config_entry.data.get("plausibility_threshold", DEFAULT_PLAUSIBILITY_THRESHOLD),
        "refill_threshold": config_entry.data.get("refill_threshold", DEFAULT_REFILL_THRESHOLD),
    }

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    async def process_tank_level_service(call):
        image_path = call.data.get("image_path")
        if not image_path:
            _LOGGER.error("Service call error: 'image_path' is required.")
            return

        try:
            sensor = hass.data[DOMAIN]['sensor']
            level = await hass.async_add_executor_job(process_image, image_path)
            sensor.update_level(level)

        except Exception as e:
            _LOGGER.error(f"Error processing tank level: {e}")

    hass.services.async_register(DOMAIN, "process_snapshot", process_tank_level_service, schema=vol.Schema({
        vol.Required('image_path'): cv.template
    }))
    return True


async def async_unload_entry(hass, config_entry):
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)
