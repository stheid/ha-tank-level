import logging

from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.discovery import async_load_platform

from .const import DOMAIN, DEFAULT_REFILL_THRESHOLD, DEFAULT_PLAUSIBILITY_THRESHOLD
from .process_image import process_image
from .sensor import TankLevelSensor
from .switch import TankRefillSwitch

_LOGGER = logging.getLogger(__name__)


# async def async_setup(hass, config, vol=None):
#    """Set up the integration from a configuration file."""
#    await setup_integration(hass, config.get(DOMAIN, {}))
#    return True


async def async_setup_entry(hass, config_entry):
    """Set up the integration from a config entry."""
    await setup_integration(hass, config_entry.data)  # Use config_entry.data
    return True  # Return True to indicate success


async def setup_integration(hass, config_data, vol=None):
    """Common setup logic for both async_setup and async_setup_entry."""
    # Store the configuration values
    hass.data[DOMAIN] = {
        "plausibility_threshold": config_data.get("plausibility_threshold", DEFAULT_PLAUSIBILITY_THRESHOLD),
        "refill_threshold": config_data.get("refill_threshold", DEFAULT_REFILL_THRESHOLD),
    }

    await async_load_platform(hass, 'switch', DOMAIN, {}, config_data)
    await async_load_platform(hass, 'sensor', DOMAIN, {}, config_data)

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
        vol.Required('image_file'): cv.string
    }))

    async def async_unload_entry(hass, config_entry):
        """Unload a config entry."""
        # Clean up the integration's resources on unload
        hass.data.pop(DOMAIN, None)  # Use None to avoid KeyError if DOMAIN is not found
        return True
