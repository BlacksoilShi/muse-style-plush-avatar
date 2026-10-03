#!/usr/bin/env python3
"""Read-only geometry estimates from hash-bound MANUAL visual annotations.

No segmentation, detection, image decoding/editing, resizing, cropping or
compositing is performed. Coordinates describe continuous image edges:
0 <= x <= width, 0 <= y <= height. Bboxes are [x0, y0, x1, y1].
Exit: 0 complete pass; 1 estimated geometry failure; 2 invalid data/I/O;
3 incomplete annotations; 4 manual structure failure only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from typing import Any

from PIL import Image

WARNING = ("Manual visual landmark estimates, not automatic segmentation or exact "
           "ground truth. Occluded hood boundaries can be uncertain. A geometry "
           "pass does not certify face construction, material, identity or artistic quality.")
ANNOTATION_KEYS = {"id", "local_path", "sha256", "annotation_source", "image_width",
                   "image_height", "circle", "hood_bbox", "panel_bbox", "shoulder_bbox",
                   "hood_span", "torso_span", "arm_span", "crown_y",
                   "hood_observation_status", "panel_observation_status", "torso_observation_status",
                   "arm_observation_status", "crown_observation_status",
                   "neck_visible", "neck_column_visible", "body_template_preserved", "rim_all_sides_visible", "panel_unbroken",
                   "notes", "hood_occluded"}
CORE_KEYS = {"local_path", "sha256", "annotation_source", "image_width", "image_height", "circle",
             "panel_bbox", "hood_span", "hood_observation_status", "panel_observation_status",
             "neck_visible", "neck_column_visible", "body_template_preserved", "rim_all_sides_visible", "panel_unbroken"}
METRICS = {
    "panel_width_to_hood_width", "panel_aspect", "hood_width_to_circle_diameter",
    "shoulder_width_to_hood_width", "shoulder_width_to_circle_diameter",
    "torso_width_to_hood_width", "torso_width_to_circle_diameter",
    "torso_row_below_panel_to_panel_height", "full_arm_span_to_hood_width",
    "crown_to_panel_bottom_to_circle_diameter",
    "panel_width_to_circle_diameter", "panel_height_to_circle_diameter",
    "panel_center_x_to_canvas_width", "panel_center_y_to_canvas_height",
    "panel_center_x_offset_to_circle_diameter", "panel_center_y_offset_to_circle_diameter",
    "hood_center_x_offset_to_circle_diameter",
}
TORSO_METRICS = {"shoulder_width_to_hood_width", "shoulder_width_to_circle_diameter",
                 "torso_width_to_hood_width", "torso_width_to_circle_diameter"}


def finite_number(value: Any) -> bool:
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def sha256_stream(stream) -> str:
    digest = hashlib.sha256()
    stream.seek(0)
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()


def validate_annotation(raw: Any, label: str, base_dir: Path | None = None) -> dict:
    result = {"id": label, "errors": [], "missing_annotations": [], "metrics": None,
              "pixel_geometry": None, "manual_structure_pass": None, "warnings": [WARNING]}
    errors, missing = result["errors"], result["missing_annotations"]
    if not isinstance(raw, dict):
        errors.append("Annotation must be an object")
        return result
    if "id" in raw:
        if not isinstance(raw["id"], str) or not raw["id"].strip():
            errors.append("id must be a nonempty string")
        else:
            result["id"] = raw["id"]
    unknown = set(raw) - ANNOTATION_KEYS
    if unknown:
        errors.append("Unknown annotation keys: " + ", ".join(sorted(unknown)))
    required = CORE_KEYS
    missing.extend(sorted(key for key in required if key not in raw))
    if "annotation_source" in raw and raw["annotation_source"] != "manual_visual_review":
        errors.append("annotation_source must be manual_visual_review")
    if "notes" in raw:
        if not isinstance(raw["notes"], str):
            errors.append("notes must be a string")
        else:
            result["notes"] = raw["notes"]
    if "hood_occluded" in raw:
        if type(raw["hood_occluded"]) is not bool:
            errors.append("hood_occluded must be a boolean")
        elif raw["hood_occluded"]:
            result["warnings"].append("Hood is marked occluded: hood-span geometry is unjudgeable, not accepted.")
            missing.append("judgeable_hood_span")

    for subject in ("hood", "panel", "torso", "arm", "crown"):
        key = subject + "_observation_status"
        if key in raw and raw[key] not in ("observed", "unjudgeable"):
            errors.append(f"{key} must be observed or unjudgeable")
        if raw.get(key) == "unjudgeable":
            result["warnings"].append(f"{subject} landmark is unjudgeable; no metric from it can pass.")
            if subject in ("hood", "panel"):
                missing.append("judgeable_" + subject + "_landmark")
    actual_size = None
    path_value = raw.get("local_path")
    if "local_path" in raw:
        if not isinstance(path_value, str) or not path_value:
            errors.append("local_path must be a nonempty local file path")
        elif not Path(path_value).is_absolute() and base_dir is None:
            errors.append("Relative local_path requires its annotation JSON directory; CWD is not used")
        else:
            path = (Path(path_value) if Path(path_value).is_absolute() else base_dir / path_value).resolve()
            result["local_path"] = str(path)
            try:
                # One read-only stream binds metadata and hash to the same opened file.
                with path.open("rb") as stream:
                    observed_hash = sha256_stream(stream)
                    stream.seek(0)
                    image = Image.open(stream)
                    actual_size = image.size  # Metadata only. No load(), pixel edits or save().
                    # Keep the stream alive: closing Image can close the supplied stream.
                    if sha256_stream(stream) != observed_hash:
                        errors.append("Image changed during metadata verification")
                result["observed_sha256"] = observed_hash
                result["actual_image_dimensions"] = list(actual_size)
                if "sha256" in raw and raw["sha256"] != observed_hash:
                    errors.append("sha256 does not match actual image bytes")
            except (OSError, ValueError, Image.DecompressionBombError) as exc:
                errors.append(f"Cannot verify image metadata: {exc}")
    if "sha256" in raw and (not isinstance(raw["sha256"], str) or
                             not re.fullmatch(r"[0-9a-f]{64}", raw["sha256"])):
        errors.append("sha256 must be 64 lowercase hexadecimal characters")

    for index, key in enumerate(("image_width", "image_height")):
        if key in raw:
            if type(raw[key]) is not int or raw[key] <= 0:
                errors.append(f"{key} must be a positive integer")
            elif actual_size is not None and raw[key] != actual_size[index]:
                errors.append(f"{key} does not match actual image metadata")
    dimensions_valid = all(type(raw.get(key)) is int and raw[key] > 0
                           for key in ("image_width", "image_height"))
    w, h = (raw["image_width"], raw["image_height"]) if dimensions_valid else (None, None)
    boxes = {}
    for key in ("hood_bbox", "panel_bbox", "shoulder_bbox"):
        if key not in raw:
            continue
        value = raw[key]
        if not isinstance(value, list) or len(value) != 4 or not all(map(finite_number, value)):
            errors.append(f"{key} must contain four finite numbers")
            continue
        x0, y0, x1, y1 = value
        if not (x0 < x1 and y0 < y1):
            errors.append(f"{key} must have positive width and height")
        elif dimensions_valid and not (0 <= x0 < x1 <= w and 0 <= y0 < y1 <= h):
            errors.append(f"{key} is outside image edge bounds")
        else:
            boxes[key] = value
    if "hood_bbox" in boxes and "panel_bbox" in boxes:
        hx0, hy0, hx1, hy1 = boxes["hood_bbox"]
        px0, py0, px1, py1 = boxes["panel_bbox"]
        if not (hx0 <= px0 < px1 <= hx1 and hy0 <= py0 < py1 <= hy1):
            errors.append("panel_bbox must be nested inside hood_bbox")
    if "circle" in raw:
        circle = raw["circle"]
        if (not isinstance(circle, dict) or set(circle) != {"cx", "cy", "r"} or
                not all(finite_number(circle[k]) for k in ("cx", "cy", "r"))):
            errors.append("circle must contain only finite cx, cy, r values")
        else:
            cx, cy, r = circle["cx"], circle["cy"], circle["r"]
            if r <= 0:
                errors.append("circle.r must be positive")
            elif dimensions_valid and not (0 <= cx-r and cx+r <= w and 0 <= cy-r and cy+r <= h):
                errors.append("circle must fit entirely inside image edge bounds")

    for key in ("hood_span", "torso_span", "arm_span"):
        if key not in raw:
            continue
        span = raw[key]
        if (not isinstance(span, dict) or set(span) != {"x0", "x1", "y"} or
                not all(finite_number(span[k]) for k in ("x0", "x1", "y"))):
            errors.append(f"{key} must contain only finite x0, x1, y values")
            continue
        x0, x1, y = span["x0"], span["x1"], span["y"]
        if x0 >= x1 or (dimensions_valid and not (0 <= x0 < x1 <= w and 0 <= y <= h)):
            errors.append(f"{key} must have positive width inside image edge bounds")
        if "panel_bbox" in boxes:
            px0, py0, px1, py1 = boxes["panel_bbox"]
            if key == "hood_span":
                if abs(y - (py0+py1)/2) > 0.5:
                    errors.append("hood_span.y must be at panel center y (within half a pixel)")
                if not (x0 <= px0 < px1 <= x1):
                    errors.append("panel horizontal extent must be nested inside hood_span")
            elif key == "torso_span" and not (py1 <= y <= py1 + 0.4*(py1-py0)):
                errors.append("torso_span.y must be in panel-bottom to bottom+0.4*panel-height strip")
    if "crown_y" in raw:
        if not finite_number(raw["crown_y"]) or (dimensions_valid and not 0 <= raw["crown_y"] <= h):
            errors.append("crown_y must be finite and inside image bounds")
        elif "panel_bbox" in boxes and raw["crown_y"] > boxes["panel_bbox"][1]:
            errors.append("crown_y cannot be below panel top")

    structure_keys = ("neck_visible", "neck_column_visible", "body_template_preserved", "rim_all_sides_visible", "panel_unbroken")
    for key in structure_keys:
        if key in raw and type(raw[key]) is not bool:
            errors.append(f"{key} must be an explicit boolean")
    identity_keys = {"local_path", "sha256", "annotation_source", "image_width", "image_height"}
    if not errors and not (set(missing) & (identity_keys | set(structure_keys))):
        result["manual_structure_pass"] = (not raw["neck_visible"] and not raw["neck_column_visible"] and
                                           raw["rim_all_sides_visible"] and raw["panel_unbroken"] and raw["body_template_preserved"])
    if not errors and not (set(missing) & identity_keys):
        result["metrics"], result["pixel_geometry"] = calculate_metrics(raw)
    if "torso_span" not in raw or raw.get("torso_observation_status") != "observed":
        result["warnings"].append("No observed core torso span: torso metrics are unavailable; arm span is never substituted.")
    if "hood_bbox" in raw or "shoulder_bbox" in raw:
        result["warnings"].append("Legacy bboxes are validated only; no inferred hood bottom or armspan-based torso width is used.")
    return result


def calculate_metrics(a: dict) -> tuple[dict, dict]:
    values, pixels = {}, {}
    if "circle" not in a or "panel_bbox" not in a or a.get("panel_observation_status") != "observed":
        return values, pixels
    px0, py0, px1, py1 = a["panel_bbox"]
    pw, ph, pcx, pcy = px1-px0, py1-py0, (px0+px1)/2, (py0+py1)/2
    cx, cy, diameter = a["circle"]["cx"], a["circle"]["cy"], 2*a["circle"]["r"]
    values.update({
        "panel_aspect": pw/ph,
        "panel_width_to_circle_diameter": pw/diameter, "panel_height_to_circle_diameter": ph/diameter,
        "panel_center_x_to_canvas_width": pcx/a["image_width"],
        "panel_center_y_to_canvas_height": pcy/a["image_height"],
        "panel_center_x_offset_to_circle_diameter": (pcx-cx)/diameter,
        "panel_center_y_offset_to_circle_diameter": (pcy-cy)/diameter,
    })
    pixels.update(panel_width=pw, panel_height=ph, panel_center=[pcx, pcy], circle_diameter=diameter)
    if "hood_span" in a and a.get("hood_observation_status") == "observed" and not a.get("hood_occluded", False):
        hood = a["hood_span"]
        hw = hood["x1"]-hood["x0"]
        values.update(panel_width_to_hood_width=pw/hw, hood_width_to_circle_diameter=hw/diameter,
                      hood_center_x_offset_to_circle_diameter=((hood["x0"]+hood["x1"])/2-cx)/diameter)
        pixels.update(hood_width=hw, hood_row=hood["y"])
        if "torso_span" in a and a.get("torso_observation_status") == "observed":
            torso = a["torso_span"]
            tw = torso["x1"]-torso["x0"]
            values.update(shoulder_width_to_hood_width=tw/hw, shoulder_width_to_circle_diameter=tw/diameter,
                          torso_width_to_hood_width=tw/hw, torso_width_to_circle_diameter=tw/diameter,
                          torso_row_below_panel_to_panel_height=(torso["y"]-py1)/ph)
            pixels.update(torso_width=tw, torso_row=torso["y"])
        if "arm_span" in a and a.get("arm_observation_status") == "observed":
            values["full_arm_span_to_hood_width"] = (a["arm_span"]["x1"]-a["arm_span"]["x0"])/hw
    if "crown_y" in a and a.get("crown_observation_status") == "observed":
        values["crown_to_panel_bottom_to_circle_diameter"] = (py1-a["crown_y"])/diameter
        pixels["crown_to_panel_bottom"] = py1-a["crown_y"]
    return values, pixels


def validate_config(config: Any) -> list[str]:
    if not isinstance(config, dict):
        return ["Config must be an object"]
    errors = []
    if config.get("schema_version") != 1 or type(config.get("schema_version")) is not int:
        errors.append("Config schema_version must be integer 1")
    if set(config) - {"schema_version", "baseline_tolerances", "acceptance_bands", "group_max_spread", "notes"}:
        errors.append("Unknown config keys")
    if not isinstance(config.get("baseline_tolerances"), dict) or not config["baseline_tolerances"]:
        errors.append("Nonempty explicit baseline_tolerances are required; no assumed defaults")
    for section in ("baseline_tolerances", "acceptance_bands", "group_max_spread"):
        mapping = config.get(section, {})
        if not isinstance(mapping, dict):
            errors.append(f"{section} must be an object")
            continue
        for metric, value in mapping.items():
            if metric not in METRICS:
                errors.append(f"Unknown metric: {metric}")
            if section == "group_max_spread":
                if not finite_number(value) or value < 0:
                    errors.append(f"{section}.{metric} must be nonnegative and finite")
                continue
            allowed = {"absolute", "relative"} if section == "baseline_tolerances" else {"min", "max"}
            if not isinstance(value, dict) or not value or set(value) - allowed:
                errors.append(f"{section}.{metric} must contain {sorted(allowed)}")
                continue
            if not all(finite_number(v) for v in value.values()):
                errors.append(f"{section}.{metric} limits must be finite numbers")
            elif section == "baseline_tolerances" and any(v < 0 for v in value.values()):
                errors.append(f"{section}.{metric} tolerances cannot be negative")
            elif section == "acceptance_bands" and value.get("min", -math.inf) > value.get("max", math.inf):
                errors.append(f"{section}.{metric} min exceeds max")
    configured_metrics = set()
    for key in ("baseline_tolerances", "acceptance_bands", "group_max_spread"):
        if isinstance(config.get(key), dict):
            configured_metrics.update(config[key])
    baseline_rules = config.get("baseline_tolerances")
    if configured_metrics & TORSO_METRICS and (not isinstance(baseline_rules, dict) or
            "torso_row_below_panel_to_panel_height" not in baseline_rules):
        errors.append("Torso-width criteria require an explicit baseline tolerance for torso_row_below_panel_to_panel_height")
    return errors


def tri_all(values: list) -> bool | None:
    if False in values:
        return False
    if not values or None in values:
        return None
    return True


def compare_metrics(metrics: dict, baseline: dict, config: dict) -> dict:
    checks, missing_metrics = {}, []
    for metric, tolerances in config["baseline_tolerances"].items():
        if metric not in metrics or metric not in baseline:
            missing_metrics.append(metric)
            checks[metric] = {"pass": None, "reason": "Required metric unavailable in image or baseline"}
            continue
        reference, value = baseline[metric], metrics[metric]
        delta = value-reference
        limit = max(tolerances.get("absolute", 0), abs(reference)*tolerances.get("relative", 0))
        checks[metric] = {"value": value, "baseline": reference, "signed_delta": delta,
                          "absolute_delta": abs(delta), "allowed_delta": limit,
                          "relative_delta": delta/abs(reference) if reference else None,
                          "pass": abs(delta) <= limit + 1e-12}
    bands = {}
    for metric, band in config.get("acceptance_bands", {}).items():
        if metric not in metrics:
            missing_metrics.append(metric)
            bands[metric] = {"pass": None, "reason": "Required metric unavailable"}
            continue
        value = metrics[metric]
        bands[metric] = {"value": value, **band,
                         "pass": band.get("min", -math.inf) <= value <= band.get("max", math.inf)}
    return {"baseline_checks": checks, "acceptance_band_checks": bands,
            "missing_required_metrics": sorted(set(missing_metrics)),
            "geometry_estimate_pass": None if missing_metrics else all(x["pass"] for x in [*checks.values(), *bands.values()])}


def review(images_document: Any, baseline_document: Any, config: Any, *,
           images_base_dir: Path | None = None, baseline_base_dir: Path | None = None) -> tuple[dict, int]:
    report = {"schema_version": 1, "warning": WARNING, "errors": [], "images": [], "baseline": None}
    errors = report["errors"]
    errors.extend(validate_config(config))
    for document, key, label in ((images_document, "images", "Images"), (baseline_document, "image", "Baseline")):
        if not isinstance(document, dict) or set(document) != {"schema_version", key}:
            errors.append(f"{label} document requires only schema_version and {key}")
        elif type(document["schema_version"]) is not int or document["schema_version"] != 1:
            errors.append(f"{label} schema_version must be integer 1")
    if errors:
        report.update(status="invalid_data", exit_code=2, geometry_estimate_pass=None, manual_structure_pass=None)
        return report, 2
    if not isinstance(images_document["images"], list) or not images_document["images"]:
        report["errors"].append("images must be a nonempty array")
        report.update(status="invalid_data", exit_code=2, geometry_estimate_pass=None, manual_structure_pass=None)
        return report, 2
    baseline = validate_annotation(baseline_document["image"], "baseline", baseline_base_dir)
    items = [validate_annotation(a, f"image_{i}", images_base_dir) for i, a in enumerate(images_document["images"])]
    report["baseline"], report["images"] = baseline, items
    for key in ("id", "local_path"):
        seen = set()
        for item in items:
            value = item.get(key)
            if value is not None and value in seen:
                item["errors"].append(f"Duplicate image {key}: {value}")
            seen.add(value)
    for item in items:
        item.update(geometry_estimate_pass=None, baseline_checks={}, acceptance_band_checks={}, missing_required_metrics=[])
        if not item["errors"] and item["metrics"] and baseline["metrics"] and not baseline["errors"]:
            item.update(compare_metrics(item["metrics"], baseline["metrics"], config))
        if item["missing_annotations"]:
            item["geometry_estimate_pass"] = None
        if baseline["errors"] or baseline["missing_annotations"]:
            item["geometry_estimate_pass"] = None
            item["blocked_by_baseline"] = True
        # Missing structure annotations never turn the whole image into an accepted image.
        item["status"] = ("invalid_data" if item["errors"] else "incomplete" if item["missing_annotations"] or item["missing_required_metrics"]
                          else "failed" if item["geometry_estimate_pass"] is False or item["manual_structure_pass"] is False
                          else "incomplete" if item["geometry_estimate_pass"] is None else "pass")

    eligible = [x for x in items if not x["errors"] and x["metrics"]]
    group = {"total_image_count": len(items), "valid_geometry_count": len(eligible),
             "statistics": {}, "spread_checks": {}, "geometry_estimate_pass": None}
    for metric in sorted(METRICS):
        values = [x["metrics"][metric] for x in eligible if metric in x["metrics"]]
        if values:
            group["statistics"][metric] = {"count": len(values), "min": min(values), "max": max(values),
                                            "mean": sum(values)/len(values), "spread": max(values)-min(values)}
    for metric, limit in config.get("group_max_spread", {}).items():
        stats = group["statistics"].get(metric)
        group["spread_checks"][metric] = {"observed_spread": stats["spread"] if stats else None,
                                           "allowed_spread": limit,
                                           "pass": stats["spread"] <= limit + 1e-12 if stats and stats["count"] == len(items) else None}
    all_annotations = [baseline, *items]
    invalid = any(x["errors"] for x in all_annotations)
    incomplete = (any(x["missing_annotations"] for x in all_annotations) or
                  any(x["missing_required_metrics"] for x in items) or
                  any(x["pass"] is None for x in group["spread_checks"].values()))
    if not invalid and not incomplete and group["spread_checks"]:
        group["geometry_estimate_pass"] = tri_all([x["pass"] for x in group["spread_checks"].values()])
    group["status"] = ("invalid_data" if invalid else "incomplete" if incomplete
                       else "not_requested" if not group["spread_checks"]
                       else "pass" if group["geometry_estimate_pass"] else "failed")
    report["group"] = group
    geometry = tri_all([x["geometry_estimate_pass"] for x in items])
    if group["spread_checks"]:
        geometry = tri_all([geometry, group["geometry_estimate_pass"]])
    structure = tri_all([x["manual_structure_pass"] for x in all_annotations])
    report["geometry_estimate_pass"], report["manual_structure_pass"] = geometry, structure
    if invalid:
        status, code = "invalid_data", 2
    elif incomplete or geometry is None or structure is None:
        status, code = "incomplete", 3
    elif geometry is False:
        status, code = "geometry_estimate_fail", 1
    elif structure is False:
        status, code = "manual_structure_fail", 4
    else:
        status, code = "pass", 0
    report.update(status=status, exit_code=code, criteria=config)
    return report, code


def read_json(path: Path) -> Any:
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f"Nonfinite JSON value: {x}")))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, required=True, help="Manual annotations document")
    parser.add_argument("--baseline", type=Path, required=True, help="Actual annotated master document")
    parser.add_argument("--config", type=Path, required=True, help="Explicit tolerances; no assumed master geometry")
    parser.add_argument("--output", type=Path, help="New report JSON path; existing files are never overwritten")
    args = parser.parse_args(argv)
    try:
        documents = [read_json(p) for p in (args.images, args.baseline, args.config)]
        report, code = review(*documents, images_base_dir=args.images.resolve().parent,
                              baseline_base_dir=args.baseline.resolve().parent)
        if args.output:
            # Refuse even a presently missing source path before any output is opened.
            protected = {p.resolve() for p in (args.images, args.baseline, args.config)}
            for doc, source in zip(documents[:2], (args.images, args.baseline)):
                if isinstance(doc, dict):
                    entries = doc.get("images", [doc.get("image")])
                    if isinstance(entries, list):
                        for item in entries:
                            if isinstance(item, dict) and isinstance(item.get("local_path"), str):
                                candidate = Path(item["local_path"])
                                protected.add((candidate if candidate.is_absolute() else source.resolve().parent / candidate).resolve())
            if args.output.resolve() in protected:
                raise ValueError("Output must not be an input image or annotation/config file")
            with args.output.open("x", encoding="utf-8") as stream:
                json.dump(report, stream, indent=2, allow_nan=False)
                stream.write("\n")
        else:
            print(json.dumps(report, indent=2, allow_nan=False))
        return code
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "invalid_data", "exit_code": 2, "errors": [str(exc)],
                          "geometry_estimate_pass": None, "manual_structure_pass": None,
                          "warning": WARNING}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
