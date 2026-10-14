"""Installer-root / traversal regression, no downloads or application data."""
from io import BytesIO
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import install_readers as installer


def main():
    with tempfile.TemporaryDirectory(prefix='tulpa-reader-install-') as tmp:
        root=Path(tmp)/'checkout';root.mkdir()
        with patch.object(installer,'ROOT',root),patch.object(installer,'urlopen',return_value=BytesIO(b'fixture-license')) as request:
            receipt=installer.download(('fixture/repo','fixed-commit','LICENSE','qq-reader'))
            assert (root/'tools/qq-reader/LICENSE').read_bytes()==b'fixture-license'
            assert receipt['source_sha256']==receipt['installed_sha256']
            assert request.call_args.args[0]=='https://raw.githubusercontent.com/fixture/repo/fixed-commit/LICENSE'
            for directory,relative in [('other','LICENSE'),('qq-reader','../../escape'),('qq-reader',str(root/'outside'))]:
                try:installer.install_target(directory,relative)
                except ValueError:pass
                else:raise AssertionError('escaped installation root')
        (root/'nested').mkdir()
        with patch.object(installer,'ROOT',root/'nested/..'):
            assert installer.install_target('wechat-reader','wechatauto/db.py')==root/'tools/wechat-reader/wechatauto/db.py'
    print('PASS isolated checkout install, canonical root and path containment; no network')


if __name__=='__main__':main()
