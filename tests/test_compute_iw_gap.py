from __future__ import annotations

import importlib.util
import json
import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("compute_iw_gap", ROOT / "analysis" / "compute_iw_gap.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ComputeIwGapTests(unittest.TestCase):
    def test_average_ranks_handle_ties(self) -> None:
        self.assertEqual(MODULE.average_ranks([10, 20, 20, 30]), [1.0, 2.5, 2.5, 4.0])

    def test_spearman_matches_frozen_report(self) -> None:
        report = json.loads((ROOT / "results" / "correlations_triple_model.json").read_text(encoding="utf-8"))
        x = [config["I"] for config in report["configs"]]
        y = [config["W"] for config in report["configs"]]
        rho, p_value, n = MODULE.spearman_rank(x, y)
        self.assertEqual(n, report["n"])
        self.assertTrue(math.isclose(rho, report["spearman_rho"], rel_tol=1e-12))
        self.assertTrue(math.isclose(p_value, report["spearman_p"], rel_tol=1e-12))


if __name__ == "__main__":
    unittest.main()
