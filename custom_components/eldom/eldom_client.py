"""A wrapper Eldom client uses whichever of the two clients is authenticaed."""

import aiohttp
from eldom.client import Client as EldomClient
from ioteldom.client import Client as IoTEldomClient

from .const import (
    DEVICE_TYPE_CONVECTOR_HEATER_ELDOM,
    DEVICE_TYPE_CONVECTOR_HEATER_IOT_ELDOM,
    DEVICE_TYPE_FLAT_BOILER_ELDOM,
    DEVICE_TYPE_FLAT_BOILER_IOT_ELDOM,
    DEVICE_TYPE_SMART_BOILER_ELDOM,
    ELDOM_API,
    IOT_ELDOM_API,
)
from .eldom_boiler import FlatEldomBoiler, SmartEldomBoiler, FlatIoTEldomBoiler
from .eldom_convector import EldomConvectorHeater, IoTEldomConvectorHeater


class EldomClientWrapper:
    """An Eldom client wrapper that uses whichever of the two clients is authenticated."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
        api: str,
    ) -> None:
        """Creates a wrapper Eldom client that operates based on which API is chosen."""
        self.username = username
        self.password = password
        self.api = api

        self.eldom_client = EldomClient(session)
        self.iot_eldom_client = IoTEldomClient(session, username, password)

    async def login(self):
        """Try to login with the clients."""
        if self.api == ELDOM_API:
            await self.eldom_client.login(self.username, self.password)
        elif self.api == IOT_ELDOM_API:
            return

    async def is_connected(self):
        """Returns true if the corresponding API client is connected."""
        if self.api == ELDOM_API:
            return await self.eldom_client.is_connected()

        if self.api == IOT_ELDOM_API:
            return await self.iot_eldom_client.is_connected()

        raise ValueError("Invalid API")

    async def get_devices(self):
        """Fetches all devices from the connected API client."""
        (
            eldom_flat_boilers,
            eldom_smart_boilers,
            eldom_convector_heaters,
        ) = await self._fetch_eldom_data()
        (
            iot_eldom_convector_heaters,
            iot_eldom_flat_boilers,
        ) = await self._fetch_iot_eldom_data()

        return {
            DEVICE_TYPE_FLAT_BOILER_ELDOM: eldom_flat_boilers,
            DEVICE_TYPE_SMART_BOILER_ELDOM: eldom_smart_boilers,
            DEVICE_TYPE_CONVECTOR_HEATER_ELDOM: eldom_convector_heaters,
            DEVICE_TYPE_CONVECTOR_HEATER_IOT_ELDOM: iot_eldom_convector_heaters,
            DEVICE_TYPE_FLAT_BOILER_IOT_ELDOM: iot_eldom_flat_boilers,
        }

    async def _fetch_eldom_data(self):
        if self.api != ELDOM_API:
            return {}, {}, {}

        devices = await self.eldom_client.get_devices()

        flat_boilers: dict[str, FlatEldomBoiler] = {
            device.id: FlatEldomBoiler(
                device.id,
                await self.eldom_client.flat_boiler.get_flat_boiler_status(device.id),
                self.eldom_client,
            )
            for device in devices
            if device.deviceType == DEVICE_TYPE_FLAT_BOILER_ELDOM
        }

        smart_boilers: dict[str, SmartEldomBoiler] = {
            device.id: SmartEldomBoiler(
                device.id,
                await self.eldom_client.smart_boiler.get_smart_boiler_status(device.id),
                self.eldom_client,
            )
            for device in devices
            if device.deviceType == DEVICE_TYPE_SMART_BOILER_ELDOM
        }

        convector_heaters: dict[str, EldomConvectorHeater] = {
            device.id: EldomConvectorHeater(
                device.id,
                await self.eldom_client.convector_heater.get_convector_heater_status(
                    device.id
                ),
                self.eldom_client,
            )
            for device in devices
            if device.deviceType == DEVICE_TYPE_CONVECTOR_HEATER_ELDOM
        }

        return flat_boilers, smart_boilers, convector_heaters

    async def _fetch_iot_eldom_data(self):
        if self.api != IOT_ELDOM_API:
            return {}, {}

        devices = await self.iot_eldom_client.get_devices()

        convector_heaters: dict[str, IoTEldomConvectorHeater] = {
            device.uuid: IoTEldomConvectorHeater(
                device,
                await self.iot_eldom_client.convector_heater.get_convector_heater_status(
                    device
                ),
                self.iot_eldom_client,
            )
            for device in devices
            if device.model == DEVICE_TYPE_CONVECTOR_HEATER_IOT_ELDOM
        }

        flat_boilers: dict[str, FlatIoTEldomBoiler] = {
            device.uuid: FlatIoTEldomBoiler(
                device,
                await self.iot_eldom_client.flat_boiler.get_flat_boiler_status(device),
                self.iot_eldom_client,
            )
            for device in devices
            if device.model == DEVICE_TYPE_FLAT_BOILER_IOT_ELDOM
        }

        return convector_heaters, flat_boilers
