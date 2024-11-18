"""Eldom objects."""

from abc import ABC, abstractmethod
import logging

from eldom.client import Client as EldomClient
from eldom.models import FlatBoilerDetails, SmartBoilerDetails

from homeassistant.components.water_heater import (
    STATE_ECO,
    STATE_ELECTRIC,
    STATE_HIGH_DEMAND,
)
from homeassistant.const import STATE_OFF

MAX_TEMP = 75
MIN_TEMP = 35

OPERATION_MODES = {
    0: STATE_OFF,
    1: STATE_ELECTRIC,  # Matches: "Heating"
    2: STATE_ECO,  # Matches: "Smart"
    3: STATE_HIGH_DEMAND,  # Matches: "Study"
}

_LOGGER = logging.getLogger(__name__)


class EldomBoiler(ABC):
    """A base class representation of an Eldom boiler."""

    @abstractmethod
    def id(self) -> int:
        """Retrieve the boiler's ID."""

    @abstractmethod
    def device_id(self) -> str:
        """Retrieve the boiler's device ID."""

    @abstractmethod
    def name(self) -> str:
        """Retrieve the boiler's name."""

    @abstractmethod
    def type(self) -> int:
        """Retrieve the boiler's type."""

    @abstractmethod
    def software_version(self) -> str:
        """Retrieve the boiler's software version."""

    @abstractmethod
    def hardware_version(self) -> str:
        """Retrieve the boiler's hardware version."""

    @abstractmethod
    def operation_modes(self) -> list[str]:
        """Retrieve the boiler's operation modes. Modes are: Off, Heating, Smart, or Study."""

    @abstractmethod
    def max_temperature(self) -> float:
        """Retrieve the boiler's maximum temperature."""

    @abstractmethod
    def min_temperature(self) -> float:
        """Retrieve the boiler's minimum temperature."""

    @abstractmethod
    def current_temperature(self) -> float:
        """Retrieve the boiler's current temperature."""

    @abstractmethod
    def target_temperature(self) -> float:
        """Retrieve the boiler's target temperature."""

    @abstractmethod
    def powerful_enabled(self) -> bool:
        """Retrieve the boiler's boost enabled status."""

    @abstractmethod
    def day_energy_consumption(self) -> float:
        """Retrieve the boiler's day energy consumption."""

    @abstractmethod
    def night_energy_consumption(self) -> float:
        """Retrieve the boiler's night energy consumption."""

    @abstractmethod
    def saved_energy(self) -> float:
        """Retrieve the boiler's saved energy."""

    @abstractmethod
    def current_operation(self) -> str:
        """Return current operation ie. Off, Heating, Smart, or Study."""

    @abstractmethod
    async def turn_on(self) -> None:
        """Turn the boiler on."""

    @abstractmethod
    async def turn_off(self) -> None:
        """Turn the boiler off."""

    @abstractmethod
    async def set_operation_mode(self, operation_mode: str) -> None:
        """Set the operation mode of the boiler."""

    @abstractmethod
    async def set_temperature(self, temperature: float) -> None:
        """Set the temperature of the boiler."""

    @abstractmethod
    async def enable_powerful_mode(self) -> None:
        """Enable the boiler's powerful mode."""


class FlatEldomBoiler(EldomBoiler):
    """An Eldom flat boiler representation object."""

    def __init__(
        self,
        id: int,
        flat_boiler_details: FlatBoilerDetails,
        eldom_client: EldomClient,
    ) -> None:
        """Initialize the flat boiler."""
        self._id = id
        self._flat_boiler_details = flat_boiler_details
        self._eldom_client = eldom_client

    @property
    def id(self) -> int:
        """Retrieve the boiler's ID."""
        return self._id

    @property
    def device_id(self) -> str:
        """Retrieve the boiler's device ID."""
        return self._flat_boiler_details.DeviceID

    @property
    def name(self) -> str:
        """Retrieve the boiler's name."""
        return f"Flat Boiler ({self._flat_boiler_details.DeviceID[-4:]})"

    @property
    def type(self) -> int:
        """Retrieve the boiler's type."""
        return self._flat_boiler_details.Type

    @property
    def software_version(self) -> str:
        """Retrieve the boiler's software version."""
        return self._flat_boiler_details.SoftwareVersion

    @property
    def hardware_version(self) -> str:
        """Retrieve the boiler's hardware version."""
        return self._flat_boiler_details.HardwareVersion

    @property
    def operation_modes(self) -> list[str]:
        """Retrieve the boiler's operation modes. Modes are: Off, Heating, Smart, or Study."""
        return list(OPERATION_MODES.values())

    @property
    def max_temperature(self) -> float:
        """Retrieve the boiler's maximum temperature."""
        return MAX_TEMP

    @property
    def min_temperature(self) -> float:
        """Retrieve the boiler's minimum temperature."""
        return MIN_TEMP

    @property
    def current_temperature(self) -> float:
        """Retrieve the boiler's current temperature."""
        return self._flat_boiler_details.STL_Temp

    @property
    def target_temperature(self) -> float:
        """Retrieve the boiler's target temperature."""
        return self._flat_boiler_details.SetTemp

    @property
    def powerful_enabled(self) -> bool:
        """Retrieve whether the boiler's powerful mode is enabled."""
        return self._flat_boiler_details.HasBoost

    @property
    def day_energy_consumption(self) -> float:
        """Retrieve the boiler's day energy consumption."""
        return self._flat_boiler_details.EnergyD

    @property
    def night_energy_consumption(self) -> float:
        """Retrieve the boiler's night energy consumption."""
        return self._flat_boiler_details.EnergyN

    @property
    def saved_energy(self) -> float:
        """Retrieve the boiler's saved energy."""
        return self._flat_boiler_details.SavedEnergy

    @property
    def current_operation(self) -> str:
        """Return current operation ie. Off, Heating, Smart, or Study."""
        return OPERATION_MODES.get(self._flat_boiler_details.State, "Unknown")

    async def turn_on(self) -> None:
        """Turn the boiler on."""
        await self.set_operation_mode(STATE_ECO)

    async def turn_off(self) -> None:
        """Turn the boiler off."""
        await self.set_operation_mode(STATE_OFF)

    async def set_operation_mode(self, operation_mode: str) -> None:
        """Set new target operation mode."""
        if operation_mode not in OPERATION_MODES.values():
            raise ValueError("Operation mode not supported")

        operation_mode_id = {v: k for k, v in OPERATION_MODES.items()}[operation_mode]

        self._flat_boiler_details.State = operation_mode_id

        await self._eldom_client.set_flat_boiler_state(
            self.device_id, operation_mode_id
        )

    async def set_temperature(self, temperature: float) -> None:
        """Set the temperature of the boiler."""
        self._flat_boiler_details.SetTemp = temperature

        await self._eldom_client.set_flat_boiler_temperature(
            self.device_id, temperature
        )

    async def enable_powerful_mode(self) -> None:
        """Enable the boiler's powerful mode."""
        self._flat_boiler_details.HasBoost = True

        await self._eldom_client.set_flat_boiler_powerful_mode_on(self.device_id)


class SmartEldomBoiler(EldomBoiler):
    """An Eldom smart boiler representation object."""

    def __init__(
        self,
        id: int,
        smart_boiler_details: SmartBoilerDetails,
        eldom_client: EldomClient,
    ) -> None:
        """Initialize the smart boiler."""
        self._id = id
        self._smart_boiler_details = smart_boiler_details
        self._eldom_client = eldom_client

    @property
    def id(self) -> int:
        """Retrieve the boiler's ID."""
        return self._id

    @property
    def device_id(self) -> str:
        """Retrieve the boiler's device ID."""
        return self._smart_boiler_details.DeviceID

    @property
    def name(self) -> str:
        """Retrieve the boiler's name."""
        return f"Smart Boiler ({self._smart_boiler_details.DeviceID[-4:]})"

    @property
    def type(self) -> int:
        """Retrieve the boiler's type."""
        return self._smart_boiler_details.Type

    @property
    def software_version(self) -> str:
        """Retrieve the boiler's software version."""
        return self._smart_boiler_details.SoftwareVersion

    @property
    def hardware_version(self) -> str:
        """Retrieve the boiler's hardware version."""
        return self._smart_boiler_details.HardwareVersion

    @property
    def operation_modes(self) -> list[str]:
        """Retrieve the boiler's operation modes. Modes are: Off, Heating, Smart, or Study."""
        return list(OPERATION_MODES.values())

    @property
    def max_temperature(self) -> float:
        """Retrieve the boiler's maximum temperature."""
        return MAX_TEMP

    @property
    def min_temperature(self) -> float:
        """Retrieve the boiler's minimum temperature."""
        return MIN_TEMP

    @property
    def current_temperature(self) -> float:
        """Retrieve the boiler's current temperature."""
        return self._smart_boiler_details.WH_TempL

    @property
    def target_temperature(self) -> float:
        """Retrieve the boiler's target temperature."""
        return self._smart_boiler_details.SetTemp

    @property
    def powerful_enabled(self) -> bool:
        """Retrieve whether the boiler's powerful mode is enabled."""
        return self._smart_boiler_details.BoostHeating

    @property
    def day_energy_consumption(self) -> float:
        """Retrieve the boiler's day energy consumption."""
        return self._smart_boiler_details.EnergyD

    @property
    def night_energy_consumption(self) -> float:
        """Retrieve the boiler's night energy consumption."""
        return self._smart_boiler_details.EnergyN

    @property
    def saved_energy(self) -> float:
        """Retrieve the boiler's saved energy."""
        return self._smart_boiler_details.SavedEnergy

    @property
    def current_operation(self) -> str:
        """Return current operation ie. Off, Heating, Smart, or Study."""
        return OPERATION_MODES.get(self._smart_boiler_details.State, "Unknown")

    async def turn_on(self) -> None:
        """Turn the boiler on."""
        await self.set_operation_mode(STATE_ECO)

    async def turn_off(self) -> None:
        """Turn the boiler off."""
        await self.set_operation_mode(STATE_OFF)

    async def set_operation_mode(self, operation_mode: str) -> None:
        """Set new target operation mode."""
        if operation_mode not in OPERATION_MODES.values():
            raise ValueError("Operation mode not supported")

        operation_mode_id = {v: k for k, v in OPERATION_MODES.items()}[operation_mode]

        self._smart_boiler_details.State = operation_mode_id

        await self._eldom_client.set_smart_boiler_state(
            self.device_id, operation_mode_id
        )

    async def set_temperature(self, temperature: float) -> None:
        """Set the temperature of the boiler."""
        self._smart_boiler_details.SetTemp = temperature

        await self._eldom_client.set_smart_boiler_temperature(
            self.device_id, temperature
        )

    async def enable_powerful_mode(self) -> None:
        """Enable the boiler's powerful mode."""
        self._smart_boiler_details.BoostHeating = True

        await self._eldom_client.set_smart_boiler_powerful_mode_on(self.device_id)
