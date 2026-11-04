import sys
from pathlib import Path
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import preflight
import data_profile
import check_results

class ScriptTests(unittest.TestCase):
    def test_preflight_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertTrue(any(c["check"] == "write_permission" and c["status"] == "PASS" for c in preflight.inspect(Path(folder))))
    def test_preflight_missing_directory(self):
        self.assertTrue(any(c["status"] == "FAIL" for c in preflight.inspect(Path("/missing-cofa-path-xyz"))))
    def test_csv_missing_and_duplicates(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "a.csv"
            p.write_text("n,x\n1,a\n2,\n1,a\n", encoding="utf-8")
            r = data_profile.profile(p)
            self.assertEqual((r["missing"]["x"], r["duplicate_rows"]), (1,1))
            self.assertEqual(r["numeric"]["n"]["numeric_ratio"], 1.0)
    def test_large_csv_full_numeric_ratio(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "big.csv"
            p.write_text("n\n" + "1\n" * 601, encoding="utf-8")
            self.assertEqual(data_profile.profile(p)["numeric"]["n"]["numeric_ratio"], 1.0)
    def test_json_profile(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "a.json"
            p.write_text('[{"a":2},{"b":"3"}]', encoding="utf-8")
            self.assertEqual(data_profile.profile(p)["missing"]["a"], 1)
    def test_json_reject_object_root(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "a.json"
            p.write_text('{"a":2}', encoding="utf-8")
            with self.assertRaises(ValueError): data_profile.profile(p)
    def test_no_tests_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(check_results.check({"checks":[]}, Path(folder))["status"], "FAIL")
    def test_zero_test_count_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            m = {"checks":[{"command":"true","test_count":0,"exit_code":0,"status":"passed"}]}
            self.assertEqual(check_results.check(m, Path(folder))["status"], "FAIL")
    def test_output_exists_and_missing(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "ok.txt").write_text("yes")
            m = {"checks":[{"command":"python -m unittest","test_count":1,"exit_code":0,"status":"passed"}],"required_outputs":["ok.txt"]}
            self.assertEqual(check_results.check(m, root)["status"], "PASS")
            m["required_outputs"] = ["missing.txt"]
            self.assertEqual(check_results.check(m, root)["status"], "FAIL")
            m["required_outputs"] = ["../escape.txt"]
            self.assertEqual(check_results.check(m, root)["status"], "FAIL")

if __name__ == "__main__":
    unittest.main()
