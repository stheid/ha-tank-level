import logging

from .const import DOMAIN, DEFAULT_REFILL_THRESHOLD, DEFAULT_PLAUSIBILITY_THRESHOLD
from .process_image import process_image

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    """Legacy setup."""
    conf = config.get(DOMAIN, {})

    # Store the configuration values
    hass.data[DOMAIN] = {
        "plausibility_threshold": conf.get("plausibility_threshold", DEFAULT_PLAUSIBILITY_THRESHOLD),
        "refill_threshold": conf.get("refill_threshold", DEFAULT_REFILL_THRESHOLD),
    }

    return True


async def async_setup_entry(hass, config_entry):
    """Set up the tank level sensor from a config entry."""
    # Store the config entry data (UI input) in hass.data for use in sensors
    hass.data[DOMAIN] = {
        "plausibility_threshold": config_entry.data.get("plausibility_threshold", DEFAULT_PLAUSIBILITY_THRESHOLD),
        "refill_threshold": config_entry.data.get("refill_threshold", DEFAULT_REFILL_THRESHOLD),
    }

    # Set up the sensor entities (sensor + switch)
    await hass.helpers.discovery.async_load_platform('sensor', DOMAIN, {}, config_entry)
    await hass.helpers.discovery.async_load_platform('switch', DOMAIN, {}, config_entry)

    # Register the service for processing the tank level
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

    hass.services.async_register(DOMAIN, "process_snapshot", process_tank_level_service)

    return True


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    # Clean up the integration's resources on unload
    hass.data.pop(DOMAIN)
    return True
