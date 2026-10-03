import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image

SPEC = importlib.util.spec_from_file_location('finish_circle', Path(__file__).parents[1] / 'scripts/finish_circle.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class CircleTests(unittest.TestCase):
    def test_reject_rgb_transparency_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'keyed.png'
            Image.new('RGB', (64,64), (12,34,56)).save(source, transparency=(12,34,56))
            with self.assertRaisesRegex(ValueError, 'transparency metadata'):
                MODULE.finish(source, root / 'out.png', 31.5, 31.5, 28,
                              [(31,10)], reviewed=True, allow_rgb=True)
            self.assertFalse((root / 'out.png').exists())
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base/'input.png'
        self.output = self.base/'output.png'
        image = Image.new('RGBA', (64,64))
        image.putdata([(x*4, y*4, 117, (x+y)%256) for y in range(64) for x in range(64)])
        image.save(self.source)
    def call(self, **kwargs):
        args = dict(cx=31.5, cy=31.5, radius=28, protected=[(31,10)], reviewed=True)
        args.update(kwargs)
        return MODULE.finish(self.source, self.output, **args)
    def test_pixels_and_qa(self):
        original = self.source.read_bytes()
        report = self.call(qa_dir=self.base/'qa')
        self.assertEqual(original, self.source.read_bytes())
        with Image.open(self.source) as a, Image.open(self.output) as b:
            self.assertEqual(a.convert('RGB').tobytes(), b.convert('RGB').tobytes())
            self.assertEqual(a.getpixel((31,31)), b.getpixel((31,31)))
            self.assertEqual(b.getpixel((0,0))[3], 0)
            self.assertTrue(all(y<=x for x,y in zip(a.getchannel('A').getdata(), b.getchannel('A').getdata())))
        self.assertTrue(report['interior_rgba_unchanged'])
        self.assertTrue((self.base/'qa/dark.png').exists())
    def test_refuses_overwrite(self):
        self.call()
        with self.assertRaises(ValueError): self.call()
        self.output = self.source
        with self.assertRaises(ValueError): self.call()
    def test_requires_review(self):
        with self.assertRaises(ValueError): self.call(reviewed=False)
    def test_protection(self):
        for points in ([], [(0,0)], [(float('nan'),0)], [(64,32)]):
            with self.assertRaises(ValueError): self.call(protected=points)
    def test_geometry(self):
        for kw in ({'radius':float('nan')},{'radius':2},{'cx':0},{'radius':100}):
            with self.assertRaises(ValueError): self.call(**kw)
    def test_rgb_explicit(self):
        Image.new('RGB',(64,64),(21,42,63)).save(self.source)
        with self.assertRaises(ValueError): self.call()
        report = self.call(allow_rgb=True)
        self.assertTrue(report['rgb_conversion'])
        with Image.open(self.output) as image:
            self.assertEqual(image.getpixel((31,31)),(21,42,63,255))
            self.assertEqual(image.getpixel((0,0)),(21,42,63,0))
    def test_existing_qa(self):
        qa = self.base/'qa'; qa.mkdir()
        with self.assertRaises(ValueError): self.call(qa_dir=qa)
        self.assertFalse(self.output.exists())
    def test_palette_rejected(self):
        Image.new('P',(64,64)).save(self.source)
        with self.assertRaises(ValueError): self.call(allow_rgb=True)
    def test_cli(self):
        run = subprocess.run([sys.executable,str(SPEC.origin),str(self.source),str(self.output),
            '--center','31.5','31.5','--radius','28','--protect-point','31','10','--reviewed'],capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertIn('"rgb_unchanged": true',run.stdout)

if __name__ == '__main__': unittest.main()
