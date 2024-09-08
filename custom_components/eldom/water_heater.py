"""Platform for Eldom water heater integration."""

import logging
from typing import Any

from eldom.flat_boiler import Client as EldomClient

from homeassistant.components.water_heater import (
    STATE_ECO,
    STATE_ELECTRIC,
    STATE_HIGH_DEMAND,
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER_NAME
from .models import EldomData

SUPPORT_FLAGS_HEATER = (
    WaterHeaterEntityFeature.TARGET_TEMPERATURE
    | WaterHeaterEntityFeature.OPERATION_MODE
)

TEMP_UNIT = UnitOfTemperature.CELSIUS

MAX_TEMP = 75
MIN_TEMP = 35

OPERATION_MODES = {
    0: STATE_OFF,
    1: STATE_ELECTRIC,  # Matches: "Heating"
    2: STATE_ECO,  # Matches: "Smart"
    3: STATE_HIGH_DEMAND,  # Matches: "Study"
}

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Eldom water heaters setup."""

    eldom_data: EldomData = hass.data[DOMAIN][entry.entry_id]

    await eldom_data.coordinator.async_config_entry_first_refresh()

    async_add_entities(
        EldomFlatWaterHeaterEntity(flat_boiler.DeviceID, eldom_data)
        for _, flat_boiler in enumerate(eldom_data.coordinator.data.values())
    )


class EldomFlatWaterHeaterEntity(WaterHeaterEntity, CoordinatorEntity):
    """Representation of an Eldom flat water heater.

    The CoordinatorEntity class provides:
      should_poll
      async_update
      async_added_to_hass
      available
    """

    def __init__(self, flat_boiler_id: str, eldom_data: EldomData) -> None:
        """Initialize the water heater."""
        super().__init__(eldom_data.coordinator)
        self._api = eldom_data.api
        self._flat_boiler_id = flat_boiler_id

        self._flat_boiler = self.coordinator.data[self._flat_boiler_id]
        self._name = f"Flat Boiler ({self._flat_boiler_id})"
        self._current_temperature = self._flat_boiler.STL_Temp
        self._target_temperature = self._flat_boiler.SetTemp
        self._current_operation = OPERATION_MODES.get(
            self._flat_boiler.State, "Unknown"
        )
        self._operation_list = list(OPERATION_MODES.values())

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this water heater."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._flat_boiler.DeviceID)},
            manufacturer=MANUFACTURER_NAME,
            model=self._flat_boiler.Type,
            sw_version=self._flat_boiler.SoftwareVersion,
            hw_version=self._flat_boiler.HardwareVersion,
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._flat_boiler.DeviceID

    @property
    def name(self) -> str:
        """Return the name of the water heater."""
        return self._name

    @property
    def supported_features(self) -> WaterHeaterEntityFeature:
        """Return the list of supported features."""
        return SUPPORT_FLAGS_HEATER

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement."""
        return TEMP_UNIT

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        return MAX_TEMP

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return MIN_TEMP

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self._current_temperature

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self._target_temperature

    @property
    def current_operation(self) -> str | None:
        """Return current operation ie. Heating, Smart, or Study."""
        return self._current_operation

    @property
    def operation_list(self) -> list[str] | None:
        """Return the list of available operation modes."""
        return self._operation_list

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set new target operation mode."""
        if operation_mode not in OPERATION_MODES.values():
            raise HomeAssistantError("Operation mode not supported")

        self._current_operation = operation_mode
        self.schedule_update_ha_state()
        operation_mode_id = {v: k for k, v in OPERATION_MODES.items()}[operation_mode]
        await self._api.set_flat_boiler_state(
            self._flat_boiler.DeviceID, operation_mode_id
        )
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get("temperature")
        self._target_temperature = temperature
        self.schedule_update_ha_state()
        await self._api.set_flat_boiler_temperature(
            self._flat_boiler.DeviceID, temperature
        )
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._flat_boiler = self.coordinator.data[self._flat_boiler_id]
        self._name = f"Flat Boiler ({self._flat_boiler_id})"
        self._current_temperature = self._flat_boiler.STL_Temp
        self._target_temperature = self._flat_boiler.SetTemp
        self._current_operation = OPERATION_MODES.get(
            self._flat_boiler.State, "Unknown"
        )
        self._operation_list = list(OPERATION_MODES.values())

        self.async_write_ha_state()
