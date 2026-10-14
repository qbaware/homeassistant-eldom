"""Minimal client for My Eldom electric boilers (device type 3, `/api/eboiler`).

These boilers (e.g. WV08039EW with a Naturela WiFi module) are not covered by
`pyeldom` yet, so the calls live here and reuse its authenticated session.
"""

from dataclasses import dataclass, field, fields
import json

import aiohttp

BASE_URL = "https://myeldom.com"


@dataclass
class EBoilerDetails:
    """Status of an electric boiler as returned by `/api/eboiler/{id}`."""

    DeviceID: str
    Type: int
    HardwareVersion: int
    SoftwareVersion: int
    ElSetTemp: int
    TBottom: int
    TTop: int
    State: int
    Heater: bool
    EnergyD: float
    EnergyN: float
    PowerIDX: int = 0
    VolumeIdx: int = 0
    AdditionalState: int = 0
    SmartControl: int = 0
    ErrorFlag: int = 0
    LastRefreshDate: str = ""
    EnergyDate: str = "0001-01-01T00:00:00Z"
    raw: dict = field(default_factory=dict, repr=False)


class EBoilerClient:
    """Eldom electric boiler API client. Requires a logged-in session."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the client with the session of the main Eldom client."""
        self.session = session

    async def get_eboiler_status(self, device_id: int) -> EBoilerDetails:
        """Get the status of an electric boiler."""
        response = await self.session.get(f"{BASE_URL}/api/eboiler/{device_id}")
        response.raise_for_status()
        response_json = json.loads(await response.text())
        boiler_json = json.loads(response_json.get("objectJson"))

        supported = {f.name for f in fields(EBoilerDetails)} - {"raw"}
        details = EBoilerDetails(
            **{k: v for k, v in boiler_json.items() if k in supported}
        )
        details.raw = boiler_json
        return details

    async def set_eboiler_state(self, device_id: str, state: int) -> None:
        """Set the state of an electric boiler (0 = On, 1 = Smart, 128 = Off)."""
        response = await self.session.post(
            f"{BASE_URL}/api/eboiler/setState",
            json={"deviceId": device_id, "state": state},
        )
        response.raise_for_status()

    async def set_eboiler_temperature(self, device_id: str, temperature: int) -> None:
        """Set the target temperature of an electric boiler."""
        response = await self.session.post(
            f"{BASE_URL}/api/eboiler/setTemperature",
            json={"deviceId": device_id, "temperature": int(temperature)},
        )
        response.raise_for_status()

    async def set_eboiler_heater_on(self, device_id: str) -> None:
        """Turn on the heating element right away (Boost)."""
        response = await self.session.post(
            f"{BASE_URL}/api/eboiler/setHeater",
            json={"deviceId": device_id, "heater": True},
        )
        response.raise_for_status()

    async def set_eboiler_smart_control(self, id: int, smart_control: int) -> None:
        """Set the "Smart control" mode (0 = Eco, 1 = Normal, 2 = Power).

        The website saves all settings at once, so the current settings are
        fetched and sent back with only `smartControl` changed.
        """
        response = await self.session.get(f"{BASE_URL}/api/eboiler/{id}")
        response.raise_for_status()
        boiler_json = json.loads(json.loads(await response.text())["objectJson"])

        alarms = [
            {
                "listeners": {},
                "validateTime": False,
                "daysEnabled": alarm["DaysEnabled"],
                "step": 1,
                "id": index,
                "enabled": alarm["Enabled"],
                "begin": _settings_time(alarm["Begin"]),
                "end": _settings_time(alarm["End"]),
                "temperature": alarm["Temperature"],
            }
            for index, alarm in enumerate(boiler_json.get("Alarms", []))
        ]

        payload = {
            "listeners": {},
            "INVALID_TEMPERATURE": -128,
            "formid": id,
            "alarms": alarms,
            "AutomaticDatetime": boiler_json.get("AutomaticDatetime"),
            "Compensation": boiler_json.get("Compensation"),
            "DelayedStart": _iso_millis(boiler_json.get("DelayedStart")),
            "deviceId": boiler_json.get("DeviceID"),
            "elSetTemp": boiler_json.get("ElSetTemp"),
            "HardwareVersion": boiler_json.get("HardwareVersion"),
            "rate1Start": _settings_time(boiler_json.get("Rate1Start")),
            "rate2Start": _settings_time(boiler_json.get("Rate2Start")),
            "smartControl": smart_control,
            "SoftwareVersion": boiler_json.get("SoftwareVersion"),
            "state": boiler_json.get("State"),
        }

        response = await self.session.post(f"{BASE_URL}/api/eboiler/save", json=payload)
        response.raise_for_status()


def _iso_millis(value: str | None) -> str | None:
    """Convert `2026-10-13T23:11:00Z` to `2026-10-13T23:11:00.000Z`."""
    if not value:
        return value
    return value.rstrip("Z").split(".")[0] + ".000Z"


def _settings_time(value: str | None) -> str | None:
    """Convert a time-of-day timestamp to the date the website sends with settings."""
    if not value:
        return value
    return "2016-02-01T" + _iso_millis(value).split("T")[1]
