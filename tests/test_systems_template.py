from __future__ import annotations

from conftest import run_script

SCRIPT = "skills/research-systems-paper-writing/scripts/init_systems_template.py"
VENUES = ["osdi2026", "sosp2026", "asplos2027", "nsdi2027"]


def test_list_venues():
    completed = run_script(SCRIPT, "--list")
    assert completed.returncode == 0
    assert completed.stdout.split() == sorted(VENUES)


def test_scaffold_meets_pipeline_contract(tmp_path):
    for venue in VENUES:
        out = tmp_path / venue / "latex_template"
        completed = run_script(SCRIPT, "--venue", venue, "--out", str(out))
        assert completed.returncode == 0, completed.stderr
        for name in ("template.tex", "guidelines.md", "references.bib"):
            assert (out / name).exists(), f"{venue}: missing {name}"
        assert not (out / "main.tex").exists()
        guidelines = (out / "guidelines.md").read_text()
        assert "current call for papers" in guidelines
        assert "%%%" not in guidelines


def test_scaffold_passes_input_validator(tmp_path):
    project = tmp_path / "paper_project"
    raw = project / "raw_materials"
    raw.mkdir(parents=True)
    (raw / "idea.md").write_text("A scheduler that places jobs by comparing queue depth across racks.\n")
    (raw / "experimental_log.md").write_text("| System | Latency |\n|---|---|\n| Ours | 41 |\n")
    out = project / "latex_template"
    assert run_script(SCRIPT, "--venue", "osdi2026", "--out", str(out)).returncode == 0
    completed = run_script("skills/paper-inputs/scripts/validate_inputs.py", str(project))
    assert completed.returncode == 0, completed.stdout
