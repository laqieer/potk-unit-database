# -*- coding:utf-8 -*-
from potk_unit_extractor.model import *
from potk_unit_extractor.loader import load_folder
from pathlib import Path
import unittest


class UnitGrTest(unittest.TestCase):
    test_gr_cases = [
        # OG 6* Masamune
        (100114, UnitType.DEX, {
            StatType.GRD: 48,
            StatType.SPR: 27,
            StatType.SPD: 69,
            StatType.TEC: 73,
        }),
        # OG 6* Failnote
        (3401913, UnitType.DEX, {
            StatType.GRD: 65,
            StatType.SPR: 40,
            StatType.SPD: 101,
            StatType.TEC: 100,
        }),
        # 6* Zwei
        (603013, UnitType.VIT, {
            StatType.HP: 97,
            StatType.SPD: 91,
            StatType.TEC: 91,
        }),
    ]

    @classmethod
    def setUpClass(cls) -> None:
        cls._loader = load_folder(Path('masterdata'))

    def test_expected_gr(self) -> None:
        for u_id, u_type, u_grs in self.test_gr_cases:
            unit = self._loader.load_unit(u_id)
            for stat, gr in u_grs.items():
                with self.subTest(u=unit.h_id, t=u_type, s=stat):
                    actual = unit.stats.of(u_type).of(stat).growth
                    self.assertEqual(gr, actual)


if __name__ == '__main__':
    unittest.main()
