# Test custom Django management commands

from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase

@patch("core.management.commands.wait_for_db.Command.check")
class CommandTests(SimpleTestCase):
    # Test waiting for database if database ready
    def test_wait_for_db_ready(self, patched_check):
        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(database=["default"])

    # Test waiting for database when getting OperationalError
    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        # "The first 2 times we call the mocked method, raise the Psycopg2Error."
        # "The next 3 times, raise the OperationalError. On the 6th time, return the value (True)."
        # 2 and 3 are arbitrary, they just roughly match the real scenario
        patched_check.side_effect = [Psycopg2Error] * 2 + [OperationalError] * 3 + [True]

        call_command('wait_for_db')
        
        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(database=["default"])