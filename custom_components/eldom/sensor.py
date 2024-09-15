"""Sensor platform for Eldom integration."""

import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER_NAME
from .models import EldomData

_LOGGER = logging.getLogger(__name__)

DAY_ENERGY_CONSUMPTION_SENSOR_NAME = "Day Energy Consumption"
DAY_ENERGY_CONSUMPTION_ICON = "mdi:lightning-bolt"

NIGHT_ENERGY_CONSUMPTION_SENSOR_NAME = "Night Energy Consumption"
NIGHT_ENERGY_CONSUMPTION_ICON = "mdi:lightning-bolt"

SAVED_ENERGY_SENSOR_NAME = "Saved Energy"
SAVED_ENERGY_SENSOR_ICON = "mdi:lightning-bolt"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eldom sensor platform."""

    eldom_data: EldomData = hass.data[DOMAIN][config_entry.entry_id]

    await eldom_data.coordinator.async_config_entry_first_refresh()

    # Add energy consumption sensors.
    async_add_entities(
        EldomDayEnergyConsumptionSensor(flat_boiler.DeviceID, eldom_data)
        for _, flat_boiler in enumerate(eldom_data.coordinator.data.values())
    )

    async_add_entities(
        EldomNightEnergyConsumptionSensor(flat_boiler.DeviceID, eldom_data)
        for _, flat_boiler in enumerate(eldom_data.coordinator.data.values())
    )

    # Add energy saved sensors.
    async_add_entities(
        EldomSavedEnergySensor(flat_boiler.DeviceID, eldom_data)
        for _, flat_boiler in enumerate(eldom_data.coordinator.data.values())
    )


class EldomDayEnergyConsumptionSensor(SensorEntity, CoordinatorEntity):
    """Representation of an Eldom day energy consumption sensor."""

    def __init__(self, flat_boiler_id: str, eldom_data: EldomData) -> None:
        """Initialize an Eldom energy consumption sensor."""
        super().__init__(eldom_data.coordinator)
        self._flat_boiler_id = flat_boiler_id
        self._api = eldom_data.api
        self._id = f"{self._flat_boiler_id}-day-energy-consumption-sensor"

        self._day_usage = self.coordinator.data[self._flat_boiler_id].EnergyD

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return DAY_ENERGY_CONSUMPTION_SENSOR_NAME

    @property
    def icon(self) -> str:
        """Return the icon of the powerful mode switch."""
        return DAY_ENERGY_CONSUMPTION_ICON

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class of the powerful mode switch."""
        return SensorDeviceClass.ENERGY

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this water heater."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._flat_boiler_id)},
            manufacturer=MANUFACTURER_NAME,
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._id

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return int(self._day_usage)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._day_usage = self.coordinator.data[self._flat_boiler_id].EnergyD

        self.async_write_ha_state()


class EldomNightEnergyConsumptionSensor(SensorEntity, CoordinatorEntity):
    """Representation of an Eldom night energy consumption sensor."""

    def __init__(self, flat_boiler_id: str, eldom_data: EldomData) -> None:
        """Initialize an Eldom energy consumption sensor."""
        super().__init__(eldom_data.coordinator)
        self._flat_boiler_id = flat_boiler_id
        self._api = eldom_data.api
        self._id = f"{self._flat_boiler_id}-night-energy-consumption-sensor"

        self._night_usage = self.coordinator.data[self._flat_boiler_id].EnergyN

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return NIGHT_ENERGY_CONSUMPTION_SENSOR_NAME

    @property
    def icon(self) -> str:
        """Return the icon of the powerful mode switch."""
        return NIGHT_ENERGY_CONSUMPTION_ICON

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class of the powerful mode switch."""
        return SensorDeviceClass.ENERGY

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this water heater."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._flat_boiler_id)},
            manufacturer=MANUFACTURER_NAME,
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._id

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return int(self._night_usage)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._night_usage = self.coordinator.data[self._flat_boiler_id].EnergyN

        self.async_write_ha_state()


class EldomSavedEnergySensor(SensorEntity, CoordinatorEntity):
    """Representation of an Eldom energy saved sensor."""

    def __init__(self, flat_boiler_id: str, eldom_data: EldomData) -> None:
        """Initialize an Eldom energy saved sensor."""
        super().__init__(eldom_data.coordinator)
        self._flat_boiler_id = flat_boiler_id
        self._api = eldom_data.api
        self._id = f"{self._flat_boiler_id}-energy-saved-sensor"

        self._saved_usage = self.coordinator.data[self._flat_boiler_id].SavedEnergy

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return SAVED_ENERGY_SENSOR_NAME

    @property
    def icon(self) -> str:
        """Return the icon of the powerful mode switch."""
        return SAVED_ENERGY_SENSOR_ICON

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class of the powerful mode switch."""
        return SensorDeviceClass.ENERGY

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this water heater."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._flat_boiler_id)},
            manufacturer=MANUFACTURER_NAME,
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._id

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return int(self._saved_usage / 100)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._saved_usage = self.coordinator.data[self._flat_boiler_id].SavedEnergy

        self.async_write_ha_state()
