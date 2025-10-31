"""
Test custom django management commands
"""
from unittest.mock import patch
from psycopg2 import OperationalError as Psycopg2Error
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Tests for custom django management commands"""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for db when the database is ready immediately,
        the command runs only once."""
        patched_check.return_value = True
        # patched_check is the mock version of Command.
        # check that we patched above.
        # We make it always return True — meaning the database is ready
        # immediately.

        call_command('wait_for_db')
        # Runs our wait_for_db management command as if we typed it in the
        # terminal.

        patched_check.assert_called_once_with(databases=['default'])
        # Verifies that check() was called exactly once,
        # with the 'default' database.
        # If the command tried to call it more than once, the test would fail.

    @patch('time.sleep')
    # We patch time.sleep to avoid actual delays during testing.
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for db when the database isn’t ready,
        the command retries multiple times until it succeeds."""
        patched_check.side_effect = [Psycopg2Error] * 2 + \
                                    [OperationalError] * 3 + [True]

        # side_effect tells the mock what to do on each call — in sequence.
        # First 2 calls → raise Psycopg2Error (Postgres not ready)
        # Next 3 calls → raise OperationalError (Django DB not ready)
        # 6th call → return True (DB is ready)
        # This simulates a real startup delay — 5 failures, then success.

        call_command('wait_for_db')
        # Runs the management command — It will internally call check() 6 times
        # before succeeding.

        self.assertEqual(patched_check.call_count, 6)
        # Asserts that check() was called exactly 6 times.
        patched_check.assert_called_with(databases=['default'])
        # Verifies that the last call to check() was with the 'default'
        # database.
