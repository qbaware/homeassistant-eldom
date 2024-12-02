"""Constants for the Eldom integration."""

DOMAIN = "eldom"

API_BASE_URL = "https://myeldom.com"
MANUFACTURER_NAME = "Eldom"

DEVICE_TYPE_FLAT_BOILER = 7
DEVICE_TYPE_SMART_BOILER = 5
DEVICE_TYPE_CONVECTOR_HEATER = 4

DEVICE_TYPE_MAPPING = {
    DEVICE_TYPE_FLAT_BOILER: "Flat Boiler",
    DEVICE_TYPE_SMART_BOILER: "Smart Boiler",
    DEVICE_TYPE_CONVECTOR_HEATER: "Convector Heater",
}
