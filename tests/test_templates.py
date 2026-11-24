from __future__ import annotations

from conftest import run_script

VENUES = ["cvpr2025", "iclr2025", "ieeeconf", "arxiv"]


def test_list_venues():
    completed = run_script("skills/research-template/scripts/init_template.py", "--list")
    assert completed.returncode == 0
    for venue in VENUES:
        assert venue in completed.stdout


def test_scaffold_all_templates(tmp_path):
    for venue in VENUES:
        out = tmp_path / venue
        completed = run_script(
            "skills/research-template/scripts/init_template.py",
            "--venue", venue,
            "--out", str(out),
        )
        assert completed.returncode == 0, completed.stderr
        assert (out / "template.tex").exists()
        assert (out / "guidelines.md").exists()
        assert (out / "references.bib").exists()
