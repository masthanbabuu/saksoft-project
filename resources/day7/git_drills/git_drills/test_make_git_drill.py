import subprocess

import pytest

import make_git_drill


def run_git(folder, *args, check=False):
    return subprocess.run(["git", "-C", str(folder), *args], capture_output=True, text=True, check=check)


@pytest.fixture
def repo(tmp_path):
    folder = tmp_path / "drill"
    make_git_drill.build(folder)
    return folder


def test_branches_exist(repo):
    branches = run_git(repo, "branch", "--format=%(refname:short)").stdout.split()
    assert {"main", "feature/a", "feature/b", "oops"} <= set(branches)


def test_merging_the_two_feature_branches_conflicts(repo):
    run_git(repo, "switch", "feature/a", check=True)
    result = run_git(repo, "merge", "feature/b")
    assert result.returncode != 0
    assert "CONFLICT" in result.stdout
    assert "<<<<<<<" in (repo / "policy.txt").read_text(encoding="utf-8")


def test_fake_secret_is_only_on_the_oops_branch(repo):
    assert not (repo / "settings.txt").exists()          # we are on main
    run_git(repo, "switch", "oops", check=True)
    assert "FAKE-NOT-A-REAL-KEY" in (repo / "settings.txt").read_text(encoding="utf-8")


def test_refuses_a_folder_that_is_not_empty(tmp_path):
    (tmp_path / "x.txt").write_text("x", encoding="utf-8")
    with pytest.raises(SystemExit):
        make_git_drill.build(tmp_path)
