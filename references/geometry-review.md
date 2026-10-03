# Manual geometry review

This helper only reads image bytes for SHA-256 and Pillow metadata. It never
reads pixels for segmentation, auto-detects a face, resizes, crops, composites,
or edits an image. It writes only a **new** JSON report, or prints JSON to stdout.
It cannot certify the accuracy of a person's landmark choices.

## Files and running

- `../scripts/geometry_review.py`: CLI and importable `review(...)` function
- `annotations.schema.json`: schema for **complete** annotations
- `baseline.template.json`, `images.template.json`: deliberately incomplete templates
- `tolerances.example.json`: proposed, explicitly configurable review limits
- `../tests/test_geometry_review.py`: synthetic fixtures and regression tests; no user images

The baseline must be the actual accepted master with manually inspected
landmarks, actual image dimensions, and matching SHA-256. There is no built-in
master geometry. Templates deliberately provide **no invented landmarks/hash**.
The example tolerances are proposals, not measured facts about the original.

```sh
python3 ../scripts/geometry_review.py --images reviewed-images.json \
  --baseline reviewed-master.json --config tolerances.example.json \
  --output new-review-report.json
python3 -m unittest discover -s ../tests -p 'test_*.py' -v
```

Python 3.10+ and Pillow are required. Existing report paths are refused. Relative
`local_path` values resolve against the containing annotation JSON file's
directory, independently for images and baseline, never the working directory.
For example, installed baseline data can refer to
`../local-references/my-reviewed-master.png`. Direct Python callers must explicitly pass
`images_base_dir=Path(...)` and `baseline_base_dir=Path(...)` for relative paths.

## Annotation convention

Coordinates are continuous image-edge coordinates: x in [0, width], y in
[0, height]. A bbox is `[x0, y0, x1, y1]`, with positive width and height. All
numbers must be finite. `annotation_source` must be `manual_visual_review`.

Use `hood_span: {x0, x1, y}` for the visible **cream hood** width on the horizontal
line through the panel center. Exclude hair, ears, ornaments, and dark external
patches that genuinely conceal the actual hood boundary. Recoloring the same physical hood does not create a new boundary: never use a cream-to-brown color transition as H merely to reduce its measured width. If a separate layer really obscures the hood, mark it unjudgeable. The row must match panel-center
y within half a pixel. If the boundary is obscured, do not guess it to force a
pass: set `hood_observation_status` to `unjudgeable`. Such images are incomplete.
`panel_observation_status` uses the same observed/unjudgeable convention.

`panel_bbox` bounds the single woven cloth inset. Its horizontal extent must
fit inside the hood span. Legacy `hood_bbox`/`shoulder_bbox` fields are optional,
validated if supplied, and **never used as a fallback**. A supplied hood bbox
must contain the panel. No hood-bottom or whole-head height is invented where
the hood merges into the torso.

Use optional `torso_span: {x0, x1, y}` for **core stuffed torso width between the
arm-attachment seams**, excluding hanging arms. Review a row in the strip from
panel bottom through panel bottom + 0.4 × panel height. Compare the same
panel-relative row as the master. Set `torso_observation_status` to `observed`
only if both seams can actually be identified; otherwise mark `unjudgeable`.
Torso-width criteria require an explicit baseline tolerance for
`torso_row_below_panel_to_panel_height`, so unmatched rows cannot silently pass.
The `shoulder_width_*` metric names are compatibility aliases for this core
torso span, not total arm span.

Optional `arm_span` plus `arm_observation_status` gives a separate full-arm-span
metric. Optional `crown_y` plus `crown_observation_status` gives crown-to-panel-
bottom distance, **not** a fabricated complete head height. Unknown optional
landmarks warn; they become incomplete only when configured criteria require
their metrics. Arm span is never substituted for missing core torso width.

Required manual semantic gates:

- `neck_visible`: any visible exposed thin/long neck
- `neck_column_visible`: any thin/long head-to-body pillar, including one hidden
  inside a tight collar or garment; review the head-to-torso strip
- `body_template_preserved`: fixed-master-like squat upper body, support and crop;
  clothing wraps the same stuffed bulk rather than introducing a tailored human
  shape. This required visual gate remains required even if torso seams cannot
  be measured. If unjudgeable, omit it and return incomplete; never infer it
  from absence of a neck
- `rim_all_sides_visible`: forehead, chin, both sides and all four corners
- `panel_unbroken`: one cloth inset; no hair/fur/mask crossing it or animal muzzle

Pass requires both neck flags false and all three positive structure/body flags true. Booleans are
explicit human observations, not inferred from coordinates. Missing gates mean
incomplete. An unjudgeable core hood/panel cannot be rescued by a numeric span.

## Outputs and decision scope

`geometry_estimate_pass` and `manual_structure_pass` are independent tri-state
values: true, false, or null (not enough valid information). Always read the
overall `status` and `exit_code`, not a metric in isolation. Any required missing
annotation/metric or unjudgeable core landmark prevents an overall pass. A
baseline missing core annotations also blocks candidate geometry acceptance.

The report includes each configured baseline delta, configured acceptance
bands, normalized ratios and panel centers, pixel landmark dimensions for
inspection, and group min/max/mean/spread with contributor counts. Group-only
criteria require observations from **every** candidate; a partial group cannot
pass. Group checks use image candidates, not an invented population estimate.

Only the configured metrics are tested. A panel-aspect-only config does **not**
enforce fixed mascot size or placement. The proposed fixed-size profile includes
hood width / circle diameter, panel / hood width, x/y panel position, panel
aspect, and core torso / hood width. Review those limits before adoption.

Baseline tolerances accept `absolute`, `relative`, or both. Allowed difference
is `max(absolute, abs(baseline_value) * relative)`. Absolute limits are differences
of the displayed normalized ratios, not percentage-relative error. A zero
baseline needs an absolute tolerance if nonzero deviation should be permitted.

Exit codes:

- 0: complete and passes the configured geometry plus manual gates
- 1: complete data, estimated geometry fails (manual failures also remain visible)
- 2: invalid data, hash/dimension mismatch, malformed JSON, bounds error, or I/O error
- 3: incomplete or unjudgeable required observations; known failed checks remain listed
- 4: complete geometry passes, manual structure fails

Invalid data takes precedence over incomplete; incomplete takes precedence over
failure codes. No claim of exact segmentation or original-reference precision
is made. Inspect the rendered avatar separately for material, identity,
accessory safety, alpha quality, and any structure the manual reviewer missed.
