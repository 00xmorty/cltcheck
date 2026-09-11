import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Checks(unittest.TestCase):
    def run_case(self, *, override=None, selected=True, clang=True, sdk=True,
                 full=False, require=False, platform='Darwin', selection_error=False):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dev = root / 'Developer'
            if selected:
                dev.mkdir()
            tool = root / 'clang'
            if clang:
                tool.write_text('#!/bin/sh\necho SHOULD_NOT_EXECUTE\n')
                tool.chmod(0o755)
            sdkpath = root / 'SDK'
            if sdk:
                sdkpath.mkdir()
            if full:
                (dev / 'usr/bin').mkdir(parents=True)
                (dev / 'usr/bin/xcodebuild').touch()
                (dev / 'usr/bin/xcodebuild').chmod(0o755)
                (dev / 'Platforms').mkdir()
            env = dict(os.environ)
            env.pop('DEVELOPER_DIR', None)
            env.update(TOOL=str(tool), SDK=str(sdkpath), SELECTED=str(dev),
                       PLATFORM=platform, SELECT_ERROR=str(int(selection_error)))
            if override is not None:
                env['DEVELOPER_DIR'] = str(dev) if override == 'valid' else override
            script = '''source ./cltcheck
probe() {
 case "$1" in
 platform) print -r -- "$PLATFORM" ;;
 selected) (( SELECT_ERROR )) && return 1; print -r -- "$SELECTED" ;;
 clang) print -r -- "$TOOL" ;;
 sdk) print -r -- "$SDK" ;;
 esac
}
main "$@"
'''
            args = ['zsh', '-c', script, 'test']
            if require:
                args.append('--require-xcode')
            proc = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True)
            self.assertNotIn(td, proc.stdout)
            self.assertNotIn('SHOULD_NOT_EXECUTE', proc.stdout)
            self.assertEqual(proc.stderr, '')
            return proc

    def test_healthy(self):
        self.assertEqual(self.run_case().returncode, 0)

    def test_missing_selection(self):
        self.assertEqual(self.run_case(selected=False).returncode, 1)

    def test_unreadable_selection(self):
        self.assertEqual(self.run_case(selection_error=True).returncode, 2)

    def test_bad_override(self):
        p = self.run_case(override='/nonexistent/example-cltcheck')
        self.assertEqual(p.returncode, 1)
        self.assertIn('DEVELOPER_DIR points to a missing', p.stdout)

    def test_empty_override(self):
        self.assertEqual(self.run_case(override='').returncode, 2)

    def test_valid_override(self):
        self.assertEqual(self.run_case(override='valid').returncode, 0)

    def test_missing_clang(self):
        self.assertEqual(self.run_case(clang=False).returncode, 2)

    def test_missing_sdk(self):
        self.assertEqual(self.run_case(sdk=False).returncode, 2)

    def test_clt_not_full_xcode(self):
        self.assertEqual(self.run_case(require=True).returncode, 1)

    def test_full_xcode(self):
        self.assertEqual(self.run_case(require=True, full=True).returncode, 0)

    def test_linux(self):
        self.assertEqual(self.run_case(platform='Linux').returncode, 2)

    def test_cli(self):
        for arg, code in [('--help', 0), ('--version', 0), ('--bad-option', 2)]:
            p = subprocess.run(['zsh', './cltcheck', arg], cwd=ROOT,
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, code)


if __name__ == '__main__':
    unittest.main()
