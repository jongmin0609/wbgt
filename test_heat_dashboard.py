import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from measurement_store import (
    read_measurement,
    validate_measurement,
    validate_profile,
    write_measurement,
)
from metabolism import calculate_calories, estimate_vo2
from utils import RISK_GUIDANCE, get_risk_guidance, should_trigger_alert
from wbgt_risk import calculate_heat_risk


class MetabolismTests(unittest.TestCase):
    def test_example_profile_produces_expected_vo2_and_calories(self):
        vo2 = estimate_vo2(age=25, sex="male", hr=130)

        self.assertAlmostEqual(vo2, 30.0)
        self.assertAlmostEqual(calculate_calories(vo2, weight=70), 10.5)

    def test_profile_and_heart_rate_validation(self):
        with self.assertRaisesRegex(ValueError, "나이는"):
            estimate_vo2(age=0, sex="male", hr=130)

        with self.assertRaisesRegex(ValueError, "심박수는"):
            estimate_vo2(age=25, sex="male", hr=0)

        with self.assertRaisesRegex(ValueError, "비정상적으로"):
            estimate_vo2(age=25, sex="male", hr=216)

        with self.assertRaisesRegex(ValueError, "성별은"):
            estimate_vo2(age=25, sex="unknown", hr=130)

    def test_weight_validation(self):
        with self.assertRaisesRegex(ValueError, "체중은"):
            calculate_calories(vo2=30, weight=0)


class HeatRiskTests(unittest.TestCase):
    def test_example_measurement_is_high_workload_and_very_dangerous(self):
        risk, workload = calculate_heat_risk(wbgt=31.2, kcal=10.5)

        self.assertEqual(workload, "고강도")
        self.assertEqual(risk, "매우 위험")

    def test_risk_thresholds_cover_dashboard_labels(self):
        self.assertEqual(calculate_heat_risk(wbgt=27.9, kcal=2), ("안전", "저강도"))
        self.assertEqual(calculate_heat_risk(wbgt=28, kcal=2), ("주의", "저강도"))
        self.assertEqual(calculate_heat_risk(wbgt=28, kcal=6), ("위험", "고강도"))
        self.assertEqual(calculate_heat_risk(wbgt=31, kcal=2), ("위험", "저강도"))
        self.assertEqual(calculate_heat_risk(wbgt=31, kcal=6), ("매우 위험", "고강도"))
        self.assertEqual(calculate_heat_risk(wbgt=33, kcal=6), ("즉시 작업중지", "고강도"))

    def test_heat_risk_rejects_invalid_inputs(self):
        with self.assertRaisesRegex(ValueError, "WBGT"):
            calculate_heat_risk(wbgt=61, kcal=2)

        with self.assertRaisesRegex(ValueError, "칼로리"):
            calculate_heat_risk(wbgt=30, kcal=-1)


class GuidanceTests(unittest.TestCase):
    def test_every_risk_label_has_rest_action_and_tone(self):
        for risk in ("안전", "주의", "위험", "매우 위험", "즉시 작업중지"):
            with self.subTest(risk=risk):
                guidance = get_risk_guidance(risk)

                self.assertEqual(guidance, RISK_GUIDANCE[risk])
                self.assertTrue(guidance["rest_time"])
                self.assertTrue(guidance["action_text"])
                self.assertTrue(guidance["tone"])

    def test_unknown_risk_label_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "알 수 없는"):
            get_risk_guidance("미정")

    def test_manager_alert_starts_at_danger_level(self):
        self.assertFalse(should_trigger_alert("안전"))
        self.assertFalse(should_trigger_alert("주의"))
        self.assertTrue(should_trigger_alert("위험"))
        self.assertTrue(should_trigger_alert("매우 위험"))
        self.assertTrue(should_trigger_alert("즉시 작업중지"))


class MeasurementStoreTests(unittest.TestCase):
    def test_written_pc_measurement_is_shared_from_json(self):
        with TemporaryDirectory() as temp_dir:
            measurement_path = Path(temp_dir) / "current_measurement.json"
            missing_sample_path = Path(temp_dir) / "missing.csv"

            write_measurement(
                heart_rate=144,
                wbgt=32.4,
                age=38,
                weight=82.5,
                sex="female",
                measurement_path=measurement_path,
                updated_at="2026-05-23T11:20:30+09:00",
            )
            measurement = read_measurement(measurement_path, missing_sample_path)

        self.assertEqual(measurement["heart_rate"], 144)
        self.assertEqual(measurement["wbgt"], 32.4)
        self.assertEqual(measurement["age"], 38)
        self.assertEqual(measurement["weight"], 82.5)
        self.assertEqual(measurement["sex"], "female")
        self.assertEqual(measurement["source"], "computer")
        self.assertEqual(measurement["updated_at"], "2026-05-23T11:20:30+09:00")

    def test_sample_measurement_is_used_before_pc_input_exists(self):
        with TemporaryDirectory() as temp_dir:
            sample_path = Path(temp_dir) / "sample.csv"
            sample_path.write_text(
                "time,heart_rate,wbgt\n10:01,121,30.4\n10:02,133,31.8\n",
                encoding="utf-8",
            )
            measurement = read_measurement(
                Path(temp_dir) / "current_measurement.json",
                sample_path,
            )

        self.assertEqual(measurement["heart_rate"], 133)
        self.assertEqual(measurement["wbgt"], 31.8)
        self.assertEqual(measurement["age"], 25)
        self.assertEqual(measurement["weight"], 70.0)
        self.assertEqual(measurement["sex"], "male")
        self.assertEqual(measurement["source"], "sample")
        self.assertEqual(measurement["updated_at"], "10:02")

    def test_external_measurement_validation_rejects_bad_ranges(self):
        with self.assertRaisesRegex(ValueError, "심박수"):
            validate_measurement(0, 31.2)

        with self.assertRaisesRegex(ValueError, "WBGT"):
            validate_measurement(130, 61)

        with self.assertRaisesRegex(ValueError, "나이"):
            validate_profile(0, 70, "male")

        with self.assertRaisesRegex(ValueError, "체중"):
            validate_profile(25, 0, "male")

        with self.assertRaisesRegex(ValueError, "성별"):
            validate_profile(25, 70, "unknown")

    def test_changed_profile_changes_heat_risk_calculation_inputs(self):
        high_vo2 = estimate_vo2(age=25, sex="male", hr=130)
        lower_vo2 = estimate_vo2(age=25, sex="female", hr=130)
        high_kcal = calculate_calories(high_vo2, weight=70)
        lower_kcal = calculate_calories(lower_vo2, weight=40)

        self.assertEqual(calculate_heat_risk(wbgt=31, kcal=high_kcal), ("매우 위험", "고강도"))
        self.assertEqual(calculate_heat_risk(wbgt=31, kcal=lower_kcal), ("위험", "중강도"))


if __name__ == "__main__":
    unittest.main()
