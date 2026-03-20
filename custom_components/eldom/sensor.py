"""Sensor platform for Eldom integration."""

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

from homeassistant.const import UnitOfTemperature

from .const import (
    DEVICE_TYPE_FLAT_BOILER_ELDOM,
    DEVICE_TYPE_FLAT_BOILER_IOT_ELDOM,
    DEVICE_TYPE_NATURELA_BOILER_ELDOM,
    DEVICE_TYPE_SMART_BOILER_ELDOM,
    DOMAIN,
)
from .coordinator import EldomCoordinator
from .eldom_boiler import EldomBoiler, FlatIoTEldomBoiler
from .models import EldomData

HEATER_STATE_ON = "On"
HEATER_STATE_OFF = "Off"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eldom sensor platform."""

    eldom_data: EldomData = hass.data[DOMAIN][config_entry.entry_id]

    entities_to_add = []

    for flat_boiler in eldom_data.coordinator.data.get(
        DEVICE_TYPE_FLAT_BOILER_ELDOM
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
        entities_to_add.append(
            EldomBoilerEnergyUsageResetDateSensor(flat_boiler, eldom_data.coordinator)
        )

    for smart_boiler in eldom_data.coordinator.data.get(
        DEVICE_TYPE_SMART_BOILER_ELDOM
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
        entities_to_add.append(
            EldomBoilerEnergyUsageResetDateSensor(smart_boiler, eldom_data.coordinator)
        )

    for naturela_boiler in eldom_data.coordinator.data.get(
        DEVICE_TYPE_NATURELA_BOILER_ELDOM
    ).values():
        entities_to_add.append(
            EldomBoilerDayEnergyConsumptionSensor(
                naturela_boiler, eldom_data.coordinator
            )
        )
        entities_to_add.append(
            EldomBoilerNightEnergyConsumptionSensor(
                naturela_boiler, eldom_data.coordinator
            )
        )
        entities_to_add.append(
            EldomBoilerHeaterSensor(naturela_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            EldomBoilerEnergyUsageResetDateSensor(
                naturela_boiler, eldom_data.coordinator
            )
        )

    for iot_flat_boiler in eldom_data.coordinator.data.get(
        DEVICE_TYPE_FLAT_BOILER_IOT_ELDOM
    ).values():
        entities_to_add.append(
            IoTFlatBoilerHeaterSensor(iot_flat_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            IoTFlatBoilerCurrentTempSensor(iot_flat_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            IoTFlatBoilerChamber1TempSensor(iot_flat_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            IoTFlatBoilerChamber2TempSensor(iot_flat_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            IoTFlatBoilerTargetTempSensor(iot_flat_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            IoTFlatBoilerPowerfulTargetTempSensor(iot_flat_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            IoTFlatBoilerEcoTargetTempChamber1Sensor(iot_flat_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            IoTFlatBoilerEcoTargetTempChamber2Sensor(iot_flat_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            IoTFlatBoilerExtraSaveRateSensor(iot_flat_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            IoTFlatBoilerReadyTimeSensor(iot_flat_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            IoTFlatBoilerRemainTimeSensor(iot_flat_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            IoTFlatBoilerDelayedStartTimeSensor(iot_flat_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            IoTFlatBoilerSmartEndTimeSensor(iot_flat_boiler, eldom_data.coordinator)
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
        return f"{self._eldom_boiler.name}'s Day Energy Consumption"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:lightning-bolt"

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
        return f"{self._eldom_boiler.name}'s Night Energy Consumption"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:lightning-bolt"

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
        return f"{self._eldom_boiler.name}'s Saved Energy"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:lightning-bolt"

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
        return f"{self._eldom_boiler.name}'s Heater"

    @property
    def icon(self) -> str:
        """Return the icon of the heater sensor."""
        return "mdi:heat-wave"

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


class EldomBoilerEnergyUsageResetDateSensor(SensorEntity, CoordinatorEntity):
    """Representation of an Eldom boiler's energy usage reset date."""

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
        return f"{self._eldom_boiler.device_id}-energy-usage-reset-date-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._eldom_boiler.name}'s Energy Usage Reset Date"

    @property
    def icon(self) -> str:
        """Return the icon of the heater sensor."""
        return "mdi:calendar-range"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        if self._eldom_boiler.energy_usage_reset_date == "0001-01-01T00:00:00Z":
            return "Never"

        return self._eldom_boiler.energy_usage_reset_date

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._eldom_boiler = self.coordinator.data.get(self._eldom_boiler.type).get(
            self._eldom_boiler.id
        )

        self.async_write_ha_state()


# ─── IoT Flat Boiler Sensors ─────────────────────────────────────────────────


class _IoTBaseSensor(SensorEntity, CoordinatorEntity):
    """Base class for all IoT Flat Boiler sensors."""

    _attr_has_entity_name = True

    def __init__(self, boiler: FlatIoTEldomBoiler, coordinator: EldomCoordinator) -> None:
        super().__init__(coordinator)
        self._boiler = boiler

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(identifiers={(DOMAIN, self._boiler.device_id)})

    @callback
    def _handle_coordinator_update(self) -> None:
        self._boiler = self.coordinator.data.get(self._boiler.type).get(self._boiler.id)
        self.async_write_ha_state()


class IoTFlatBoilerCurrentTempSensor(_IoTBaseSensor):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_icon = "mdi:thermometer"

    @property
    def unique_id(self): return f"{self._boiler.device_id}-current-temp-sensor"

    @property
    def name(self): return "Current Temperature"

    @property
    def native_value(self): return self._boiler.current_temperature


class IoTFlatBoilerHeaterSensor(_IoTBaseSensor):
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_icon = "mdi:heat-wave"
    _attr_options = [HEATER_STATE_ON, HEATER_STATE_OFF]

    @property
    def unique_id(self): return f"{self._boiler.device_id}-heater-sensor"

    @property
    def name(self): return "Heater"

    @property
    def native_value(self): return HEATER_STATE_ON if self._boiler.heater_enabled else HEATER_STATE_OFF


class IoTFlatBoilerChamber1TempSensor(_IoTBaseSensor):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_icon = "mdi:thermometer"

    @property
    def unique_id(self): return f"{self._boiler.device_id}-chamber1-temp-sensor"

    @property
    def name(self): return "Chamber 1 Temperature"

    @property
    def native_value(self): return self._boiler.chamber1_temperature


class IoTFlatBoilerChamber2TempSensor(_IoTBaseSensor):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_icon = "mdi:thermometer"

    @property
    def unique_id(self): return f"{self._boiler.device_id}-chamber2-temp-sensor"

    @property
    def name(self): return "Chamber 2 Temperature"

    @property
    def native_value(self): return self._boiler.chamber2_temperature


class IoTFlatBoilerTargetTempSensor(_IoTBaseSensor):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_icon = "mdi:thermometer-check"

    @property
    def unique_id(self): return f"{self._boiler.device_id}-target-temp-sensor"

    @property
    def name(self): return "Target Temperature"

    @property
    def native_value(self): return self._boiler.target_temperature


class IoTFlatBoilerPowerfulTargetTempSensor(_IoTBaseSensor):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_icon = "mdi:thermometer-high"

    @property
    def unique_id(self): return f"{self._boiler.device_id}-powerful-target-temp-sensor"

    @property
    def name(self): return "Powerful Target Temperature"

    @property
    def native_value(self): return self._boiler.powerful_target_temp


class IoTFlatBoilerEcoTargetTempChamber1Sensor(_IoTBaseSensor):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_icon = "mdi:thermometer"

    @property
    def unique_id(self): return f"{self._boiler.device_id}-eco-target-temp-chamber1-sensor"

    @property
    def name(self): return "Eco Target Temperature Chamber 1"

    @property
    def native_value(self): return self._boiler.eco_target_temp_chamber1


class IoTFlatBoilerEcoTargetTempChamber2Sensor(_IoTBaseSensor):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_icon = "mdi:thermometer"

    @property
    def unique_id(self): return f"{self._boiler.device_id}-eco-target-temp-chamber2-sensor"

    @property
    def name(self): return "Eco Target Temperature Chamber 2"

    @property
    def native_value(self): return self._boiler.eco_target_temp_chamber2


class IoTFlatBoilerExtraSaveRateSensor(_IoTBaseSensor):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:calendar-clock"

    @property
    def unique_id(self): return f"{self._boiler.device_id}-extra-save-rate-sensor"

    @property
    def name(self): return "Extra Save Rate"

    @property
    def native_value(self): return self._boiler.extra_save_rate


class IoTFlatBoilerReadyTimeSensor(_IoTBaseSensor):
    _attr_icon = "mdi:clock-check"

    @property
    def unique_id(self): return f"{self._boiler.device_id}-ready-time-sensor"

    @property
    def name(self): return "Ready Time"

    @property
    def native_value(self): return self._boiler.ready_time or None


class IoTFlatBoilerRemainTimeSensor(_IoTBaseSensor):
    _attr_icon = "mdi:timer-outline"

    @property
    def unique_id(self): return f"{self._boiler.device_id}-remain-time-sensor"

    @property
    def name(self): return "Remaining Time"

    @property
    def native_value(self): return self._boiler.remain_time or None


class IoTFlatBoilerDelayedStartTimeSensor(_IoTBaseSensor):
    _attr_icon = "mdi:clock-start"

    @property
    def unique_id(self): return f"{self._boiler.device_id}-delayed-start-time-sensor"

    @property
    def name(self): return "Delayed Start Time"

    @property
    def native_value(self): return self._boiler.delayed_start_time or None


class IoTFlatBoilerSmartEndTimeSensor(_IoTBaseSensor):
    _attr_icon = "mdi:clock-end"

    @property
    def unique_id(self): return f"{self._boiler.device_id}-smart-end-time-sensor"

    @property
    def name(self): return "Smart Mode End Time"

    @property
    def native_value(self): return self._boiler.smart_end_time or None
