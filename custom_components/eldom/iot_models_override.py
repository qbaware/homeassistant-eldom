from dataclasses import dataclass


@dataclass
class User:
    id: int
    """
    User ID.
    """
    login: str
    """
    Username.
    """
    email: str
    """
    Email.
    """


@dataclass
class Device:
    uuid: str
    """
    Device UUID. E.g., AD5B221071124F28
    """
    model: str
    """
    Device model. E.g., HTRCNV, BLR2T
    """
    fmodel: str
    """
    Another device model. This seems to be the actual device model. E.g., RH30NW, R0530
    """
    name: str
    """
    Device name. Seems to correlate with the FModel. E.g., RH30NW, R0530
    """
    pairTok: str
    """
    Pair token. Not really sure what a pair token is, but this is used in all API calls as the device ID. E.g., R7alOFhj9kDslr2X
    """


@dataclass
class ConvectorHeaterDetails:
    ID: str
    """
    Device pair token. This is the value that's used as device ID in the API calls. Yeah, the API is kind of odd.
    """
    T: str
    """
    Temperature reading. For 20 degrees, the value is 200.
    """
    TSet: str
    """
    Target temperature. For 19 degrees, use 190.
    """
    Status: str
    """
    Not sure what status is this.
    """
    Operation: str
    """
    Whether it's on or off. 16 - ON, 0 - OFF.
    """


@dataclass
class ConvectorHeaterStateChangeResponse:
    Res: str
    """
    Response status - "On", "Off", "SetParams", etc.
    """
    Code: str
    """
    Execution code - "0" for success.
    """
    Type: str
    """
    Type of response. E.g., "OK".
    """
    Reason: str
    """
    Reason for the response. E.g., "SUCCESS".
    """


@dataclass
class FlatBoilerDetails:
    ID: str
    """Device pair token. This is the value that's used as device ID in the API calls. Yeah, the API is kind of odd."""
    Tin: str
    """Temperature reading of the second chamber. For 20 degrees, the value is 20."""
    Tout: str
    """Temperature reading of the first chamber. For 20 degrees, the value is 20."""
    Smart: str
    """Not sure."""
    EcoTin: str
    """Second heater target temperature in Eco mode. For 55 degrees, the value is 55."""
    Heater: str
    """Not sure."""
    Status: str
    """Not sure what status is this."""
    EcoMode: str
    """Not sure what EcoMode is."""
    EcoTout: str
    """First heater target temperature in Eco mode. For 55 degrees, the value is 55."""
    ReadyTime: str
    """Not sure."""
    BoilerMode: str
    """The currently selected operation mode. It can be any of 0 - Off, 2 - Powerful, 4 - Smart, 6 - Eco, 8 - Extra Safe."""
    RemainTime: str
    """Not sure."""
    ExtraSaveRate: str
    """Not sure."""
    Powerfull_Tset: str
    """I guess the target temperature when in Powerful mode. For 65 degrees, the value is 65. This might be for both chambers."""
    DT: str = ""
    """Device timestamp."""
    DateTime: str = ""
    """Device datetime timestamp."""
    DelayedStartTime: str = ""
    """Delayed start time."""
    SmartEndTime: str = ""
    """Smart mode end time."""
    RateStart_2_1: str = ""
    """2-rate tariff: start time slot 1 (minutes from midnight)."""
    RateStart_2_2: str = ""
    """2-rate tariff: start time slot 2 (minutes from midnight)."""
    RateTset_2_1: str = ""
    """2-rate tariff: target temp slot 1 (°C)."""
    RateTset_2_2: str = ""
    """2-rate tariff: target temp slot 2 (°C)."""
    RateStart_3_1: str = ""
    """3-rate tariff: start time slot 1."""
    RateStart_3_2: str = ""
    """3-rate tariff: start time slot 2."""
    RateStart_3_3: str = ""
    """3-rate tariff: start time slot 3."""
    RateTset_3_1: str = ""
    """3-rate tariff: target temp slot 1 (°C)."""
    RateTset_3_2: str = ""
    """3-rate tariff: target temp slot 2 (°C)."""
    RateTset_3_3: str = ""
    """3-rate tariff: target temp slot 3 (°C)."""
    RateStart_4_1: str = ""
    """4-rate tariff: start time slot 1."""
    RateStart_4_2: str = ""
    """4-rate tariff: start time slot 2."""
    RateStart_4_3: str = ""
    """4-rate tariff: start time slot 3."""
    RateStart_4_4: str = ""
    """4-rate tariff: start time slot 4."""
    RateTset_4_1: str = ""
    """4-rate tariff: target temp slot 1 (°C)."""
    RateTset_4_2: str = ""
    """4-rate tariff: target temp slot 2 (°C)."""
    RateTset_4_3: str = ""
    """4-rate tariff: target temp slot 3 (°C)."""
    RateTset_4_4: str = ""
    """4-rate tariff: target temp slot 4 (°C)."""
