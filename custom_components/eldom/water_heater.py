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
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EldomCoordinator

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
    api: EldomClient = hass.data[DOMAIN][entry.entry_id]
    coordinator = EldomCoordinator(hass, api)

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        EldomFlatWaterHeaterEntity(coordinator, flat_boiler.DeviceID, api)
        for _, flat_boiler in enumerate(coordinator.data.values())
    )


class EldomFlatWaterHeaterEntity(WaterHeaterEntity, CoordinatorEntity):
    """Representation of an Eldom flat water heater.

    The CoordinatorEntity class provides:
      should_poll
      async_update
      async_added_to_hass
      available
    """

    def __init__(self, coordinator, flat_boiler_id, api: EldomClient) -> None:
        """Initialize the water heater."""
        super().__init__(coordinator)
        self._flat_boiler = coordinator.data[flat_boiler_id]
        self._api = api
        self._name = self._flat_boiler.DeviceID
        self._current_temperature = self._flat_boiler.STL_Temp
        self._target_temperature = self._flat_boiler.SetTemp
        self._current_operation = OPERATION_MODES.get(
            self._flat_boiler.State, "Unknown"
        )
        self._operation_list = list(OPERATION_MODES.values())

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
        self._name = self._flat_boiler.DeviceID
        self._flat_boiler = self.coordinator.data[self._flat_boiler.DeviceID]
        self._current_temperature = self._flat_boiler.STL_Temp
        self._target_temperature = self._flat_boiler.SetTemp
        self._current_operation = OPERATION_MODES.get(
            self._flat_boiler.State, "Unknown"
        )
        self.async_write_ha_state()
