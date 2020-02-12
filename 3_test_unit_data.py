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
            StatType.HP:  97,
            StatType.SPD: 91,
            StatType.TEC: 91,
        }),
        # 6* LR Naegling
        (3100613, UnitType.DEX, {
            StatType.GRD: 57,
            StatType.SPR: 33,
            StatType.SPD: 97,
            StatType.TEC: 98,
        }),
        # 6* OG Naegling
        (100624, UnitType.DEX, {
            StatType.GRD: 69,
            StatType.SPR: 31,
            StatType.SPD: 74,
            StatType.TEC: 58,
        }),
        # 6* Gaku Naegling
        (100653, UnitType.DEX, {
            StatType.GRD: 54,
            StatType.SPR: 29,
            StatType.SPD: 97,
            StatType.TEC: 99,
        }),
        # 6* SS Naegling
        (2100613, UnitType.DEX, {
            StatType.GRD: 58,
            StatType.SPR: 29,
            StatType.SPD: 99,
            StatType.TEC: 99,
        }),
        # 6* CCS Naegling
        (100663, UnitType.DEX, {
            StatType.GRD: 50,
            StatType.SPR: 34,
            StatType.SPD: 93,
            StatType.TEC: 95,
        }),
        # 6* SS Chalice
        (2602513, UnitType.DEX, {
            StatType.GRD: 35,
            StatType.SPR: 69,
            StatType.SPD: 101,
            StatType.TEC: 101,
        }),
    ]

    def test_expected_gr(self) -> None:
        for u_id, u_type, u_grs in self.test_gr_cases:
            unit = loader.load_unit(u_id)
            for stat, gr in u_grs.items():
                with self.subTest(u=unit.h_id, t=u_type, s=stat):
                    actual = unit.stats.of(u_type).of(stat).growth
                    self.assertEqual(gr, actual)


class UnitEvoTest(unittest.TestCase):
    test_evo_cases = [
        (300435, 300434),
    ]

    def test_expected_evo(self) -> None:
        for a_id, b_id in self.test_evo_cases:
            awakened = loader.load_unit(a_id)
            base = loader.load_unit(b_id)
            for t in UnitType:
                for s in StatType:
                    with self.subTest(u=awakened.h_id, t=t, s=s):
                        expected = base.stats.of(t).of(s).evo_bonus
                        actual = awakened.stats.of(t).of(s).evo_bonus
                        self.assertEqual(expected, actual)


class UnitCCInitialTest(unittest.TestCase):
    test_ini_cases = [
        # 6* Zwei
        (603013, ClassChangeType.VERTEX1, {
            StatType.HP: 130,
            StatType.MGC: 23,
        }),
    ]

    def test_expected_ini(self) -> None:
        # Unit type does not affect base values.
        t = UnitType.BAL
        for u_id, u_cc, u_ini in self.test_ini_cases:
            unit = loader.load_unit(u_id)
            for stat, ini in u_ini.items():
                with self.subTest(u=unit.h_id, c=u_cc, s=stat):
                    actual = unit.get_cc(u_cc).stats.of(t).of(stat).initial
                    self.assertEqual(ini, actual)


if __name__ == '__main__':
    loader = load_folder(Path('masterdata'))
    unittest.main()
