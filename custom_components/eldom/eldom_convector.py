"""Eldom convector heater objects."""

import logging

from eldom.client import Client as EldomClient
from eldom.models import ConvectorHeaterDetails

from homeassistant.components.climate import HVACMode

OPERATION_MODES = {0: HVACMode.OFF, 1: HVACMode.HEAT}

MAX_TEMP = 35
MIN_TEMP = 5

_LOGGER = logging.getLogger(__name__)


class EldomConvectorHeater:
    """An Eldom convector heater representation object."""

    def __init__(
        self,
        id: int,
        convector_heater_details: ConvectorHeaterDetails,
        eldom_client: EldomClient,
    ) -> None:
        """Initialize the heater."""
        self._id = id
        self._convector_heater_details = convector_heater_details
        self._eldom_client = eldom_client

    @property
    def id(self) -> int:
        """Retrieve the heater's ID."""
        return self._id

    @property
    def device_id(self) -> str:
        """Retrieve the heater's device ID."""
        return self._convector_heater_details.DeviceID

    @property
    def name(self) -> str:
        """Retrieve the heater's name."""
        return f"Convector Heater ({self._convector_heater_details.DeviceID[-4:]})"

    @property
    def type(self) -> int:
        """Retrieve the heater's type."""
        return self._convector_heater_details.Type

    @property
    def software_version(self) -> str:
        """Retrieve the heater's software version."""
        return self._convector_heater_details.SoftwareVersion

    @property
    def hardware_version(self) -> str:
        """Retrieve the heater's hardware version."""
        return self._convector_heater_details.HardwareVersion

    @property
    def operation_modes(self) -> list[HVACMode]:
        """Retrieve the heater's operation modes. Modes are: Off, Heat."""
        return list(OPERATION_MODES.values())

    @property
    def max_temperature(self) -> float:
        """Retrieve the heater's maximum temperature."""
        return MAX_TEMP

    @property
    def min_temperature(self) -> float:
        """Retrieve the heater's minimum temperature."""
        return MIN_TEMP

    @property
    def current_temperature(self) -> float:
        """Retrieve the heater's current temperature."""
        return self._convector_heater_details.AmbientTemp

    @property
    def target_temperature(self) -> float:
        """Retrieve the heater's target temperature."""
        return self._convector_heater_details.SetTemp

    @property
    def powerful_enabled(self) -> bool:
        """Retrieve whether the heater's powerful mode is enabled."""
        return self._convector_heater_details.BoostHeating

    @property
    def day_energy_consumption(self) -> float:
        """Retrieve the heater's day energy consumption."""
        return self._convector_heater_details.EnergyD

    @property
    def night_energy_consumption(self) -> float:
        """Retrieve the heater's night energy consumption."""
        return self._convector_heater_details.EnergyN

    @property
    def current_operation(self) -> HVACMode:
        """Return current operation ie. Off or Heat."""
        return OPERATION_MODES.get(self._convector_heater_details.State, "Unknown")

    @property
    def power_level(self) -> int:
        """Retrieve the heating level of the heater."""
        return self._convector_heater_details.Power

    async def turn_on(self) -> None:
        """Turn the heater on."""
        await self.set_operation_mode(HVACMode.HEAT)

    async def turn_off(self) -> None:
        """Turn the heater off."""
        await self.set_operation_mode(HVACMode.OFF)

    async def set_operation_mode(self, operation_mode: HVACMode) -> None:
        """Set new target operation mode."""
        if operation_mode not in OPERATION_MODES.values():
            raise ValueError("Operation mode not supported")

        operation_mode_id = {v: k for k, v in OPERATION_MODES.items()}[operation_mode]

        self._convector_heater_details.State = operation_mode_id

        await self._eldom_client.set_convector_heater_state(
            self.device_id, operation_mode_id
        )

    async def set_temperature(self, temperature: float) -> None:
        """Set the temperature of the heater."""
        self._convector_heater_details.SetTemp = temperature

        await self._eldom_client.set_convector_heater_temperature(
            self.device_id, temperature
        )
