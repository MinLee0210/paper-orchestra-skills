from __future__ import annotations

import os
import shutil
import subprocess

import pytest

from conftest import ROOT

pytestmark = pytest.mark.skipif(shutil.which("bash") is None, reason="bash is required")

MARKER = ".research-orchestra-installed"
SKILLS = sorted(p.name for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").exists())


def shim(directory, name, body):
    directory.mkdir(exist_ok=True)
    path = directory / name
    path.write_text("#!/bin/sh\n" + body + "\n")
    path.chmod(0o755)


def install(*args, home, platform=None, path_prefix=None, extra_env=None):
    env = dict(os.environ, HOME=str(home))
    env.pop("INSTALL_SH_PLATFORM", None)
    if platform:
        env["INSTALL_SH_PLATFORM"] = platform
    if path_prefix:
        env["PATH"] = f"{path_prefix}{os.pathsep}{env['PATH']}"
    env.update(extra_env or {})
    return subprocess.run(
        ["bash", str(ROOT / "install.sh"), *args],
        capture_output=True, text=True, env=env, cwd=str(ROOT),
    )


def test_script_is_lf_and_pinned_by_gitattributes():
    assert b"\r" not in (ROOT / "install.sh").read_bytes()
    assert "*.sh text eol=lf" in (ROOT / ".gitattributes").read_text()


def test_unix_default_symlinks_and_uninstall(tmp_path):
    target = tmp_path / "skills"
    done = install("--target", str(target), home=tmp_path)
    assert done.returncode == 0, done.stderr
    assert all((target / name).is_symlink() for name in SKILLS)

    again = install("--target", str(target), home=tmp_path)
    assert again.stdout.count("  ok      ") == len(SKILLS)

    removed = install("--target", str(target), "--uninstall", home=tmp_path)
    assert removed.returncode == 0
    assert not any((target / name).exists() for name in SKILLS)
    assert (ROOT / "skills" / "research-orchestra" / "SKILL.md").exists()


def test_copy_mode_marks_copies_and_refreshes_them(tmp_path):
    target = tmp_path / "skills"
    done = install("--target", str(target), "--copy", home=tmp_path)
    assert done.returncode == 0, done.stderr
    for name in SKILLS:
        assert not (target / name).is_symlink()
        assert (target / name / "SKILL.md").exists()
        assert (target / name / MARKER).exists()
    assert f"{len(SKILLS)} skills were copied" in done.stdout

    stale = target / "research-orchestra" / "stale.txt"
    stale.write_text("old")
    again = install("--target", str(target), "--copy", home=tmp_path)
    assert again.returncode == 0
    assert not stale.exists(), "a re-run must refresh our own copy"


def test_uninstall_removes_only_what_the_script_created(tmp_path):
    target = tmp_path / "skills"
    mine = target / "somebody-elses-skill"
    mine.mkdir(parents=True)
    (mine / "SKILL.md").write_text("not ours")
    foreign = target / "research-orchestra"
    foreign.mkdir()
    (foreign / "notes.txt").write_text("a user's own directory with a clashing name")

    done = install("--target", str(target), "--copy", home=tmp_path)
    assert done.returncode == 0
    assert "skip    research-orchestra (exists; use --force)" in done.stderr
    assert not (foreign / MARKER).exists()

    install("--target", str(target), "--uninstall", home=tmp_path)
    assert (mine / "SKILL.md").exists()
    assert (foreign / "notes.txt").exists(), "an unmarked directory must survive --uninstall"
    assert not (target / "research-outline").exists()

    forced = install("--target", str(target), "--copy", "--force", home=tmp_path)
    assert forced.returncode == 0
    assert (foreign / MARKER).exists()


def test_windows_falls_back_to_copy_when_symlinks_are_refused(tmp_path):
    bin_dir = tmp_path / "bin"
    shim(bin_dir, "ln", "echo 'Operation not permitted' >&2; exit 1")
    target = tmp_path / "skills"
    done = install("--target", str(target), home=tmp_path, platform="windows", path_prefix=bin_dir)
    assert done.returncode == 0, done.stderr
    assert all((target / name / MARKER).exists() for name in SKILLS)
    assert not any((target / name).is_symlink() for name in SKILLS)
    assert "Windows refused symlinks" in done.stdout

    removed = install("--target", str(target), "--uninstall", home=tmp_path, platform="windows", path_prefix=bin_dir)
    assert removed.returncode == 0
    assert not any((target / name).exists() for name in SKILLS)
    assert (ROOT / "skills" / "research-orchestra" / "SKILL.md").exists()


def test_windows_cleans_up_when_ln_silently_copies(tmp_path):
    """MSYS without winsymlinks makes `ln -s` copy instead of link. That must not be reported as linked."""
    bin_dir = tmp_path / "bin"
    shim(bin_dir, "ln", 'cp -R "$2" "$3"')
    target = tmp_path / "skills"
    done = install("--target", str(target), home=tmp_path, platform="windows", path_prefix=bin_dir)
    assert done.returncode == 0, done.stderr
    assert "linked" not in done.stdout.split("Installed")[0]
    assert all((target / name / MARKER).exists() for name in SKILLS)


def test_windows_uses_symlinks_when_allowed(tmp_path):
    target = tmp_path / "skills"
    done = install("--target", str(target), home=tmp_path, platform="windows")
    assert done.returncode == 0, done.stderr
    assert all((target / name).is_symlink() for name in SKILLS)
    assert "copied" not in done.stdout


def test_windows_default_target_follows_userprofile_not_home(tmp_path):
    profile = tmp_path / "Users" / "someone"
    other_home = tmp_path / "msys-home"
    other_home.mkdir()
    bin_dir = tmp_path / "bin"
    shim(bin_dir, "cygpath", 'echo "$2"')  # `cygpath -u X` -> X
    done = install(
        "--copy", home=other_home, platform="windows", path_prefix=bin_dir,
        extra_env={"USERPROFILE": str(profile)},
    )
    assert done.returncode == 0, done.stderr
    assert (profile / ".claude" / "skills" / "research-orchestra" / "SKILL.md").exists()
    assert (profile / ".config" / "opencode" / "skills" / "research-orchestra" / "SKILL.md").exists()
    assert not (other_home / ".claude").exists()
