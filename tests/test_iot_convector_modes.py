"""Regressions for vendor modes that used to prevent entity creation."""

from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock

from homeassistant.components.climate import HVACMode

from custom_components.eldom.climate import IoTEldomConvectorHeaterEntity
from custom_components.eldom.eldom_convector import IoTEldomConvectorHeater


class ModeTests(unittest.TestCase):
    def heater(self, operation):
        return IoTEldomConvectorHeater(
            SimpleNamespace(uuid="test-0128", model="HTRCNV"),
            SimpleNamespace(Operation=operation, T="153", TSet="150"),
            Mock(),
        )

    def test_known_modes_still_work(self):
        for code, mode in [("0", HVACMode.OFF), ("16", HVACMode.HEAT), (16, HVACMode.HEAT)]:
            with self.subTest(code=code):
                self.assertEqual(self.heater(code).current_operation, mode)

    def test_unknown_mode_does_not_break_actual_ha_climate_state(self):
        for code in ["64", 64, "unrecognised", "-1", "256", "16.0", None, "NaN"]:
            with self.subTest(code=code):
                heater = self.heater(code)
                entity = IoTEldomConvectorHeaterEntity(heater, Mock(config_entry=None))
                self.assertIsNone(entity.state)
                self.assertEqual(entity.current_temperature, 15.3)
                self.assertEqual(entity.target_temperature, 15)
                self.assertEqual(entity.extra_state_attributes["eldom_operation_code"], str(code))
                # No command may be sent to resolve an unknown mode.
                heater._iot_eldom_client.assert_not_called()
                self.assertEqual(heater._iot_eldom_client.mock_calls, [])

    def test_weekly_program_is_native_auto_with_readable_programme(self):
        for code in ["32", 32, "36"]:
            with self.subTest(code=code):
                heater = self.heater(code)
                entity = IoTEldomConvectorHeaterEntity(heater, Mock(config_entry=None))
                self.assertEqual(entity.state, "auto")
                self.assertIn(HVACMode.AUTO, entity.hvac_modes)
                self.assertEqual(
                    entity.extra_state_attributes["eldom_operation_mode"],
                    "weekly_program",
                )
                self.assertEqual(entity.current_temperature, 15.3)
                self.assertEqual(heater._iot_eldom_client.mock_calls, [])

    def test_low_flags_do_not_erase_manual_or_off_mode(self):
        for code, expected in [("1", HVACMode.OFF), ("18", HVACMode.HEAT), ("20", HVACMode.HEAT)]:
            with self.subTest(code=code):
                self.assertEqual(self.heater(code).current_operation, expected)

    def test_timer_remains_distinct_from_weekly_programme(self):
        heater = self.heater("48")
        self.assertEqual(heater.current_operation, HVACMode.AUTO)
        self.assertEqual(heater.operation_name, "timer")



class CommandSafetyTests(unittest.IsolatedAsyncioTestCase):
    def heater(self, operation):
        client = Mock()
        client.convector_heater.set_convector_heater_state = AsyncMock()
        return IoTEldomConvectorHeater(
            SimpleNamespace(uuid="test-0128", model="HTRCNV"),
            SimpleNamespace(Operation=operation, T="153", TSet="150"),
            client,
        )

    async def test_retaining_auto_never_writes_or_changes_schedule(self):
        heater = self.heater("32")
        await heater.set_operation_mode(HVACMode.AUTO)
        self.assertEqual(heater.operation_code, "32")
        self.assertEqual(heater._iot_eldom_client.mock_calls, [])

    async def test_auto_is_not_offered_or_activated_from_manual(self):
        heater = self.heater("16")
        self.assertNotIn(HVACMode.AUTO, heater.operation_modes)
        with self.assertRaises(ValueError):
            await heater.set_operation_mode(HVACMode.AUTO)
        self.assertEqual(heater.operation_code, "16")
        self.assertEqual(heater._iot_eldom_client.mock_calls, [])

    async def test_existing_on_off_commands_keep_original_ids(self):
        for target, expected in [(HVACMode.OFF, 0), (HVACMode.HEAT, 16)]:
            with self.subTest(target=target):
                heater = self.heater("32")
                await heater.set_operation_mode(target)
                command = heater._iot_eldom_client.convector_heater.set_convector_heater_state
                command.assert_awaited_once_with(
                    heater._convector_heater_device, expected
                )
