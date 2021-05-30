"""
Tests for combat column
"""

import unittest

from bot_heard_round.fleet import CombatColumn


class CombatColumnTestCase(unittest.TestCase):
    """
    Tests for combat column
    """

    def test_adjacent_columns(self):
        """
        Test adjacent columns
        :return:
        """
        cases = [
            (
                CombatColumn.LEFT,
                [CombatColumn.MIDDLE]
            ),
            (
                CombatColumn.MIDDLE,
                [CombatColumn.LEFT, CombatColumn.RIGHT]
            ),
            (
                CombatColumn.RIGHT,
                [CombatColumn.MIDDLE]
            ),
        ]

        for passed, expected in cases:
            with self.subTest(passed=passed, expected=expected):
                self.assertListEqual(CombatColumn.adjacent_columns(passed), expected)


if __name__ == '__main__':
    unittest.main()
