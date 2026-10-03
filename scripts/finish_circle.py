#!/usr/bin/env python3
"""Reviewed circular alpha finishing, offline; Pillow only. Never modify source RGB."""
import argparse
import io
import json
import math
from pathlib import Path
from PIL import Image, ImageChops


def finish(source, output, cx, cy, radius, protected, reviewed=False,
           allow_rgb=False, qa_dir=None):
    source, output = Path(source), Path(output)
    if not reviewed:
        raise ValueError('Inspect framing and all important features before --reviewed')
    if source.resolve() == output.resolve() or output.exists():
        raise ValueError('Input and existing outputs must not be overwritten')
    if output.suffix.lower() != '.png':
        raise ValueError('Output must have a .png extension')
    qa = Path(qa_dir) if qa_dir else None
    if qa and qa.exists():
        raise ValueError('QA directory must be new; existing files are never overwritten')
    with Image.open(source) as image:
        if getattr(image, 'n_frames', 1) != 1:
            raise ValueError('Animated inputs are unsupported')
        source_mode = image.mode
        if source_mode == 'RGB' and allow_rgb:
            original = image.convert('RGBA')
        elif source_mode == 'RGBA':
            original = image.copy()
        else:
            raise ValueError('Require RGBA, or RGB with explicit --allow-rgb; other modes unsupported')
        if image.getexif().get(274, 1) != 1:
            raise ValueError('Normalize EXIF orientation in a separate copy and review it first')
    w, h = original.size
    if not all(math.isfinite(v) for v in (cx, cy, radius)) or radius < 4:
        raise ValueError('Circle values must be finite and radius >= 4')
    if cx-radius < 0 or cy-radius < 0 or cx+radius > w-1 or cy+radius > h-1:
        raise ValueError('Circle must fit within the image; regenerate framing instead of clipping features')
    if not protected:
        raise ValueError('Provide visually reviewed extreme feature points')
    for px, py in protected:
        if (not all(math.isfinite(v) for v in (px, py)) or
                not (0 <= px < w and 0 <= py < h) or
                math.hypot(px-cx, py-cy) > radius-3):
            raise ValueError('Protected feature outside safe circle; revise framing')
    mask = Image.new('L', (w, h))
    values = bytearray(w*h)
    offsets = (-.375, -.125, .125, .375)
    for y in range(h):
        for x in range(w):
            distance = math.hypot(x-cx, y-cy)
            if distance < radius-1:
                coverage = 255
            elif distance > radius+1:
                coverage = 0
            else:
                count = sum((x+dx-cx)**2 + (y+dy-cy)**2 <= radius**2
                            for dx in offsets for dy in offsets)
                coverage = round(count*255/16)
            values[y*w+x] = coverage
    mask.frombytes(bytes(values))
    result = original.copy()
    result.putalpha(ImageChops.darker(original.getchannel('A'), mask))
    # Deliberately copy pixel bytes only, avoiding personal EXIF/metadata in output.
    result = Image.frombytes('RGBA', result.size, result.tobytes())
    before, after = list(original.getdata()), list(result.getdata())
    assert all(a[:3] == b[:3] and b[3] <= a[3] for a, b in zip(before, after))
    assert all(a == b for i, (a, b) in enumerate(zip(before, after))
               if math.hypot(i % w-cx, i // w-cy) < radius-1)
    assert all(b[3] == 0 for i, b in enumerate(after)
               if math.hypot(i % w-cx, i // w-cy) > radius+1)
    report = dict(center=[cx, cy], radius=radius, source_mode=source_mode,
                  rgb_unchanged=True, interior_rgba_unchanged=True,
                  outside_alpha_max=0, outside_definition='pixel centers farther than radius + 1',
                  alpha_never_increased=True, protected_points=protected,
                  rgb_conversion=source_mode == 'RGB',
                  changed_alpha_pixels=sum(a[3] != b[3] for a,b in zip(before, after)))
    # Encode first; exclusive create protects against accidental overwrite races.
    buffer = io.BytesIO()
    result.save(buffer, format='PNG')
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as handle:
        handle.write(buffer.getvalue())
    if qa:
        qa.mkdir(parents=True, exist_ok=False)
        for name, color in [('dark', (28, 31, 38, 255)), ('light', (255, 255, 255, 255))]:
            background = Image.new('RGBA', (w,h), color)
            background.alpha_composite(result)
            with (qa / (name + '.png')).open('xb') as handle:
                background.convert('RGB').save(handle, format='PNG')
        with (qa / 'verification.json').open('x') as handle:
            json.dump(report, handle, indent=2)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source'); parser.add_argument('output')
    parser.add_argument('--center', nargs=2, type=float, required=True)
    parser.add_argument('--radius', type=float, required=True)
    parser.add_argument('--protect-point', nargs=2, type=float, action='append', required=True)
    parser.add_argument('--reviewed', action='store_true')
    parser.add_argument('--allow-rgb', action='store_true', help='Add alpha=255 to decoded RGB first; no background removal')
    parser.add_argument('--qa-dir', help='New directory for dark/light previews and JSON verification')
    args = parser.parse_args()
    try:
        report = finish(args.source, args.output, *args.center, args.radius,
                        args.protect_point, args.reviewed, args.allow_rgb, args.qa_dir)
        print(json.dumps(report, indent=2))
    except (ValueError, OSError) as error:
        parser.error(str(error))

if __name__ == '__main__':
    main()
