"""Platform for Eldom water heater integration."""

import logging
from typing import Any

from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DEVICE_TYPE_FLAT_BOILER_ELDOM,
    DEVICE_TYPE_MAPPING,
    DEVICE_TYPE_NATURELA_BOILER_ELDOM,
    DEVICE_TYPE_SMART_BOILER_ELDOM,
    DEVICE_TYPE_FLAT_BOILER_IOT_ELDOM,
    DOMAIN,
    MANUFACTURER_NAME,
)
from .coordinator import EldomCoordinator
from .eldom_boiler import EldomBoiler, IoTEldomBoiler
from .models import EldomData

SUPPORT_FLAGS_ELDOM_HEATER = (
    WaterHeaterEntityFeature.TARGET_TEMPERATURE
    | WaterHeaterEntityFeature.OPERATION_MODE
    | WaterHeaterEntityFeature.ON_OFF
)

SUPPORT_FLAGS_ELDOM_HEATER_NO_TEMP = (
    WaterHeaterEntityFeature.OPERATION_MODE | WaterHeaterEntityFeature.ON_OFF
)

SUPPORT_FLAGS_IOT_ELDOM_HEATER = (
    WaterHeaterEntityFeature.OPERATION_MODE | WaterHeaterEntityFeature.ON_OFF
)

TEMP_UNIT = UnitOfTemperature.CELSIUS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Eldom water heaters setup."""

    eldom_data: EldomData = hass.data[DOMAIN][entry.entry_id]

    await eldom_data.coordinator.async_config_entry_first_refresh()

    async_add_entities(
        EldomWaterHeaterEntity(flat_boiler, eldom_data.coordinator)
        for flat_boiler in eldom_data.coordinator.data.get(
            DEVICE_TYPE_FLAT_BOILER_ELDOM
        ).values()
    )

    async_add_entities(
        EldomWaterHeaterEntity(smart_boiler, eldom_data.coordinator)
        for smart_boiler in eldom_data.coordinator.data.get(
            DEVICE_TYPE_SMART_BOILER_ELDOM
        ).values()
    )

    async_add_entities(
        EldomWaterHeaterEntity(naturela_boiler, eldom_data.coordinator)
        for naturela_boiler in eldom_data.coordinator.data.get(
            DEVICE_TYPE_NATURELA_BOILER_ELDOM
        ).values()
    )

    async_add_entities(
        IoTEldomWaterHeaterEntity(flat_boiler, eldom_data.coordinator)
        for flat_boiler in eldom_data.coordinator.data.get(
            DEVICE_TYPE_FLAT_BOILER_IOT_ELDOM
        ).values()
    )


class EldomWaterHeaterEntity(WaterHeaterEntity, CoordinatorEntity):
    """Representation of an Eldom flat water heater.

    The CoordinatorEntity class provides:
        should_poll
        async_update
        async_added_to_hass
        available
    """

    def __init__(
        self, eldom_boiler: EldomBoiler, coordinator: EldomCoordinator
    ) -> None:
        """Initialize an Eldom water heater."""
        super().__init__(coordinator)

        self._eldom_boiler = eldom_boiler

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this water heater."""
        return DeviceInfo(
            name=self._eldom_boiler.name,
            identifiers={(DOMAIN, self._eldom_boiler.device_id)},
            manufacturer=MANUFACTURER_NAME,
            model=DEVICE_TYPE_MAPPING.get(self._eldom_boiler.type),
            sw_version=self._eldom_boiler.software_version,
            hw_version=self._eldom_boiler.hardware_version,
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._eldom_boiler.device_id

    @property
    def name(self) -> str:
        """Return the name of the water heater."""
        return self._eldom_boiler.name

    @property
    def supported_features(self) -> WaterHeaterEntityFeature:
        """Return the list of supported features."""
        if self._eldom_boiler.type == DEVICE_TYPE_NATURELA_BOILER_ELDOM:
            return SUPPORT_FLAGS_ELDOM_HEATER_NO_TEMP
        return SUPPORT_FLAGS_ELDOM_HEATER

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement."""
        return TEMP_UNIT

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        return self._eldom_boiler.max_temperature

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return self._eldom_boiler.min_temperature

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self._eldom_boiler.current_temperature

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self._eldom_boiler.target_temperature

    @property
    def current_operation(self) -> str | None:
        """Return current operation ie. Heating, Smart, or Study."""
        return self._eldom_boiler.current_operation

    @property
    def operation_list(self) -> list[str] | None:
        """Return the list of available operation modes."""
        return self._eldom_boiler.operation_modes

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the water heater on."""
        await self._eldom_boiler.turn_on()
        self.schedule_update_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the water heater off."""
        await self._eldom_boiler.turn_off()
        self.schedule_update_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set new target operation mode."""
        try:
            await self._eldom_boiler.set_operation_mode(operation_mode)
            self.schedule_update_ha_state()
            await self.coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error("Error while setting operation mode: %s", e)
            raise HomeAssistantError("Error while setting operation mode") from e

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get("temperature")
        await self._eldom_boiler.set_temperature(temperature)
        self.schedule_update_ha_state()
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._eldom_boiler = self.coordinator.data.get(self._eldom_boiler.type).get(
            self._eldom_boiler.id
        )

        self.async_write_ha_state()


class IoTEldomWaterHeaterEntity(WaterHeaterEntity, CoordinatorEntity):
    """Representation of an IoT Eldom flat water heater.

    The CoordinatorEntity class provides:
        should_poll
        async_update
        async_added_to_hass
        available
    """

    def __init__(
        self, iot_eldom_boiler: IoTEldomBoiler, coordinator: EldomCoordinator
    ) -> None:
        """Initialize an Eldom water heater."""
        super().__init__(coordinator)

        self._iot_eldom_boiler = iot_eldom_boiler

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this water heater."""
        return DeviceInfo(
            name=self._iot_eldom_boiler.name,
            identifiers={(DOMAIN, self._iot_eldom_boiler.device_id)},
            manufacturer=MANUFACTURER_NAME,
            model=DEVICE_TYPE_MAPPING.get(self._iot_eldom_boiler.type),
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._iot_eldom_boiler.device_id

    @property
    def name(self) -> str:
        """Return the name of the water heater."""
        return self._iot_eldom_boiler.name

    @property
    def supported_features(self) -> WaterHeaterEntityFeature:
        """Return the list of supported features."""
        return SUPPORT_FLAGS_IOT_ELDOM_HEATER

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement."""
        return TEMP_UNIT

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self._iot_eldom_boiler.current_temperature

    @property
    def current_operation(self) -> str | None:
        """Return current operation ie. Heating, Smart, or Study."""
        return self._iot_eldom_boiler.current_operation

    @property
    def operation_list(self) -> list[str] | None:
        """Return the list of available operation modes."""
        return self._iot_eldom_boiler.operation_modes

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the water heater on."""
        await self._iot_eldom_boiler.turn_on()
        self.schedule_update_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the water heater off."""
        await self._iot_eldom_boiler.turn_off()
        self.schedule_update_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set new target operation mode."""
        try:
            await self._iot_eldom_boiler.set_operation_mode(operation_mode)
            self.schedule_update_ha_state()
            await self.coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error("Error while setting operation mode: %s", e)
            raise HomeAssistantError("Error while setting operation mode") from e

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._iot_eldom_boiler = self.coordinator.data.get(
            self._iot_eldom_boiler.type
        ).get(self._iot_eldom_boiler.id)

        self.async_write_ha_state()
