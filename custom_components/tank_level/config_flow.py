import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, DEFAULT_PLAUSIBILITY_THRESHOLD, DEFAULT_REFILL_THRESHOLD


@callback
def configured_instances(hass):
    """Return a list of configured instances."""
    return [entry.title for entry in hass.config_entries.async_entries(DOMAIN)]


class TankLevelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 0
    MINOR_VERSION = 4

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            # Validate input
            return self.async_create_entry(title="Tank Level Sensor", data=user_input)

        # Schema for the user input fields
        data_schema = vol.Schema({
            vol.Optional("plausibility_threshold", default=DEFAULT_PLAUSIBILITY_THRESHOLD): int,
            vol.Optional("refill_threshold", default=DEFAULT_REFILL_THRESHOLD): int,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors={},
        )
