import pytest

from check_version import BranchFileNotFound
from check_version import BranchPathNotFound
from check_version import get_version


def test_get_version_local_missing_path_raises_keyerror(tmp_path, monkeypatch):
    file_path = tmp_path / "config.toml"
    file_path.write_text('[section]\nversion = "1.0.0"\n')
    monkeypatch.chdir(tmp_path)

    with pytest.raises(KeyError):
        get_version("config.toml", "other/version")


def test_get_version_branch_missing_path_raises_branch_path_not_found(
    tmp_path, monkeypatch
):
    file_path = tmp_path / "config.toml"
    file_path.write_text('[section]\nversion = "1.0.0"\n')
    monkeypatch.chdir(tmp_path)

    def fake_fetch(branch, file_path):
        return '[section]\nversion = "1.0.0"\n'

    monkeypatch.setattr("check_version.fetch_file_from_branch", fake_fetch)

    with pytest.raises(BranchPathNotFound):
        get_version("config.toml", "other/version", branch="main")


def test_get_version_branch_missing_file_still_raises_branch_file_not_found(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    def fake_fetch(branch, file_path):
        raise BranchFileNotFound(f"Could not fetch {file_path} from {branch=}")

    monkeypatch.setattr("check_version.fetch_file_from_branch", fake_fetch)

    with pytest.raises(BranchFileNotFound):
        get_version("config.toml", "section/version", branch="main")
