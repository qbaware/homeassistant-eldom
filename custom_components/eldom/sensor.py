"""Sensor platform for Eldom integration."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEVICE_TYPE_FLAT_BOILER, DEVICE_TYPE_SMART_BOILER, DOMAIN
from .coordinator import EldomCoordinator
from .eldom_boiler import EldomBoiler
from .models import EldomData

_LOGGER = logging.getLogger(__name__)

DAY_ENERGY_CONSUMPTION_SENSOR_NAME = "Day Energy Consumption"
DAY_ENERGY_CONSUMPTION_ICON = "mdi:lightning-bolt"

NIGHT_ENERGY_CONSUMPTION_SENSOR_NAME = "Night Energy Consumption"
NIGHT_ENERGY_CONSUMPTION_ICON = "mdi:lightning-bolt"

SAVED_ENERGY_SENSOR_NAME = "Saved Energy"
SAVED_ENERGY_SENSOR_ICON = "mdi:lightning-bolt"

HEATER_SENSOR_NAME = "Heater"
HEATER_SENSOR_ICON = "mdi:heat-wave"
HEATER_STATE_ON = "On"
HEATER_STATE_OFF = "Off"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eldom sensor platform."""

    eldom_data: EldomData = hass.data[DOMAIN][config_entry.entry_id]

    await eldom_data.coordinator.async_config_entry_first_refresh()

    entities_to_add = []

    for flat_boiler in eldom_data.coordinator.data.get(
        DEVICE_TYPE_FLAT_BOILER
    ).values():
        entities_to_add.append(
            EldomBoilerDayEnergyConsumptionSensor(flat_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            EldomBoilerNightEnergyConsumptionSensor(flat_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            EldomBoilerSavedEnergySensor(flat_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            EldomBoilerHeaterSensor(flat_boiler, eldom_data.coordinator)
        )

    for smart_boiler in eldom_data.coordinator.data.get(
        DEVICE_TYPE_SMART_BOILER
    ).values():
        entities_to_add.append(
            EldomBoilerDayEnergyConsumptionSensor(smart_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            EldomBoilerNightEnergyConsumptionSensor(
                smart_boiler, eldom_data.coordinator
            )
        )
        entities_to_add.append(
            EldomBoilerSavedEnergySensor(smart_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            EldomBoilerHeaterSensor(smart_boiler, eldom_data.coordinator)
        )

    async_add_entities(entities_to_add)


class EldomBoilerDayEnergyConsumptionSensor(SensorEntity, CoordinatorEntity):
    """Representation of an Eldom boiler day energy consumption sensor."""

    def __init__(
        self, eldom_boiler: EldomBoiler, coordinator: EldomCoordinator
    ) -> None:
        """Initialize an Eldom energy consumption sensor."""
        super().__init__(coordinator)

        self._eldom_boiler = eldom_boiler

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this water heater."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._eldom_boiler.device_id)},
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._eldom_boiler.device_id}-day-energy-consumption-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._eldom_boiler.name}'s {DAY_ENERGY_CONSUMPTION_SENSOR_NAME}"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return DAY_ENERGY_CONSUMPTION_ICON

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class of the sensor."""
        return SensorDeviceClass.ENERGY

    @property
    def state_class(self) -> SensorStateClass:
        """Return the state class of the sensor."""
        return SensorStateClass.TOTAL_INCREASING

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return int(self._eldom_boiler.day_energy_consumption)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._eldom_boiler = self.coordinator.data.get(self._eldom_boiler.type).get(
            self._eldom_boiler.id
        )

        self.async_write_ha_state()


class EldomBoilerNightEnergyConsumptionSensor(SensorEntity, CoordinatorEntity):
    """Representation of an Eldom boiler night energy consumption sensor."""

    def __init__(
        self, eldom_boiler: EldomBoiler, coordinator: EldomCoordinator
    ) -> None:
        """Initialize an Eldom energy consumption sensor."""
        super().__init__(coordinator)

        self._eldom_boiler = eldom_boiler

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this water heater."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._eldom_boiler.device_id)},
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._eldom_boiler.device_id}-night-energy-consumption-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._eldom_boiler.name}'s {NIGHT_ENERGY_CONSUMPTION_SENSOR_NAME}"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return NIGHT_ENERGY_CONSUMPTION_ICON

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class of the sensor."""
        return SensorDeviceClass.ENERGY

    @property
    def state_class(self) -> SensorStateClass:
        """Return the state class of the sensor."""
        return SensorStateClass.TOTAL_INCREASING

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return int(self._eldom_boiler.night_energy_consumption)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._eldom_boiler = self.coordinator.data.get(self._eldom_boiler.type).get(
            self._eldom_boiler.id
        )

        self.async_write_ha_state()


class EldomBoilerSavedEnergySensor(SensorEntity, CoordinatorEntity):
    """Representation of an Eldom boiler energy saved sensor."""

    def __init__(
        self, eldom_boiler: EldomBoiler, coordinator: EldomCoordinator
    ) -> None:
        """Initialize an Eldom energy saved sensor."""
        super().__init__(coordinator)

        self._eldom_boiler = eldom_boiler

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this water heater."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._eldom_boiler.device_id)},
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._eldom_boiler.device_id}-energy-saved-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._eldom_boiler.name}'s {SAVED_ENERGY_SENSOR_NAME}"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return SAVED_ENERGY_SENSOR_ICON

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class of the sensor."""
        return SensorDeviceClass.ENERGY

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return int(self._eldom_boiler.saved_energy / 100)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._eldom_boiler = self.coordinator.data.get(self._eldom_boiler.type).get(
            self._eldom_boiler.id
        )

        self.async_write_ha_state()


class EldomBoilerHeaterSensor(SensorEntity, CoordinatorEntity):
    """Representation of an Eldom boiler's heater."""

    def __init__(
        self, eldom_boiler: EldomBoiler, coordinator: EldomCoordinator
    ) -> None:
        """Initialize a sensor for an Eldom boiler's heater."""
        super().__init__(coordinator)

        self._eldom_boiler = eldom_boiler

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this water heater."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._eldom_boiler.device_id)},
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._eldom_boiler.device_id}-heater-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._eldom_boiler.name}'s {HEATER_SENSOR_NAME}"

    @property
    def icon(self) -> str:
        """Return the icon of the heater sensor."""
        return HEATER_SENSOR_ICON

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class of the sensor."""
        return SensorDeviceClass.ENUM

    @property
    def options(self) -> list[str]:
        """Return a set of possible options."""
        return [HEATER_STATE_ON, HEATER_STATE_OFF]

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return (
            HEATER_STATE_ON if self._eldom_boiler.heater_enabled else HEATER_STATE_OFF
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._eldom_boiler = self.coordinator.data.get(self._eldom_boiler.type).get(
            self._eldom_boiler.id
        )

        self.async_write_ha_state()
