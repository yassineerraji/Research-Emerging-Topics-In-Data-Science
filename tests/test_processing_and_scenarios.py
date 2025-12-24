import unittest

import pandas as pd

from src.io import load_iea_annex, load_owid_raw
from src.processing import process_iea_data, process_owid_data, build_canonical_dataset
from src.scenarios import run_scenario_analysis
from src.config import IEA_ALLOWED_FLOWS, EMISSIONS_UNIT, BASELINE_SCENARIO, NET_ZERO_SCENARIO


class TestProcessingAndScenarios(unittest.TestCase):
    def test_iea_processing_is_nonempty_and_unique(self):
        iea_raw = load_iea_annex()
        iea = process_iea_data(iea_raw)

        self.assertFalse(iea.empty)
        self.assertTrue(set(iea["sector"].unique()).issubset(set(IEA_ALLOWED_FLOWS)))
        self.assertTrue((iea["unit"] == EMISSIONS_UNIT).all())

        dup = iea.groupby(["year", "scenario", "sector"]).size().max()
        self.assertEqual(int(dup), 1)

    def test_scenario_annualization_total_has_full_years(self):
        owid_raw = load_owid_raw()
        iea_raw = load_iea_annex()

        canonical = build_canonical_dataset(process_owid_data(owid_raw), process_iea_data(iea_raw))
        results = run_scenario_analysis(canonical)

        traj = results["trajectories"]
        total = traj[traj["sector"] == "Total energy supply"].copy()

        for scen in [BASELINE_SCENARIO, NET_ZERO_SCENARIO]:
            years = total[total["scenario"] == scen]["year"].unique()
            self.assertTrue(len(years) > 0)
            self.assertEqual(int(years.min()), 2020)
            self.assertEqual(int(years.max()), 2050)


if __name__ == "__main__":
    unittest.main()


