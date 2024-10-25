import logging

from .const import DOMAIN, DEFAULT_REFILL_THRESHOLD, DEFAULT_PLAUSIBILITY_THRESHOLD
from .process_image import process_image
from .sensor import TankLevelSensor
from .switch import TankRefillSwitch

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config, vol=None):
    """Set up the integration from a configuration file."""
    await setup_integration(hass, config.get(DOMAIN, {}))
    return True


async def async_setup_entry(hass, config_entry):
    """Set up the integration from a config entry."""
    await setup_integration(hass, config_entry.data)  # Use config_entry.data
    return True  # Return True to indicate success


async def setup_integration(hass, config_data):
    """Common setup logic for both async_setup and async_setup_entry."""
    # Store the configuration values
    hass.data[DOMAIN] = {
        "plausibility_threshold": config_data.get("plausibility_threshold", DEFAULT_PLAUSIBILITY_THRESHOLD),
        "refill_threshold": config_data.get("refill_threshold", DEFAULT_REFILL_THRESHOLD),
        "sensor": TankLevelSensor(hass),  # Pass `hass` if needed for access
        "switch": TankRefillSwitch(),
    }

    await hass.helpers.discovery.async_load_platform('sensor', DOMAIN, {}, config_data)
    await hass.helpers.discovery.async_load_platform('switch', DOMAIN, {}, config_data)

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


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    # Clean up the integration's resources on unload
    hass.data.pop(DOMAIN, None)  # Use None to avoid KeyError if DOMAIN is not found
    return True
