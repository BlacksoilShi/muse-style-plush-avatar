"""All test images are newly created synthetic fixtures; no user images are read."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image

MODULE = Path(__file__).parents[1] / "scripts" / "geometry_review.py"
spec = importlib.util.spec_from_file_location("geometry_review", MODULE)
geometry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geometry)


class GeometryReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.baseline = {"schema_version": 1, "image": self.annotation("master")}
        self.images = {"schema_version": 1, "images": [self.annotation("candidate")]}
        self.config = {"schema_version": 1, "baseline_tolerances": {
            "panel_aspect": {"absolute": 0.06},
            "panel_width_to_hood_width": {"absolute": 0.03},
            "hood_width_to_circle_diameter": {"absolute": 0.03},
            "panel_center_x_offset_to_circle_diameter": {"absolute": 0.015},
            "panel_center_y_offset_to_circle_diameter": {"absolute": 0.02},
            "torso_width_to_hood_width": {"absolute": 0.05},
            "torso_row_below_panel_to_panel_height": {"absolute": 0.02}},
            "group_max_spread": {"panel_center_x_offset_to_circle_diameter": 0.01}}

    def tearDown(self):
        self.temp.cleanup()

    def annotation(self, name, scale=1):
        path = self.root / (name + ".png")
        # Synthetic opaque square, not a rendered face and not a canonical master.
        Image.new("RGBA", (1000*scale, 1000*scale), (140, 170, 190, 255)).save(path)
        return {"id": name, "local_path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "annotation_source": "manual_visual_review", "image_width": 1000*scale, "image_height": 1000*scale,
                "circle": {"cx": 500*scale, "cy": 500*scale, "r": 480*scale},
                "panel_bbox": [v*scale for v in (285, 300, 715, 600)],
                "hood_span": {"x0": 200*scale, "x1": 800*scale, "y": 450*scale},
                "torso_span": {"x0": 150*scale, "x1": 850*scale, "y": 660*scale},
                "hood_observation_status": "observed", "panel_observation_status": "observed",
                "torso_observation_status": "observed", "neck_visible": False, "neck_column_visible": False,
                "body_template_preserved": True,
                "rim_all_sides_visible": True, "panel_unbroken": True,
                "notes": "Synthetic schema/math fixture; not real visual evidence or user/master geometry."}

    def run_review(self):
        return geometry.review(self.images, self.baseline, self.config)

    def test_equal_normalized_geometry_passes(self):
        report, code = self.run_review()
        self.assertEqual(code, 0)
        self.assertTrue(report["geometry_estimate_pass"])
        self.assertTrue(report["manual_structure_pass"])
        self.assertAlmostEqual(report["images"][0]["metrics"]["panel_aspect"], 430/300)

    def test_different_resolution_same_proportions_passes(self):
        self.images["images"] = [self.annotation("large", 2)]
        self.assertEqual(self.run_review()[1], 0)

    def test_drift_fails_geometry(self):
        self.images["images"][0]["hood_span"]["x1"] = 900
        report, code = self.run_review()
        self.assertEqual(code, 1)
        self.assertFalse(report["geometry_estimate_pass"])
        self.assertTrue(report["manual_structure_pass"])

    def test_hash_mismatch_is_invalid(self):
        self.images["images"][0]["sha256"] = "0"*64
        self.assertEqual(self.run_review()[1], 2)

    def test_dimensions_must_match_real_metadata(self):
        self.images["images"][0]["image_width"] = 1001
        self.assertEqual(self.run_review()[1], 2)

    def test_panel_must_fit_inside_hood_span(self):
        self.images["images"][0]["panel_bbox"][0] = 100
        self.assertEqual(self.run_review()[1], 2)

    def test_optional_legacy_bbox_nesting_is_validated(self):
        self.images["images"][0]["hood_bbox"] = [300, 200, 900, 800]
        self.assertEqual(self.run_review()[1], 2)

    def test_circle_outside_canvas_is_invalid(self):
        self.images["images"][0]["circle"]["r"] = 501
        self.assertEqual(self.run_review()[1], 2)

    def test_boolean_is_not_numeric_coordinate(self):
        self.images["images"][0]["hood_span"]["x0"] = True
        self.assertEqual(self.run_review()[1], 2)

    def test_nan_is_invalid(self):
        self.images["images"][0]["panel_bbox"][0] = float("nan")
        self.assertEqual(self.run_review()[1], 2)

    def test_missing_panel_is_incomplete_not_pass(self):
        del self.images["images"][0]["panel_bbox"]
        report, code = self.run_review()
        self.assertEqual(code, 3)
        self.assertIsNone(report["geometry_estimate_pass"])

    def test_missing_manual_gate_is_incomplete(self):
        del self.images["images"][0]["neck_column_visible"]
        report, code = self.run_review()
        self.assertEqual(code, 3)
        self.assertIsNone(report["manual_structure_pass"])

    def test_clothed_neck_column_fails_semantics(self):
        self.images["images"][0]["neck_column_visible"] = True
        report, code = self.run_review()
        self.assertEqual(code, 4)
        self.assertTrue(report["geometry_estimate_pass"])
        self.assertFalse(report["manual_structure_pass"])

    def test_changed_body_template_fails_manual_structure(self):
        self.images["images"][0]["body_template_preserved"] = False
        report, code = self.run_review()
        self.assertEqual(code, 4)
        self.assertFalse(report["manual_structure_pass"])

    def test_missing_body_gate_is_incomplete_even_without_torso_metric(self):
        del self.images["images"][0]["body_template_preserved"]
        self.config = {"schema_version": 1, "baseline_tolerances": {"panel_aspect": {"absolute": 0.06}}}
        report, code = self.run_review()
        self.assertEqual(code, 3)
        self.assertIsNone(report["manual_structure_pass"])

    def test_rim_and_panel_gate_failures(self):
        for gate in ("rim_all_sides_visible", "panel_unbroken"):
            with self.subTest(gate=gate):
                self.images["images"][0][gate] = False
                self.assertEqual(self.run_review()[1], 4)
                self.images["images"][0][gate] = True

    def test_occlusion_cannot_pass_even_with_numeric_span(self):
        self.images["images"][0]["hood_observation_status"] = "unjudgeable"
        report, code = self.run_review()
        self.assertEqual(code, 3)
        self.assertIsNone(report["geometry_estimate_pass"])
        self.assertNotIn("hood_width_to_circle_diameter", report["images"][0]["metrics"])

    def test_old_occlusion_flag_also_blocks(self):
        self.images["images"][0]["hood_occluded"] = True
        self.assertEqual(self.run_review()[1], 3)

    def test_missing_optional_torso_does_not_fail_core(self):
        del self.images["images"][0]["torso_span"]
        del self.config["baseline_tolerances"]["torso_width_to_hood_width"]
        del self.config["baseline_tolerances"]["torso_row_below_panel_to_panel_height"]
        report, code = self.run_review()
        self.assertEqual(code, 0)
        self.assertTrue(any("No observed core torso" in w for w in report["images"][0]["warnings"]))

    def test_missing_required_torso_is_incomplete(self):
        del self.images["images"][0]["torso_span"]
        report, code = self.run_review()
        self.assertEqual(code, 3)
        self.assertIn("torso_width_to_hood_width", report["images"][0]["missing_required_metrics"])

    def test_unknown_torso_never_substitutes_armspan(self):
        a = self.images["images"][0]
        a["torso_observation_status"] = "unjudgeable"
        a["arm_span"] = {"x0": 50, "x1": 950, "y": 680}
        a["arm_observation_status"] = "observed"
        report, code = self.run_review()
        self.assertEqual(code, 3)
        self.assertNotIn("torso_width_to_hood_width", report["images"][0]["metrics"])
        self.assertAlmostEqual(report["images"][0]["metrics"]["full_arm_span_to_hood_width"], 1.5)

    def test_torso_row_must_match_master_relative_row(self):
        self.images["images"][0]["torso_span"]["y"] = 710
        self.assertEqual(self.run_review()[1], 1)

    def test_torso_row_outside_strip_invalid(self):
        self.images["images"][0]["torso_span"]["y"] = 800
        self.assertEqual(self.run_review()[1], 2)

    def test_hood_row_must_match_panel_center(self):
        self.images["images"][0]["hood_span"]["y"] = 460
        self.assertEqual(self.run_review()[1], 2)

    def test_baseline_with_unjudgeable_hood_blocks_all(self):
        self.baseline["image"]["hood_observation_status"] = "unjudgeable"
        self.assertEqual(self.run_review()[1], 3)

    def test_partial_baseline_never_displays_geometry_true(self):
        self.config = {"schema_version": 1, "baseline_tolerances": {"panel_aspect": {"absolute": 0}}}
        del self.baseline["image"]["hood_span"]
        report, code = self.run_review()
        self.assertEqual(code, 3)
        self.assertIsNone(report["geometry_estimate_pass"])
        self.assertIsNone(report["images"][0]["geometry_estimate_pass"])
        self.assertEqual(report["images"][0]["status"], "incomplete")

    def test_huge_integer_coordinate_is_invalid_not_crash(self):
        self.images["images"][0]["hood_span"]["x0"] = 10**1000
        self.assertEqual(self.run_review()[1], 2)

    def test_huge_integer_tolerance_is_invalid_not_crash(self):
        self.config["baseline_tolerances"]["panel_aspect"]["absolute"] = 10**1000
        self.assertEqual(self.run_review()[1], 2)

    def test_group_only_optional_metric_missing_is_incomplete(self):
        self.config["group_max_spread"] = {"crown_to_panel_bottom_to_circle_diameter": 0.02}
        report, code = self.run_review()
        self.assertEqual(code, 3)
        self.assertIsNone(report["group"]["geometry_estimate_pass"])
        self.assertIsNone(report["geometry_estimate_pass"])

    def test_group_spread_can_fail_individually_passing_images(self):
        self.images["images"].append(self.annotation("second"))
        for a, delta in zip(self.images["images"], (-8, 8)):
            a["panel_bbox"][0] += delta
            a["panel_bbox"][2] += delta
        report, code = self.run_review()
        self.assertEqual(code, 1)
        self.assertTrue(all(a["geometry_estimate_pass"] for a in report["images"]))
        self.assertFalse(report["group"]["geometry_estimate_pass"])

    def test_partial_group_is_incomplete(self):
        self.images["images"].append(self.annotation("second"))
        del self.images["images"][1]["panel_bbox"]
        report, code = self.run_review()
        self.assertEqual(code, 3)
        self.assertEqual(report["group"]["statistics"]["panel_aspect"]["count"], 1)
        self.assertIsNone(report["group"]["geometry_estimate_pass"])

    def test_empty_config_does_not_silently_pass(self):
        self.config["baseline_tolerances"] = {}
        self.assertEqual(self.run_review()[1], 2)

    def test_torso_width_requires_row_tolerance(self):
        del self.config["baseline_tolerances"]["torso_row_below_panel_to_panel_height"]
        self.assertEqual(self.run_review()[1], 2)

    def test_duplicate_image_invalid(self):
        self.images["images"].append(copy.deepcopy(self.images["images"][0]))
        self.assertEqual(self.run_review()[1], 2)

    def test_wrong_annotation_source_invalid(self):
        self.images["images"][0]["annotation_source"] = "auto_detected"
        self.assertEqual(self.run_review()[1], 2)

    def test_read_only_image_bytes_unchanged(self):
        paths = [Path(self.baseline["image"]["local_path"]), Path(self.images["images"][0]["local_path"])]
        before = [p.read_bytes() for p in paths]
        self.run_review()
        self.assertEqual(before, [p.read_bytes() for p in paths])

    def test_relative_paths_use_annotation_directory(self):
        a = self.images["images"][0]
        a["local_path"] = "candidate.png"
        self.baseline["image"]["local_path"] = "master.png"
        report, code = geometry.review(self.images, self.baseline, self.config,
                                       images_base_dir=self.root, baseline_base_dir=self.root)
        self.assertEqual(code, 0)
        self.assertEqual(report["images"][0]["local_path"], str(self.root / "candidate.png"))

    def test_relative_path_without_base_does_not_use_cwd(self):
        self.images["images"][0]["local_path"] = "candidate.png"
        self.assertEqual(self.run_review()[1], 2)

    def test_cli_relative_parent_path(self):
        annotations = self.root / "annotations"
        annotations.mkdir()
        docs = {"images": copy.deepcopy(self.images), "baseline": copy.deepcopy(self.baseline), "config": self.config}
        docs["images"]["images"][0]["local_path"] = "../candidate.png"
        docs["baseline"]["image"]["local_path"] = "../master.png"
        args = [sys.executable, str(MODULE)]
        for key, doc in docs.items():
            path = annotations / (key + ".json")
            path.write_text(json.dumps(doc))
            args += ["--"+key, str(path)]
        result = subprocess.run(args, cwd="/", capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_relative_tolerance_uses_baseline_magnitude(self):
        result = geometry.compare_metrics({"panel_aspect": 1.51}, {"panel_aspect": 1.5},
                 {"baseline_tolerances": {"panel_aspect": {"relative": 0.01}}})
        self.assertTrue(result["geometry_estimate_pass"])
        self.assertEqual(result["baseline_checks"]["panel_aspect"]["allowed_delta"], 0.015)

    def test_acceptance_band_failure(self):
        self.config["acceptance_bands"] = {"panel_aspect": {"min": 1.6, "max": 1.7}}
        self.assertEqual(self.run_review()[1], 1)

    def cli(self, output=None):
        args = [sys.executable, str(MODULE)]
        for flag, value in (("images", self.images), ("baseline", self.baseline), ("config", self.config)):
            path = self.root / (flag + ".json")
            path.write_text(json.dumps(value))
            args += ["--"+flag, str(path)]
        if output:
            args += ["--output", str(output)]
        return subprocess.run(args, capture_output=True, text=True)

    def test_cli_writes_new_json_report(self):
        output = self.root / "report.json"
        result = self.cli(output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(output.read_text())["status"], "pass")

    def test_cli_cannot_overwrite_image(self):
        output = Path(self.images["images"][0]["local_path"])
        before = output.read_bytes()
        self.assertEqual(self.cli(output).returncode, 2)
        self.assertEqual(output.read_bytes(), before)

    def test_cli_cannot_overwrite_existing_report(self):
        output = self.root / "existing.json"
        output.write_text("keep me")
        self.assertEqual(self.cli(output).returncode, 2)
        self.assertEqual(output.read_text(), "keep me")

    def test_duplicate_json_keys_rejected(self):
        path = self.root / "duplicate.json"
        path.write_text('{"schema_version":1,"schema_version":2}')
        with self.assertRaisesRegex(ValueError, "Duplicate JSON"):
            geometry.read_json(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
