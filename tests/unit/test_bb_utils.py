"""
Unit tests for wic.bb.utils.mkdirhier: a mkdir -p wrapper that rejects
unexpanded bitbake variables and, on error, tolerates an already-existing
directory while re-raising every real failure.
"""
import sys
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parent.parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from wic.bb.utils import mkdirhier


class TestMkdirhier:
    def test_creates_missing_directories(self, tmp_path):
        target = tmp_path / "a" / "b" / "c"
        mkdirhier(str(target))
        assert target.is_dir()

    def test_existing_directory_is_accepted(self, tmp_path):
        # Calling it on a directory that already exists is not an error.
        mkdirhier(str(tmp_path))
        mkdirhier(str(tmp_path))
        assert tmp_path.is_dir()

    def test_unexpanded_bitbake_variable_is_rejected(self, tmp_path):
        target = tmp_path / "${WORKDIR}" / "sub"
        with pytest.raises(Exception, match="unexpanded bitbake variable"):
            mkdirhier(str(target))
        assert not (tmp_path / "${WORKDIR}").exists()

    def test_plain_brace_is_not_treated_as_a_variable(self, tmp_path):
        # Only the '${' marker trips the guard; a bare brace is a legal
        # (if unusual) directory name.
        target = tmp_path / "plain{brace"
        mkdirhier(str(target))
        assert target.is_dir()

    def test_dollar_without_brace_is_allowed(self, tmp_path):
        # The guard keys on the literal '${' marker; a '$' on its own is
        # not an unexpanded variable and is a legal directory name.
        target = tmp_path / "price$5"
        mkdirhier(str(target))
        assert target.is_dir()

    def test_path_under_a_file_raises(self, tmp_path):
        # A parent component that is a regular file makes the underlying
        # mkdir fail; the error must surface rather than be swallowed.
        afile = tmp_path / "afile"
        afile.write_text("x")
        with pytest.raises(OSError):
            mkdirhier(str(afile / "sub"))

    def test_existing_file_at_target_raises(self, tmp_path):
        # The target already exists but is a file, not a directory: the
        # error must propagate rather than be tolerated.
        afile = tmp_path / "afile"
        afile.write_text("x")
        with pytest.raises(OSError):
            mkdirhier(str(afile))

    def test_concurrent_creation_is_treated_as_success(self, tmp_path, monkeypatch):
        # If the directory appears while mkdirhier runs (a create race
        # with another process), that is success, not an error.
        import errno

        import wic.bb.utils as bb_utils

        target = tmp_path / "made-concurrently"

        def racing_makedirs(path, exist_ok=False):
            target.mkdir()  # someone else wins the race
            raise OSError(errno.EEXIST, "File exists", str(path))

        monkeypatch.setattr(bb_utils.os, "makedirs", racing_makedirs)
        mkdirhier(str(target))  # must not raise
        assert target.is_dir()
