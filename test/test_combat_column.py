import unittest

from bot_heard_round.fleet import CombatColumn


class CombatColumnTestCase(unittest.TestCase):
    def test_adjacent_columns(self):
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
